# hx-requests — Audit Findings & Remediation Plan

A prioritized list of issues found in an architecture/code audit, with concrete
fix plans. Ordered by leverage: do them top to bottom. Each item notes the
mechanism, the code involved, the fix, and how to ship it without breaking users.

Severity legend: 🔴 security / correctness · 🟠 performance / robustness · 🟡 quality / adoption

---

## Summary of the core problem

The package dispatches to handlers by a client-supplied `hx_request_name` query
param, and passes objects/kwargs to those handlers as client-controlled,
tamperable query strings. Most of the package's complexity (the registry, the
security matrix, the serialization scheme) exists to compensate for that routing
decision. The two highest-leverage fixes — **signing the round-trip** and
**fixing the dispatch chain** — close the real vulnerabilities with small diffs.
The **URL router** is the longer-term adoption play.

---

## What the package is genuinely good at (protect this through every change)

Before the fixes, name the value — because several fixes below touch the machinery
that delivers it, and none of them should weaken it.

1. **Many handlers, one URL, one registration.** A single page (e.g. a data table
   with search/sort/paginate plus create/edit/delete modals plus per-row refresh)
   can host a dozen distinct HTMX interactions, each routed to its own class,
   without hand-wiring a dozen URLconf entries or a pile of
   `if request.headers.get(...)` branches. Plain htmx requests (sort/filter/page)
   that omit `hx_request_name` fall through to the underlying view automatically.
   **This is the founding pitch actually paying off** — and it's the thing that
   would be genuinely tedious to reproduce with N separate vanilla views. It is a
   *dispatch-ergonomics* win, not a context-inheritance one.

   *Note the tension with #10:* the URL router splits handlers onto their own URLs,
   which is literally "less one-URL." That's fine — what must be preserved is the
   *ergonomic*, not the mechanism: declaring a handler stays "add a class with a
   `name`" (no hand-authored URLconf per handler), and plain-htmx fall-through keeps
   working. #10 changes how routing happens under the hood; it must not change how a
   handler is declared. Don't cite this item to block #10 — preserve the ergonomic
   *through* the change.

2. **The form/modal round-trip.** `FormModalHxRequest` encodes the fiddly lifecycle
   every Django+HTMX team reinvents: invalid form re-renders the GET partial with
   errors inline (200, not a redirect), valid form closes the modal via
   `HX-Trigger` + retargets/reswaps, success/error messages ride along. Nobody in
   the ecosystem packages this. It's the clearest unowned value.

3. **Response-orchestration mixins compose cleanly.** Because handlers are classes
   with `get_triggers`/`post`/header hooks, cross-cutting behaviors — server-side
   confirm dialogs, "refresh this row", "refresh the parent tab" — drop in as small
   reusable mixins that stack via MRO. This composition is only possible because the
   response shaping is expressed declaratively on a class, and it survives any
   restructure untouched (the mixins only touch triggers/headers/`post`).

What is **not** carrying its weight: implicit context inheritance from the page view
(easy to make explicit; see #4) and the six-knob security matrix (per-handler
permission decorators are the idiomatic pattern people actually reach for; see #9).
The fixes below are calibrated to keep #1–#3 sharp while shedding the rest.

### Docs changes to surface this

The README's "why" section already leads with #1, which is right — but the docs bury
#2 and #3 as how-tos among many. Suggested changes:

- **Lead the landing page with #1 and #2 as the two headline features**, with a
  runnable data-table-with-modals example. That example *is* the pitch; it should be
  the first thing a visitor sees, not `basic_tutorial`.
- **Add an honest "How this compares" page**: vs. writing separate views (fine for
  1–2 interactions; this wins as they multiply), vs. `django-htmx` (that's the
  request/response *primitive* layer — hx-requests sits on top and should arguably
  depend on it, not compete), vs. template partials (they render fragments; they
  don't handle dispatch, forms, or the modal lifecycle — complementary, not
  competing). Positioning against these *increases* trust; pretending they don't
  exist decreases it.
- **Promote the mixin-composition pattern (#3) to a first-class "recipes" page**:
  confirm-before-action, refresh-a-row, refresh-a-tab. These are the reusable moves
  that make the package feel powerful; today a user has to invent them.
- **Stop marketing implicit context-sharing as a headline.** Document it as a minor
  convenience with an explicit opt-in (see #4), so nobody builds a mental model that
  the restructure later has to break.

---

## 1. 🔴 Sign the serialized round-trip (object + kwargs) — ✅ DONE

> **Fixed** on branch `feat/sign-round-trip`. `{name, object, kwargs}` are now packed
> into one HMAC-signed `hx` token (`django.core.signing`, constant salt — name is
> inside the signed blob so a per-name salt is redundant). `HtmxViewMixin` verifies
> the token in `dispatch` and rebuilds `request.GET` from *verified* data only;
> `get_hx_extra_kwargs` sources kwargs solely from the token (never raw GET). Closes
> the IDOR, cross-model swap, `___can_edit` context forgery, and garbage-500 vectors.
> Shipped as a clean `feat!` break. Docs updated to the token wire format.

**Problem.** The template tags emit loose, client-editable params:
`?hx_request_name=...&object=model_instance__app__model__pk&___key=value`.
On the way back in, `HtmxViewMixin.dispatch` deserializes these and:

- loads *any* model row the client names via `deserialize` → `_base_manager.get(pk=pk)`
  (`utils.py:21-28`) — bypasses default-manager scoping (soft-deletes, tenant filters),
- merges `___`-prefixed kwargs over URLconf kwargs (`views.py:39`),
- injects those kwargs straight into template context (`hx_requests.py:124-125`,
  `kwargs_as_context = True` default) where client values **win over view context**.

Concrete exploits this enables:
- **IDOR (same model, different pk):** `users__user__1` → `users__user__2`.
  GET renders victim's data into the form; POST saves over it. No error, no log.
- **Cross-model instance swap:** `users__user__1` → `shared__resident__1`.
  ModelForm's `construct_instance` copies overlapping fields and saves — renames
  the resident. (ModelForm never checks instance matches `Meta.model`.)
- **Context flag forgery:** append `&___can_edit=true` to any hx URL from page
  source. `json.loads("true")` → `True` → overrides `context["can_edit"]` → the
  `{% if can_edit %}` branch renders. Data leak if the flag gates data, not chrome.
- **500s on garbage:** `?___note=hello` (not JSON) → unhandled `JSONDecodeError`.

**Fix.** Pack everything the template tag controls into one HMAC-signed token via
`django.core.signing`. The client can read it (base64 JSON) but cannot forge it
without `SECRET_KEY`.

```python
# get_url() — server-rendered template-tag side (utils.py)
from django.core import signing
payload = {
    "name": hx_request_name,
    "obj": serialize(obj) if obj else None,
    "kwargs": serialize_kwargs(**kwargs),
}
token = signing.dumps(payload, salt="hx-requests")
url = f"{request.path}?hx={token}"
```

```python
# HtmxViewMixin dispatch side (views.py)
try:
    payload = signing.loads(request.GET["hx"], salt="hx-requests")
except (KeyError, signing.BadSignature):
    raise Http404  # tampered, truncated, or hand-crafted
```

This alone kills the forging in #1's exploits, the `___can_edit` injection, and
the `json.loads` 500s (garbage fails signature check before any deserializer runs).

**Caveats to document:**
- Signing stops *forging*, not *replay* — a token issued to A verifies when B
  sends it. Narrows enumeration hugely (only objects rendered into *someone's*
  page are usable) but object-level authz still matters for per-user data.
  Optional: bind token to `request.user.pk`, with an opt-out for anonymous/cached pages.
- Runtime params (`hx-vals`, `hx-include`, form fields) can't be signed — they're
  added client-side at request time. That's fine: signed token = trusted framework
  data; `request.GET`/`request.POST` = ordinary untrusted input that never gets
  merged into kwargs/context. The signature line is the explicit trust boundary.
- Tokens are longer but deterministic per payload, so page caching still works.
  Don't set `max_age` by default (would 404 buttons on a page left open overnight).

**Shipping.** Ship as a clean breaking change (`feat!:`) with a migration note.
The only real breakage is *pre-deploy rendered pages* still holding old loose-param
URLs, which 404 when clicked until the page is refreshed (URLs are re-rendered
server-side every request, so new pages get signed tokens immediately), plus anyone
hand-constructing the query params. No dual-format window needed.

---

## 2. 🔴 Add an object-scoping hook (`get_queryset`)

**Problem.** Even with signing (which stops forging), there's no idiomatic slot to
express row-level authorization ("A may edit user 1 but not user 2"). Django's
`UpdateView.get_queryset()` routes every client-controlled lookup through an
overridable, scoped queryset. hx-requests fetches in framework code
(`utils.deserialize` → `_base_manager.get(pk=pk)`) before the user's class runs,
using `_base_manager` (widest possible), with no hook to narrow it.

**Fix.** Give `BaseHxRequest` a `model` / `get_queryset()` contract that
deserialization resolves through, mirroring DRF/Django CBV conventions:

```python
class BaseHxRequest:
    def get_queryset(self):
        # default: model's default manager, not _base_manager
        return None  # falls back to current behavior if unset

    def get_hx_object(self, request, **kwargs):
        # resolve the signed/deserialized object through get_queryset() when provided
        ...
```

Document that `get_hx_object`/`get_queryset` is the ownership-scoping seam, the way
CBV docs teach `get_queryset` for the URL-pk trust boundary.

---

## 3. 🔴 Fix the `dispatch` chain (MRO / permission-mixin trap)

**Problem.** `HtmxViewMixin.dispatch` (`views.py:30-47`) never calls
`super().dispatch()`. Django's `LoginRequiredMixin`/`PermissionRequiredMixin` work
by overriding dispatch and chaining via super. Consequences:

- `class V(HtmxViewMixin, LoginRequiredMixin, ListView)` **silently skips auth** —
  HtmxViewMixin short-circuits the MRO. Only `LoginRequiredMixin` *before*
  HtmxViewMixin works, with zero warning when ordering is wrong.
- Method decorators on the view's `get`/`post` are bypassed for HTMX requests,
  since the handler comes from the HxRequest class, not the view.

**Fix.** Two paths, handled differently — and note that `super().dispatch()` is
*only* correct for one of them:

- **Non-HTMX path:** call `super().dispatch()` so the page view's mixins
  (`LoginRequiredMixin` etc.) chain normally. Today the mixin does its own handler
  lookup instead of chaining, which is why they're skipped.
- **HTMX path:** `super().dispatch()` is **wrong** here — it would route to the page
  view's own `get`/`post`, not to the resolved hx handler, defeating the whole
  dispatch. So auth on this path cannot be delegated to super; it must be enforced
  **per-handler** (a `permission`/`login` declaration on the HxRequest class, run
  before its `get`/`post`). This is the idiomatic pattern anyway and is exactly what
  the URL router (#10) makes native — so #3 and #10 converge on the same answer:
  per-handler authorization. Interim: at minimum detect a permission mixin sitting
  after HtmxViewMixin in the MRO and raise/warn, so the silent-skip can't happen
  unnoticed.

---

## 4. 🟠 Make `view.get()` context-harvest lazy (perf) — ✅ DONE

> **Fixed** on `perf/lazy-view-context`. `view_response` is now a `cached_property`;
> `_setup_hx_request` only triggers the harvest when the view context will actually
> be rendered (`_renders_view_context`), so a POST that renders nothing from the view
> (`refresh_page` / `redirect` / `return_empty`) never runs `view.get()` and never
> pays the page-view query cost. The harvest still happens *before* `post()` on every
> rendering path, so the pre-mutation ("stale") context semantics are preserved
> exactly — the pure-lazy-in-`get_context_data` version the note below sketched would
> have moved the snapshot *after* the POST mutation and broken that contract, so the
> trigger is kept at setup for rendering paths and skipped only for no-render POSTs.
> The explicit-opt-in redesign and the non-`TemplateResponse` no-op doc remain open
> (they belong with #10).

**Problem.** `_setup_hx_request` eagerly calls `self.view.get(request, ...)`
(`views.py`/`hx_requests.py:170-171`) to harvest `context_data` — on **POST** too,
before anyone knows if it's needed. A tiny partial pays full page-view query cost.
Silently no-ops for views returning plain `HttpResponse` (not `TemplateResponse`).
`refresh_views_context_on_POST` runs it *again*.

**Fix.** Make `view_response` a `cached_property` accessed lazily inside
`get_context_data`:

- Form invalid → GET template re-renders → context accessed → view runs (same as today).
- Form valid + `refresh_page`/`redirect`/`return_empty` → nothing renders → view
  context never accessed → **`view.get()` never runs**. Pure savings, zero behavior change.

Note: context-sharing is a *minor convenience*, not the differentiator (that's the
dispatch ergonomics + form/modal round-trip; see the "genuinely good at" section).
So there's room to go further than the lazy fix — move it to an explicit opt-in
(`shares_context_from = SomeView`, or just reconstruct what's needed from
`self.hx_object`) and stop harvesting it implicitly. That kills the surprise and the
perf cost for the common case, and de-risks the #10 URL split (which removes the page
view from the request cycle and so ends implicit sharing anyway). Also document that
context-sharing silently no-ops for non-`TemplateResponse` views.

---

## 5. 🟡 Bump Python / Django floor; fix packaging metadata

**Problem.** `hx_requests.py:91` uses `dict[str, str]` in a class-level annotation
with **no** `from __future__ import annotations` — a `TypeError` on Python 3.8
(annotations evaluate eagerly). So the package can't import on the oldest version
its classifiers advertise. Classifiers stop at Django 4.1 / Python 3.11 → reads
abandoned despite an active changelog.

**Fix.** Set `python = "^3.11"` in `pyproject.toml`, prune stale classifiers, add
current Django versions. Cheap win that also fixes the "looks abandoned" signal.

---

## 6. 🟠 Replace fragile string-craft with Django primitives

Three separate items:

**6a. CSRF token (`utils.py:84`). — ✅ DONE.** Hand-splits the raw `Cookie` header on
`"csrftoken="`. Breaks with `CSRF_USE_SESSIONS = True` (no cookie → all POSTs 403),
and picks the wrong token if another cookie name contains `csrftoken`.
→ Replace with `django.middleware.csrf.get_token(request)` (handles all CSRF
configs + masking/rotation).
> **Fixed** on `fix/string-craft-primitives`. `get_csrf_token` now delegates to
> `django.middleware.csrf.get_token`, which mints a masked token from the request
> under any CSRF config — so `hx_post` always carries a valid `X-CSRFTOKEN`.

**6b. Unquoted HTML attributes (`hx_tags.py:17,27-31`). — ✅ DONE.** Emits `hx-get={url}` and
`hx-headers={...}` with no quotes. Works today only because encoding produces no
spaces; one space in a value truncates the attribute.
→ Use `format_html('hx-get="{}"', url)` etc.
> **Fixed** on `fix/string-craft-primitives`. `hx_get`/`hx_post` build attributes
> with `format_html` (quoted + HTML-escaped); `hx-headers` is single-quoted so its
> JSON double-quotes survive. Matches the already-documented quoted wire format.

**6c. Deserializer reachable by raw input (`utils.py:28`).** `json.loads` on raw
query strings → 500 on malformed input. (The recent "don't break on NoneType"
commit was one instance of this class.)
→ Signing (#1) fixes this: unsigned/mangled input is rejected before deserialize.
500s matter: they page on-call, pollute error tracking, and give anyone a free way
to generate server errors that scanners flag.

> **Partially covered by #1.** kwargs/object now deserialize *only* from the signed
> token, and `_use_current_url` strips framework keys — so no raw query input reaches
> `json.loads`/`deserialize` anymore. Remaining #6c work is unrelated raw-input paths
> if any surface later; the `use_current_url` framework-injection hole is closed.

---

## 7. 🟡 Reduce API surface — ✅ DONE

> **Fixed** on `refactor/api-surface`.
> - **7a.** `_render_templates` no longer silently returns `""` on an unmatched
>   shape — it raises a descriptive `ValueError` naming the bad
>   `templates`/`blocks` types. A single template with `None` block now renders the
>   whole template (a falsy block name means "no block") instead of falling through
>   to blank.
> - **7b.** `get_error_message` builds its markup with `format_html` (escaped +
>   `SafeString`) instead of `mark_safe` on an interpolated f-string, and emits the
>   valid `<br>` (was the invalid `</br>`). `mark_safe` is gone from the module.
>   Kept as an overridable method rather than extracting a template, to avoid
>   churning the `get_error_message`/`get_success_message` override contract.
> - **7c.** `hx_object_to_str` uses `_meta.verbose_name` (upper-casing the first
>   char) instead of `str.capitalize()` on the class name, which mangled CamelCase
>   (`MyModel` → `Mymodel`).

**7a.** `GET_template`/`GET_block` each accept `str | list | dict` with a
four-branch case analysis in `_render_templates` (`hx_requests.py:250-291`) that
silently returns `""` on no match. Consider narrowing accepted shapes / failing loud.

**7b.** `get_error_message` builds HTML in Python with `mark_safe` and an invalid
`</br>` tag (`hx_requests.py:466-478`). Move markup to a template.

**7c.** `hx_object_to_str` uses `.capitalize()` → `MyModel` becomes `Mymodel`
(`hx_requests.py:180-181`). Use `_meta.verbose_name`.

---

## 8. 🟡 Remove dead code; improve diagnostics

**8a.** `django_views.py` is referenced by nothing (package, docs, or tests). Remove
or wire it up.

**8b.** Registry raises bare `Exception` for duplicate names and silently swallows
`SyntaxError` in `_parse_file` (`hx_registry.py:96,101-103`) — a typo in a user's
`hx_requests.py` makes their handlers vanish, surfacing later as a mystifying 404.
Add logging/warnings on parse failure and skipped files.

**8c.** All security denials raise `Http404` (`views.py`) with no logging — hard to
debug "why is my request 404ing." Add a debug-level log line explaining the denial.

---

## 9. 🟡 Simplify the security matrix → per-handler authorization

**Problem.** `is_hx_allowed` (`views.py:80-128`) combines six knobs:
`HX_REQUESTS_REQUIRE_AUTH`, `HX_REQUESTS_UNAUTHENTICATED_ALLOW`,
`HX_REQUESTS_ENFORCE_SAME_APP`, `HX_REQUESTS_GLOBAL_ALLOW`, per-view
`allowed_hx_requests`, `use_global_hx_rules`. Recent git history (two allowlist
`fix:` commits + a breaking rename) shows the matrix is hard to reason about. The
matrix also answers the wrong question — "which *view* may invoke this handler" —
when the natural question is "may this *user* run this *handler*." In practice
teams reach for per-handler permission checks and route around the matrix entirely.

**Fix.** Make **per-handler authorization the first-class, documented mechanism** —
a permission/login declaration (or decorator) on the HxRequest class, checked before
its `get`/`post`. This is the same answer #3's HTMX path and #10's URL router
converge on, so all three should land together conceptually. Once per-handler auth
is first-class, the six-knob matrix collapses to at most `allowed_hx_requests`
(default same-app) as a lightweight scoping default, and most of the settings can be
deprecated. This is a stronger, earlier move than originally framed — not a
leftover cleanup after #10.

---

## 10. 🟢 Adoption: mount HxRequests on real URLs (long-term)

**Problem (framework smell).** Name-based dispatch through query strings means no
`reverse()`, no URL-level middleware/decorators, no per-endpoint caching, and
grep-invisible magic strings in templates. Django devs distrust exactly this.

**Fix.** Generate real URLs from the registry (the DRF-router move):

```python
urlpatterns = [
    path("hx/", include(HxRequestRegistry.urls)),  # -> /hx/<name>/
]
```

Each HxRequest becomes a view at `/hx/<name>/`. Template tags keep their API but
call `reverse()` under the hood. Wins: per-endpoint decorators/middleware,
`LoginRequiredMixin` working normally (no MRO trap, no global-gateway problem — so
most of #9 can be deleted), URL-level caching, endpoints visible in `show_urls`.
Context-sharing survives as an explicit `view = MyListView` declaration on the
HxRequest class instead of being implied by which page fired the request. Composes
with signing (#1) — the token rides on `/hx/edit_user/?hx=...` just as well.

**Must preserve (do not regress the value in the "genuinely good at" section).**
The URL split must keep **"many handlers, one registration"** — users should still
declare a handler by adding a class with a `name`, not by hand-authoring a URLconf
entry per handler. Generate the `urlpatterns` from the registry (see below) so the
ergonomic is unchanged; the router is an implementation detail, not new user work.
Likewise the plain-htmx fall-through (sort/filter/paginate that omit
`hx_request_name` and hit the underlying view) must keep working.

The URLs can be generated dynamically from the existing registry — the AST scan
already yields names cheaply without importing handlers, so lazy loading is
preserved (only the *names* are needed to build `path()` entries; the class imports
on first request). One ordering caveat to test: `urls.py` importing the registry
runs during startup, so confirm the app registry is populated first (it normally is,
since `ROOT_URLCONF` loads after `apps.populate()`).

**Shipping.** Additive: add the router alongside query-param dispatch, deprecate the
old path over several releases (or a clean `feat!:` break per the #1 rationale).

---

## Security review notes (implementation-readiness pass on #1–#3, #6)

A second pass over the security fixes as *implementation specs* rather than
directions. The three headline fixes (#1 signing, #2 scoping, #3 dispatch) are the
right three and do close the holes — these notes tighten specs that are currently a
bit optimistic about coverage. Fold each into its item before implementing.

**#1 — signing: three corrections.**
- *Salt reasoning.* `salt="hx-requests"` is a public constant in an OSS package; it
  adds **namespacing, not secrecy** (security comes from `SECRET_KEY`). Don't lean on
  it for forging resistance. Better: use a **per-name salt**,
  `salt=f"hx-requests:{hx_request_name}"`, so a token minted for `edit_user` can't be
  replayed against `delete_user`. Nearly free, and it narrows the residual replay
  surface flagged in #1's caveats.
- *Caching claim is wrong.* `signing.dumps` embeds a timestamp, so tokens are **not**
  byte-stable across renders — two renders of the same page yield different `hx`
  tokens. Functionally fine, but it breaks fragment caching keyed on rendered HTML and
  any test asserting exact URLs. Correct the "caching still works" line and decide
  whether non-stable tokens are acceptable (they usually are).
- *Path binding.* `name` lives in the signed blob but nothing checks the request's
  `path` against the token. Low priority under query-param dispatch; note it if
  same-URL dispatch is kept.

**#2 — scoping hook: make the safe path the default, not opt-in.** As written,
`get_queryset()` returning `None` falls back to the insecure `_base_manager` path —
so the vuln is only closed for handlers that opt in, which repeats the original sin
(people forget to scope). **Load-bearing change: default resolution to the model's
`_default_manager`, not `_base_manager`**, so soft-delete / tenant scoping on the
default manager is respected automatically; `_base_manager` becomes the explicit
opt-out. That one swap in `utils.deserialize` is a security fix worth doing on its
own. Also note the plumbing: `deserialize` is a free function with no instance
access, so wiring `get_queryset()` in requires moving resolution into the
`get_hx_object` *method* — a real refactor, not a one-liner.

**#3 — dispatch chain: make the MRO check a Django system check.** The interim
"detect a permission mixin after HtmxViewMixin" guard should use
`django.core.checks` (surfaces at startup / `manage.py check`), not a runtime raise —
that's the idiomatic home for "your view classes are misconfigured" and it's seen
earlier. Otherwise the two-path split is correct as written.

**#6c — signing does NOT fully subsume input validation.** #1 only protects data that
flows through the *signed token*. Anything still reading raw `request.GET`/`POST` —
notably the `use_current_url` feature, which merges arbitrary current-URL params —
remains reachable by raw input. Keep defensive `try/except` around any `json.loads`
that can see unsigned input; don't retire #6c just because #1 shipped.

**New — GET must not mutate.** Orthogonal to everything above: signing and CSRF-token
delivery (#6a) don't stop a `get()` override from performing writes, and a signed
token embedded in a page is still replayable cross-site via `<img src>` etc. because
GETs aren't CSRF-protected. Add a rule to the plan: **mutations happen only on POST**
(document it, and ideally assert it — e.g. warn if a handler overrides `get()` and
also writes). Without this, there's a CSRF gap independent of the token work.

**Priority within the security work:** the `_default_manager` default (#2) is the one
to insist on — without it the "scoping hook" is opt-in security, which is the pattern
that created the bug. The rest are spec tightenings, not direction changes.

---

## Suggested order

1. **#1 signing** + **#3 dispatch chain** — small diffs, close the real vulns.
   (#3's HTMX path points at per-handler auth, so it previews #9.)
2. **#2 scoping hook** — completes the object-authz story.
3. **#5 metadata** + **#6 string-craft** — cheap robustness/adoption wins.
4. **#4 lazy context** — perf, backwards compatible; sets up the explicit-opt-in
   direction for context-sharing.
5. **#7 / #8** — quality cleanup.
6. **#9 per-handler authorization** + **#10 URL router** — the adoption arc, landed
   together: per-handler auth is the mechanism, the router is the delivery. Collapse
   the six-knob matrix as part of this, not before it.

Throughout: protect the three things in "genuinely good at" — many-handlers-one-URL,
the form/modal round-trip, and composable trigger/confirm mixins. Any change that
makes those harder is the wrong change, however clean it looks.

---

## Appendix: the bigger bet — make HxRequests *real* Django views

This is the endgame that #10 (URL router) and #9 (per-handler auth) point toward.
It's a larger rewrite than the numbered items and is recorded here as a direction,
not a committed step. The pitch changes from *"learn our parallel routing framework,
registry, security matrix, and serialization scheme"* to **"it's a Django
`UpdateView` that returns an HTMX partial instead of a full page."** That one-sentence
framing is the whole adoption argument — it rides knowledge Django devs already have
(the same reason django-components and DRF get traction) instead of asking for new
concepts.

### Why it's feasible

HxRequest classes are already ~90% views: they have `get`/`post` returning
`HttpResponse`, hold `self.request`, and `_get_response` is a dispatch. The only thing
making them *not* views is the route-through-the-page-view design. Once #10 puts them
on their own URLs, "be a real view" is the consequence, not extra work.

### How it works — compose Django's mixins, don't subclass `FusedView`

The naive version (`class FormHxRequest(FormView)`) **does not work**, and that's the
main gotcha. Django's `FormView.form_valid(self, form)` takes the form as an arg and
returns a redirect; ours is `form_valid(self, **kwargs)`, reads `self.form`, and
returns `None`-or-`HttpResponse`. `FormView.post` renders a full template. Subclassing
the generic views directly means fighting them at every override.

The approach that *does* work is how Django itself builds generic views — cherry-pick
the small mixins:

- **Inherit the data/auth mixins** (the correct, battle-tested parts currently
  reimplemented):
  - `View` → dispatch + auth machinery. This is what makes `LoginRequiredMixin`,
    `PermissionRequiredMixin`, `UserPassesTestMixin`, method decorators, and
    third-party CBV auth all Just Work. **Deletes #3 and most of #9 outright.**
  - `SingleObjectMixin` → `get_object`/`get_queryset`/`model`. **This is #2 — the
    scoping hook — for free and idiomatic.** No more `_base_manager.get(pk)`.
  - `FormMixin` → `get_form`/`get_form_kwargs`/`get_initial`.
- **Replace the response mixins** — this is hx-requests' actual value-add:
  - `TemplateResponseMixin` → the `Renderer` (blocks, multiple templates, messages,
    modal retarget).
  - `ProcessFormView.post` → the `None`-or-`HttpResponse` contract.

```python
class FormHxRequest(HxRenderMixin, FormMixin, SingleObjectMixin, View):
    # inherit get_form_kwargs / get_object / get_queryset / auth
    # override post, form_valid, form_invalid, and rendering
```

That's exactly how `UpdateView` is assembled internally — reuse the parts Django gets
right (that we currently get subtly wrong) while keeping full control of rendering.
This restructure **subsumes #2, #3, #9, and #10** into one coherent 1.0 story rather
than four separate fixes.

### The one real cost: context sharing

This is the feature Django CBVs don't hand you, because it's hx-requests' own
invention. Today the hx request piggybacks on the page view's request cycle and
harvests `view.get().context_data` for free. Once the hx request has its own URL,
there's no page view in the cycle — so **automatic context sharing breaks**.

It doesn't disappear, it becomes explicit. Two patterns:

1. **Instantiate-and-harvest** (closest to today): `shares_context_from = ProjectListView`
   on the HxRequest; the framework instantiates it, runs `view.setup()` + the
   type-specific `object`/`object_list` preamble, and calls `get_context_data()`.
   Friction: `get_context_data` needs `self.object`/`self.object_list` set first
   (why today's code calls the full `view.get()`); Django has no single "just give me
   the context" method, so you provide small per-view-type setup helpers. **The dead
   `django_views.py` module is a half-built version of exactly these** — resurrect it.
2. **Shared-context mixin** (idiomatic Django): extract the shared context into a
   mixin both the page view and the hx view inherit. No cross-view instantiation, no
   re-running another view's `get()`. Cost: not automatic — the user refactors their
   view, and the hx view only gets what it explicitly mixes in.

Ship #1 as the migration-compatible path so existing behavior survives with a one-line
declaration; document #2 as the cleaner target. Note this aligns with #4: making
context explicit kills the surprise *and* the perf cost for everyone who doesn't opt in.

### Honest risks / open questions

- **Scope discipline.** This is a rewrite of the dispatch core, so it wants a branch
  with the base classes rebuilt mixin-first — not an incremental patch. High risk of a
  long-lived branch that drifts.
- **`form_valid` signature change.** Aligning toward Django's `(self, form)` vs.
  keeping the existing `(self, **kwargs)` + `self.form` is a public-API decision. Either
  way it touches every consumer's overrides — the biggest breaking-change surface.
- **The "why not just write it myself" risk.** If the restructure thins the package to
  mixins-on-CBVs, a user might look at what's left and reimplement the few header
  helpers. Defense: make `FormModalHxRequest` genuinely excellent — the annoying-enough
  round-trip that people would rather `pip install`. That component is the moat;
  context sharing and dispatch never were.
- **Do you even keep the registry?** With real `as_view()` URLs, users *could* wire
  `path("edit-user/", EditUserHx.as_view())` by hand like any CBV. The registry becomes
  a *convenience* (auto-generated URLs) rather than a necessity. Open question whether
  auto-routing earns its keep once handlers are ordinary views — decide deliberately
  rather than carrying it forward by default.
- **Ecosystem positioning.** The honest version of this package leans on, rather than
  competes with, `django-htmx` (request/response primitives) and Django template
  partials (fragment rendering). The 1.0 could reasonably *depend* on django-htmx and
  drop `django-render-block` in favor of partials — smaller surface, clearer identity.
