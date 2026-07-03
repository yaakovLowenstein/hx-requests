"""Unit tests for the generic-view get helpers in hx_requests.django_views."""

import pytest
from django.http import Http404
from django.test import RequestFactory
from test_app.models import Widget
from test_app.views import WidgetListView, WidgetUpdateView

from hx_requests.django_views import (
    create_view_get,
    date_view_get,
    delete_view_get,
    detail_view_get,
    list_view_get,
    update_view_get,
)

pytestmark = pytest.mark.django_db


def make_list_view(**attrs):
    view = WidgetListView()
    view.kwargs = {}
    view.request = RequestFactory().get("/")
    for key, value in attrs.items():
        setattr(view, key, value)
    return view


def make_object_view(**kwargs):
    view = WidgetUpdateView()
    view.kwargs = kwargs
    view.request = RequestFactory().get("/")
    return view


class TestListViewGet:
    def test_sets_object_list(self, widget):
        view = make_list_view()
        list_view_get(view, view.request)
        assert list(view.object_list) == [widget]

    def test_allow_empty_false_with_results_passes(self, widget):
        view = make_list_view(allow_empty=False)
        list_view_get(view, view.request)
        assert list(view.object_list) == [widget]

    def test_allow_empty_false_and_empty_raises_404(self):
        view = make_list_view(allow_empty=False)
        with pytest.raises(Http404):
            list_view_get(view, view.request)

    def test_allow_empty_false_uses_cheap_exists_check_when_paginated(self):
        view = make_list_view(allow_empty=False, paginate_by=5)
        with pytest.raises(Http404):
            list_view_get(view, view.request)


def test_update_view_get_sets_object(widget):
    view = make_object_view(pk=widget.pk)
    update_view_get(view, view.request)
    assert view.object == widget


def test_detail_view_get_sets_object(widget):
    view = make_object_view(pk=widget.pk)
    detail_view_get(view, view.request)
    assert view.object == widget


def test_delete_view_get_sets_object(widget):
    view = make_object_view(pk=widget.pk)
    delete_view_get(view, view.request)
    assert view.object == widget


def test_create_view_get_sets_object_to_none():
    view = make_object_view()
    create_view_get(view, view.request)
    assert view.object is None


def test_date_view_get_returns_dated_context():
    class FakeDateView:
        def get_dated_items(self):
            return (["2020"], list(Widget.objects.none()), {"extra_key": "x"})

    result = date_view_get(FakeDateView(), None)
    assert result == {"object_list": [], "date_list": ["2020"], "extra_key": "x"}
