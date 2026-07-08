"""Tests for the hx_tags template tags."""

import html
import json
import re
from urllib.parse import parse_qs, urlparse

import pytest
from django.template import Context, Template

from hx_requests.templatetags.hx_tags import hx_get, hx_post, hx_url
from hx_requests.utils import HX_TOKEN_PARAM, deserialize, deserialize_kwargs, unsign_hx_payload
from tests.helpers import make_context


def attr_value(attr, name):
    # Attributes are emitted quoted, e.g. `hx-get="/page/?hx=<token>"`; the URL
    # is HTML-escaped inside the quotes, so unescape before parsing.
    match = re.search(rf"""{name}=(["'])(.*?)\1""", attr)
    assert match, f"{name} not found in {attr!r}"
    return html.unescape(match.group(2))


def payload_from_attr(attr, name="hx-get"):
    url = attr_value(attr, name)
    query = parse_qs(urlparse(url).query)
    return unsign_hx_payload(query[HX_TOKEN_PARAM][0])


def test_hx_get_renders_quoted_attribute():
    out = hx_get(make_context(), "simple_get")
    assert out.startswith('hx-get="/page/?')
    assert out.endswith('"')
    assert payload_from_attr(out)["name"] == "simple_get"


@pytest.mark.django_db()
def test_hx_get_includes_object_and_kwargs(widget):
    out = hx_get(make_context(), "simple_get", object=widget, flavor="spicy")
    payload = payload_from_attr(out)
    assert payload["name"] == "simple_get"
    assert deserialize(payload["object"]) == widget
    assert deserialize_kwargs(**payload["kwargs"]) == {"flavor": "spicy"}


def test_hx_post_renders_quoted_attribute_and_csrf_headers():
    out = hx_post(make_context(), "simple_get")
    assert out.startswith('hx-post="/page/?')
    assert payload_from_attr(out, "hx-post")["name"] == "simple_get"

    # hx-headers is emitted as a quoted attribute carrying JSON; the JSON's
    # double quotes are HTML-escaped inside the attribute value.
    headers = json.loads(attr_value(out, "hx-headers"))
    token = headers["X-CSRFTOKEN"]
    # A non-empty CSRF token string is emitted. The exact length/format is
    # Django's business (a masked token today) -- don't couple the test to it.
    assert isinstance(token, str)
    assert token


def test_hx_post_always_includes_csrf_headers():
    # get_token mints a token from the request regardless of cookies, so the
    # CSRF header is always present (previously it was dropped when no
    # csrftoken cookie was set, silently breaking POSTs).
    assert "hx-headers" in hx_post(make_context(), "simple_get")
    assert "hx-headers" in hx_post(make_context(HTTP_COOKIE="a=b"), "simple_get")


def test_hx_url_returns_bare_url():
    out = hx_url(make_context(), "simple_get")
    assert out.startswith("/page/?")
    query = parse_qs(urlparse(out).query)
    assert unsign_hx_payload(query[HX_TOKEN_PARAM][0])["name"] == "simple_get"


def test_tags_render_through_the_template_engine():
    template = Template("{% load hx_tags %}{% hx_url 'simple_get' %}")
    rendered = template.render(Context(make_context()))
    assert rendered.startswith("/page/?")
    query = parse_qs(urlparse(rendered).query)
    assert unsign_hx_payload(query[HX_TOKEN_PARAM][0])["name"] == "simple_get"
