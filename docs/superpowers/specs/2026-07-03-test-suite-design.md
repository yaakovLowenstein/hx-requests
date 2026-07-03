# hx-requests Test Suite Design

**Date:** 2026-07-03
**Branch:** `test-suite` (off `master`)

## Goal

A comprehensive pytest test suite for the whole `hx_requests` package. The
`tests/` directory is currently empty (only stale `__pycache__` from a deleted
suite); pytest is not yet a dev dependency. This is a greenfield suite.

Two complementary layers:

1. **Integration tests** — drive a real request through `HtmxViewMixin.dispatch()`
   using `RequestFactory`-based helpers (adapted from the user's other repos), so
   object deserialization, security checks, form handling, rendering, and
   trigger/header assembly all run end to end.
2. **Unit tests** — direct tests of every attribute, method, and pure function:
   trigger formatting, header assembly, modal HTML building, form
   kwargs/initial/message logic, serialization utils, security specs, registry
   internals. Anything that is supposed to work gets a direct test.

## Framework & Config

- pytest + pytest-django + pytest-cov (added to `[tool.poetry.group.dev.dependencies]`).
- `[tool.pytest.ini_options]` in `pyproject.toml`:
  `DJANGO_SETTINGS_MODULE = "tests.settings"`, `testpaths = ["tests"]`.
- No CI / tox in this pass (explicitly out of scope).

## Test Project Scaffolding (`tests/`)

- `settings.py` — minimal Django settings: `hx_requests`, `tests.test_app`,
  `tests.test_app_two` installed; in-memory SQLite; sessions, auth, and messages
  middleware; template dirs (`tests/templates`); sane `HX_REQUESTS_*` defaults
  (messages template, modal template). Individual tests use `override_settings`
  / pytest-django's `settings` fixture for the security and messages matrices.
- `test_app/` — primary app:
  - `models.py` — a simple model (e.g. `Widget(name, description)`).
  - `forms.py` — a `ModelForm` for the model and a plain `Form` with a required
    field (to drive invalid submissions).
  - `views.py` — `HtmxViewMixin` views: a `TemplateView`-based view (with
    `get_context_data`), a `ListView`, and an `UpdateView` (for
    `refresh_views_context_on_POST`).
  - `hx_requests.py` — HxRequest classes exercising every attribute; this file
    doubles as the AST-discovery fixture for file-style registry discovery.
- `test_app_two/` — secondary app:
  - Uses the `hx_requests/` **directory** layout (including a nested
    subpackage) to test directory-style discovery.
  - Serves as the "other app" in cross-app security-policy tests.
- `templates/` — GET/POST templates; templates with `{% block %}`s for
  django-render-block (single and multiple blocks); a messages template; a
  modal template with body/title/size context.
- `helpers.py` — the user's `hx_get`/`hx_post` helpers, adapted: real session
  via `SessionMiddleware`/`MessageMiddleware` (not the `"session"` string),
  since `use_messages` paths need working storage.
- `conftest.py` — fixtures: users (authed/anonymous), model instances, and an
  autouse guard around `HxRequestRegistry` global state (`reset()` where tests
  mutate it, restore discovery afterward).

## Test Files by Concern

### Integration (through `HtmxViewMixin`)

- `test_base_hx_request.py` — GET/POST round trips; `GET_template` /
  `POST_template` as str and list; fallback to the view's `template_name`;
  blocks as str / list / dict (and `ValueError` for invalid combos);
  `refresh_page`, `redirect`, `return_empty`, `no_swap` response headers and
  empty bodies; `kwargs_as_context` True/False; `get_views_context=False`
  (view context absent); `refresh_views_context_on_POST` (context re-fetched,
  view object refreshed); `hx_object` deserialization + custom
  `hx_object_name`; `use_current_url` GET-param merging (hx-vals params win);
  messages rendered/suppressed via `HX_REQUESTS_USE_HX_MESSAGES` ×
  `show_messages`; unsupported methods return 405; non-HTMX
  requests fall through to the normal view.
- `test_form_hx_request.py` — valid flow (object saved, success message,
  `POST_template`); invalid flow (GET_template re-rendered with bound form,
  error message); `instance` passed from `hx_object`; `get_form_kwargs`
  override; `set_initial_from_kwargs`; `show_form_invalid_message=False`;
  `add_form_errors_to_error_message`; `form_valid`/`form_invalid` returning
  their own `HttpResponse` short-circuits `post()` (the recent refactor);
  returning `None` builds the standard response.
- `test_delete_hx_request.py` — object deleted from DB; success message;
  custom `delete()` returning an `HttpResponse` short-circuits.
- `test_modal.py` — GET wraps `GET_template` in the modal template;
  title/`modal_size_classes` kwargs override class attributes; missing
  `HX_REQUESTS_MODAL_TEMPLATE` raises; custom
  `HX_REQUESTS_MODAL_CONTAINER_ID`/`HX_REQUESTS_MODAL_BODY_ID`;
  `FormModalHxRequest`: `closeHxModal` trigger on valid save (list and dict
  trigger returns), `close_modal_on_save=False`, `HX-Retarget` +
  `HX-Reswap: innerHTML` on invalid.
- `test_security.py` — the `is_hx_allowed` decision matrix through real
  requests: auth gate (`HX_REQUESTS_REQUIRE_AUTH` on/off,
  `HX_REQUESTS_UNAUTHENTICATED_ALLOW` list and dict forms incl. `__all__`);
  same-app allowed / cross-app blocked with `HX_REQUESTS_ENFORCE_SAME_APP`;
  `HX_REQUESTS_GLOBAL_ALLOW` list and dict forms; view `allowed_hx_requests`;
  `use_global_hx_rules` additive vs strict; Http404 for missing or unknown
  `hx_request_name` and for disallowed requests.

### Unit

- `test_triggers_unit.py` — `_format_trigger_value` (strings only → comma
  join; any dict → merged JSON; mixed); `get_trigger_headers` for list return,
  details merged into JSON; `format_triggers` output
  (list and dict input); `trigger_header_map` coverage of all three headers.
- `test_headers_unit.py` — `get_headers` precedence: `refresh_page` beats
  `redirect`; `no_swap` on GET and POST; trigger headers merged in.
- `test_attributes_unit.py` — every class attribute default asserted
  (`name`, `hx_object_name`, templates/blocks, flags) so accidental default
  changes are caught; `is_post_request` / `use_messages` cached properties;
  `hx_object_to_str`.
- `test_form_unit.py` — `get_form_kwargs` (GET vs POST, with/without
  `hx_object`); `get_initial` with `set_initial_from_kwargs` (matching and
  non-matching keys); `get_success_message` / `get_error_message` with and
  without `hx_object`; `get_form_errors` formatting (field and `__all__`
  errors).
- `test_modal_unit.py` — `_get_modal_html` context assembly; `modal_template`
  / `modal_container_id` / `modal_body_selector` settings resolution.
- `test_registry.py` — AST discovery of both layouts and nested dirs;
  `name = "..."` and `name: str = "..."` forms; non-string / missing `name`
  ignored; duplicate-name raises; lazy tuple entries resolved and cached on
  `get_hx_request`; unknown name → `None`; non-`BaseHxRequest` class with a
  `name` filtered at load; `register_hx_request` manual registration and
  duplicate rejection; `get_all_hx_requests` forces loading; `reset()`.
- `test_security_utils.py` — `is_allowed_by_spec` for list/tuple/set, dict
  with `__all__`, dict with name lists, empty/None spec, invalid rule values;
  `app_label_for_object` / `app_label_from_module` (real app, fallback,
  unknown module → None).
- `test_utils.py` — `serialize`/`deserialize` round trip for model instances
  (via `_base_manager`) and JSON values (str, int, dict, None, dates via
  `DjangoJSONEncoder`); `serialize_kwargs`/`deserialize_kwargs` prefixing and
  non-prefixed keys ignored; `is_htmx_request`; `get_url` (basic, with object,
  with kwargs, `use_full_path` filtering of internal params, existing query
  string → `&`); `get_csrf_token` (cookie present, absent, other cookies).
- `test_hx_tags.py` — `{% hx_get %}` / `{% hx_post %}` (CSRF `hx-headers`
  emitted when the cookie exists) / `{% hx_url %}` rendered through the real
  template engine with a request in context.
- `test_renderer_unit.py` — `Renderer.render` with and without a block name.

## Error Handling / Edge Cases Covered

- Invalid template/block combinations raise `ValueError`.
- Deleted `hx_object` on POST (`refresh_from_db` suppressed via
  `ObjectDoesNotExist`).
- `deserialize` of `None`-safe kwargs.
- 405 responses for unsupported HTTP methods on HTMX requests.

## Out of Scope

- CI workflows, tox, multi-version matrices.
- `django_views.py` helper functions beyond what the integration views
  exercise (ListView/UpdateView paths cover the used ones).
- Browser/JS behavior (modal.css, actual HTMX swaps).

## Success Criteria

- `pytest` passes from the repo root with no network or fixtures beyond
  SQLite in memory.
- Every documented attribute and public method of the package has at least
  one test; ~120–180 tests expected.
- Coverage (informational via pytest-cov) high across `hx_requests/`, with the
  registry, security, and hx_requests modules near-complete.
