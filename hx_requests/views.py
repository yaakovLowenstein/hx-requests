import importlib
import inspect
import json
from typing import Any, Dict

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import View

from hx_requests.utils import deserialize_kwargs, is_htmx_request


@method_decorator(ensure_csrf_cookie, name="dispatch")
class HtmxVIewMixin(View):
    """
    Mixin to be added to views that are using HXRequests.
    Hijacks the get and post to route them to the proper
    HXReqeust.
    """

    hx_requests: Dict = []

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if is_htmx_request(request):
            super().get(request, *args, **kwargs)
            hx_request = self.get_hx_request(request)
            hx_request.view = self
            kwargs = self.get_extra_kwargs(request)
            return hx_request.get(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if is_htmx_request(request):
            # Call get to setup neccessary parts for the context
            super().get(request, *args, **kwargs)
            hx_request = self.get_hx_request(request)
            hx_request.view = self
            kwargs = self.get_extra_kwargs(request)
            return hx_request.post(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def get_hx_request(self, request):
        hx_request_name = request.GET.get("hx_request_name")
        self._get_hx_reqeust_classes()
        hx_request = next(
            hx_request
            for name, hx_request in self.hx_requests.items()
            if name == hx_request_name
        )
        return hx_request()

    @classmethod
    def _get_hx_reqeust_classes(cls):
        from .hx_requests import HXRequest

        # If the hx_requests are already set don't need to do the whole collection.
        if getattr(cls, "hx_requests", None):
            return
        modules = []
        hx_request_classes = {}
        for app in apps.get_app_configs():
            if app.label != __package__:
                try:
                    modules.append(importlib.import_module(f"{app.label}.hx_requests"))
                except ModuleNotFoundError:
                    pass
        for module in modules:
            clsmembers = inspect.getmembers(module, inspect.isclass)
            for _, obj in clsmembers:
                if issubclass(obj, HXRequest) and getattr(obj, "name", None):
                    hx_request_classes[obj.name] = obj
        cls.hx_requests = hx_request_classes

    def get_extra_kwargs(self, request):
        kwargs = {}
        for key in request.GET:
            kwargs[key] = request.GET.get(key)

        return deserialize_kwargs(**kwargs)


class MessagesMixin:
    show_messages: bool = getattr(settings, "HX_REQUESTS_SHOW_MESSAGES", False)
    success_message: str = ""
    error_message: str = ""

    def get_success_message(self, request, **kwargs) -> str:
        return self.success_message

    def get_error_message(self, request, **kwargs) -> str:
        return self.error_message

    def get_POST_headers(self, **kwargs) -> Dict:
        headers = {}
        message = kwargs.get("message")
        level = kwargs.get("level")

        if self.refresh_page == True:
            if level == "success":
                messages.success(self.request, message)
            elif level == "danger":
                messages.error(self.request, message)
            else:
                messages.info(self.request, message)
            return {}
        elif self.show_messages:
            headers["HX-Trigger"] = json.dumps(
                {"showMessages": {"message": message, "level": level}}
            )
        return headers
