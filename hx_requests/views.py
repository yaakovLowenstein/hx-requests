from typing import Dict
from urllib.parse import parse_qs, urlparse

from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from hx_requests.hx_registry import HxRequestRegistry
from hx_requests.utils import deserialize_kwargs, is_htmx_request


@method_decorator(ensure_csrf_cookie, name="dispatch")
class HtmxViewMixin:
    """
    Mixin to be added to views that are using HxRequests.
    Hijacks the get and post to route them to the proper
    HxRequest.
    """

    hx_requests: Dict = []

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler_class = self
            # If it's an HTMX request, use the HxRequest class to handle the request
            # otherwise, use the view class to handle the request.
            if is_htmx_request(request):
                kwargs.update(self.get_hx_extra_kwargs(request))
                handler_class = self._setup_hx_request(request, *args, **kwargs)

                # Use request from hx_request, in case use_current_url is set to True
                request = handler_class.request
            handler = getattr(handler_class, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_hx_request(self, request):
        hx_request_name = request.GET.get("hx_request_name")
        hx_request_class = HxRequestRegistry.get_hx_request(hx_request_name)
        if not hx_request_class:
            raise Http404(
                f"No HxRequest found with the name {hx_request_name}. Are you sure it's spelled correctly?"
            )
        return hx_request_class()

    def get_hx_extra_kwargs(self, request):
        kwargs = {}
        for key in request.GET:
            kwargs[key] = request.GET.get(key)

        return deserialize_kwargs(**kwargs)

    def _setup_hx_request(self, request, *args, **kwargs):
        hx_request = self.get_hx_request(request)
        hx_request.view = self

        if hx_request.use_current_url:
            request = self._use_current_url(request)
        hx_request._setup_hx_request(request, *args, **kwargs)
        return hx_request

    def _use_current_url(self, request):
        # Start with the current GET params
        merged_get = request.GET.copy()

        # Check if HX-Current-URL is in the headers
        hx_current_url = request.headers.get("HX-Current-URL")
        if hx_current_url:
            # Parse the URL and extract its query parameters
            parsed_url = urlparse(hx_current_url)
            additional_params = parse_qs(parsed_url.query)

            # Add each HX param only if not already present
            for key, values in additional_params.items():
                if key not in merged_get:
                    merged_get.setlist(key, values)

        # Now override request.GET
        request.GET = merged_get
        return request
