"""Integration tests for DeleteHxRequest."""

import pytest
from test_app import hx_requests as hx
from test_app.models import Widget
from test_app.views import BaseView

from tests.helpers import hx_post

pytestmark = pytest.mark.django_db


def test_post_deletes_the_object(widget):
    response = hx_post(hx.WidgetDeleteHx, BaseView, hx_kwargs={"object": widget})
    assert not Widget.objects.filter(pk=widget.pk).exists()
    assert response.status_code == 200


def test_post_sets_success_message(widget):
    response = hx_post(hx.WidgetDeleteHx, BaseView, hx_kwargs={"object": widget})
    assert "MSG[success:Widget deleted successfully.]" in response.content.decode()


def test_post_renders_post_template(widget):
    response = hx_post(hx.WidgetDeleteHx, BaseView, hx_kwargs={"object": widget})
    assert "post-template" in response.content.decode()


def test_delete_returning_response_short_circuits(widget):
    response = hx_post(hx.ShortCircuitDeleteHx, BaseView, hx_kwargs={"object": widget})
    assert response.content.decode() == "custom-delete-response"
    # The custom delete() never deleted the object.
    assert Widget.objects.filter(pk=widget.pk).exists()
