"""Directory-style HxRequest module, discovered by the registry's dir scan."""

from hx_requests.hx_requests import BaseHxRequest


class OtherAppHx(BaseHxRequest):
    name = "other_app_hx"
    GET_template = "simple.html"
