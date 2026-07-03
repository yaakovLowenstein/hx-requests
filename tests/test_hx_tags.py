"""Tests for the hx_tags template tags."""

import pytest
from django.template import Context, Template
from django.test import RequestFactory

from hx_requests.templatetags.hx_tags import hx_get, hx_post, hx_url


def make_context(path="/page/", **extra):
    return {"request": RequestFactory().get(path, **extra)}


def test_hx_get_renders_attribute():
    assert hx_get(make_context(), "simple_get") == "hx-get=/page/?hx_request_name=simple_get"


@pytest.mark.django_db()
def test_hx_get_includes_object_and_kwargs(widget):
    out = hx_get(make_context(), "simple_get", object=widget, flavor="spicy")
    assert out.startswith("hx-get=/page/?hx_request_name=simple_get")
    assert f"object=model_instance__test_app__widget__{widget.pk}" in out
    assert "___flavor=%22spicy%22" in out


def test_hx_post_includes_csrf_headers_from_cookie():
    context = make_context(HTTP_COOKIE="csrftoken=tok123")
    out = hx_post(context, "simple_get")
    assert out.startswith("hx-post=/page/?hx_request_name=simple_get")
    assert 'hx-headers={"X-CSRFTOKEN":"tok123"}' in out


def test_hx_post_without_csrf_cookie_omits_headers():
    out = hx_post(make_context(), "simple_get")
    assert "hx-headers" not in out


def test_hx_url_returns_bare_url():
    assert hx_url(make_context(), "simple_get") == "/page/?hx_request_name=simple_get"


def test_tags_render_through_the_template_engine():
    template = Template("{% load hx_tags %}{% hx_url 'simple_get' %}")
    rendered = template.render(Context(make_context()))
    assert rendered == "/page/?hx_request_name=simple_get"
