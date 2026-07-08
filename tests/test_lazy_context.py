"""Tests that the page view's context harvest is lazy (audit item #4).

The page view's ``get()`` is only run to harvest its ``context_data`` when the
HxRequest actually renders that context. A POST that renders nothing from the
view (``refresh_page`` / ``redirect`` / ``return_empty``) must never pay the
page view's query cost.
"""

import pytest
from helpers import hx_get, hx_post
from test_app import hx_requests as hx
from test_app.views import CountingView


@pytest.mark.django_db()
def test_view_get_skipped_when_post_renders_nothing():
    CountingView.get_call_count = 0
    hx_post(hx.RefreshHx, CountingView)
    assert CountingView.get_call_count == 0


@pytest.mark.django_db()
def test_view_get_skipped_on_redirect_post():
    CountingView.get_call_count = 0
    hx_post(hx.RedirectHx, CountingView)
    assert CountingView.get_call_count == 0


@pytest.mark.django_db()
def test_view_get_skipped_on_return_empty_post():
    CountingView.get_call_count = 0
    hx_post(hx.ReturnEmptyHx, CountingView)
    assert CountingView.get_call_count == 0


@pytest.mark.django_db()
def test_view_get_runs_once_when_context_is_rendered():
    CountingView.get_call_count = 0
    hx_get(hx.SimpleGetHx, CountingView)
    assert CountingView.get_call_count == 1


@pytest.mark.django_db()
def test_refresh_context_on_post_reharvests_through_view_get():
    # refresh_views_context_on_POST rebuilds the view context by re-invoking
    # the same view.get() harvest path (not a divergent get_context_data call),
    # so the post-mutation snapshot goes through identical machinery. That is
    # the pre-post snapshot plus one fresh re-harvest = two view.get() calls.
    CountingView.get_call_count = 0
    hx_post(hx.AddWidgetRefreshContextHx, CountingView)
    assert CountingView.get_call_count == 2
