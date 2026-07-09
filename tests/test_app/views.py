from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView, UpdateView
from test_app.models import Widget

from hx_requests.views import HtmxViewMixin


class BaseView(HtmxViewMixin, TemplateView):
    template_name = "base_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_flavor"] = "from-the-view"
        return context


class WidgetListView(HtmxViewMixin, ListView):
    model = Widget
    template_name = "widget_list.html"


class WidgetContextView(HtmxViewMixin, TemplateView):
    """View whose context mixes lazy and evaluated (snapshotted) values."""

    template_name = "widget_context.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # A separate, never-evaluated queryset: stays lazy until render time.
        context["widget_qs"] = Widget.objects.order_by("name")
        # A queryset force-evaluated now: its result cache is populated, so it
        # behaves like a snapshot from here on.
        evaluated_qs = Widget.objects.order_by("name")
        len(evaluated_qs)
        context["evaluated_qs"] = evaluated_qs
        snapshot = list(Widget.objects.order_by("name"))
        context["widget_list"] = snapshot  # evaluated snapshot
        context["widget_count"] = len(snapshot)  # scalar snapshot
        context["widget_names"] = [widget.name for widget in snapshot]  # array snapshot
        return context


class WidgetUpdateView(HtmxViewMixin, UpdateView):
    model = Widget
    fields = ["name", "description"]
    template_name = "widget_update.html"


class CountingView(HtmxViewMixin, TemplateView):
    """Records how many times its get() runs.

    Used to prove the page view's context harvest is deferred until the
    context is actually rendered -- and skipped entirely when a POST renders
    nothing (refresh_page / redirect / return_empty).
    """

    template_name = "base_view.html"
    get_call_count = 0

    def get(self, request, *args, **kwargs):
        type(self).get_call_count += 1
        return super().get(request, *args, **kwargs)


class AuthAfterHxView(HtmxViewMixin, LoginRequiredMixin, TemplateView):
    """
    Auth mixin ordered *after* HtmxViewMixin -- the trap the system check flags.
    Non-HTMX requests are still gated now that dispatch chains via super(); the
    HTMX path is not (that needs per-handler auth).

    ``raise_exception`` makes an unauthenticated request 403 instead of
    redirecting, so the test doesn't depend on a login URL / URLconf.
    """

    template_name = "base_view.html"
    raise_exception = True


class AuthBeforeHxView(LoginRequiredMixin, HtmxViewMixin, TemplateView):
    """Correct ordering: auth mixin before HtmxViewMixin gates every path."""

    template_name = "base_view.html"
    login_url = "/login/"
