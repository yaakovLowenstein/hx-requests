How To Detect And Inspect An HxRequest
--------------------------------------

The routing data (name, object, kwargs) is signed inside a single :code:`hx`
token, so it is no longer readable as loose :code:`hx_request_name` /
:code:`object` / :code:`___kwarg` query parameters. To work with an inbound
request from your own view code, use the helpers in :code:`hx_requests.utils`.

Checking If A Request Is An HxRequest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`is_hx_request(request)` returns :code:`True` when the request carries a
valid signed token — i.e. it is bound for a registered :code:`HxRequest`.

This is different from :code:`is_htmx_request(request)`, which only checks the
:code:`HX-Request` header and is :code:`True` for *any* htmx request. The common
use is telling a plain htmx request (sort / filter / paginate) apart from one
routed to an :code:`HxRequest`, so the plain one can fall through to the
underlying view:

.. code-block:: python

    from hx_requests.utils import is_htmx_request, is_hx_request

    def dispatch(self, request, *args, **kwargs):
        # Plain htmx (no hx token) -> let the underlying view handle it.
        if is_htmx_request(request) and not is_hx_request(request):
            return SomeListView.dispatch(self, request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

Reading The Name, Object, And Kwargs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you need the request's data before dispatch runs:

- :code:`get_hx_request_name(request)` returns the verified name (or :code:`None`).
- :code:`get_hx_payload(request)` returns the full verified payload,
  :code:`{"name": ..., "object": ..., "kwargs": ...}` (or :code:`None`).

.. code-block:: python

    from hx_requests.utils import get_hx_request_name, get_hx_payload

    name = get_hx_request_name(request)

    payload = get_hx_payload(request)
    if payload:
        name = payload["name"]

The :code:`object` and :code:`kwargs` in the payload are still in serialized
form. Run them through :code:`deserialize` / :code:`deserialize_kwargs` to get
live values:

.. code-block:: python

    from hx_requests.utils import get_hx_payload, deserialize, deserialize_kwargs

    payload = get_hx_payload(request)
    if payload:
        obj = deserialize(payload["object"]) if payload["object"] else None
        kwargs = deserialize_kwargs(**payload["kwargs"])

.. note::

    All of these helpers return :code:`None` / :code:`False` on a missing or
    tampered token — they never raise — so they are safe to call on any request.
