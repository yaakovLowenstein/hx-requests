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


class WidgetUpdateView(HtmxViewMixin, UpdateView):
    model = Widget
    fields = ["name", "description"]
    template_name = "widget_update.html"


class AllowListView(BaseView):
    """View that explicitly allows a cross-app HxRequest (additive rules)."""

    allowed_hx_requests = ["other_app_hx"]


class StrictAllowListView(BaseView):
    """View whose allow list is exclusive (global rules turned off)."""

    allowed_hx_requests = ["simple_get"]
    use_global_hx_rules = False
