"""Integration tests for BaseHxRequest driven through HtmxViewMixin."""

import json

import pytest
from django.http import Http404
from django.test import RequestFactory, override_settings
from test_app import hx_requests as hx
from test_app.models import Widget
from test_app.views import BaseView, WidgetContextView, WidgetListView, WidgetUpdateView

from tests.helpers import add_middleware_to_request, hx_get, hx_post

pytestmark = pytest.mark.django_db


def content_of(response):
    return response.content.decode()


# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------


def test_get_renders_get_template():
    response = hx_get(hx.SimpleGetHx, BaseView)
    assert response.status_code == 200
    assert "simple-template" in content_of(response)


def test_get_template_falls_back_to_view_template():
    response = hx_get(hx.ViewTemplateFallbackHx, BaseView)
    assert "base-view-template" in content_of(response)


def test_post_renders_post_template():
    response = hx_post(hx.PostTemplateHx, BaseView)
    assert "post-template" in content_of(response)


def test_post_template_falls_back_to_view_template():
    response = hx_post(hx.ViewTemplateFallbackHx, BaseView)
    assert "base-view-template" in content_of(response)


def test_multiple_get_templates_all_rendered():
    response = hx_get(hx.MultiTemplateHx, BaseView)
    html = content_of(response)
    assert "simple-template" in html
    assert "second-template" in html


def test_single_block_renders_only_the_block():
    response = hx_get(hx.SingleBlockHx, BaseView)
    html = content_of(response)
    assert "block-content" in html
    assert "full-blocks-template" not in html
    assert "block-footer" not in html


def test_multiple_blocks_of_one_template():
    response = hx_get(hx.MultiBlockHx, BaseView)
    html = content_of(response)
    assert "block-content" in html
    assert "block-footer" in html
    assert "full-blocks-template" not in html


def test_dict_blocks_render_blocks_per_template():
    response = hx_get(hx.DictBlockHx, BaseView)
    html = content_of(response)
    assert "block-content" in html
    assert "block-b1" in html
    assert "block-b2" in html
    # The GET_template (falling back to the view's template) is appended too.
    assert "base-view-template" in html
    # Whole block templates are not rendered.
    assert "full-blocks-template" not in html
    assert "full-blocks2-template" not in html


def test_dict_blocks_with_a_list_of_templates_appends_all_templates():
    response = hx_get(hx.DictBlockMultiTemplateHx, BaseView)
    html = content_of(response)
    assert "block-content" in html
    assert "simple-template" in html
    assert "second-template" in html
    assert "full-blocks-template" not in html


def test_list_of_templates_with_list_of_blocks_raises():
    with pytest.raises(ValueError, match="blocks must be a dictionary"):
        hx_get(hx.InvalidBlocksHx, BaseView)


# --------------------------------------------------------------------------
# Response headers / body shape
# --------------------------------------------------------------------------


def test_refresh_page_sets_hx_refresh_and_empty_body():
    response = hx_post(hx.RefreshHx, BaseView)
    assert response["HX-Refresh"] == "true"
    assert response.content == b""


def test_redirect_sets_hx_redirect_and_empty_body():
    response = hx_post(hx.RedirectHx, BaseView)
    assert response["HX-Redirect"] == "/somewhere-else/"
    assert response.content == b""


def test_return_empty_returns_empty_body():
    response = hx_post(hx.ReturnEmptyHx, BaseView)
    assert response.content == b""


def test_no_swap_sets_hx_reswap_none():
    response = hx_get(hx.NoSwapHx, BaseView)
    assert response["HX-Reswap"] == "none"
    assert "simple-template" in content_of(response)


def test_refresh_and_redirect_only_apply_on_post():
    response = hx_get(hx.RefreshHx, BaseView)
    assert not response.has_header("HX-Refresh")
    response = hx_get(hx.RedirectHx, BaseView)
    assert not response.has_header("HX-Redirect")


# --------------------------------------------------------------------------
# Context
# --------------------------------------------------------------------------


def test_views_context_is_available():
    response = hx_get(hx.SimpleGetHx, BaseView)
    assert "view_flavor:from-the-view" in content_of(response)


def test_get_views_context_false_excludes_view_context():
    response = hx_get(hx.NoViewsContextHx, BaseView)
    assert "view_flavor:-" in content_of(response)


def test_kwargs_as_context_puts_kwargs_directly_in_context():
    response = hx_get(hx.KwargsContextHx, BaseView, hx_kwargs={"flavor": "spicy"})
    html = content_of(response)
    assert "direct:spicy" in html
    assert "namespaced:-" in html


def test_kwargs_as_context_false_namespaces_kwargs():
    response = hx_get(hx.KwargsNamespacedHx, BaseView, hx_kwargs={"flavor": "spicy"})
    html = content_of(response)
    assert "direct:-" in html
    assert "namespaced:spicy" in html


def test_kwargs_flow_through_on_post():
    response = hx_post(hx.PostTemplateHx, BaseView, hx_kwargs={"flavor": "smoky"})
    assert "post-template|flavor:smoky" in content_of(response)


def test_list_view_context_is_available(widget):
    Widget.objects.create(name="second-widget")
    response = hx_get(hx.ListEchoHx, WidgetListView)
    assert "list-count:2" in content_of(response)


def test_refresh_views_context_on_post_refreshes_view_object(widget):
    response = hx_post(hx.RefreshViewsContextHx, WidgetUpdateView, view_kwargs={"pk": widget.pk})
    assert "refreshed-object:updated-behind-the-scenes" in content_of(response)


def test_views_context_stale_without_refresh_flag(widget):
    response = hx_post(hx.StaleViewsContextHx, WidgetUpdateView, view_kwargs={"pk": widget.pk})
    assert "refreshed-object:gizmo" in content_of(response)


def test_refresh_context_on_post_picks_up_new_queryset_rows(widget):
    # The POST creates a second widget; the refreshed context re-evaluates
    # querysets, lists, scalars, and arrays built from them.
    response = hx_post(hx.AddWidgetRefreshContextHx, WidgetContextView)
    html = content_of(response)
    assert "qs-count:2" in html
    assert "list-count:2" in html
    assert "count:2" in html
    assert "names:added-in-post,gizmo" in html


def test_stale_context_keeps_snapshotted_values_but_lazy_querysets_reevaluate(widget):
    response = hx_post(hx.AddWidgetStaleContextHx, WidgetContextView)
    html = content_of(response)
    # Values evaluated when the view context was captured stay stale.
    assert "list-count:1" in html
    assert "count:1" in html
    assert "names:gizmo" in html
    # But a lazy queryset in the context re-evaluates at render time and sees
    # the new row even without refresh_views_context_on_POST.
    assert "qs-count:2" in html


def test_force_evaluated_queryset_behaves_like_a_snapshot(widget):
    # A queryset evaluated while building the view context (len() populated
    # its result cache) no longer re-evaluates at render time: without the
    # refresh flag it stays stale, unlike its lazy twin.
    response = hx_post(hx.AddWidgetStaleContextHx, WidgetContextView)
    html = content_of(response)
    assert "evaluated-qs-count:1" in html
    assert "qs-count:2" in html

    # With the refresh flag the context is rebuilt, so it re-evaluates too.
    response = hx_post(hx.AddWidgetRefreshContextHx, WidgetContextView)
    assert "evaluated-qs-count:3" in content_of(response)


# --------------------------------------------------------------------------
# hx_object
# --------------------------------------------------------------------------


def test_hx_object_deserialized_into_context(widget):
    response = hx_get(hx.ObjectEchoHx, BaseView, hx_kwargs={"object": widget})
    assert "object|gizmo" in content_of(response)


def test_hx_object_name_renames_context_key(widget):
    response = hx_get(hx.NamedObjectHx, BaseView, hx_kwargs={"object": widget})
    html = content_of(response)
    assert "named-object|gizmo" in html
    assert "hx_object:-" in html


def test_no_object_leaves_hx_object_none():
    response = hx_get(hx.ObjectEchoHx, BaseView)
    assert "object|-" in content_of(response)


# --------------------------------------------------------------------------
# use_current_url
# --------------------------------------------------------------------------


def test_use_current_url_merges_params_from_hx_current_url_header():
    response = hx_get(
        hx.CurrentUrlHx,
        BaseView,
        get_params={"bar": "from-request"},
        request_attrs={
            "META": {"HTTP_HX_CURRENT_URL": "http://testserver/page?foo=from-url&bar=from-url"}
        },
    )
    html = content_of(response)
    assert "foo:from-url" in html
    # Params submitted with the request win over the current-URL ones.
    assert "bar:from-request" in html


def test_use_current_url_without_header_is_a_noop():
    response = hx_get(hx.CurrentUrlHx, BaseView, get_params={"bar": "from-request"})
    html = content_of(response)
    assert "foo:-" in html
    assert "bar:from-request" in html


# --------------------------------------------------------------------------
# Triggers
# --------------------------------------------------------------------------


def test_trigger_list_emitted_on_hx_trigger_header():
    response = hx_get(hx.TriggerListHx, BaseView)
    assert response["HX-Trigger"] == "eventA, eventB"


def test_trigger_with_details_emitted_as_json():
    response = hx_get(hx.TriggerDetailsHx, BaseView)
    assert json.loads(response["HX-Trigger"]) == {
        "plainEvent": True,
        "showMessage": {"level": "info", "message": "Saved!"},
    }


def test_no_triggers_means_no_trigger_header():
    response = hx_get(hx.SimpleGetHx, BaseView)
    assert not response.has_header("HX-Trigger")


# --------------------------------------------------------------------------
# Messages
# --------------------------------------------------------------------------


def test_message_rendered_after_post():
    response = hx_post(hx.MessagePostHx, BaseView)
    assert "MSG[info:posted-message]" in content_of(response)


def test_show_messages_false_suppresses_messages():
    response = hx_post(hx.SilentMessagePostHx, BaseView)
    assert "MSG[" not in content_of(response)


@override_settings(HX_REQUESTS_USE_HX_MESSAGES=False)
def test_messages_disabled_globally():
    response = hx_post(hx.MessagePostHx, BaseView)
    assert "MSG[" not in content_of(response)


# --------------------------------------------------------------------------
# Dispatch / routing
# --------------------------------------------------------------------------


def test_unsupported_method_returns_405():
    request = RequestFactory().patch("/?hx_request_name=simple_get")
    request.META["HTTP_HX_REQUEST"] = True
    add_middleware_to_request(request)
    response = BaseView.as_view()(request)
    assert response.status_code == 405


def test_unknown_http_method_is_rejected_by_the_view():
    request = RequestFactory().generic("FOOBAR", "/")
    response = BaseView.as_view()(request)
    assert response.status_code == 405


def test_non_htmx_request_falls_through_to_the_view():
    request = RequestFactory().get("/")
    response = BaseView.as_view()(request)
    response.render()
    assert "base-view-template" in content_of(response)
    assert "view_flavor:from-the-view" in content_of(response)


def test_missing_hx_request_name_raises_404():
    request = RequestFactory().get("/")
    request.META["HTTP_HX_REQUEST"] = True
    add_middleware_to_request(request)
    with pytest.raises(Http404, match="Missing required query param"):
        BaseView.as_view()(request)


def test_unknown_hx_request_name_raises_404():
    request = RequestFactory().get("/", data={"hx_request_name": "does_not_exist"})
    request.META["HTTP_HX_REQUEST"] = True
    add_middleware_to_request(request)
    with pytest.raises(Http404, match="No HxRequest found"):
        BaseView.as_view()(request)
