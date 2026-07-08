"""Tests for the additive /hx/<name>/ URL router (#10)."""

from __future__ import annotations

import pytest
from django.http import Http404
from django.test import RequestFactory

from hx_requests.hx_registry import HxRequestRegistry
from hx_requests.hx_requests import BaseHxRequest
from hx_requests.utils import HX_TOKEN_PARAM, sign_hx_payload
from hx_requests.views import bind_hx_token

# --------------------------------------------------------------------------
# Shared token trust boundary (bind_hx_token)
# --------------------------------------------------------------------------


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


# --------------------------------------------------------------------------
# BaseHxRequest without a page view (router path)
# --------------------------------------------------------------------------


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


# --------------------------------------------------------------------------
# Registry -> urlpatterns
# --------------------------------------------------------------------------


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


# --------------------------------------------------------------------------
# Router endpoint (HxEndpointView) via real resolved URLs
# --------------------------------------------------------------------------


@pytest.fixture()
def hx_client(db, django_user_model):
    """A logged-in test client (handlers default to login_required=True)."""
    from django.test import Client

    user = django_user_model.objects.create_user(username="router", password="pw")
    client = Client()
    client.force_login(user)
    return client


def test_router_dispatches_get_to_handler(hx_client, clean_registry):
    from test_app.hx_requests import SimpleGetHx

    from tests.helpers import hx_get_url

    response = hx_get_url(hx_client, SimpleGetHx)
    assert response.status_code == 200
    assert b"simple" in response.content.lower()


def test_router_path_binding_rejects_replayed_token(hx_client, clean_registry):
    from django.urls import reverse
    from test_app.hx_requests import SimpleGetHx

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
    from django.test import Client
    from test_app.hx_requests import SimpleGetHx

    from tests.helpers import hx_get_url

    # Anonymous client + login_required default -> 404 (bodiless).
    anon = Client()
    response = hx_get_url(anon, SimpleGetHx)
    assert response.status_code == 404


def test_router_composes_with_bind_to_path(hx_client, clean_registry):
    from urllib.parse import urlparse

    from hx_requests.utils import get_url

    # A bind_to_path handler (the default): get_url binds the token to the router
    # endpoint URL it targets, so dispatching that exact URL through the endpoint
    # verifies (request.path there == the bound path).
    url = get_url({"request": RequestFactory().get("/page/")}, "simple_get", None)
    assert urlparse(url).path == "/hx/simple_get/"
    response = hx_client.get(url, HTTP_HX_REQUEST="true")
    assert response.status_code == 200


def test_router_rejects_token_bound_to_a_different_path(hx_client, clean_registry):
    from django.core import signing
    from django.urls import reverse

    from hx_requests.utils import HX_SIGNING_SALT

    # A token bound to the legacy page path, replayed against the router
    # endpoint, is rejected by the path-binding check.
    token = signing.dumps(
        {"name": "simple_get", "object": None, "kwargs": {}, "path": "/page/"},
        salt=HX_SIGNING_SALT,
    )
    response = hx_client.get(
        reverse("hx:simple_get"), data={HX_TOKEN_PARAM: token}, HTTP_HX_REQUEST="true"
    )
    assert response.status_code == 404


# --------------------------------------------------------------------------
# Template tag get_url(): reverse() with a legacy fallback
# --------------------------------------------------------------------------


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


# --------------------------------------------------------------------------
# Context sharing, plain-htmx fall-through, startup ordering
# --------------------------------------------------------------------------


def test_shares_context_from_reproduces_view_context(hx_client, clean_registry):
    from test_app.hx_requests import SharesContextHx

    from tests.helpers import hx_get_url

    response = hx_get_url(hx_client, SharesContextHx)
    assert response.status_code == 200
    assert b"from-the-view" in response.content


def test_no_shares_context_gets_no_view_context(hx_client, clean_registry):
    from django.urls import reverse

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
