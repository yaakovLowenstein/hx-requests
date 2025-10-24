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
---------------

Global settings define the **default security policy** for all :code:`HxRequests` in your project.


Enforce Same-App Rule
~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~

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


Per-HxRequest Controls
----------------------

Each :code:`HxRequest` class can define its own access rules.


allowed
~~~~~~~

The :code:`allowed` attribute defines which apps (or specific views)
are permitted to call the request.

.. code-block:: python

    class SampleHx(BaseHxRequest):
        allowed = ["app1", "app2"]

This allows the request to be triggered from any url in the
:code:`app1` or :code:`app2` apps.

You can also specify URL-level granularity:

.. code-block:: python

    class SampleHx(BaseHxRequest):
        allowed = {
            "app1": ["url_name_1"],
            "app2": "__all__"
        }

This allows all :code:`app2` urls and only the :code:`url_name_1`
url within :code:`app1`.


allow_additive
~~~~~~~~~~~~~~

Determines whether the :code:`allowed` list **adds to** or **replaces**
the base same-app rule.

**Additive (default):**

.. code-block:: python

    class SampleHx(BaseHxRequest):
        allowed = ["app1"]
        allow_additive = True

Allowed if **either**:
- The HxRequest and url are in the same app, **or**
- The url's app is in the :code:`allowed` list.

**Restrictive:**

.. code-block:: python

    class SampleHx(BaseHxRequest):
        allowed = ["app1"]
        allow_additive = False

Allowed **only** from the listed apps — not from the same app.


Example 4 – Combining Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you define both global and per-class allowlists, the system follows this precedence:

1. Global allowlist (always grants access)
2. Per-class :code:`allowed`
3. Base same-app rule (if enforced)

Additive mode merges (2) and (3).
Restrictive mode uses only (2).


Summary
-------

==============================  ===========================================
**Control**                     **Purpose**
==============================  ===========================================
:code:`HX_REQUESTS_ENFORCE_SAME_APP`   Default: restrict to same-app requests
:code:`HX_REQUESTS_GLOBAL_ALLOW`       Define trusted apps or HxRequests globally
:code:`allowed`                        Per-request allowlist (apps or URLs)
:code:`allow_additive`                 Whether to combine with same-app rule
==============================  ===========================================

.. warning::

    Always follow the **principle of least privilege**.
    Only grant cross-app access when absolutely necessary
    and only to trusted, internal apps.
