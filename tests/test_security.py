"""Tests for per-handler authorization on HxRequests.

Authorization lives on the HxRequest itself (login_required /
permission_required / has_permission), enforced in dispatch before get/post --
not in a view-boundary policy matrix. A request the handler rejects raises
Http404 for anonymous users (leaks nothing) and PermissionDenied (403) for an
authenticated user who lacks permission.
"""

import logging

import pytest
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.core.exceptions import PermissionDenied
from django.http import Http404
from test_app.hx_requests import (
    MultiPermRequiredHx,
    OwnerOnlyHx,
    PermRequiredHx,
    PublicGetHx,
    SimpleGetHx,
)
from test_app.views import BaseView

from hx_requests.hx_requests import BaseHxRequest
from tests.helpers import hx_get

pytestmark = pytest.mark.django_db


def perm(codename):
    return Permission.objects.get(content_type__app_label="test_app", codename=codename)


# --------------------------------------------------------------------------
# login_required (the default)
# --------------------------------------------------------------------------


def test_login_required_is_the_default():
    assert BaseHxRequest.login_required is True


def test_anonymous_user_gets_404_by_default():
    with pytest.raises(Http404):
        hx_get(SimpleGetHx, BaseView, request_attrs={"user": AnonymousUser()})


def test_authenticated_user_passes_the_login_gate():
    response = hx_get(SimpleGetHx, BaseView, request_attrs={"user": User()})
    assert response.status_code == 200


def test_public_handler_allows_anonymous():
    response = hx_get(PublicGetHx, BaseView, request_attrs={"user": AnonymousUser()})
    assert response.status_code == 200


# --------------------------------------------------------------------------
# permission_required
# --------------------------------------------------------------------------


def test_permission_required_blocks_user_without_permission(user):
    with pytest.raises(PermissionDenied):
        hx_get(PermRequiredHx, BaseView, request_attrs={"user": user})


def test_permission_required_allows_user_with_permission(user):
    user.user_permissions.add(perm("change_widget"))
    user = User.objects.get(pk=user.pk)  # reload so the perm cache is fresh
    response = hx_get(PermRequiredHx, BaseView, request_attrs={"user": user})
    assert response.status_code == 200


def test_permission_required_anonymous_gets_404_not_403():
    # Anonymous users leak nothing: a missing permission on an anonymous request
    # is a 404, not a 403.
    with pytest.raises(Http404):
        hx_get(PermRequiredHx, BaseView, request_attrs={"user": AnonymousUser()})


def test_multiple_permissions_requires_all(user):
    user.user_permissions.add(perm("change_widget"))  # only one of two
    user = User.objects.get(pk=user.pk)
    with pytest.raises(PermissionDenied):
        hx_get(MultiPermRequiredHx, BaseView, request_attrs={"user": user})

    user.user_permissions.add(perm("add_widget"))
    user = User.objects.get(pk=user.pk)
    response = hx_get(MultiPermRequiredHx, BaseView, request_attrs={"user": user})
    assert response.status_code == 200


# --------------------------------------------------------------------------
# has_permission override
# --------------------------------------------------------------------------


def test_has_permission_override_allows_matching_user():
    response = hx_get(OwnerOnlyHx, BaseView, request_attrs={"user": User(username="owner")})
    assert response.status_code == 200


def test_has_permission_override_denies_other_users():
    with pytest.raises(PermissionDenied):
        hx_get(OwnerOnlyHx, BaseView, request_attrs={"user": User(username="someone_else")})


# --------------------------------------------------------------------------
# Cross-app is no longer gated by the framework (the matrix is gone)
# --------------------------------------------------------------------------


def test_cross_app_handler_runs_when_the_handler_authorizes_it():
    # With the six-knob matrix removed, a handler from another app is reachable;
    # its own authorization (here PublicGetHx opts out of login) is the boundary.
    from test_app_two.hx_requests.widgets import OtherAppHx

    OtherAppHx.login_required = False
    try:
        response = hx_get(OtherAppHx, BaseView, request_attrs={"user": AnonymousUser()})
        assert response.status_code == 200
    finally:
        OtherAppHx.login_required = True


# --------------------------------------------------------------------------
# Denial logging (debug line explaining a 404)
# --------------------------------------------------------------------------


def test_unknown_name_logs_a_debug_explanation(caplog):
    from hx_requests.utils import HX_TOKEN_PARAM, sign_hx_payload

    request_query = {HX_TOKEN_PARAM: sign_hx_payload("does_not_exist", None)}
    from django.test import RequestFactory

    request = RequestFactory().get("/", data=request_query)
    request.META["HTTP_HX_REQUEST"] = True
    request.user = User()
    with caplog.at_level(logging.DEBUG, logger="hx_requests.views"), pytest.raises(Http404):
        BaseView.as_view()(request)
    assert "no HxRequest registered" in caplog.text
