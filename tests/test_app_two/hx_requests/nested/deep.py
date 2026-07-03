"""Nested module inside hx_requests/, discovered via the recursive dir walk."""

from hx_requests.hx_requests import BaseHxRequest


class DeepHx(BaseHxRequest):
    # Annotated form, exercising the ast.AnnAssign branch of the registry.
    name: str = "deep_hx"
    GET_template = "simple.html"
