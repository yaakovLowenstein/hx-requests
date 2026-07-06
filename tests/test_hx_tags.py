"""Tests for the hx_tags template tags."""

from urllib.parse import parse_qs, urlparse

import pytest
from django.template import Context, Template
from django.test import RequestFactory

from hx_requests.templatetags.hx_tags import hx_get, hx_post, hx_url
from hx_requests.utils import HX_TOKEN_PARAM, deserialize, deserialize_kwargs, unsign_hx_payload


def make_context(path="/page/", **extra):
    return {"request": RequestFactory().get(path, **extra)}


def payload_from_attr(attr):
    # attr looks like `hx-get=/page/?hx=<token>` (optionally with more attrs).
    url = attr.split("=", 1)[1].split(" ", 1)[0]
    query = parse_qs(urlparse(url).query)
    return unsign_hx_payload(query[HX_TOKEN_PARAM][0])


def test_hx_get_renders_attribute():
    out = hx_get(make_context(), "simple_get")
    assert out.startswith("hx-get=/page/?")
    assert payload_from_attr(out)["name"] == "simple_get"


@pytest.mark.django_db()
def test_hx_get_includes_object_and_kwargs(widget):
    out = hx_get(make_context(), "simple_get", object=widget, flavor="spicy")
    payload = payload_from_attr(out)
    assert payload["name"] == "simple_get"
    assert deserialize(payload["object"]) == widget
    assert deserialize_kwargs(**payload["kwargs"]) == {"flavor": "spicy"}


def test_hx_post_includes_csrf_headers_from_cookie():
    context = make_context(HTTP_COOKIE="csrftoken=tok123")
    out = hx_post(context, "simple_get")
    assert out.startswith("hx-post=/page/?")
    assert payload_from_attr(out)["name"] == "simple_get"
    assert 'hx-headers={"X-CSRFTOKEN":"tok123"}' in out


def test_hx_post_without_csrf_cookie_omits_headers():
    out = hx_post(make_context(), "simple_get")
    assert "hx-headers" not in out


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
