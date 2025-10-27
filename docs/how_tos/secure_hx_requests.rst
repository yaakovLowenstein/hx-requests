How To Secure HxRequests
------------------------

HxRequests allow modular, component-level interactions between the frontend and backend.
However, without proper access controls, any request can be triggered from any page
by including the :code:`hx_request_name` parameter in the URL.

This guide explains **how to secure HxRequests**, enforce app boundaries,
and explicitly allow cross-app usage where appropriate.

For an explanation of *why* these controls exist and the risks they prevent,
see :ref:`Why HxRequest Security Is Needed <why-hxrequest-security>`.


Global Settings
~~~~~~~~~~~~~~~

Global settings define the **default security policy** for all :code:`HxRequests` in your project.


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
~~~~~~~~~~~~~~~~~~~~~~

Each :code:`View` class can define its own access rules.


allowed_hx_requests
^^^^^^^^^^^^^^^^^^^

The :code:`allowed_hx_requests` attribute defines which :code:`HxRequests`
are permitted to be triggered from that view.

.. code-block:: python

    class TestView(View):
        allowed_hx_requests = ["hx_request_1", "hx_request_2"]

This allows only the specified :code:`HxRequests` to be called from this view,
regardless of the app they belong to.


hx_requests_allow_additive
^^^^^^^^^^^^^^^^^^^^^^^^^^

Determines whether the :code:`allowed_hx_requests` list **adds to** or **replaces**
the base same-app rule.

**Additive (default):**

.. code-block:: python

    class TestView(View):
        allowed_hx_requests = ["hx_request_1", "hx_request_2"]
        hx_requests_allow_additive = True

Allowed if **either**:
- The HxRequest and url are in the same app, **or**
- The HxRequest is in the allowed list.

**Restrictive:**

.. code-block:: python

    class TestView(View):
        allowed_hx_requests = ["hx_request_3", "hx_request_4"]
        hx_requests_allow_additive = False

Only HxRequests in the allowed list can be called, regardless of app.



Summary
~~~~~~~

==============================  ===========================================
**Control**                     **Purpose**
==============================  ===========================================
:code:`HX_REQUESTS_ENFORCE_SAME_APP`   Default: restrict to same-app requests
:code:`HX_REQUESTS_GLOBAL_ALLOW`       Define trusted apps or HxRequests globally
:code:`allowed_hx_requests`            Per-View allowed HxRequests
:code:`hx_requests_allow_additive`     Whether per-View list adds to or replaces base rule
==============================  ===========================================

.. warning::

    Always follow the **principle of least privilege**.
    Only grant cross-app access when absolutely necessary
    and only to trusted, internal apps.
