"""Test helpers for driving ``hx_requests`` through a real view.

Instead of hand-instantiating an ``HxRequest`` and setting its internal
state, these build a request and dispatch it through the view's
``HtmxViewMixin`` so the full chain runs (object deserialization, security
checks, form handling, trigger/header assembly, messages).
"""

from __future__ import annotations

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import RequestFactory
from django.views import View

from hx_requests.utils import serialize, serialize_kwargs


def add_middleware_to_request(request):
    SessionMiddleware(lambda r: HttpResponse()).process_request(request)
    request._messages = FallbackStorage(request)
    return request


def _create_test_request(
    hx_request,
    request_attrs=None,
    hx_kwargs=None,
    get_params=None,
    method="GET",
    post_data=None,
):
    hx_kwargs = hx_kwargs or {}
    request_attrs = dict(request_attrs or {})
    get_params = get_params or {}

    def set_request_attrs(request):
        META = request_attrs.pop("META", {})
        for attr, value in request_attrs.items():
            setattr(request, attr, value)
        request.META["HTTP_HX_REQUEST"] = True
        request.META.update(META)
        if not hasattr(request, "user"):
            request.user = AnonymousUser()
        return request

    # Used even on POST to set kwargs to GET params
    hx_object = hx_kwargs.pop("object", None)
    hx_kwargs = serialize_kwargs(**hx_kwargs)
    if hx_object is not None:
        hx_kwargs["object"] = serialize(hx_object)
    hx_kwargs["hx_request_name"] = hx_request.name
    hx_kwargs.update(get_params)
    request = RequestFactory().get("/", data=hx_kwargs)

    if method == "POST":
        request = RequestFactory().post(f"/?{request.META['QUERY_STRING']}", data=post_data or {})

    request = set_request_attrs(request)
    add_middleware_to_request(request)
    return request


def hx_get(
    hx_request: type,
    view: type[View],
    request_attrs: dict | None = None,
    view_kwargs: dict | None = None,
    hx_kwargs: dict | None = None,
    get_params: dict | None = None,
) -> HttpResponse:
    """Test an HxRequest with a GET request through a view."""
    request = _create_test_request(hx_request, request_attrs, hx_kwargs, get_params=get_params)
    view_kwargs = view_kwargs or {}
    return view.as_view()(request, **view_kwargs)


def hx_post(
    hx_request: type,
    view: type[View],
    request_attrs: dict | None = None,
    view_kwargs: dict | None = None,
    hx_kwargs: dict | None = None,
    get_params: dict | None = None,
    post_data: dict | None = None,
) -> HttpResponse:
    """Test an HxRequest with a POST request through a view."""
    request = _create_test_request(
        hx_request,
        request_attrs=request_attrs,
        hx_kwargs=hx_kwargs,
        method="POST",
        get_params=get_params,
        post_data=post_data,
    )
    view_kwargs = view_kwargs or {}
    return view.as_view()(request, **view_kwargs)
