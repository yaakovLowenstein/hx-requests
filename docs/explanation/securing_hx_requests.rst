Why HxRequest Security Is Needed
--------------------------------

HxRequests make it easy to build modular, dynamic interfaces using HTMX.
Because they are registered globally, controlling *which* view may invoke *which*
handler still matters — that is what the controls on this page provide.

This page explains **why these security controls exist**, the risks they prevent,
and the principles behind their design.

.. note::

    **Request signing comes first.** The :code:`HxRequest` name, object, and
    kwargs are delivered in a single HMAC-signed :code:`hx` token, so a client
    **cannot forge or hand-craft** a request for an arbitrary handler — a
    missing or tampered token is rejected with :code:`Http404` before any
    routing happens. The controls below are the *next* layer: they scope which
    registered handlers a given view/app is willing to run, which is what still
    governs a token that was issued legitimately somewhere and then replayed
    against a view that shouldn't accept it.

See also: :ref:`How To Secure HxRequests <how-to-secure-hxrequests>`


The Problem
~~~~~~~~~~~

Signing stops a client from *hand-crafting* a request for an arbitrary handler
— a URL like :code:`/home/?hx=<made-up-token>` is rejected because the token
won't verify. What signing does **not** decide is *scope*: which registered
handlers a given view is willing to run.

Because :code:`HtmxViewMixin` routes any HTMX request by the (verified) name
inside the token, **any view that includes the mixin** is a potential entry
point for any registered :code:`HxRequest` — provided a valid token for that
handler exists. Tokens are minted server-side by the template tags, so the risk
is a legitimately-issued token being **replayed against a view where it was
never meant to run**.

For example, you may design an :code:`HxRequest` such as
:code:`delete_all_records_hx` to be used **only** from an internal admin page.
If a valid token for it is rendered somewhere a user can see, nothing about the
signature alone stops them from replaying it against an unrelated view:

.. code-block:: html

    <button hx-post="/home/?hx=<a-real-token-for-delete_all_records_hx>">Run Delete</button>

If :code:`/home` is a simple, public-facing view that includes
the :code:`HtmxViewMixin`, and does not itself require authentication or scope
its handlers, this request would still reach and execute the deletion logic.

In other words:
    - The actual page or route doesn’t matter — any view that uses the mixin
      becomes a potential gateway for any registered HxRequest it doesn't scope.
    - An unrelated view (like a homepage) could run an administrative HxRequest
      if it neither restricts which handlers it accepts nor enforces auth.
    - Authentication or permission checks on the *originally intended* view
      (where the HxRequest was meant to run) do not automatically apply here.

This means, without the controls below:
    - Users could replay private or destructive actions from public pages.
    - Views could unintentionally expose data or behavior from other apps.
    - Third-party templates, plugins, or unreviewed code could invoke internal
      logic from views that never scoped their handlers.

So while signing removes the forging vector, app-isolation and per-view scoping
remain the layer that keeps a registered handler from becoming a global entry
point into your application’s internal request logic.

Design Goals
~~~~~~~~~~~~

The new HxRequest security layer enforces:

1. **App Isolation** – Prevent cross-app access by default (i.e 3rd party untrusted packages).
2. **Explicit Trust** – Cross-app usage must be declared via settings or per-view rules.
3. **Safe Extensibility** – Shared internal libraries can safely opt in to wider access via settings.
4. **Predictability** – Even if enforcement is disabled, the logic runs consistently.


What Happens Without Controls
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you remove these checks, anyone holding a valid token for an
:code:`HxRequest` (one rendered on any page they can reach) can:

    - Replay that request against unrelated views.
    - Modify or delete data outside its intended scope.
    - Execute sensitive operations from unprotected endpoints.


Security Model Overview
~~~~~~~~~~~~~~~~~~~~~~~

============================  ============================================
**Layer**                     **Responsibility**
============================  ============================================
Base Rule                     Enforces same-app isolation (default)
Global Allowlist              Declares trusted apps or HxRequests
Per-View Controls             Adds fine-grained access (allowed HxRequests)
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

Signing ensures a request's name, object, and kwargs can't be forged. On top of
that, the controls here ensure a registered handler doesn't become a remote-call
interface to your entire Django project by respecting application boundaries and
explicit trust.

Continue to :ref:`How To Secure HxRequests <how-to-secure-hxrequests>`
for configuration examples.
