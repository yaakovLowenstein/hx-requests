"""Integration tests for FormHxRequest driven through HtmxViewMixin."""

import pytest
from test_app import hx_requests as hx
from test_app.models import Widget
from test_app.views import BaseView

from tests.helpers import hx_get, hx_post

pytestmark = pytest.mark.django_db


def content_of(response):
    return response.content.decode()


# --------------------------------------------------------------------------
# GET
# --------------------------------------------------------------------------


def test_get_renders_unbound_form():
    response = hx_get(hx.WidgetFormHx, BaseView)
    html = content_of(response)
    assert "FORM-TEMPLATE" in html
    assert "HAS-ERRORS" not in html


def test_get_with_object_binds_form_to_instance(widget):
    response = hx_get(hx.WidgetFormHx, BaseView, hx_kwargs={"object": widget})
    assert "name-value:gizmo" in content_of(response)


def test_set_initial_from_kwargs_prefills_matching_fields():
    response = hx_get(
        hx.InitialKwargsFormHx, BaseView, hx_kwargs={"name": "prefill", "bogus": "ignored"}
    )
    assert "name-value:prefill" in content_of(response)


def test_initial_from_kwargs_off_by_default():
    response = hx_get(hx.WidgetFormHx, BaseView, hx_kwargs={"name": "prefill"})
    assert "name-value:-" in content_of(response)


def test_custom_form_kwargs_reach_the_form():
    response = hx_get(hx.CustomKwargsFormHx, BaseView)
    assert 'name="custom-name"' in content_of(response)


# --------------------------------------------------------------------------
# POST - valid
# --------------------------------------------------------------------------


def test_valid_post_saves_and_renders_post_template():
    response = hx_post(hx.WidgetFormHx, BaseView, post_data={"name": "new-widget", "description": "x"})
    assert Widget.objects.filter(name="new-widget").exists()
    assert "FORM-SAVED" in content_of(response)


def test_valid_post_sets_success_message():
    response = hx_post(hx.WidgetFormHx, BaseView, post_data={"name": "new-widget"})
    assert "MSG[success:Saved Successfully]" in content_of(response)


def test_valid_post_with_object_updates_instance_and_refreshes_context(widget):
    response = hx_post(
        hx.WidgetFormHx,
        BaseView,
        hx_kwargs={"object": widget},
        post_data={"name": "renamed", "description": ""},
    )
    widget.refresh_from_db()
    assert widget.name == "renamed"
    html = content_of(response)
    # hx_object is refreshed from the db before rendering the POST template.
    assert "FORM-SAVED|renamed" in html
    assert "MSG[success:Widget Saved Successfully.]" in html


# --------------------------------------------------------------------------
# POST - invalid
# --------------------------------------------------------------------------


def test_invalid_post_rerenders_get_template_with_errors():
    response = hx_post(hx.WidgetFormHx, BaseView, post_data={"name": ""})
    html = content_of(response)
    assert "FORM-TEMPLATE" in html
    assert "HAS-ERRORS" in html
    assert "FORM-SAVED" not in html


def test_invalid_post_sets_error_message():
    response = hx_post(hx.WidgetFormHx, BaseView, post_data={"name": ""})
    assert "Did not save successfully" in content_of(response)


def test_invalid_post_error_message_names_the_object(widget):
    response = hx_post(hx.WidgetFormHx, BaseView, hx_kwargs={"object": widget}, post_data={"name": ""})
    assert "Widget did not save" in content_of(response)


def test_form_errors_added_to_error_message():
    response = hx_post(hx.ErrorsInMessageFormHx, BaseView, post_data={"name": ""})
    html = content_of(response)
    assert "name:" in html
    assert "required" in html


def test_show_form_invalid_message_false_suppresses_error_message():
    response = hx_post(hx.NoInvalidMessageFormHx, BaseView, post_data={"name": ""})
    html = content_of(response)
    assert "MSG[" not in html
    # The form (with its errors) is still re-rendered.
    assert "HAS-ERRORS" in html


def test_invalid_post_does_not_save():
    hx_post(hx.WidgetFormHx, BaseView, post_data={"name": ""})
    assert Widget.objects.count() == 0


# --------------------------------------------------------------------------
# form_valid / form_invalid short-circuit
# --------------------------------------------------------------------------


def test_form_valid_returning_response_short_circuits():
    response = hx_post(hx.ShortCircuitFormHx, BaseView, post_data={"name": "made-it"})
    assert content_of(response) == "custom-valid-response"
    # The save from super().form_valid() still happened.
    assert Widget.objects.filter(name="made-it").exists()


def test_form_invalid_returning_response_short_circuits():
    response = hx_post(hx.ShortCircuitFormHx, BaseView, post_data={"name": ""})
    assert content_of(response) == "custom-invalid-response"
