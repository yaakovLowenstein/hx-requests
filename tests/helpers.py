"""Test helpers for driving ``hx_requests`` through a real view.

Instead of hand-instantiating an ``HxRequest`` and setting its internal
state, these build a request and dispatch it through the view's
``HtmxViewMixin`` so the full chain runs (object deserialization, security
checks, form handling, trigger/header assembly, messages).
"""

from __future__ import annotations

from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse
from django.views import View

from hx_requests.utils import HX_TOKEN_PARAM, sign_hx_payload


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
            # Handlers require an authenticated user by default (login_required),
            # so default to one. An unsaved User() is authenticated and holds no
            # permissions. Auth tests pass an anonymous / unprivileged user via
            # request_attrs.
            request.user = User()
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


def _router_query(hx_request, hx_kwargs=None, get_params=None):
    hx_kwargs = dict(hx_kwargs or {})
    get_params = dict(get_params or {})
    hx_object = hx_kwargs.pop("object", None)
    query = {HX_TOKEN_PARAM: sign_hx_payload(hx_request.name, hx_object, **hx_kwargs)}
    query.update(get_params)
    return query


def hx_get_url(client, hx_request, hx_kwargs=None, get_params=None):
    """Drive a GET through the router URL (reverse('hx:<name>'))."""
    url = reverse(f"hx:{hx_request.name}")
    return client.get(
        url, data=_router_query(hx_request, hx_kwargs, get_params), HTTP_HX_REQUEST="true"
    )


def hx_post_url(client, hx_request, hx_kwargs=None, get_params=None, post_data=None):
    """Drive a POST through the router URL (reverse('hx:<name>'))."""
    url = reverse(f"hx:{hx_request.name}")
    query = _router_query(hx_request, hx_kwargs, get_params)
    return client.post(f"{url}?{urlencode(query)}", data=post_data or {}, HTTP_HX_REQUEST="true")


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
