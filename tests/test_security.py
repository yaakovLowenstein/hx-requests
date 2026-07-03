"""Tests for the HtmxViewMixin security policy (is_hx_allowed and friends)."""

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.http import Http404
from django.test import RequestFactory, override_settings
from test_app.hx_requests import SimpleGetHx, TriggerListHx
from test_app.views import AllowListView, BaseView, StrictAllowListView
from test_app_two.hx_requests.widgets import OtherAppHx

from hx_requests.hx_requests import BaseHxRequest
from tests.helpers import hx_get


def is_allowed(view_cls, hx_cls, user=None, **overrides):
    request = RequestFactory().get("/")
    request.user = user or AnonymousUser()
    with override_settings(**overrides):
        return view_cls().is_hx_allowed(hx_cls, request)


def authed_user():
    # An unsaved User instance is enough: is_authenticated is always True.
    return User()


# --------------------------------------------------------------------------
# Auth gate
# --------------------------------------------------------------------------


def test_require_auth_blocks_anonymous():
    assert is_allowed(BaseView, SimpleGetHx, HX_REQUESTS_REQUIRE_AUTH=True) is False


def test_require_auth_allows_authenticated():
    assert is_allowed(BaseView, SimpleGetHx, user=authed_user(), HX_REQUESTS_REQUIRE_AUTH=True)


def test_require_auth_off_allows_anonymous():
    assert is_allowed(BaseView, SimpleGetHx, HX_REQUESTS_REQUIRE_AUTH=False)


@pytest.mark.parametrize(
    "spec",
    [
        ["test_app"],
        {"test_app": "__all__"},
        {"test_app": ["simple_get"]},
    ],
)
def test_unauthenticated_allow_specs_open_the_auth_gate(spec):
    assert is_allowed(
        BaseView,
        SimpleGetHx,
        HX_REQUESTS_REQUIRE_AUTH=True,
        HX_REQUESTS_UNAUTHENTICATED_ALLOW=spec,
    )


def test_unauthenticated_allow_does_not_match_other_names():
    assert (
        is_allowed(
            BaseView,
            SimpleGetHx,
            HX_REQUESTS_REQUIRE_AUTH=True,
            HX_REQUESTS_UNAUTHENTICATED_ALLOW={"test_app": ["some_other_name"]},
        )
        is False
    )


# --------------------------------------------------------------------------
# Same-app enforcement and global allow
# --------------------------------------------------------------------------


def test_same_app_is_allowed_by_default():
    assert is_allowed(BaseView, SimpleGetHx)


def test_cross_app_is_blocked_by_default():
    assert is_allowed(BaseView, OtherAppHx) is False


def test_enforce_same_app_off_with_no_allow_list_allows_everything():
    assert is_allowed(BaseView, OtherAppHx, HX_REQUESTS_ENFORCE_SAME_APP=False)


@pytest.mark.parametrize(
    "spec",
    [
        ["test_app_two"],
        {"test_app_two": "__all__"},
        {"test_app_two": ["other_app_hx"]},
    ],
)
def test_global_allow_specs_permit_cross_app(spec):
    assert is_allowed(BaseView, OtherAppHx, HX_REQUESTS_GLOBAL_ALLOW=spec)


def test_global_allow_does_not_match_other_names():
    assert is_allowed(BaseView, OtherAppHx, HX_REQUESTS_GLOBAL_ALLOW={"test_app_two": ["nope"]}) is False


def test_hx_request_without_a_name_is_never_allowed():
    assert is_allowed(BaseView, BaseHxRequest) is False


# --------------------------------------------------------------------------
# View allow lists
# --------------------------------------------------------------------------


def test_view_allow_list_permits_cross_app():
    assert is_allowed(AllowListView, OtherAppHx)


def test_view_allow_list_is_additive_by_default():
    # simple_get is not on AllowListView's list, but same-app still allows it.
    assert is_allowed(AllowListView, SimpleGetHx)


def test_strict_allow_list_permits_listed():
    assert is_allowed(StrictAllowListView, SimpleGetHx)


def test_strict_allow_list_blocks_unlisted_even_same_app():
    assert is_allowed(StrictAllowListView, TriggerListHx) is False


# --------------------------------------------------------------------------
# Integration: disallowed requests raise 404 through the view
# --------------------------------------------------------------------------


@pytest.mark.django_db()
class TestSecurityIntegration:
    def test_allowed_request_succeeds(self):
        response = hx_get(SimpleGetHx, BaseView)
        assert response.status_code == 200

    def test_cross_app_request_raises_404(self):
        with pytest.raises(Http404, match="not allowed here"):
            hx_get(OtherAppHx, BaseView)

    @override_settings(HX_REQUESTS_REQUIRE_AUTH=True)
    def test_anonymous_request_raises_404_when_auth_required(self):
        with pytest.raises(Http404, match="not allowed here"):
            hx_get(SimpleGetHx, BaseView)

    @override_settings(HX_REQUESTS_REQUIRE_AUTH=True)
    def test_authenticated_request_succeeds_when_auth_required(self, user):
        response = hx_get(SimpleGetHx, BaseView, request_attrs={"user": user})
        assert response.status_code == 200

    @override_settings(HX_REQUESTS_GLOBAL_ALLOW=["test_app_two"])
    def test_globally_allowed_cross_app_request_succeeds(self):
        response = hx_get(OtherAppHx, BaseView)
        assert response.status_code == 200

    def test_view_allow_list_permits_cross_app_request(self):
        response = hx_get(OtherAppHx, AllowListView)
        assert response.status_code == 200

    def test_strict_view_blocks_unlisted_same_app_request(self):
        with pytest.raises(Http404, match="not allowed here"):
            hx_get(TriggerListHx, StrictAllowListView)
