"""Tests for hx_requests.checks (Django system checks)."""

# Importing the views registers them as HtmxViewMixin subclasses so the check
# (which walks __subclasses__) can see them.
from test_app.views import AuthAfterHxView, AuthBeforeHxView  # noqa: F401

from hx_requests.checks import W_AUTH_MIXIN_ORDER, check_auth_mixin_ordering


def _flagged_view_names():
    return {
        getattr(warning.obj, "__name__", None)
        for warning in check_auth_mixin_ordering(app_configs=None)
        if warning.id == W_AUTH_MIXIN_ORDER
    }


def test_warns_when_auth_mixin_is_after_htmxviewmixin():
    assert "AuthAfterHxView" in _flagged_view_names()


def test_does_not_warn_when_auth_mixin_is_before_htmxviewmixin():
    assert "AuthBeforeHxView" not in _flagged_view_names()
