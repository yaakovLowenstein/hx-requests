"""Root URLconf for the test suite: mounts the additive HxRequest router."""

from django.urls import include, path

from hx_requests.hx_registry import HxRequestRegistry

urlpatterns = [
    path("hx/", include((HxRequestRegistry.get_urls(), "hx_requests"), namespace="hx")),
]
