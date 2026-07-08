"""Security tests for the signed round-trip token (IMPROVEMENTS #1).

These assert, through a real view, that the exploits the loose-param scheme
allowed are closed: framework data (name/object/kwargs) is only trusted when it
arrives inside the HMAC-signed ``hx`` token. Anything a client appends to the
raw query string is ignored, so it can neither forge context flags nor shadow
the signed object, and malformed input fails the signature check instead of
reaching a deserializer (no 500s).
"""

import pytest
from django.http import Http404
from django.test import RequestFactory
from test_app import hx_requests as hx
from test_app.views import BaseView

from hx_requests.utils import HX_TOKEN_PARAM, sign_hx_payload
from tests.helpers import add_middleware_to_request, content_of, hx_get

pytestmark = pytest.mark.django_db


def test_loose_kwarg_param_is_not_injected_into_context():
    # Attacker appends &___flavor="forged" to a URL that carries a valid token.
    # The loose kwarg must never reach the template context.
    response = hx_get(hx.KwargsContextHx, BaseView, get_params={"___flavor": '"forged"'})
    html = content_of(response)
    assert "direct:-" in html
    assert "forged" not in html


def test_non_json_loose_kwarg_does_not_500():
    # A non-JSON loose ___ param used to hit json.loads -> JSONDecodeError -> 500.
    # It is now ignored (kwargs come only from the signed token).
    response = hx_get(hx.KwargsContextHx, BaseView, get_params={"___flavor": "not-json"})
    assert response.status_code == 200
    assert "direct:-" in content_of(response)


def test_unsigned_hx_token_is_rejected():
    # A hand-crafted token that was never signed fails verification -> 404,
    # not an unhandled deserializer error.
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: "totally-not-a-token"})
    request.META["HTTP_HX_REQUEST"] = True
    add_middleware_to_request(request)
    with pytest.raises(Http404, match="Invalid or tampered"):
        BaseView.as_view()(request)


def test_resolve_strips_client_supplied_framework_params():
    # Everything the framework trusts comes from the token; any framework params
    # a client tacks onto the raw query string are dropped before dispatch, so
    # they cannot shadow or forge the verified values. Non-framework params
    # (page filters etc.) survive.
    token = sign_hx_payload("simple_get")
    request = RequestFactory().get(
        "/",
        data={
            HX_TOKEN_PARAM: token,
            "object": "model_instance__test_app__widget__999",
            "hx_request_name": "other",
            "page": "2",
        },
    )
    add_middleware_to_request(request)

    BaseView()._resolve_hx_token(request)

    assert request.GET.get("object") is None  # loose object dropped, token had none
    assert request.hx_payload["name"] == "simple_get"  # from token, not "other"
    assert request.GET["page"] == "2"  # legit loose param preserved
    # A loose param a client invents (whatever its name) is harmless: kwargs are
    # sourced only from the signed token, never from raw query input.
    assert request._hx_kwargs == {}  # kwargs sourced only from the token


def test_resolve_does_not_smuggle_framework_data_through_get(widget):
    # The verified name/object ride on request.hx_payload, never written back
    # into request.GET. Otherwise a page-view template's
    # `{{ request.GET.urlencode }}` (e.g. a pagination link) would carry
    # hx_request_name/object into every link on the page.
    token = sign_hx_payload("edit_widget", widget, flavor="spicy")
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: token, "page": "2"})
    add_middleware_to_request(request)

    BaseView()._resolve_hx_token(request)

    assert request.hx_payload["name"] == "edit_widget"
    assert request.hx_payload["object"]  # serialized ref present in the payload
    assert "hx_request_name" not in request.GET
    assert "object" not in request.GET
    assert HX_TOKEN_PARAM not in request.GET
    assert request.GET.urlencode() == "page=2"  # only the loose param survives
