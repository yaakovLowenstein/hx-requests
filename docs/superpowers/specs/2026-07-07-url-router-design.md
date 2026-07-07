# Design: Mount HxRequests on real URLs (#10, the URL router)

Status: **draft for review** — no implementation until approved. This is the
plan for `IMPROVEMENTS.md` item #10.

## What this is (and is not)

This plans the **additive URL router**: generate real `/hx/<name>/` URLs from
the registry and route named handlers through them, so `reverse()`, URL-level
decorators/middleware, per-endpoint caching, and `show_urls` all start working.

It is **deliberately scoped as step 1 of the "real Django views" arc** (the
IMPROVEMENTS.md appendix), not that rewrite. The rewrite (rebuild the base
classes mixin-first on `View` + `SingleObjectMixin` + `FormMixin`, change the
`form_valid` signature) is a separate 1.0 effort with a long-lived-branch risk
the appendix itself flags. Two reasons to do the router first instead of folding
it in:

- **It ships in the reviewable, stacked style that has worked for #1–#9.** The
  rewrite does not.
- **#9 already banked half the rewrite's payoff.** Per-handler auth
  (`login_required` / `permission_required` / `has_permission`) is done. The
  rewrite's headline "deletes #3 and most of #9" would now partly *re-do* work we
  just shipped. Better to treat the rewrite as a deliberate later step.

The router is only worth doing if it **moves dispatch onto the URLs** rather than
adding a parallel path that the rewrite later rips out. That is the design below:
the endpoint becomes the real request cycle for a named handler; the page-view
handoff (`HtmxViewMixin`) stays only for backward compatibility during migration.

### Non-goals (YAGNI / explicitly out of scope)

- No `form_valid(self, form)` signature change — that is the rewrite.
- Do **not** delete per-handler auth, the registry, or the base-class hierarchy.
- No subclassing of Django generic views (`FormView`, `UpdateView`) — the
  appendix explains why that fights the framework at every override.

## The value that must survive (do not regress)

From IMPROVEMENTS.md's "genuinely good at" section — the router must preserve all
three:

1. **Many handlers, one registration.** Declaring a handler stays "add a class
   with a `name`." URLs are *generated from the registry*; users never
   hand-author a `path()` per handler.
2. **The form/modal round-trip.** Untouched — it lives in the response mixins,
   which the router does not change.
3. **Composable trigger/confirm mixins.** Untouched — they touch
   triggers/headers/`post`, not routing.

Plus the **plain-htmx fall-through** (sort/filter/paginate requests that omit a
handler name and hit the underlying page view) must keep working.

## Architecture

### 1. Registry → urlpatterns

Add `HxRequestRegistry.get_urls()`. It calls `initialize()` (the existing AST
scan, which yields *names* without importing handler classes — lazy loading is
preserved) and returns one `path()` per registered name:

```python
# hx_registry.py
@classmethod
def get_urls(cls):
    cls.initialize()
    return [
        path(f"{name}/", HxEndpointView.as_view(hx_name=name), name=name)
        for name in cls._registry
    ]
```

Users wire it once, in their root URLconf:

```python
from hx_requests.hx_registry import HxRequestRegistry

urlpatterns = [
    path("hx/", include((HxRequestRegistry.get_urls(), "hx_requests"), namespace="hx")),
]
```

`reverse("hx:edit_user")` → `/hx/edit_user/`. Only handler *names* are needed to
build the patterns; the handler class still imports lazily on first request via
`get_hx_request(name)`.

**Startup-ordering caveat (must test).** The root URLconf is built after
`apps.populate()`, so the app registry is populated when `get_urls()` runs. But
`get_urls()` calls `initialize()` (an AST filesystem scan) at URLconf-build time.
Confirm this is safe and cheap, and that a later hot-reload / test `reset()` does
not leave stale patterns. Patterns are a snapshot at URLconf build; document that
adding a handler needs a server restart (same as any URLconf change).

### 2. `HxEndpointView` — the new request cycle

A thin Django `View` that becomes the real endpoint for one named handler:

```python
class HxEndpointView(View):
    hx_name = None  # set per-path by as_view(hx_name=...)

    def dispatch(self, request, *args, **kwargs):
        hx_cls = HxRequestRegistry.get_hx_request(self.hx_name)
        if hx_cls is None:
            raise Http404(...)
        payload = self._verify_token(request)          # reuse today's token logic
        if payload["name"] != self.hx_name:            # path binding (see below)
            raise Http404(...)
        hx_request = hx_cls()
        hx_request.view = None                          # no page view here (see §3)
        hx_request._setup_hx_request(request, *args, **kwargs)
        return hx_request.dispatch(hx_request.request, *args, **kwargs)
```

Key points:

- **The handler name comes from the URL path, not a client query param.** This
  closes the security-review "Path binding" note: a token minted for `edit_user`
  can no longer be replayed against `delete_user`'s endpoint — the endpoint checks
  `payload["name"] == self.hx_name` and 404s on mismatch. (Cheaper and clearer
  than the per-name-salt alternative from that note.)
- **Per-handler auth is unchanged** — `HxRequest.dispatch` still runs
  `check_permissions` before `get`/`post`. It works identically here.
- **Django auth now composes natively.** Because the endpoint is a real `View`,
  `login_required` decorators / `LoginRequiredMixin` can wrap it, and the
  `hx_requests.W001` MRO trap simply does not exist on this path (there is no
  page-view handoff to short-circuit). W001 stays for the legacy page-view path.

The token-verification and GET-sanitizing logic currently in
`HtmxViewMixin._resolve_hx_token` / `get_hx_extra_kwargs` is factored into a
shared helper both `HtmxViewMixin` (legacy) and `HxEndpointView` call, so there is
one trust boundary, not two.

### 3. Context sharing — the one real cost

With a handler on its own URL there is **no page view in the cycle**, so today's
implicit `view.get().context_data` harvest cannot happen. Decision (matches the
appendix's recommended migration path and #4's explicit-opt-in direction):

- **`shares_context_from = SomeView`** (opt-in class attribute). When set, the
  endpoint instantiates that view, runs `view.setup(request, ...)`, the
  type-specific `object` / `object_list` preamble, and `get_context_data()`, and
  merges the result — reproducing today's behavior with a one-line declaration.
  The dead `django_views.py` removed in #8a was a half-built version of exactly
  these per-view-type setup helpers; resurrect that shape here.
- **Document the shared-context mixin as the cleaner long-term pattern** (extract
  shared context into a mixin both the page view and the handler inherit — no
  cross-view instantiation).

Handlers with no `shares_context_from` simply get no page-view context on the
router path — which is the explicit, non-surprising behavior #4 was steering
toward. `get_context_on_GET` / `get_context_on_POST` / `hx_object` still work.

### 4. Template tags call `reverse()` — additively

`get_url()` (utils.py) changes from `f"{request.path}?{token}"` to preferring the
router, with a zero-config fallback:

```python
try:
    base = reverse(f"hx:{hx_request_name}")   # router installed
except NoReverseMatch:
    base = request.path                        # legacy page-view dispatch
```

So a project that has not wired the router keeps working unchanged; a project that
has gets real URLs with no template edits. The signed `hx` token rides on the
query string exactly as today (`/hx/edit_user/?hx=...`), so signing (#1) composes
unchanged. `use_current_url` and loose page-filter params behave as they do now.

### 5. Plain-htmx fall-through

Unaffected. The router only mounts *named* handlers. Token-less HTMX requests
(sort/filter/paginate that the user wires with their own `hx-get` on a table) still
hit the page view, which still exists and still handles them. Nothing about that
path moves.

## Data flow (router path)

```
browser  --GET /hx/edit_user/?hx=<token>-->  HxEndpointView(hx_name="edit_user")
  -> get_hx_request("edit_user")                  # lazy import, cached
  -> verify token; assert payload.name == "edit_user"
  -> HxRequest()._setup_hx_request(request)        # object resolution via get_queryset (#2)
  -> HxRequest.dispatch()                          # check_permissions (#9), GET-write guard (#202)
  -> get()/post() -> Renderer -> HTMX partial
```

## Error handling

- Unknown name / unregistered: `Http404` (as today, with the #8c debug log line).
- Missing / tampered / unsigned token: `Http404` (reuse `get_hx_payload`).
- Token name ≠ URL name: `Http404` (new — the path-binding check).
- Auth: `Http404` (anon) / `PermissionDenied` (authed, no perm) — unchanged, from
  per-handler auth.
- `HttpResponseNotAllowed` for an unsupported method — unchanged.

## Testing strategy

- **Registry:** `get_urls()` returns one pattern per registered name and does
  **not** import handler classes (assert entries stay tuples / lazy).
- **Resolution:** `reverse("hx:<name>")` resolves; the URL dispatches to the right
  handler.
- **Path binding:** a token minted for handler A, sent to handler B's URL, 404s.
- **Auth parity:** re-run the per-handler-auth scenarios (login/permission/
  has_permission) through the new URL — same 404/403/200 outcomes.
- **GET-write guard (#202):** still fires on the router path.
- **Template tag:** emits a `reverse()` URL when the router is installed; falls
  back to `request.path` (with `hx_request_name` for legacy dispatch) when it is
  not.
- **Context sharing:** `shares_context_from` reproduces the declared view's
  context; absent it, the handler gets no page-view context (explicit).
- **Fall-through:** a token-less HTMX request still hits the page view.
- **Startup ordering:** importing the URLconf builds patterns without error when
  the registry has not been touched yet.

Tests drive real requests through `reverse()`-resolved URLs (extend
`tests/helpers.py` with an `hx_get_url` / `hx_post_url` that go through the router)
rather than hand-instantiating handlers.

## Shipping

Additive: the router and the legacy page-view dispatch coexist, so existing
projects are untouched until they wire the `include()`. The endgame — per the #1
clean-break rationale and the user's stated dislike of long-lived deprecation
shims — is a later `feat!:` that makes the router the only path and removes
`HtmxViewMixin`'s query-param dispatch. This spec ships the additive introduction;
the removal is a separate, later decision.

Docs: new "Mounting HxRequests on URLs" how-to (wiring the `include`, `reverse`
usage, `shares_context_from`), and an update to the securing/how-it-works pages
noting Django auth composes natively on the router path.

## Open questions (resolve before/while writing the implementation plan)

1. **Legacy dispatch: deprecation window vs. clean break.** Ship additive now and
   remove query-param dispatch in a later `feat!:` (recommended), or break in this
   PR? The user dislikes shims, which argues for a nearer clean break — but the
   router forces the `shares_context_from` migration, which argues for a window.
2. **Namespace.** Fixed `hx:` namespace (assumed above) vs. configurable, for
   projects that mount the router more than once or want a custom prefix.
3. **`get_urls()` timing.** Confirm calling `initialize()` at URLconf-build time is
   acceptable, or whether patterns should be built lazily on first resolve.
4. **`shares_context_from` for `object`/`object_list` views.** How much per-view-
   type preamble to resurrect from `django_views.py` — `ListView` and
   `DetailView` need `object_list` / `object` set before `get_context_data()`.
```
