Configuration
=============

These settings should be added to :code:`settings.py` to control :code:`hx-requests` behavior.


Messages Configuration
----------------------

HX_REQUESTS_USE_HX_MESSAGES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** `False`

Set this to `True` to enable `hx-requests` messages.
If `False`, messages will not be displayed, even if they are set.


HX_REQUESTS_HX_MESSAGES_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** *No Default*

Path to the template used for displaying messages.
The context in this template has access to :code:`messages`, following the same behavior as Django’s
`Messages framework <https://docs.djangoproject.com/en/5.0/ref/contrib/messages/#displaying-messages>`_.


Modal Configuration
-------------------

HX_REQUESTS_MODAL_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** `None`

Path to the template used for modals.


HX_REQUESTS_MODAL_BODY_ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** `#hx_modal_body`

A CSS selector for the modal body.
Set this only if :code:`HX_REQUESTS_MODAL_TEMPLATE` is overridden.

.. note::
    See :ref:`How To Use Modals` for details on overriding the default modal template.


Security Configuration
----------------------

The following settings control which :code:`HxRequests` can be triggered from which views or apps.
They are designed to protect your project from unintended or cross-app access.


HX_REQUESTS_ENFORCE_SAME_APP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** `True`

When set to :code:`True`, each :code:`HxRequest` can only be triggered from views in the **same Django app**.
This enforces strict app isolation by default.

.. code-block:: python

    HX_REQUESTS_ENFORCE_SAME_APP = True

If set to :code:`False`, :code:`HxRequests` can be triggered from **any app**, unless restricted
by more specific allowlists.

.. warning::

    Disabling this setting allows cross-app access for all :code:`HxRequests`.
    Only disable it in highly controlled environments where all apps are trusted
    and data exposure is not a risk.


HX_REQUESTS_GLOBAL_ALLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** `[]`

Defines a global allowlist of apps or specific :code:`HxRequests` that may be called
from anywhere in the project, even across app boundaries.

Two forms are supported:

**List form:** Allow all :code:`HxRequests` from specific apps.

.. code-block:: python

    HX_REQUESTS_GLOBAL_ALLOW = ["app1", "app2"]

**Dict form:** Map app names to specific :code:`HxRequest` class names.
Use :code:`"__all__"` to allow all requests from that app.

.. code-block:: python

    HX_REQUESTS_GLOBAL_ALLOW = {
        "app1": ["safe_hx_request", "safe_hx_2"],
        "app2": "__all__"
    }

.. note::
    This setting is ideal for internal shared libraries or utility apps that are
    intentionally designed for cross-app use.

.. warning::
    Avoid whitelisting untrusted or third-party apps.
    Doing so allows them to execute their :code:`HxRequests` anywhere in your project.

HX_REQUESTS_REQUIRE_AUTH
~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** `True`

When set to `True`, all `HxRequests` require an authenticated user by default.
Unauthenticated users will be blocked unless the request is explicitly listed
in the unauthenticated allowlist below.

.. code-block:: python

    HX_REQUESTS_REQUIRE_AUTH = True


HX_REQUESTS_UNAUTHENTICATED_ALLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** `{}`

Defines specific `HxRequests` that may be executed **without authentication**.
This setting uses the same structure as the global allowlist.

**List form:** allow all `HxRequests` from the listed apps.

.. code-block:: python

    HX_REQUESTS_UNAUTHENTICATED_ALLOW = ["app1"]

**Dict form:** map app labels to specific `HxRequest` names, or `"__all__"` to allow every request in that app.

.. code-block:: python

    HX_REQUESTS_UNAUTHENTICATED_ALLOW = {
        "app1": "__all__",
        "app2": ["hx_request_1", "hx_request_2"]
    }

.. warning::
    Only include safe, read-only, or non-sensitive `HxRequests` here.
    Requests listed in this allowlist can be executed by unauthenticated users.
