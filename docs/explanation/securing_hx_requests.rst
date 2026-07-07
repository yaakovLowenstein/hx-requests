.. _why-hxrequest-security:

Why HxRequest Security Is Needed
--------------------------------

HxRequests make it easy to build modular, dynamic interfaces using HTMX.
Because they are registered globally and routed by name, deciding *whether the
current user may run a given handler* still matters — that is what per-handler
authorization provides.

This page explains **why that layer exists**, the risk it prevents, and why it
lives on the handler rather than in a project-wide settings matrix.

.. note::

    **Request signing comes first.** The :code:`HxRequest` name, object, and
    kwargs are delivered in a single HMAC-signed :code:`hx` token, so a client
    **cannot forge or hand-craft** a request for an arbitrary handler — a
    missing or tampered token is rejected with :code:`Http404` before any
    routing happens. Authorization is the *next* layer: it decides whether the
    user behind a legitimately-issued token is allowed to run the handler.

See also: :ref:`How To Secure HxRequests <how-to-secure-hxrequests>`


The Problem
~~~~~~~~~~~

Signing stops a client from *hand-crafting* a request for an arbitrary handler
— a URL like :code:`/home/?hx=<made-up-token>` is rejected because the token
won't verify. What signing does **not** decide is *authorization*: whether the
user making the request is allowed to run that handler.

Because :code:`HtmxViewMixin` routes any HTMX request by the (verified) name
inside the token, a legitimately-issued token can be **replayed** — sent from a
different page, or by a different user than the one it was rendered for. Tokens
are minted server-side by the template tags, so the risk isn't forgery; it's a
real token being used by someone who shouldn't be able to.

For example, you may design an :code:`HxRequest` such as
:code:`delete_all_records_hx` for administrators. If a valid token for it is
ever rendered somewhere a non-admin can see, nothing about the *signature* stops
them from replaying it:

.. code-block:: html

    <button hx-post="/home/?hx=<a-real-token-for-delete_all_records_hx>">Run Delete</button>

The token verifies. What must stop the request is the handler asking *"may this
user do this?"* — and getting the answer wrong (or not asking) is the whole
vulnerability.


Why per-handler authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The natural question is *"may this **user** run this **handler**"* — a property
of the handler and the request, not of which view happened to include the mixin.
So the check lives on the :code:`HxRequest`, enforced in its :code:`dispatch`
before :code:`get` / :code:`post`, no matter where the request originated:

- :code:`login_required` (default ``True``) — a handler requires an
  authenticated user unless it explicitly opts out. Secure by default: a new
  handler is not anonymously reachable by accident.
- :code:`permission_required` — a permission (or list) the user must hold.
- :code:`has_permission` — an override for row-level / ownership / tenancy
  checks, the same seam Django CBVs give you.

Answering the authorization question *at the handler* means the
:code:`delete_all_records_hx` example above is safe wherever its token is
replayed: the handler itself refuses a user who lacks the permission, regardless
of which view routed the request.


What Happens Without It
~~~~~~~~~~~~~~~~~~~~~~~~

If a handler declares no authorization (and opts out of the login default),
anyone holding a valid token for it — one rendered on any page they can reach —
can:

    - Replay that request from an unrelated page.
    - Modify or delete data they were never meant to touch.
    - Execute sensitive operations they aren't authorized for.

The defense is to make each handler responsible for its own authorization —
which the secure-by-default :code:`login_required` makes the path of least
resistance.


GET must not mutate
~~~~~~~~~~~~~~~~~~~~

Signing and per-handler authorization decide *who* may run a handler; they say
nothing about *which HTTP method* does the writing. That still matters, because
GET requests are not CSRF-protected. A valid GET URL — signed token and all — is
replayable cross-site: an attacker embeds it in an :code:`<img src>`, a
prefetch, or a :code:`<link>`, and the victim's browser fires it automatically
against any page they visit. If the handler's :code:`get()` performs a write,
that write happens with no CSRF check and no user intent.

The rule is the ordinary web one: **mutations happen only on POST** (which
carries CSRF protection), and GET is for rendering. hx-requests nudges you
toward it — a database write during :code:`get()` logs a warning naming the
handler — but never blocks the request, since a handful of GET writes (idempotent
bookkeeping such as a "last seen" touch) are legitimately safe and can opt out
with :code:`allow_writes_on_get = True`.


Summary
~~~~~~~

Signing ensures a request's name, object, and kwargs can't be forged.
Per-handler authorization ensures a *legitimate* token can't be used by someone
who shouldn't run the handler — because the handler decides, every time,
regardless of which view routed the request.

Continue to :ref:`How To Secure HxRequests <how-to-secure-hxrequests>`
for configuration examples.
