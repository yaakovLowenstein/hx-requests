"""Integration tests for ModalHxRequest and FormModalHxRequest."""

import pytest
from django.test import override_settings
from test_app import hx_requests as hx
from test_app.models import Widget
from test_app.views import BaseView

from tests.helpers import content_of, hx_get, hx_post

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------
# ModalHxRequest
# --------------------------------------------------------------------------


def test_get_wraps_template_in_modal():
    response = hx_get(hx.BasicModalHx, BaseView)
    html = content_of(response)
    assert "MODAL[title=Class Title" in html
    assert "size=modal-lg" in html
    assert "MODAL-BODY-CONTENT" in html


def test_modal_body_gets_full_context():
    response = hx_get(hx.BasicModalHx, BaseView)
    assert "view_flavor:from-the-view" in content_of(response)


def test_title_and_size_kwargs_override_class_attributes():
    response = hx_get(
        hx.BasicModalHx,
        BaseView,
        hx_kwargs={"title": "Kwarg Title", "modal_size_classes": "modal-sm"},
    )
    html = content_of(response)
    assert "title=Kwarg Title" in html
    assert "size=modal-sm" in html


def test_post_is_not_wrapped_in_modal():
    response = hx_post(hx.BasicModalHx, BaseView)
    assert "MODAL[" not in content_of(response)


@override_settings(HX_REQUESTS_MODAL_TEMPLATE=None)
def test_missing_modal_template_setting_raises():
    with pytest.raises(Exception, match="HX_REQUESTS_MODAL_TEMPLATE"):
        hx_get(hx.BasicModalHx, BaseView)


# --------------------------------------------------------------------------
# FormModalHxRequest
# --------------------------------------------------------------------------


def test_form_modal_get_renders_form_inside_modal():
    response = hx_get(hx.WidgetFormModalHx, BaseView)
    html = content_of(response)
    assert "MODAL[" in html
    assert "FORM-TEMPLATE" in html


def test_valid_post_triggers_close_modal():
    response = hx_post(hx.WidgetFormModalHx, BaseView, post_data={"name": "modal-widget"})
    assert "closeHxModal" in response["HX-Trigger"]
    assert Widget.objects.filter(name="modal-widget").exists()


def test_close_modal_trigger_combines_with_custom_triggers():
    response = hx_post(hx.ExtraTriggersFormModalHx, BaseView, post_data={"name": "phase-widget"})
    assert "closeHxModal" in response["HX-Trigger"]
    assert "customEvent" in response["HX-Trigger"]


def test_close_modal_on_save_false_keeps_modal_open():
    response = hx_post(hx.KeepOpenFormModalHx, BaseView, post_data={"name": "kept-open"})
    assert not response.has_header("HX-Trigger")


def test_invalid_post_retargets_the_modal_body():
    response = hx_post(hx.WidgetFormModalHx, BaseView, post_data={"name": ""})
    assert response["HX-Retarget"] == "#hx_modal_body"
    assert response["HX-Reswap"] == "innerHTML"
    assert "HAS-ERRORS" in content_of(response)


def test_invalid_post_does_not_close_modal():
    response = hx_post(hx.WidgetFormModalHx, BaseView, post_data={"name": ""})
    assert not response.has_header("HX-Trigger")


@override_settings(HX_REQUESTS_MODAL_BODY_ID="#custom-body")
def test_modal_body_selector_setting_controls_retarget():
    response = hx_post(hx.WidgetFormModalHx, BaseView, post_data={"name": ""})
    assert response["HX-Retarget"] == "#custom-body"
