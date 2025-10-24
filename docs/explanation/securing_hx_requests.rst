Why HxRequest Security Is Needed
--------------------------------

HxRequests make it easy to build modular, dynamic interfaces using HTMX.
However, because they are registered globally, any request can be triggered
from any view by passing the right :code:`hx_request_name`— unless you explicitly
restrict it.

This page explains **why these security controls exist**, the risks they prevent,
and the principles behind their design.

See also: :ref:`How To Secure HxRequests <how-to-secure-hxrequests>`


The Problem
~~~~~~~~~~~

Without validation, any page or script can issue a request like:

.. code-block:: html+django

    <button hx-get="/some/unrelated/view/?hx_request_name=delete_all_records_hx">
        Run Dangerous Request
    </button>

If :code:`delete_all_records_hx` exists anywhere in your project,
it would execute—even if the current view or user shouldn’t have access to it.

This can happen because the :code:`HtmxViewMixin` automatically routes
based on the :code:`hx_request_name` parameter. As long as the target view
includes this mixin, **any page** pointing to that view can call
any registered :code:`HxRequest`, regardless of where it was intended to run.

For example, you may design an :code:`HxRequest` such as
:code:`delete_all_records_hx` to be used **only** from an internal admin page.
But a malicious user (or even a public page) could send the same request from:

.. code-block:: html

    <button hx-get="/home/?hx_request_name=delete_all_records_hx">Run Delete</button>

If :code:`/home` is a simple, public-facing view that includes
the :code:`HtmxViewMixin`, and does not require authentication,
this button would still reach and execute the deletion logic.

In other words:
    - The actual page or route doesn’t matter — any page that uses the mixin
      becomes a potential gateway for any registered HxRequest.
    - A completely unrelated view (like a homepage) could call an
      administrative HxRequest simply by passing its name in the query string.
    - Authentication or permission checks on the original intended view
      (where the HxRequest was meant to run) are **bypassed entirely**.

This means:
    - Users could trigger private or destructive actions from public pages.
    - Views could unintentionally expose data or behavior from other apps.
    - Third-party templates, plugins, or unreviewed code could invoke internal logic
      by referencing the right :code:`hx_request_name`.

Without additional security controls, any :code:`hx_request_name` becomes a
global entry point into your application’s internal request logic.

Design Goals
~~~~~~~~~~~~

The new HxRequest security layer enforces:

1. **App Isolation** – Prevent cross-app access by default (i.e 3rd party untrusted packages).
2. **Explicit Trust** – Cross-app usage must be declared via settings or per-request rules.
3. **Safe Extensibility** – Shared internal libraries can safely opt in to wider access.
4. **Predictability** – Even if enforcement is disabled, the logic runs consistently.


What Happens Without Controls
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you remove these checks, anyone who knows (or guesses) an :code:`hx_request_name`
can:

    - Trigger arbitrary requests from unrelated views.
    - Modify or delete data outside their intended scope.
    - Execute sensitive operations from unprotected endpoints.


Security Model Overview
~~~~~~~~~~~~~~~~~~~~~~~

============================  ============================================
**Layer**                     **Responsibility**
============================  ============================================
Base Rule                     Enforces same-app isolation (default)
Global Allowlist              Declares trusted apps or HxRequests
Per-HxRequest Controls        Adds fine-grained access (apps or URLs)
Additive Logic                Combines or replaces base rule
============================  ============================================


When To Relax Controls
~~~~~~~~~~~~~~~~~~~~~~

You should loosen restrictions only when you **trust the source** of the request
and the operation is something that **any user could safely perform**—
for example, when triggering a non-sensitive UI component or an action that does
not expose or modify private data.

Typical valid cases include:

    - Shared internal UI libraries that are reviewed and sandboxed.
    - Administrative tools explicitly designed for cross-app access.
    - Controlled internal environments (single-tenant, internal users only).

.. warning::

    Do not disable app enforcement globally or allow untrusted apps.
    Doing so allows external or third-party code to trigger
    **any HxRequest** in your project. code to trigger
    **any HxRequest** in your project.


Summary
~~~~~~~

Without these controls, :code:`hx_request_name` effectively exposes
a remote-call interface to your entire Django project.

The HxRequest security layer ensures this system respects
application boundaries and explicit trust.

Continue to :ref:`How To Secure HxRequests <how-to-secure-hxrequests>`
for configuration examples.
