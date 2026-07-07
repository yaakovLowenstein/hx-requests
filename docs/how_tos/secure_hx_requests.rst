.. _how-to-secure-hxrequests:

How To Secure HxRequests
------------------------

Request signing stops a client from forging a request for an arbitrary handler
or tampering with its object/kwargs. What signing does **not** decide is whether
the current user is *allowed* to run a given handler. That is per-handler
authorization, and it lives on the :code:`HxRequest` itself.

Every :code:`HxRequest` gates itself in :code:`dispatch`, before :code:`get` /
:code:`post` run, regardless of which view or template triggered it. This is the
one authorization seam — there is no project-wide settings matrix to reason
about.

For an explanation of *why* these controls exist and the risks they prevent,
see :ref:`Why HxRequest Security Is Needed <why-hxrequest-security>`.


Require authentication (the default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every :code:`HxRequest` requires an authenticated user by default
(:code:`login_required = True`). An anonymous request raises :code:`Http404`
(bodiless, so nothing about the handler leaks).

Opt a handler out to make it public:

.. code-block:: python

    class PublicSearchHx(BaseHxRequest):
        name = "public_search"
        login_required = False


Require a permission
~~~~~~~~~~~~~~~~~~~~~

Set :code:`permission_required` to a permission string or a list of them. An
authenticated user missing **any** of them gets a :code:`403` (an anonymous user
still gets a :code:`404`).

.. code-block:: python

    class EditWidgetHx(FormHxRequest):
        name = "edit_widget"
        permission_required = "widgets.change_widget"

    class PublishHx(BaseHxRequest):
        name = "publish"
        permission_required = ["widgets.change_widget", "widgets.publish_widget"]


Custom / row-level authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Override :code:`has_permission` for anything the declarative attributes can't
express — object ownership, role checks, tenancy. It is called only for
authenticated users (the :code:`login_required` gate runs first), and returning
:code:`False` yields a :code:`403`.

.. code-block:: python

    class EditInvoiceHx(FormHxRequest):
        name = "edit_invoice"

        def has_permission(self, request):
            # self.hx_object is the (scoped) round-trip object; see get_queryset.
            return self.hx_object.owner_id == request.user.pk

For row-level *resolution* (so an out-of-scope object 404s before it is ever
loaded), pair this with :code:`get_queryset` — see :ref:`Object Serialization`.


Ordering Django auth mixins on the view
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Per-handler authorization gates the **HTMX** path. The page view's own
:code:`get` (a full page load) is still gated by ordinary Django auth mixins —
but only when they are ordered correctly. If you combine :code:`HtmxViewMixin`
with a Django auth mixin (:code:`LoginRequiredMixin`,
:code:`PermissionRequiredMixin`, :code:`UserPassesTestMixin`), **put the auth
mixin first**:

.. code-block:: python

    # Correct: LoginRequiredMixin.dispatch runs before the HTMX handoff, so it
    # gates full page loads (the HTMX path is gated per-handler regardless).
    class MyView(LoginRequiredMixin, HtmxViewMixin, ListView):
        ...

    # Trap: the auth mixin is skipped on the HTMX path.
    class MyView(HtmxViewMixin, LoginRequiredMixin, ListView):
        ...

:code:`HtmxViewMixin.dispatch` hands HTMX requests to the resolved
:code:`HxRequest` without calling :code:`super().dispatch()`, so an auth mixin
listed *after* it never runs for HTMX requests — which is exactly why the HTMX
path must rely on per-handler authorization. A Django system check
(:code:`hx_requests.W001`) warns at startup / :code:`manage.py check` when the
ordering is wrong.


Keep mutations on POST
~~~~~~~~~~~~~~~~~~~~~~~

A :code:`get()` handler must not write to the database. A GET request is not
CSRF-protected, so a valid GET URL is replayable cross-site (an attacker can
embed it in an :code:`<img src>`, a prefetch, or a :code:`<link>` and fire it
from any page the victim visits). Put every mutation in :code:`post()` /
:code:`form_valid` / :code:`delete`, which carry CSRF protection.

The framework helps enforce this: if a handler's :code:`get()` runs a database
write, it logs a :code:`WARNING` naming the handler (it never blocks the
request). For the rare GET write that is genuinely safe — idempotent
bookkeeping like a "last seen" touch — opt out per-handler:

.. code-block:: python

    class TrackViewHx(BaseHxRequest):
        name = "track_view"
        allow_writes_on_get = True  # silence the guard for a known-safe GET write

        def get(self, request, *args, **kwargs):
            request.user.profile.touch_last_seen()  # idempotent, safe to replay
            return super().get(request, *args, **kwargs)


Summary
~~~~~~~

============================  ===========================================
**Control**                   **Purpose**
============================  ===========================================
:code:`login_required`        Require an authenticated user (default ``True``); anon → 404
:code:`permission_required`   Require a permission (str or list); authed-but-missing → 403
:code:`has_permission`        Override for custom / row-level authorization
:code:`allow_writes_on_get`   Silence the "GET must not mutate" warning for a known-safe GET write
============================  ===========================================

.. warning::

    Follow the **principle of least privilege**. Handlers require authentication
    by default; only set :code:`login_required = False` when the interaction is
    demonstrably safe for anonymous users, and reach for
    :code:`permission_required` / :code:`has_permission` for anything that acts
    on per-user or per-object data.
