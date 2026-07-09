.. _why-hxrequest-security:

Why HxRequest Security Is Needed
--------------------------------

HxRequests make it easy to build modular, dynamic interfaces using HTMX.
Because they are registered globally, controlling *which* view may invoke *which*
handler still matters — that is what the controls on this page provide.

This page explains the risk these controls prevent, the model that prevents it,
and when it is safe to relax it.

.. note::

    **Request signing comes first** (see :ref:`Request Signing`): a client
    **cannot forge or tamper with** a request's routing data. The layers after it
    govern a *legitimately-issued* token — used from a page, or by a user, it
    shouldn't be.

See also: :ref:`How To Secure HxRequests <how-to-secure-hxrequests>`


Request Signing
~~~~~~~~~~~~~~~

The routing data an :code:`HxRequest` runs on — the handler **name**, the
**object** it acts on, and any **kwargs** — travels in a single HMAC-signed
:code:`hx` token instead of as loose, client-editable query parameters. The
token is produced with :code:`django.core.signing` and your project's
:code:`SECRET_KEY`: a client can read it (it is base64-encoded JSON) but cannot
alter or fabricate one, because any change invalidates the signature.
:code:`HtmxViewMixin` rebuilds the request from the *verified* payload only, and
returns :code:`Http404` on a missing, tampered, or hand-crafted token before any
deserializer or handler runs.

**What signing protects.** When the name, object, and kwargs were loose query
parameters, a client could edit them on the URL. Signing closes those tampering
vectors:

    - **Object tampering / IDOR** — a client can't change the serialized
      :code:`object` (e.g. swap a primary key) to make a handler act on a record
      that isn't theirs.
    - **Cross-model instance swap** — the serialized object can't be repointed at
      a different model.
    - **Context / kwarg forgery** — a client can't inject kwargs (e.g. a
      :code:`can_edit` flag) to force values into the handler's context.
    - **Handler spoofing** — a client can't hand-craft a token that routes to an
      arbitrary handler name.
    - **Garbage-input 500s** — malformed routing data fails the signature check
      and 404s, instead of reaching a deserializer and raising.

**What signing does not decide.** A signature proves a token was issued by your
server and hasn't been altered — not *where* it may be used or *who* may use it.
A legitimately-issued token can still be sent from another page, or by another
user. *Where* is constrained by path-binding (below). *Who* is **not** answered
by the scoping controls here — it comes from requiring authentication
(:code:`HX_REQUESTS_REQUIRE_AUTH`) and the permissions on the view a request
routes through. The scoping controls below are a third axis: which handlers a
given view or app may run at all.

.. warning::

    None of the layers on this page authorize *individual users*. Signing,
    path-binding, and app/handler scoping establish that a request is genuine, on
    its own page, and allowed for the view — **not** that *this user* may perform
    the action. To restrict who can run a handler you still have to require
    authentication (:code:`HX_REQUESTS_REQUIRE_AUTH`) and enforce your own
    permission checks on the view each :code:`HxRequest` routes through, exactly
    as you would protect any other view.


The Threat: Replaying a Valid Token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Signing proves a token is genuine, but it doesn't decide *scope*: which
registered handlers a given view is willing to run.

Because :code:`HtmxViewMixin` routes any HTMX request by the (verified) name
inside the token, **any view that includes the mixin** is a potential entry
point for any registered :code:`HxRequest` — provided a valid token for that
handler exists. Tokens are minted server-side by the template tags, so the risk
isn't forgery; it's a legitimately-issued token being **replayed against a view
where it was never meant to run**.

For example, you may design an :code:`HxRequest` such as
:code:`delete_all_records_hx` to be used **only** from an internal admin page.
If a valid token for it is rendered somewhere a user can see, nothing about the
signature alone stops them from replaying it against an unrelated view:

.. code-block:: html

    <button hx-post="/home/?hx=<a-real-token-for-delete_all_records_hx>">Run Delete</button>

If :code:`/home` is a simple, public-facing view that includes the
:code:`HtmxViewMixin` and neither scopes its handlers nor enforces auth, this
request would still reach and execute the deletion logic.

.. note::

    By default this exact cross-page replay is **already blocked**: tokens are
    :ref:`path-bound <path-binding>`, so a token minted on the admin page is
    rejected on :code:`/home`. The scenario here is what happens *without* that
    layer — or when it is relaxed. App-isolation and scoping remain necessary for
    the case path-binding can't cover: a handler minted from a view or app that
    should never render it (e.g. a third-party template), where the token is
    bound to *that* page and posting it back there succeeds.

The consequences:

    - The route doesn't matter — any view using the mixin is a potential gateway
      for any registered :code:`HxRequest` it doesn't scope.
    - Permission checks on the *originally intended* view do not automatically
      apply where the token is replayed.
    - So users could replay private or destructive actions from public pages, and
      third-party or unreviewed templates could invoke internal logic from views
      that never scoped their handlers.

Signing removes the *forging* vector; app-isolation and per-view scoping are the
layer that keeps a registered handler from becoming a global entry point into
your application's internal request logic.


The Controls: App Isolation and Scoping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The security layer is built around four goals:

1. **App Isolation** – Prevent cross-app access by default (i.e. 3rd-party untrusted packages).
2. **Explicit Trust** – Cross-app usage must be declared via settings or per-view rules.
3. **Safe Extensibility** – Shared internal libraries can safely opt in to wider access via settings.
4. **Predictability** – Even if enforcement is disabled, the logic runs consistently.

They are enforced through four layers:

============================  ============================================
**Layer**                     **Responsibility**
============================  ============================================
Base Rule                     Enforces same-app isolation (default)
Global Allowlist              Declares trusted apps or HxRequests
Per-View Controls             Adds fine-grained access (allowed HxRequests)
Additive Logic                Combines or replaces base rule
============================  ============================================

See :ref:`How To Secure HxRequests <how-to-secure-hxrequests>` for configuration
examples of each layer.


.. _path-binding:

Path-Binding
~~~~~~~~~~~~

The controls above answer *which handlers a given view may run*. On top of them,
every signed token is, by default, **bound to the URL path it was rendered on**:
the token records the server-side :code:`request.path` at mint time (never the
client-supplied :code:`HX-Current-URL` header), and it verifies only when
replayed back to that same path. The
:code:`/home/?hx=<a-real-token-for-delete_all_records_hx>` replay above therefore
fails and returns :code:`Http404` before the request is routed.

This narrows *where* a token can be used; it is **not** an authorization check. A
user who can load the page a token was minted on still holds a token valid for
that path — so the scoping controls (and any auth on the originating view) remain
the layer that decides *who* may run the handler.

Path-binding is automatic. For the rare case where a token must work across paths
(e.g. a proxy that rewrites :code:`request.path`), a handler can opt out with
:code:`bind_to_path = False`, or the whole project can disable it with
:code:`HX_REQUESTS_BIND_TOKEN_TO_PATH = False` — see
:ref:`How To Secure HxRequests <how-to-secure-hxrequests>`.


When To Relax Controls
~~~~~~~~~~~~~~~~~~~~~~~~

You should loosen restrictions only when you **trust the source** of the request
and the operation is something that **any user could safely perform** —
for example, when triggering a non-sensitive UI component or an action that does
not expose or modify private data.

Typical valid cases include:

    - Shared internal UI libraries that are reviewed and sandboxed.
    - Administrative tools explicitly designed for cross-app access.
    - Controlled internal environments (single-tenant, internal users only).

.. warning::

    Do not disable app enforcement globally or allow untrusted apps.
    Doing so allows external or third-party code to trigger
    **any HxRequest** in your project.


Summary
~~~~~~~

- **Signing** ensures a request's name, object, and kwargs can't be forged.
- **App-isolation and scoping** ensure a registered handler doesn't become a
  remote-call interface to your whole project, by respecting application
  boundaries and explicit trust.
- **Path-binding** binds each token to the page it was rendered on by default, so
  a token can't be replayed against a different view's path; opt out per handler
  with :code:`bind_to_path = False`.

Continue to :ref:`How To Secure HxRequests <how-to-secure-hxrequests>`
for configuration examples.
