"""Unit tests for FormHxRequest internals (kwargs, initial, messages, errors)."""

import pytest
from django.test import RequestFactory
from test_app.forms import CleanErrorForm, WidgetForm
from test_app.hx_requests import WidgetFormHx


def make_hx(method="get", data=None, hx_object=None):
    hx = WidgetFormHx()
    factory = RequestFactory()
    hx.request = factory.post("/", data=data or {}) if method == "post" else factory.get("/")
    hx.hx_object = hx_object
    return hx


class TestGetFormKwargs:
    def test_get_request_has_only_initial(self):
        assert make_hx().get_form_kwargs() == {"initial": {}}

    def test_post_request_includes_data_and_files(self):
        kwargs = make_hx("post", data={"name": "x"}).get_form_kwargs()
        assert kwargs["data"]["name"] == "x"
        assert "files" in kwargs

    @pytest.mark.django_db()
    def test_hx_object_becomes_the_form_instance(self, widget):
        kwargs = make_hx(hx_object=widget).get_form_kwargs()
        assert kwargs["instance"] == widget


class TestGetInitial:
    def test_empty_by_default(self):
        assert make_hx().get_initial(name="x") == {}

    def test_set_initial_from_kwargs_uses_only_form_fields(self):
        hx = make_hx()
        hx.set_initial_from_kwargs = True
        initial = hx.get_initial(name="x", description="y", bogus="z")
        assert initial == {"name": "x", "description": "y"}


class TestMessages:
    def test_success_message_without_object(self):
        assert make_hx().get_success_message() == "Saved Successfully"

    @pytest.mark.django_db()
    def test_success_message_with_object(self, widget):
        assert make_hx(hx_object=widget).get_success_message() == "Widget Saved Successfully."

    def test_error_message_without_object(self):
        assert "Did not save successfully" in make_hx().get_error_message()

    @pytest.mark.django_db()
    def test_error_message_with_object(self, widget):
        assert "Widget did not save" in make_hx(hx_object=widget).get_error_message()

    def test_error_message_includes_form_errors_when_enabled(self):
        hx = make_hx()
        hx.add_form_errors_to_error_message = True
        hx.form = WidgetForm(data={})
        assert hx.form.is_valid() is False
        message = hx.get_error_message()
        assert "name:" in message
        assert "required" in message


class TestGetFormErrors:
    def test_field_errors_are_prefixed_with_the_field_name(self):
        hx = make_hx()
        hx.form = WidgetForm(data={})
        hx.form.is_valid()
        errors = hx.get_form_errors()
        assert errors.startswith("name:")
        assert "required" in errors

    def test_non_field_errors_have_no_prefix(self):
        hx = make_hx()
        hx.form = CleanErrorForm(data={"name": "x"})
        hx.form.is_valid()
        errors = hx.get_form_errors()
        assert "top level problem" in errors
        assert "__all__" not in errors
