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

from hx_requests.utils import HX_TOKEN_PARAM, sign_hx_payload


def add_middleware_to_request(request):
    SessionMiddleware(lambda r: HttpResponse()).process_request(request)
    request._messages = FallbackStorage(request)
    return request


def content_of(response):
    """Decode a response body to text."""
    return response.content.decode()


def make_context(path="/page/", **extra):
    """A minimal template-tag context wrapping a GET request."""
    return {"request": RequestFactory().get(path, **extra)}


def make_hx(method="get", **attrs):
    """
    Instantiate a bare BaseHxRequest with a request and the given attributes,
    for unit tests that exercise a single method in isolation. (Handlers that
    need a wired get_triggers or a concrete form subclass build their own.)
    """
    from hx_requests.hx_requests import BaseHxRequest

    hx = BaseHxRequest()
    hx.request = getattr(RequestFactory(), method)("/")
    for key, value in attrs.items():
        setattr(hx, key, value)
    return hx


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

    # The framework's routing data (name, object, kwargs) rides in one signed
    # token, exactly as the template tags emit it; get_params stay loose.
    hx_object = hx_kwargs.pop("object", None)
    query = {HX_TOKEN_PARAM: sign_hx_payload(hx_request.name, hx_object, **hx_kwargs)}
    query.update(get_params)
    request = RequestFactory().get("/", data=query)

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
