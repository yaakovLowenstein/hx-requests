# URL Router (#10) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an additive `/hx/<name>/` URL router so named `HxRequest` handlers can be reached through real Django URLs (`reverse()`, URL decorators/middleware, per-endpoint caching, `show_urls`), without changing how a handler is declared.

**Architecture:** The registry gains `get_urls()`, which turns each registered *name* into one `path()` bound to a thin `HxEndpointView`. The endpoint verifies the signed token, enforces **path binding** (token name must equal the URL name), then runs the existing `HxRequest.dispatch` — the same per-handler auth + get/post cycle the legacy page-view path uses. The two trust-boundary operations (token verify+sanitize, current-URL merge) are factored into module functions that both `HtmxViewMixin` (legacy) and `HxEndpointView` (router) call, so there is one trust boundary. The template tag prefers `reverse("hx:<name>")` and falls back to `request.path`, so the router is zero-config and additive.

**Tech Stack:** Python 3.11+, Django 4.2+, pytest, `render_block`. Tests run with `.venv/bin/python -m pytest`; lint/format with `~/.local/bin/ruff` (`ruff check` **and** `ruff format --check`); commit with `--no-verify` (pre-commit is broken in this repo).

## Global Constraints

- **Additive only.** The legacy page-view dispatch (`HtmxViewMixin` query-param routing) must keep working unchanged. A project that does not wire the `include()` sees no behavior change. Removing the legacy path is a separate, later `feat!:`.
- **Do not regress the three protected values:** many-handlers-one-registration (URLs are generated from the registry — users never hand-author a `path()` per handler), the form/modal round-trip, and composable trigger/confirm mixins. Plus plain-htmx fall-through (token-less HTMX still hits the page view).
- **Lazy loading preserved.** `get_urls()` builds patterns from names only; it must not import handler classes.
- **Namespace is the fixed string `hx`** (spec open-question #2 resolved to the documented default).
- **One trust boundary.** Token verification/sanitization is shared code, not duplicated per path.
- Python floor 3.11, Django floor 4.2. Use `from __future__ import annotations` and `X | None` unions (matches the existing files).
- Commit messages end with the repo's trailer convention; use `feat:` (additive, non-breaking).

## File structure

- `hx_requests/views.py` — add module functions `bind_hx_token(request, expected_name=None)` and `merge_current_url(request)` (factored out of `HtmxViewMixin`), and the new `HxEndpointView`. `HtmxViewMixin` is rewired to call the shared functions.
- `hx_requests/hx_registry.py` — add `HxRequestRegistry.get_urls()` (imports `HxEndpointView` lazily inside the method to avoid a circular import).
- `hx_requests/hx_requests.py` — make `BaseHxRequest` tolerate `self.view is None` and add the `shares_context_from` class attribute.
- `hx_requests/utils.py` — `get_url()` prefers `reverse("hx:<name>")` with a `NoReverseMatch` fallback.
- `tests/urls.py` (new) — root URLconf wiring the router; `tests/settings.py` points `ROOT_URLCONF` at it.
- `tests/helpers.py` — add `hx_get_url` / `hx_post_url` that drive real requests through `reverse()`-resolved router URLs via the Django test `Client`.
- `tests/test_url_router.py` (new) — registry `get_urls`, resolution, path binding, auth parity, template-tag reverse/fallback, context sharing, fall-through, startup ordering.
- `tests/test_app/hx_requests.py` — add a `shares_context_from` fixture handler.
- `tests/test_app/views.py` — a plain `TemplateView` used as a `shares_context_from` source (no `HtmxViewMixin`).
- `docs/` — new "Mounting HxRequests on URLs" how-to + a note on the securing/how-it-works pages.

---

### Task 1: `HxRequestRegistry.get_urls()`

**Files:**
- Modify: `hx_requests/hx_registry.py`
- Test: `tests/test_url_router.py` (new)

**Interfaces:**
- Consumes: existing `HxRequestRegistry.initialize()` / `_registry` (name → class-or-tuple).
- Produces: `HxRequestRegistry.get_urls() -> list[django.urls.URLPattern]`, one `path(f"{name}/", HxEndpointView.as_view(hx_name=name), name=name)` per registered name. Does **not** import handler classes. (`HxEndpointView` is created in Task 4; Task 1 imports it lazily inside the method, so the two tasks can land in either order but the test in Task 1 only passes once Task 4 exists — see Step 2.)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_url_router.py`:

```python
"""Tests for the additive /hx/<name>/ URL router (#10)."""

from __future__ import annotations

import pytest

from hx_requests.hx_registry import HxRequestRegistry


def test_get_urls_returns_one_pattern_per_registered_name(clean_registry):
    HxRequestRegistry.reset()
    HxRequestRegistry.initialize()
    urls = HxRequestRegistry.get_urls()

    names = {pattern.name for pattern in urls}
    assert "simple_get" in names
    assert "other_app_hx" in names
    assert "deep_hx" in names
    assert len(urls) == len(HxRequestRegistry._registry)


def test_get_urls_does_not_import_handler_classes(clean_registry):
    HxRequestRegistry.reset()
    HxRequestRegistry.get_urls()
    # Building URLs must stay lazy: entries remain (module, class) tuples.
    assert isinstance(HxRequestRegistry._registry["simple_get"], tuple)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_url_router.py -v`
Expected: FAIL — `AttributeError: type object 'HxRequestRegistry' has no attribute 'get_urls'` (and, until Task 4 lands, an `ImportError` for `HxEndpointView`).

- [ ] **Step 3: Write minimal implementation**

Add to `hx_requests/hx_registry.py` inside `HxRequestRegistry`:

```python
    @classmethod
    def get_urls(cls):
        """
        Build one ``path()`` per registered handler name, routed to
        :class:`~hx_requests.views.HxEndpointView`.

        Wire it into a root URLconf once::

            from hx_requests.hx_registry import HxRequestRegistry

            urlpatterns = [
                path("hx/", include((HxRequestRegistry.get_urls(), "hx_requests"), namespace="hx")),
            ]

        Patterns are built from names only -- handler classes still import
        lazily on first request -- so this is cheap and preserves lazy loading.
        Patterns are a snapshot at URLconf-build time: adding a handler needs a
        server restart, same as any URLconf change.
        """
        # Imported here, not at module scope: views.py imports this module, so a
        # top-level import would be circular.
        from hx_requests.views import HxEndpointView

        cls.initialize()
        return [
            path(f"{name}/", HxEndpointView.as_view(hx_name=name), name=name)
            for name in cls._registry
        ]
```

Add `from django.urls import path` to the imports at the top of `hx_registry.py`.

- [ ] **Step 4: Run test to verify it passes** (requires Task 4's `HxEndpointView`; if executing in order, land Task 4's view stub first or run this after Task 4)

Run: `.venv/bin/python -m pytest tests/test_url_router.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add hx_requests/hx_registry.py tests/test_url_router.py
git commit --no-verify -m "feat: build urlpatterns from the HxRequest registry"
```

---

### Task 2: Factor the token trust boundary into shared functions

**Files:**
- Modify: `hx_requests/views.py`
- Test: `tests/test_url_router.py`

**Interfaces:**
- Produces:
  - `bind_hx_token(request, expected_name=None) -> HttpRequest` — verifies the signed `hx` token, rebuilds `request.GET` with only trusted framework data (drops client-supplied `hx`, `hx_request_name`, `object`, and `___`-prefixed kwargs; re-sets `hx_request_name`/`object` from the verified payload), stashes verified kwargs on `request._hx_kwargs`. Raises `Http404` on a missing/tampered token. When `expected_name` is given, the token's `name` must equal it (path binding) or `Http404` is raised.
  - `merge_current_url(request) -> HttpRequest` — merges non-framework params from the `HX-Current-URL` header into `request.GET` (the existing `use_current_url` behavior).
- Consumes: `HxEndpointView` (Task 4) and `HtmxViewMixin` (rewired here) both call these.

This is a pure refactor: `HtmxViewMixin._resolve_hx_token` / `_use_current_url` become thin wrappers, so the existing suite must stay green.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_url_router.py`:

```python
from django.http import Http404
from django.test import RequestFactory

from hx_requests.utils import HX_TOKEN_PARAM, sign_hx_payload
from hx_requests.views import bind_hx_token


def test_bind_hx_token_rejects_name_mismatch():
    token = sign_hx_payload("simple_get")
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: token})
    # A token minted for simple_get replayed against another endpoint 404s.
    with pytest.raises(Http404):
        bind_hx_token(request, expected_name="post_template")


def test_bind_hx_token_accepts_matching_name():
    token = sign_hx_payload("simple_get")
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: token})
    bound = bind_hx_token(request, expected_name="simple_get")
    assert bound.GET["hx_request_name"] == "simple_get"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_url_router.py::test_bind_hx_token_rejects_name_mismatch tests/test_url_router.py::test_bind_hx_token_accepts_matching_name -v`
Expected: FAIL — `ImportError: cannot import name 'bind_hx_token' from 'hx_requests.views'`.

- [ ] **Step 3: Write minimal implementation**

In `hx_requests/views.py`, add these module-level functions (after the imports, before `HtmxViewMixin`):

```python
def bind_hx_token(request, expected_name=None):
    """
    Verify the signed ``hx`` token and rebuild ``request.GET`` so the rest of
    the chain reads *trusted* framework data. Everything the framework controls
    (name, object, kwargs) comes from the signed token; any client-supplied
    framework params on the raw query string are dropped so they cannot shadow
    or forge the verified values. Non-framework params (page filters, runtime
    hx-vals) are left untouched.

    When ``expected_name`` is given (the router path, where the name comes from
    the URL), the token's ``name`` must equal it -- a token minted for one
    handler cannot be replayed against another endpoint. Raises ``Http404`` on a
    missing/tampered token or a name mismatch.
    """
    if not request.GET.get(HX_TOKEN_PARAM):
        logger.debug("hx_requests: denied (404) -- request carried no '%s' token.", HX_TOKEN_PARAM)
        raise Http404("Missing required query param 'hx' for HTMX request.")
    payload = get_hx_payload(request)
    if payload is None:
        logger.debug(
            "hx_requests: denied (404) -- '%s' token was missing, tampered, or unsigned.",
            HX_TOKEN_PARAM,
        )
        raise Http404("Invalid or tampered hx token.")
    if expected_name is not None and payload["name"] != expected_name:
        logger.debug(
            "hx_requests: denied (404) -- token minted for '%s' replayed against '%s'.",
            payload["name"],
            expected_name,
        )
        raise Http404("hx token does not match this endpoint.")

    sanitized = request.GET.copy()
    for key in list(sanitized.keys()):
        if key in (HX_TOKEN_PARAM, "hx_request_name", "object") or key.startswith(KWARG_PREFIX):
            del sanitized[key]
    sanitized["hx_request_name"] = payload["name"]
    if payload.get("object"):
        sanitized["object"] = payload["object"]

    request.GET = sanitized
    # Verified, serialized kwargs from the token -- the only source of
    # kwargs-as-context. Raw query params never feed this again.
    request._hx_kwargs = payload.get("kwargs", {})
    return request


def merge_current_url(request):
    """
    Merge non-framework params from the ``HX-Current-URL`` header into
    ``request.GET`` (the ``use_current_url`` behavior). Framework params
    (name/object/kwargs/token) are never merged from the current URL: those are
    trusted only via the signed token, not raw query input.
    """
    merged_get = request.GET.copy()
    hx_current_url = request.headers.get("HX-Current-URL")
    if hx_current_url:
        parsed_url = urlparse(hx_current_url)
        additional_params = parse_qs(parsed_url.query)
        for key, values in additional_params.items():
            if key in (HX_TOKEN_PARAM, "hx_request_name", "object") or key.startswith(KWARG_PREFIX):
                continue
            if key not in merged_get:
                merged_get.setlist(key, values)
    request.GET = merged_get
    return request
```

Then rewire `HtmxViewMixin` to delegate (replace the bodies of `_resolve_hx_token` and `_use_current_url`):

```python
    def _resolve_hx_token(self, request):
        return bind_hx_token(request)

    def _use_current_url(self, request):
        return merge_current_url(request)
```

- [ ] **Step 4: Run test to verify it passes (and the full suite stays green)**

Run: `.venv/bin/python -m pytest tests/test_url_router.py tests/test_security.py tests/test_base_hx_request.py -v`
Expected: PASS (new token tests pass; the refactor leaves legacy behavior identical).

- [ ] **Step 5: Commit**

```bash
git add hx_requests/views.py tests/test_url_router.py
git commit --no-verify -m "refactor: share the token trust boundary between legacy and router paths"
```

---

### Task 3: Make `BaseHxRequest` tolerate `view = None` + add `shares_context_from`

**Files:**
- Modify: `hx_requests/hx_requests.py`
- Test: `tests/test_url_router.py`

**Interfaces:**
- Produces: `BaseHxRequest.shares_context_from: type | None = None` class attribute; `BaseHxRequest` works when `self.view is None` (no page-view context harvested, template falls back to `None` so an explicit `GET_template`/`POST_template` is required).
- Consumes: `HxEndpointView` (Task 4) sets `hx_request.view = None` or an instantiated `shares_context_from` view.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_url_router.py`:

```python
from hx_requests.hx_requests import BaseHxRequest


def test_base_hx_request_sets_up_with_no_view():
    class NoViewHx(BaseHxRequest):
        name = "no_view_hx_unit"
        GET_template = "simple.html"

    hx = NoViewHx()
    hx.view = None
    request = RequestFactory().get("/")
    request.user = None
    # Must not raise despite there being no page view to harvest context from.
    hx._setup_hx_request(request)
    assert hx.GET_template == "simple.html"
    context = hx.get_context_data()
    assert context["hx_request"] is hx


def test_shares_context_from_defaults_to_none():
    assert BaseHxRequest.shares_context_from is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_url_router.py::test_base_hx_request_sets_up_with_no_view tests/test_url_router.py::test_shares_context_from_defaults_to_none -v`
Expected: FAIL — `AttributeError: 'NoneType' object has no attribute 'template_name'` (in `_setup_hx_request`) and `AttributeError: ... 'shares_context_from'`.

- [ ] **Step 3: Write minimal implementation**

In `hx_requests/hx_requests.py`:

1. Add the class attribute near `model` (around line 90):

```python
    #: Optional Django view class to harvest page-view context from on the
    #: router path (there is no page view in the request cycle there). When set,
    #: the endpoint instantiates it, runs ``setup()``, and assigns it as the
    #: context source -- reproducing the legacy implicit-context behavior with a
    #: one-line declaration. Leave unset (the explicit, non-surprising default)
    #: and a router handler simply gets no page-view context;
    #: ``get_context_on_GET`` / ``get_context_on_POST`` / ``hx_object`` still work.
    shares_context_from = None
```

2. In `_setup_hx_request`, replace the template fallback and eager-harvest lines:

```python
        view_template = getattr(self.view, "template_name", None)
        self.GET_template = self.GET_template or view_template
        self.POST_template = self.POST_template or view_template

        if not hasattr(self, "hx_object"):
            self.hx_object = self.get_hx_object(request, **kwargs)

        # Harvest the page view's context up front when it will be rendered, so
        # that on POST it reflects state captured before post() mutates anything
        # (the documented stale-context behavior). When the POST renders nothing
        # from the view, the harvest -- and the page view's query cost -- is
        # skipped entirely. With no page view (router path) there is nothing to
        # harvest.
        if self.view is not None and self.get_views_context and self._renders_view_context():
            _ = self.view_response
```

3. In `get_context_data`, guard the harvest:

```python
        if self.view is not None and self.get_views_context and hasattr(self.view_response, "context_data"):
            context.update(self.view_response.context_data)
```

4. In `get_context_on_POST`, guard the refresh block:

```python
        if self.refresh_views_context_on_POST and self.view is not None:
            if hasattr(self.view, "object") and self.view.object:
                self.view.object.refresh_from_db()
                context["object"] = self.view.object
            context.update(self.view.get_context_data(**kwargs))
```

- [ ] **Step 4: Run test to verify it passes (and the legacy suite stays green)**

Run: `.venv/bin/python -m pytest tests/test_url_router.py tests/test_base_hx_request.py tests/test_lazy_context.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add hx_requests/hx_requests.py tests/test_url_router.py
git commit --no-verify -m "feat: let BaseHxRequest run without a page view (router path)"
```

---

### Task 4: `HxEndpointView` — the router request cycle

**Files:**
- Modify: `hx_requests/views.py`
- Test: `tests/test_url_router.py`, `tests/urls.py` (new), `tests/settings.py`, `tests/helpers.py`

**Interfaces:**
- Consumes: `bind_hx_token` / `merge_current_url` (Task 2), `HxRequestRegistry.get_hx_request` / `get_urls` (Task 1), `BaseHxRequest` view=None support + `shares_context_from` (Task 3).
- Produces: `HxEndpointView(View)` with class attribute `hx_name = None`, set per-path via `as_view(hx_name=...)`. Its `dispatch` resolves the handler, binds the token with path binding, wires the context view, and delegates to `hx_request.dispatch`. Test helpers `hx_get_url(client, hx_request, ...)` / `hx_post_url(client, hx_request, ...)` drive real requests through `reverse("hx:<name>")`.

- [ ] **Step 1: Wire a test URLconf and helpers (scaffolding for this task's test)**

Create `tests/urls.py`:

```python
"""Root URLconf for the test suite: mounts the additive HxRequest router."""

from django.urls import include, path

from hx_requests.hx_registry import HxRequestRegistry

urlpatterns = [
    path("hx/", include((HxRequestRegistry.get_urls(), "hx_requests"), namespace="hx")),
]
```

In `tests/settings.py`, change `ROOT_URLCONF = None` to:

```python
ROOT_URLCONF = "urls"
```

Add to `tests/helpers.py`:

```python
from django.urls import reverse

from hx_requests.utils import HX_TOKEN_PARAM, sign_hx_payload  # (already imported; keep one import)


def _router_query(hx_request, hx_kwargs=None, get_params=None):
    hx_kwargs = dict(hx_kwargs or {})
    get_params = dict(get_params or {})
    hx_object = hx_kwargs.pop("object", None)
    query = {HX_TOKEN_PARAM: sign_hx_payload(hx_request.name, hx_object, **hx_kwargs)}
    query.update(get_params)
    return query


def hx_get_url(client, hx_request, hx_kwargs=None, get_params=None):
    """Drive a GET through the router URL (reverse('hx:<name>'))."""
    url = reverse(f"hx:{hx_request.name}")
    return client.get(url, data=_router_query(hx_request, hx_kwargs, get_params), HTTP_HX_REQUEST="true")


def hx_post_url(client, hx_request, hx_kwargs=None, get_params=None, post_data=None):
    """Drive a POST through the router URL (reverse('hx:<name>'))."""
    url = reverse(f"hx:{hx_request.name}")
    query = _router_query(hx_request, hx_kwargs, get_params)
    return client.post(
        f"{url}?{urlencode(query)}", data=post_data or {}, HTTP_HX_REQUEST="true"
    )
```

Add `from urllib.parse import urlencode` to the top of `tests/helpers.py`.

- [ ] **Step 2: Write the failing test**

Add to `tests/test_url_router.py`:

```python
from django.test import Client


@pytest.fixture()
def hx_client(db, django_user_model):
    """A logged-in test client (handlers default to login_required=True)."""
    user = django_user_model.objects.create_user(username="router", password="pw")
    client = Client()
    client.force_login(user)
    return client


def test_router_dispatches_get_to_handler(hx_client, clean_registry):
    from tests.helpers import hx_get_url
    from test_app.hx_requests import SimpleGetHx

    response = hx_get_url(hx_client, SimpleGetHx)
    assert response.status_code == 200
    assert b"simple" in response.content.lower()


def test_router_path_binding_rejects_replayed_token(hx_client, clean_registry):
    from django.urls import reverse
    from test_app.hx_requests import SimpleGetHx
    from hx_requests.utils import HX_TOKEN_PARAM, sign_hx_payload

    # Token minted for simple_get, sent to post_template's URL -> 404.
    url = reverse("hx:post_template")
    token = sign_hx_payload(SimpleGetHx.name)
    response = hx_client.get(url, data={HX_TOKEN_PARAM: token}, HTTP_HX_REQUEST="true")
    assert response.status_code == 404


def test_router_missing_token_404s(hx_client, clean_registry):
    from django.urls import reverse

    response = hx_client.get(reverse("hx:simple_get"), HTTP_HX_REQUEST="true")
    assert response.status_code == 404


def test_router_enforces_per_handler_auth(db, clean_registry):
    from test_app.hx_requests import SimpleGetHx
    from tests.helpers import hx_get_url

    # Anonymous client + login_required default -> 404 (bodiless).
    anon = Client()
    response = hx_get_url(anon, SimpleGetHx)
    assert response.status_code == 404
```

- [ ] **Step 3: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_url_router.py -k router -v`
Expected: FAIL — `ImportError: cannot import name 'HxEndpointView'` / `NoReverseMatch`.

- [ ] **Step 4: Write minimal implementation**

In `hx_requests/views.py`:

1. Add imports at the top:

```python
from django.views import View
```

2. Update the `deserialize_kwargs` import line (it is already imported from `hx_requests.utils` — confirm `deserialize_kwargs` and `KWARG_PREFIX` are in that import list; they are).

3. Add the endpoint (after `HtmxViewMixin`):

```python
@method_decorator(ensure_csrf_cookie, name="dispatch")
class HxEndpointView(View):
    """
    The router request cycle for one named ``HxRequest``.

    Mounted at ``/hx/<name>/`` by :meth:`HxRequestRegistry.get_urls`. Because the
    handler name comes from the URL path (not a client query param), a token
    minted for one handler cannot be replayed against another endpoint -- the
    endpoint asserts ``token.name == url.name`` (path binding). Per-handler
    authorization is unchanged: it runs inside ``HxRequest.dispatch`` before
    ``get`` / ``post``. Because this is a real Django ``View``, Django's own
    ``login_required`` / ``LoginRequiredMixin`` compose natively on this path.
    """

    hx_name = None  # set per-path by as_view(hx_name=...)

    def dispatch(self, request, *args, **kwargs):
        hx_cls = HxRequestRegistry.get_hx_request(self.hx_name)
        if hx_cls is None:
            logger.debug(
                "hx_requests: denied (404) -- no HxRequest registered under the name '%s'.",
                self.hx_name,
            )
            raise Http404(f"No HxRequest found with the name '{self.hx_name}'.")

        request = bind_hx_token(request, expected_name=self.hx_name)
        kwargs.update(deserialize_kwargs(**getattr(request, "_hx_kwargs", {})))

        hx_request = hx_cls()

        # No page view in the router cycle. A handler opts back into page-view
        # context with `shares_context_from = SomeView`; the endpoint stands that
        # view up and assigns it as the context source (the same `view` seam the
        # legacy path uses), so BaseHxRequest harvests it unchanged.
        context_view_cls = getattr(hx_cls, "shares_context_from", None)
        if context_view_cls is not None:
            context_view = context_view_cls()
            context_view.setup(request, *args, **kwargs)
            hx_request.view = context_view
        else:
            hx_request.view = None

        if getattr(hx_request, "use_current_url", False):
            request = merge_current_url(request)

        hx_request._setup_hx_request(request, *args, **kwargs)
        return hx_request.dispatch(hx_request.request, *args, **kwargs)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_url_router.py -v`
Expected: PASS

- [ ] **Step 6: Run the FULL suite (ROOT_URLCONF change is global — nothing else may break)**

Run: `.venv/bin/python -m pytest -q`
Expected: all pass. If a pre-existing test broke on the `ROOT_URLCONF` change, fix the test wiring (not the router).

- [ ] **Step 7: Commit**

```bash
git add hx_requests/views.py tests/urls.py tests/settings.py tests/helpers.py tests/test_url_router.py
git commit --no-verify -m "feat: add HxEndpointView router endpoint with path binding"
```

---

### Task 5: Template tag `get_url()` prefers `reverse()`

**Files:**
- Modify: `hx_requests/utils.py`
- Test: `tests/test_url_router.py`

**Interfaces:**
- Consumes: `reverse` / `NoReverseMatch` from `django.urls`.
- Produces: `get_url()` returns `reverse("hx:<name>")?hx=<token>` when the router is installed, else `request.path?hx=<token>` (legacy). Signature unchanged. The signed token still carries name/object/kwargs, so signing composes unchanged and loose page-filter params behave as today.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_url_router.py`:

```python
from django.template import Context, Template


def _render(template_str, context):
    return Template("{% load hx_tags %}" + template_str).render(Context(context))


def test_get_url_uses_reverse_when_router_installed(rf, clean_registry):
    from hx_requests.utils import get_url

    request = rf.get("/some/page/")
    url = get_url({"request": request}, "simple_get", None)
    # Router installed (tests/urls.py) -> reversed router URL, not request.path.
    assert url.startswith("/hx/simple_get/?")
    assert "hx=" in url


def test_get_url_falls_back_to_request_path_for_unknown_name(rf, clean_registry):
    from hx_requests.utils import get_url

    request = rf.get("/some/page/")
    url = get_url({"request": request}, "not_a_registered_router_name", None)
    assert url.startswith("/some/page/?")
```

Note: `not_a_registered_router_name` has no `path()` so `reverse()` raises `NoReverseMatch`, exercising the fallback. (`rf` is pytest-django's `RequestFactory` fixture.)

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_url_router.py -k get_url -v`
Expected: FAIL — the current `get_url` always returns `request.path`, so the first test fails on the `/hx/simple_get/` assertion.

- [ ] **Step 3: Write minimal implementation**

In `hx_requests/utils.py`, add the import:

```python
from django.urls import NoReverseMatch, reverse
```

Replace the final `return` of `get_url`:

```python
    params[HX_TOKEN_PARAM] = sign_hx_payload(hx_request_name, obj, **kwargs)

    # Prefer the router URL when it is installed; fall back to the current path
    # (legacy page-view dispatch) so a project that has not wired the router
    # keeps working with no template edits.
    try:
        base = reverse(f"hx:{hx_request_name}")
    except NoReverseMatch:
        base = request.path

    return f"{base}?{urlencode(params, doseq=True)}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_url_router.py -k get_url tests/test_hx_tags.py -v`
Expected: PASS (router tests pass; existing `test_hx_tags.py` still passes — those requests resolve names the router doesn't register, or assert on the `hx=` token which is unchanged. If a tag test now sees `/hx/<name>/` where it asserted `request.path`, update that assertion to accept the reversed URL — the token is what matters.)

- [ ] **Step 5: Commit**

```bash
git add hx_requests/utils.py tests/test_url_router.py
git commit --no-verify -m "feat: template tags emit reverse() router URLs with a legacy fallback"
```

---

### Task 6: `shares_context_from` end-to-end + plain-htmx fall-through + startup ordering

**Files:**
- Modify: `tests/test_app/hx_requests.py`, `tests/test_app/views.py`
- Test: `tests/test_url_router.py`

**Interfaces:**
- Consumes: `HxEndpointView` (Task 4), `shares_context_from` (Task 3), the router (Task 1).
- Produces: a fixture handler `SharesContextHx` (`shares_context_from = RouterContextView`) proving page-view context is reproduced on the router path; tests that a handler without it gets no page-view context; a fall-through test; a startup-ordering test.

- [ ] **Step 1: Add fixtures**

In `tests/test_app/views.py`, add a plain view (no `HtmxViewMixin` — it is only a context source):

```python
class RouterContextView(TemplateView):
    template_name = "base_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_flavor"] = "from-the-view"
        return context
```

In `tests/test_app/hx_requests.py`, add the import near the existing `from test_app.forms import WidgetForm` line, then the handler (there is no import cycle: `test_app/views.py` imports from `hx_requests.views`, not from `test_app.hx_requests`):

```python
from test_app.views import RouterContextView


class SharesContextHx(BaseHxRequest):
    name = "shares_context"
    GET_template = "view_flavor.html"
    shares_context_from = RouterContextView
```

The registry discovers it by its string `name` via AST without importing the module; the import runs lazily on first request.

Create `tests/templates/view_flavor.html`:

```html
<div>{{ view_flavor|default:"no-view-context" }}</div>
```

- [ ] **Step 2: Write the failing test**

Add to `tests/test_url_router.py`:

```python
def test_shares_context_from_reproduces_view_context(hx_client, clean_registry):
    from tests.helpers import hx_get_url
    from test_app.hx_requests import SharesContextHx

    response = hx_get_url(hx_client, SharesContextHx)
    assert response.status_code == 200
    assert b"from-the-view" in response.content


def test_no_shares_context_gets_no_view_context(hx_client, clean_registry):
    from django.urls import reverse
    from hx_requests.utils import sign_hx_payload, HX_TOKEN_PARAM

    # simple_get has no shares_context_from; view context is simply absent.
    # (It renders fine because it declares its own GET_template.)
    response = hx_client.get(
        reverse("hx:simple_get"),
        data={HX_TOKEN_PARAM: sign_hx_payload("simple_get")},
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200


def test_plain_htmx_without_token_is_not_a_router_request():
    # A token-less HTMX request carries no signed payload, so it is not an
    # hx-requests request -- the page view (legacy path) handles it. The router
    # only mounts named handlers; it never intercepts token-less htmx.
    from hx_requests.utils import is_hx_request

    request = RequestFactory().get("/", HTTP_HX_REQUEST="true")
    assert is_hx_request(request) is False


def test_urlconf_builds_without_touching_the_registry(clean_registry):
    # Importing the URLconf must build patterns without error even if the
    # registry was reset (initialize() runs inside get_urls()).
    HxRequestRegistry.reset()
    urls = HxRequestRegistry.get_urls()
    assert any(p.name == "simple_get" for p in urls)
```

- [ ] **Step 3: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_url_router.py -k "shares_context or plain_htmx or urlconf_builds" -v`
Expected: FAIL — `shares_context` handler / `view_flavor.html` not yet present (or context assertion fails).

- [ ] **Step 4: Implement (fixtures from Step 1) and re-run**

Run: `.venv/bin/python -m pytest tests/test_url_router.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_app/hx_requests.py tests/test_app/views.py tests/templates/view_flavor.html tests/test_url_router.py
git commit --no-verify -m "test: cover shares_context_from, fall-through, and startup ordering"
```

---

### Task 7: Documentation

**Files:**
- Create: `docs/` how-to page "Mounting HxRequests on URLs".
- Modify: the securing / how-it-works pages to note Django auth composes natively on the router path.

**Interfaces:** none (docs only). Locate the docs layout first: `ls docs/` and follow the existing `.rst`/`.md` convention and toctree.

- [ ] **Step 1: Inspect docs layout**

Run: `ls docs/ && find docs -name "*.rst" -o -name "index.*" | head`
Read the toctree/index to learn where a new how-to is registered.

- [ ] **Step 2: Write the how-to** (match the existing file format — `.rst` if the others are)

Cover, with runnable snippets:
- Wiring the router once in the root URLconf:
  ```python
  from hx_requests.hx_registry import HxRequestRegistry
  urlpatterns = [
      path("hx/", include((HxRequestRegistry.get_urls(), "hx_requests"), namespace="hx")),
  ]
  ```
- That it is additive/zero-config: templates need no edits (`hx_get`/`hx_post` emit `reverse("hx:<name>")` automatically, falling back to the current path when the router is not installed).
- `reverse("hx:<name>")` now works for hand-built URLs.
- Path binding: a token is bound to its handler's URL and cannot be replayed against another endpoint.
- `shares_context_from = SomeView` to reproduce page-view context on the router path, and the shared-context mixin as the cleaner long-term pattern. Note a router handler must declare its own `GET_template`/`POST_template` (there is no page-view template to fall back to), and that `shares_context_from` best fits `TemplateView`/`ListView` (a `DetailView`/`UpdateView` needing a URL pk is out of scope for the additive router — use `hx_object` from the token instead).
- That adding a handler needs a server restart (URLconf snapshot).

- [ ] **Step 3: Note native Django auth on the securing / how-it-works pages**

Add a short paragraph: on the router path the endpoint is a real Django `View`, so `login_required` / `LoginRequiredMixin` compose natively and the `hx_requests.W001` MRO trap does not apply (it remains relevant only for the legacy page-view path). Per-handler auth (`login_required` / `permission_required` / `has_permission`) works identically on both paths.

- [ ] **Step 4: Validate RST (if applicable) and commit**

If docs are `.rst`, validate with docutils as in prior PRs:
Run: `.venv/bin/pip install docutils >/dev/null 2>&1; .venv/bin/python -c "from docutils.core import publish_doctree; publish_doctree(open('docs/<newfile>.rst').read())"` (sphinx-only role warnings are fine).

```bash
git add docs/
git commit --no-verify -m "docs: how-to for mounting HxRequests on URLs (#10)"
```

---

## Final verification

- [ ] Run the full suite: `.venv/bin/python -m pytest -q` — all green.
- [ ] Lint: `~/.local/bin/ruff check hx_requests tests && ~/.local/bin/ruff format --check hx_requests tests` — clean (run `ruff format` to fix wrapping; pre-commit's ruff-format hook is what CI-adjacent checks use).
- [ ] Update `IMPROVEMENTS.md`: mark #10's status. Note this branch does not carry #202's GET-write guard (sibling branch); the guard composes automatically on the router path once #202 is in the base, because it lives in `HxRequest.dispatch`. Add a `test_get_writes`-style router assertion when this branch is rebased onto a base that includes #202.
- [ ] Update `PR #203` body: it currently says "Plan/spec only — no implementation." Change it to describe the implemented router (or confirm with the user whether the implementation should live on #203's `docs/url-router-spec` branch or a fresh `feat/url-router` branch stacked after #202).

## Open questions resolved (from the spec), for the record

1. **Legacy dispatch:** additive now; a later `feat!:` removes query-param dispatch. (Spec's recommendation.)
2. **Namespace:** fixed `hx:`. (Spec's assumption.)
3. **`get_urls()` timing:** `initialize()` at URLconf-build time; patterns are a snapshot; adding a handler needs a restart (documented).
4. **`shares_context_from` per-view-type preamble:** resolved by *reusing the existing `view` harvest seam* (assign the instantiated view to `hx_request.view`) rather than resurrecting `django_views.py`'s per-view-type setup. This reproduces today's behavior with near-zero new code (YAGNI); `TemplateView`/`ListView` are supported, pk-bound `DetailView`/`UpdateView` are explicitly out of scope for the additive step (use `hx_object`). This is a deliberate resolution of the spec's open question #4, not a contradiction of an approved decision — flag it for the user.
