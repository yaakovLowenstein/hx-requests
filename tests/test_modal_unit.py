"""Unit tests for modal settings resolution and modal HTML assembly."""

import pytest
from django.test import RequestFactory, override_settings
from test_app.hx_requests import BasicModalHx, WidgetFormModalHx

from hx_requests.hx_requests import ModalHxRequest, Renderer


def make_modal(cls=BasicModalHx):
    hx = cls()
    hx.request = RequestFactory().get("/")
    hx.renderer = Renderer()
    hx.view_response = None
    hx.hx_object = None
    return hx


def test_modal_container_id_default():
    assert make_modal().modal_container_id == "hx_modal_container"


@override_settings(HX_REQUESTS_MODAL_CONTAINER_ID="my_container")
def test_modal_container_id_from_settings():
    assert make_modal().modal_container_id == "my_container"


def test_modal_template_from_settings():
    assert make_modal().modal_template == "hx_modal.html"


@override_settings(HX_REQUESTS_MODAL_TEMPLATE=None)
def test_modal_template_missing_raises():
    with pytest.raises(Exception, match="HX_REQUESTS_MODAL_TEMPLATE"):
        make_modal().modal_template  # noqa: B018


def test_modal_body_selector_default():
    assert make_modal(WidgetFormModalHx).modal_body_selector == "#hx_modal_body"


@override_settings(HX_REQUESTS_MODAL_BODY_ID="#elsewhere")
def test_modal_body_selector_from_settings():
    assert make_modal(WidgetFormModalHx).modal_body_selector == "#elsewhere"


def test_get_modal_html_assembles_title_size_and_body():
    hx = make_modal()
    html = hx._get_modal_html({})
    assert "title=Class Title" in html
    assert "size=modal-lg" in html
    assert "MODAL-BODY-CONTENT" in html


def test_get_modal_html_kwargs_override_attributes():
    hx = make_modal()
    html = hx._get_modal_html({"title": "Other", "modal_size_classes": "sm"})
    assert "title=Other" in html
    assert "size=sm" in html


def test_generic_modal_defaults():
    assert ModalHxRequest.title == ""
    assert ModalHxRequest.modal_size_classes == ""
