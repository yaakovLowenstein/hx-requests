How To Secure HxRequests
------------------------

HxRequests allow modular, component-level interactions between the frontend and backend.
However, without proper access controls, any request can be triggered from any page
by including the :code:`hx_request_name` parameter in the URL.

This guide explains **how to secure HxRequests**, enforce app boundaries,
require authentication when appropriate, and explicitly allow cross-app usage where needed.

For an explanation of *why* these controls exist and the risks they prevent,
see :ref:`Why HxRequest Security Is Needed <why-hxrequest-security>`.


Global Settings
~~~~~~~~~~~~~~~

Global settings define the **default security policy** for all :code:`HxRequests` in your project.


Require Authentication
^^^^^^^^^^^^^^^^^^^^^^

Require users to be authenticated before running any :code:`HxRequest`. You can also
define exceptions that are allowed without authentication (see *Unauthenticated Allowlist*).

.. code-block:: python

    # settings.py
    HX_REQUESTS_REQUIRE_AUTH = True

With :code:`HX_REQUESTS_REQUIRE_AUTH = True`, unauthenticated users are blocked from
executing HxRequests **unless** the request is explicitly whitelisted in
:code:`HX_REQUESTS_UNAUTHENTICATED_ALLOW` (below).


Unauthenticated Allowlist
^^^^^^^^^^^^^^^^^^^^^^^^^

Define the subset of HxRequests that may be executed **without authentication**.
The structure mirrors the global allowlist shapes:

- List/tuple/set of app labels → allow **all** HxRequests in those apps.
- Dict of :code:`{app_label: "__all__"}` → same as above.
- Dict of :code:`{app_label: ["HxNameA", "HxNameB"]}` → allow **only** those Hx names.

.. code-block:: python

    # settings.py
    HX_REQUESTS_UNAUTHENTICATED_ALLOW = {
        "app1": "__all__",              # all HxRequests in app1
        "app2": ["hx_request_1", "hx_request_2"], # specific requests in app2
    }

.. note::

   The authentication check runs **first**. If authentication is required and the user
   is not authenticated, only HxRequests listed in :code:`HX_REQUESTS_UNAUTHENTICATED_ALLOW`
   are allowed to proceed to the other access controls.


Enforce Same-App Rule
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    HX_REQUESTS_ENFORCE_SAME_APP = True

By default, :code:`hx_requests` can only be triggered from **views in the same Django app**.

For example, a request defined in :code:`app1.hx_requests` can only be invoked by
views in the :code:`app1` app.

If you disable this rule:

.. code-block:: python

    HX_REQUESTS_ENFORCE_SAME_APP = False

HxRequests become callable from any app unless restricted by other rules.

.. warning::

    Disabling :code:`HX_REQUESTS_ENFORCE_SAME_APP` effectively removes app-level isolation.
    Any view can call any registered :code:`HxRequest`.
    Only disable this in controlled environments with strict allowlists in place.


Global Allowlist
^^^^^^^^^^^^^^^^

The global allowlist defines exceptions to the same-app rule. It lets you mark specific
apps or individual HxRequests as trusted and callable across apps.

Two forms are supported:

**List form:**

Allow all HxRequests from the given apps to run anywhere.

.. code-block:: python

    HX_REQUESTS_GLOBAL_ALLOW = ["app1", "app2"]

**Dict form:**

Map app names to specific HxRequest names (name attribute on HxRequests).
The value :code:`"__all__"` allows every request in that app.

.. code-block:: python

    HX_REQUESTS_GLOBAL_ALLOW = {
        "app1": ["safe_hx_request", "other_safe_hx_request"],
        "app2": "__all__"
    }

.. warning::

    Adding third-party or unreviewed apps here grants them global access.
    Only include internal apps or trusted apps.


Per-View Controls
~~~~~~~~~~~~~~~~~

Each :code:`View` class can define its own access rules via an **allowed list** and an
**additive** flag.


allowed_hx_requests
^^^^^^^^^^^^^^^^^^^

The :code:`allowed_hx_requests` attribute defines which :code:`HxRequests`
are permitted to be triggered from that view.

.. code-block:: python

    class TestView(View):
        allowed_hx_requests = ["hx_request_1", "hx_request_2"]

This allows only the specified :code:`HxRequests` to be called from this view,
regardless of the app they belong to.


use_global_hx_rules
^^^^^^^^^^^^^^^^^^^^^^^^^^

Determines whether the :code:`allowed_hx_requests` list **adds to** or **replaces**
the base same-app/global rules.

**Additive (default):**

.. code-block:: python

    class TestView(View):
        allowed_hx_requests = ["hx_request_1", "hx_request_2"]
        use_global_hx_rules = True

Allowed if **either**:
- The HxRequest is in :code:`allowed_hx_requests`, **or**
- The request passes the base rules (same-app if enforced, or globally allowed).

**Restrictive:**

.. code-block:: python

    class TestView(View):
        allowed_hx_requests = ["hx_request_3", "hx_request_4"]
        use_global_hx_rules = False

Only HxRequests in :code:`allowed_hx_requests` can be called from this view
(regardless of same-app/global rules).




Evaluation Order
~~~~~~~~~~~~~~~~

1. **Authentication gate**
   - If :code:`HX_REQUESTS_REQUIRE_AUTH` is True and the user is not authenticated:
     - Allow only if the HxRequest matches :code:`HX_REQUESTS_UNAUTHENTICATED_ALLOW`.
     - Otherwise, deny.

2. **Per-view allowlist**
   - If the HxRequest is listed in :code:`allowed_hx_requests`, allow.
   - If :code:`use_global_hx_rules` is False and it’s **not** listed, deny.
   - If :code:`use_global_hx_rules` is True and it’s not listed, proceed to step 3

3. **Base rules**
   - Allow if **globally allowed** (per :code:`HX_REQUESTS_GLOBAL_ALLOW`), or
   - Allow if **same-app** and :code:`HX_REQUESTS_ENFORCE_SAME_APP` is True.
   - Allow if :code:`HX_REQUESTS_ENFORCE_SAME_APP` is False.


Summary
~~~~~~~

=======================================  ===========================================
**Control**                              **Purpose**
=======================================  ===========================================
:code:`HX_REQUESTS_REQUIRE_AUTH`         Require authentication for HxRequests
:code:`HX_REQUESTS_UNAUTHENTICATED_ALLOW` Allow specific HxRequests/apps without auth
:code:`HX_REQUESTS_ENFORCE_SAME_APP`     Default: restrict to same-app requests
:code:`HX_REQUESTS_GLOBAL_ALLOW`         Define trusted apps or HxRequests globally
:code:`allowed_hx_requests`              Per-view allowed HxRequests
:code:`use_global_hx_rules`              Whether per-view list builds upon the global list or restricts it further
=======================================  ===========================================

.. warning::

    Always follow the **principle of least privilege**.
    Require authentication for HxRequests by default, only whitelist
    unauthenticated requests when they are demonstrably safe, and grant
    cross-app access only to trusted, internal apps.

.. info::

   When :code:`HX_REQUESTS_REQUIRE_AUTH = True`, unauthenticated users may only
   invoke HxRequests listed in :code:`HX_REQUESTS_UNAUTHENTICATED_ALLOW`. After that gate,
   the per-view rules above still apply.
