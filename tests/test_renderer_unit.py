"""Unit tests for the Renderer template/block dispatcher."""

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


def test_render_templates_returns_empty_for_unmatched_shapes():
    hx = SimpleGetHx()
    hx.request = RequestFactory().get("/")
    hx.renderer = Renderer()
    hx.view_response = None
    hx.hx_object = None
    # blocks=None matches no template/block case and falls through to "".
    assert hx._render_templates("simple.html", None) == ""
