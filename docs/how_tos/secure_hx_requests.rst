.. _how-to-secure-hxrequests:

How To Secure HxRequests
------------------------

Request signing stops a client from forging a request for an arbitrary handler
or tampering with its object/kwargs. What signing does **not** decide is whether
the current user is *allowed* to run a given handler. That is per-handler
authorization, and it lives on the :code:`HxRequest` itself.

Every :code:`HxRequest` gates itself in :code:`dispatch`, before :code:`get` /
:code:`post` run, regardless of which view or template triggered it.

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


Relaxing Path-Binding
~~~~~~~~~~~~~~~~~~~~~~~

By default, every signed token is bound to the URL path it was rendered on, so it
only verifies when replayed back to that same path (see
:ref:`Why HxRequest Security Is Needed <why-hxrequest-security>`). This is
automatic — there is nothing to enable.

You only need to relax it when the path Django sees at dispatch can legitimately
differ from the path a token was rendered on. That comes up in two shapes.


Disabling Globally
^^^^^^^^^^^^^^^^^^

If your whole project sits behind a proxy or middleware that rewrites or strips
part of the path (a locale prefix, a mount sub-path / :code:`SCRIPT_NAME`)
between the browser and Django, the rendered path and the dispatched path won't
match. Turn path-binding off project-wide:

.. code-block:: python

    # settings.py
    HX_REQUESTS_BIND_TOKEN_TO_PATH = False

This disables both minting new bound tokens **and** enforcing existing ones, so
it takes effect immediately — already-rendered pages stop failing without a
reload.


Opting Out Per Handler
^^^^^^^^^^^^^^^^^^^^^^^^

For a single handler whose token must work from a path other than where it was
rendered — e.g. you build the request URL yourself, or reuse one token across
several URLs instead of letting the tags emit it — opt that handler out:

.. code-block:: python

    class CrossPageHx(BaseHxRequest):
        name = "cross_page"
        bind_to_path = False

In ordinary usage you never hit either case: the template tags bake the render
path into the request URL, so the token is always posted back to the path it was
bound to.


Summary
~~~~~~~

==========================================  ================================================================================
**Control**                                 **Purpose**
==========================================  ================================================================================
:code:`login_required`                      Require an authenticated user (default ``True``); anon → 404
:code:`permission_required`                 Require a permission (str or list); authed-but-missing → 403
:code:`has_permission`                      Override for custom / row-level authorization
:code:`HX_REQUESTS_BIND_TOKEN_TO_PATH`      Default: bind each token to its render path (set False to disable project-wide)
:code:`bind_to_path`                        Per-handler opt-out of path-binding
==========================================  ================================================================================

.. warning::

    Follow the **principle of least privilege**. Handlers require authentication
    by default; only set :code:`login_required = False` when the interaction is
    demonstrably safe for anonymous users, and reach for
    :code:`permission_required` / :code:`has_permission` for anything that acts
    on per-user or per-object data.
