"""
HxRequest fixtures for the test suite.

This module is discovered by the registry's AST scan (file-style layout), so
every class here with a string-literal ``name`` doubles as a discovery
fixture. Names must be unique across the whole test project.
"""

from django.contrib import messages
from django.http import HttpResponse
from test_app.forms import WidgetForm
from test_app.models import Gadget, Widget

from hx_requests.hx_requests import (
    BaseHxRequest,
    DeleteHxRequest,
    FormHxRequest,
    FormModalHxRequest,
    ModalHxRequest,
)

# --------------------------------------------------------------------------
# Basic GET/POST + template/block variations
# --------------------------------------------------------------------------


class SimpleGetHx(BaseHxRequest):
    name = "simple_get"
    GET_template = "simple.html"


class ViewTemplateFallbackHx(BaseHxRequest):
    name = "view_template_fallback"


class PostTemplateHx(BaseHxRequest):
    name = "post_template"
    GET_template = "simple.html"
    POST_template = "post.html"


class MultiTemplateHx(BaseHxRequest):
    name = "multi_template"
    GET_template = ["simple.html", "second.html"]


class SingleBlockHx(BaseHxRequest):
    name = "single_block"
    GET_template = "blocks.html"
    GET_block = "content"


class MultiBlockHx(BaseHxRequest):
    name = "multi_block"
    GET_template = "blocks.html"
    GET_block = ["content", "footer"]


class DictBlockHx(BaseHxRequest):
    name = "dict_block"
    GET_block = {"blocks.html": "content", "blocks2.html": ["b1", "b2"]}


class DictBlockMultiTemplateHx(BaseHxRequest):
    name = "dict_block_multi_template"
    GET_template = ["simple.html", "second.html"]
    GET_block = {"blocks.html": "content"}


class InvalidBlocksHx(BaseHxRequest):
    name = "invalid_blocks"
    GET_template = ["simple.html", "second.html"]
    GET_block = ["content"]


# --------------------------------------------------------------------------
# Response header behaviors
# --------------------------------------------------------------------------


class RefreshHx(BaseHxRequest):
    name = "refresh"
    refresh_page = True


class RedirectHx(BaseHxRequest):
    name = "redirect_hx"
    redirect = "/somewhere-else/"


class ReturnEmptyHx(BaseHxRequest):
    name = "return_empty_hx"
    return_empty = True


class NoSwapHx(BaseHxRequest):
    name = "no_swap_hx"
    GET_template = "simple.html"
    no_swap = True


# --------------------------------------------------------------------------
# Context behaviors
# --------------------------------------------------------------------------


class KwargsContextHx(BaseHxRequest):
    name = "kwargs_context"
    GET_template = "kwargs.html"


class KwargsNamespacedHx(BaseHxRequest):
    name = "kwargs_namespaced"
    GET_template = "kwargs.html"
    kwargs_as_context = False
    # TemplateView.get_context_data(**kwargs) would put the kwargs into the
    # view context anyway; turn it off so the flag is tested in isolation.
    get_views_context = False


class NoViewsContextHx(BaseHxRequest):
    name = "no_views_context"
    GET_template = "simple.html"
    get_views_context = False


class RefreshViewsContextHx(BaseHxRequest):
    name = "refresh_views_context"
    POST_template = "refresh.html"
    refresh_views_context_on_POST = True

    def post(self, request, *args, **kwargs):
        # Simulate a side effect that changes the view's object behind the
        # scenes; the refreshed context should pick it up.
        Widget.objects.filter(pk=self.view.object.pk).update(name="updated-behind-the-scenes")
        return super().post(request, *args, **kwargs)


class StaleViewsContextHx(RefreshViewsContextHx):
    name = "stale_views_context"
    refresh_views_context_on_POST = False


class AddWidgetRefreshContextHx(BaseHxRequest):
    name = "add_widget_refresh_context"
    refresh_views_context_on_POST = True

    def post(self, request, *args, **kwargs):
        Widget.objects.create(name="added-in-post")
        return super().post(request, *args, **kwargs)


class AddWidgetStaleContextHx(AddWidgetRefreshContextHx):
    name = "add_widget_stale_context"
    refresh_views_context_on_POST = False


class CurrentUrlHx(BaseHxRequest):
    name = "current_url_hx"
    GET_template = "current_url.html"
    use_current_url = True


class ObjectEchoHx(BaseHxRequest):
    name = "object_echo"
    GET_template = "object.html"


class NamedObjectHx(BaseHxRequest):
    name = "named_object"
    GET_template = "widget_object.html"
    hx_object_name = "widget"


class ListEchoHx(BaseHxRequest):
    name = "list_echo"
    GET_template = "list_echo.html"


class ScopedGadgetHx(BaseHxRequest):
    """Scopes resolution via ``model`` -> the Gadget default manager, which
    hides archived rows."""

    name = "scoped_gadget"
    GET_template = "object.html"
    model = Gadget


class QuerysetScopedHx(BaseHxRequest):
    """Scopes resolution via an explicit ``get_queryset`` override."""

    name = "queryset_scoped"
    GET_template = "object.html"

    def get_queryset(self):
        return Widget.objects.filter(name__startswith="ok-")


# --------------------------------------------------------------------------
# Triggers
# --------------------------------------------------------------------------


class TriggerListHx(BaseHxRequest):
    name = "trigger_list"
    GET_template = "simple.html"

    def get_triggers(self, **kwargs):
        return ["eventA", "eventB"]


class TriggerDetailsHx(BaseHxRequest):
    name = "trigger_details"
    GET_template = "simple.html"

    def get_triggers(self, **kwargs):
        return ["plainEvent", {"showMessage": {"level": "info", "message": "Saved!"}}]


# --------------------------------------------------------------------------
# Messages
# --------------------------------------------------------------------------


class MessagePostHx(BaseHxRequest):
    name = "message_post"
    GET_template = "simple.html"

    def post(self, request, *args, **kwargs):
        messages.info(request, "posted-message")
        return super().post(request, *args, **kwargs)


class SilentMessagePostHx(MessagePostHx):
    name = "silent_message_post"
    show_messages = False


# --------------------------------------------------------------------------
# Forms
# --------------------------------------------------------------------------


class WidgetFormHx(FormHxRequest):
    name = "widget_form"
    form_class = WidgetForm
    GET_template = "form.html"
    POST_template = "form_success.html"


class InitialKwargsFormHx(WidgetFormHx):
    name = "initial_kwargs_form"
    set_initial_from_kwargs = True


class ErrorsInMessageFormHx(WidgetFormHx):
    name = "errors_in_message_form"
    add_form_errors_to_error_message = True


class NoInvalidMessageFormHx(WidgetFormHx):
    name = "no_invalid_message_form"
    show_form_invalid_message = False


class ShortCircuitFormHx(WidgetFormHx):
    name = "short_circuit_form"

    def form_valid(self, **kwargs):
        super().form_valid(**kwargs)
        return HttpResponse("custom-valid-response")

    def form_invalid(self, **kwargs):
        super().form_invalid(**kwargs)
        return HttpResponse("custom-invalid-response")


class CustomKwargsFormHx(WidgetFormHx):
    name = "custom_kwargs_form"

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super().get_form_kwargs(**kwargs)
        form_kwargs["prefix"] = "custom"
        return form_kwargs


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------


class WidgetDeleteHx(DeleteHxRequest):
    name = "widget_delete"
    POST_template = "post.html"


class ShortCircuitDeleteHx(DeleteHxRequest):
    name = "short_circuit_delete"

    def delete(self, **kwargs):
        # Deliberately does not delete; proves the short-circuit path.
        return HttpResponse("custom-delete-response")


# --------------------------------------------------------------------------
# Modals
# --------------------------------------------------------------------------


class BasicModalHx(ModalHxRequest):
    name = "basic_modal"
    GET_template = "modal_body.html"
    title = "Class Title"
    modal_size_classes = "modal-lg"


class WidgetFormModalHx(FormModalHxRequest):
    name = "widget_form_modal"
    form_class = WidgetForm
    GET_template = "form.html"
    POST_template = "form_success.html"


class KeepOpenFormModalHx(WidgetFormModalHx):
    name = "keep_open_form_modal"
    close_modal_on_save = False


class ExtraTriggersFormModalHx(WidgetFormModalHx):
    name = "extra_triggers_form_modal"

    def get_triggers(self, **kwargs):
        return [*super().get_triggers(**kwargs), "customEvent"]


# --------------------------------------------------------------------------
# Registry edge case: a class with a `name` that is NOT an HxRequest
# --------------------------------------------------------------------------


class NotAnHxRequest:
    name = "not_an_hx_request"
