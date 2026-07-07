"""Unit tests for the Renderer template/block dispatcher."""

import pytest
from django.test import RequestFactory
from test_app.hx_requests import SimpleGetHx

from hx_requests.hx_requests import Renderer


def test_renders_whole_template_without_block():
    html = Renderer().render("simple.html", None, {"view_flavor": "unit"}, None)
    assert "simple-template" in html
    assert "view_flavor:unit" in html


def test_renders_only_the_named_block():
    html = Renderer().render("blocks.html", "content", {}, None)
    assert html == "block-content"


def _bare_hx():
    hx = SimpleGetHx()
    hx.request = RequestFactory().get("/")
    hx.renderer = Renderer()
    hx.view_response = None
    hx.hx_object = None
    return hx


def test_render_templates_renders_whole_template_when_block_is_none():
    # A single template with no block renders the whole template (a falsy block
    # name means "no block"), rather than silently returning "".
    html = _bare_hx()._render_templates("simple.html", None)
    assert "simple-template" in html


def test_render_templates_raises_on_unsupported_shapes():
    with pytest.raises(ValueError, match="Unsupported template/block combination"):
        _bare_hx()._render_templates("simple.html", 123)
