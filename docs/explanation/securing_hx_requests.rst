.. _why-hxrequest-security:

Why HxRequest Security Is Needed
--------------------------------

HxRequests make it easy to build modular, dynamic interfaces using HTMX.
Because they are registered globally and routed by name, deciding *whether the
current user may run a given handler* still matters — that is what per-handler
authorization provides.

This page explains **why that layer exists**, the risk it prevents, and why it
lives on the handler.

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
inside the token, a legitimately-issued token can be used by **a different user
than the one it was rendered for**. Anyone who can load a page holds valid tokens
for every handler rendered on it; the signature proves a token is genuine, not
that *this* user may run it. Tokens are minted server-side by the template tags,
so the risk isn't forgery — it's a real token being used by someone who
shouldn't be able to.

For example, suppose a :code:`delete_all_records_hx` button is rendered on a
dashboard that ordinary users can also load. Its token is genuine and is posted
back to the same page it was rendered on, so signing **and** path-binding
(below) both pass:

.. code-block:: html

    <button hx-post="/dashboard/?hx=<a-real-token-for-delete_all_records_hx>">Run Delete</button>

The token verifies and it is on the right path. The only thing left to stop a
non-admin from running it is the handler asking *"may this user do this?"* — and
getting that answer wrong (or not asking) is the whole vulnerability.


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

    - Run that handler themselves, from any page its token is rendered on
      (and, if it opts out of path-binding, from other pages too).
    - Modify or delete data they were never meant to touch.
    - Execute sensitive operations they aren't authorized for.

The defense is to make each handler responsible for its own authorization —
which the secure-by-default :code:`login_required` makes the path of least
resistance.


.. _path-binding:

Path-Binding
~~~~~~~~~~~~

Per-handler authorization answers *who* may run a handler. On a separate axis,
every signed token is, by default, **bound to the URL path it was rendered on**:
the token records the server-side :code:`request.path` at mint time (never the
client-supplied :code:`HX-Current-URL` header), and it verifies only when
replayed back to that same path. So the dashboard token above cannot be lifted
and posted to a different view — :code:`/somewhere-else/?hx=<that-token>` returns
:code:`Http404` before the request is routed.

This blocks *cross-page* replay, but it is **not** an authorization check, and it
does nothing for the dashboard example above: that request is posted back to the
very page the token was minted on, so path-binding passes and only per-handler
authorization decides *who* may run the handler.

Path-binding is automatic. For the rare case where a token must work across paths
(e.g. a proxy that rewrites :code:`request.path`), a handler can opt out with
:code:`bind_to_path = False`, or the whole project can disable it with
:code:`HX_REQUESTS_BIND_TOKEN_TO_PATH = False` — see
:ref:`How To Secure HxRequests <how-to-secure-hxrequests>`.


Summary
~~~~~~~

Signing ensures a request's name, object, and kwargs can't be forged.
Per-handler authorization ensures a *legitimate* token can't be used by someone
who shouldn't run the handler — because the handler decides, every time,
regardless of which view routed the request.

Path-binding adds a *where* constraint on top: a token verifies only on the
path it was rendered on, unless a handler opts out with
:code:`bind_to_path = False`.

Continue to :ref:`How To Secure HxRequests <how-to-secure-hxrequests>`
for configuration examples.
