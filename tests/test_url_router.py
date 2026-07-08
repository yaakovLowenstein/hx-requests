"""Tests for the additive /hx/<name>/ URL router (#10)."""

from __future__ import annotations

import pytest
from django.http import Http404
from django.test import RequestFactory

from hx_requests.hx_registry import HxRequestRegistry
from hx_requests.utils import HX_TOKEN_PARAM, sign_hx_payload
from hx_requests.views import bind_hx_token

# --------------------------------------------------------------------------
# Shared token trust boundary (bind_hx_token)
# --------------------------------------------------------------------------


def test_bind_hx_token_rejects_name_mismatch():
    token = sign_hx_payload("simple_get")
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: token})
    # A token minted for simple_get replayed against another endpoint 404s.
    with pytest.raises(Http404):
        bind_hx_token(request, expected_name="post_template")


def test_bind_hx_token_accepts_matching_name():
    token = sign_hx_payload("simple_get")
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: token})
    bound = bind_hx_token(request, expected_name="simple_get")
    assert bound.GET["hx_request_name"] == "simple_get"
