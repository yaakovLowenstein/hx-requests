"""
Django system checks for hx-requests.

These surface configuration mistakes at startup / ``manage.py check`` rather
than as silent runtime surprises.
"""

from __future__ import annotations

from django.core.checks import Warning, register

W_AUTH_MIXIN_ORDER = "hx_requests.W001"


def _all_subclasses(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from _all_subclasses(sub)


@register()
def check_auth_mixin_ordering(app_configs, **kwargs):
    """
    Warn when a Django auth mixin (any ``AccessMixin`` subclass --
    ``LoginRequiredMixin``, ``PermissionRequiredMixin``,
    ``UserPassesTestMixin``) is listed *after* ``HtmxViewMixin`` in a view's
    base classes.

    ``HtmxViewMixin.dispatch`` hands HTMX requests off to the resolved
    ``HxRequest`` without calling ``super().dispatch()``, so any auth mixin
    ordered after it never runs on the HTMX path -- authentication is silently
    skipped for HTMX requests with no error. Auth mixins must come *before*
    ``HtmxViewMixin`` so their ``dispatch`` runs first (or authorization must be
    enforced per-handler on the ``HxRequest``).

    Best effort: only view classes that have been imported are visible via
    ``__subclasses__``; this catches the common case at startup.
    """
    from django.contrib.auth.mixins import AccessMixin

    from hx_requests.views import HtmxViewMixin

    errors = []
    for view_cls in _all_subclasses(HtmxViewMixin):
        mro = view_cls.__mro__
        try:
            hx_index = mro.index(HtmxViewMixin)
        except ValueError:  # pragma: no cover - defensive
            continue

        for later in mro[hx_index + 1 :]:
            if later is not AccessMixin and issubclass(later, AccessMixin):
                errors.append(
                    Warning(
                        f"{view_cls.__module__}.{view_cls.__qualname__} lists the auth "
                        f"mixin {later.__name__} after HtmxViewMixin.",
                        hint=(
                            "HtmxViewMixin.dispatch routes HTMX requests to the HxRequest "
                            "handler without calling super().dispatch(), so an auth mixin "
                            "placed after it is skipped on the HTMX path and authentication "
                            "is silently bypassed. Put auth mixins BEFORE HtmxViewMixin in "
                            "the base-class list, and/or enforce authorization per-handler "
                            "on the HxRequest."
                        ),
                        obj=view_cls,
                        id=W_AUTH_MIXIN_ORDER,
                    )
                )
                break

    return errors
