"""Security tests for optional path-binding of the signed hx token.

A handler may set ``bind_to_path = True`` to have its token bound to the URL
path it was rendered on. Such a token verifies only when it is replayed back to
that same path, which narrows the "replay from another page" surface. This is
origin hardening layered on top of authorization -- not a replacement for it.
"""

from urllib.parse import parse_qs, urlparse

import pytest
from django.core import signing
from django.http import Http404
from django.test import RequestFactory, override_settings
from test_app.views import BaseView

from hx_requests.templatetags.hx_tags import hx_url
from hx_requests.utils import HX_SIGNING_SALT, HX_TOKEN_PARAM, unsign_hx_payload
from tests.helpers import add_middleware_to_request

pytestmark = pytest.mark.django_db


def _payload_from_url(url):
    query = parse_qs(urlparse(url).query)
    return unsign_hx_payload(query[HX_TOKEN_PARAM][0])


def _bound_request(path, bound_to):
    # A validly-signed token whose payload is bound to ``bound_to``, arriving at
    # ``path``. Built by hand so the wire format is explicit and the test does
    # not depend on the mint side.
    token = signing.dumps(
        {"name": "simple_get", "object": None, "kwargs": {}, "path": bound_to},
        salt=HX_SIGNING_SALT,
    )
    request = RequestFactory().get(path, data={HX_TOKEN_PARAM: token})
    request.META["HTTP_HX_REQUEST"] = True
    add_middleware_to_request(request)
    return request


def test_tokens_are_path_bound_by_default():
    # Path-binding is on by default: an ordinary handler binds its render path.
    out = hx_url({"request": RequestFactory().get("/page/")}, "simple_get")
    assert _payload_from_url(out).get("path") == "/page/"


def test_opted_out_handler_has_no_path():
    # A handler with bind_to_path = False mints an unbound token.
    out = hx_url({"request": RequestFactory().get("/page/")}, "unbound")
    assert "path" not in _payload_from_url(out)


def test_replaying_bound_token_to_a_different_path_is_rejected():
    # The exact vector path-binding closes: a real token minted on /page/ is
    # replayed against /other/. It must be rejected before dispatch.
    request = _bound_request(path="/other/", bound_to="/page/")
    with pytest.raises(Http404):
        BaseView()._resolve_hx_token(request)


def test_bound_token_on_its_own_path_is_accepted():
    # The legitimate case: the token is used on the path it was bound to.
    request = _bound_request(path="/page/", bound_to="/page/")
    BaseView()._resolve_hx_token(request)
    assert request.GET["hx_request_name"] == "simple_get"


@override_settings(HX_REQUESTS_BIND_TOKEN_TO_PATH=False)
def test_global_setting_disables_binding_at_mint():
    # The global kill switch stops new tokens from being path-bound at all.
    out = hx_url({"request": RequestFactory().get("/page/")}, "simple_get")
    assert "path" not in _payload_from_url(out)


@override_settings(HX_REQUESTS_BIND_TOKEN_TO_PATH=False)
def test_global_setting_disables_enforcement():
    # It also stops enforcement, so already-minted bound tokens stop 404ing
    # immediately (e.g. after enabling it to work around path rewriting).
    request = _bound_request(path="/other/", bound_to="/page/")
    BaseView()._resolve_hx_token(request)
    assert request.GET["hx_request_name"] == "simple_get"
