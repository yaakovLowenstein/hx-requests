Object Serialization
--------------------

Serialization in :code:`hx_requests` ensures that Django model instances and other data types
can be safely passed through HTMX requests. The serialization process takes place in the :ref:`template tag <Hx Tags>`.

Since HTMX requests don’t natively support passing complex Python objects,
:code:`hx_requests` provides a custom serialization method that allows Django models
and additional data to be included in GET and POST requests.

The serialized values (the object and the kwargs) are not appended to the URL as
loose query parameters. They are packed, together with the :code:`HxRequest`
name, into a single HMAC-signed :code:`hx` token. The signature is what makes
them trustworthy on the way back in — the values below describe the *contents*
of that token, not editable URL params.

Serializing Model Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a model instance is serialized, it is converted into a structured string format
that includes the prefix :code:`model_instance`, to distinguish it from a plain JSON
value, followed by the app label, model name, and primary key.

For example, a :code:`User` instance with :code:`pk=5` in the :code:`auth` app
would be represented as:

.. code-block:: text

    model_instance__auth__user__5

This ensures that objects can be passed in requests without requiring JSON encoding.

If the value being serialized is not a Django model instance,
it is simply converted to JSON.

Deserializing Model Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a serialized object is received, it needs to be converted back into a Django model instance.
This is done by extracting the app label, model name, and primary key,
then retrieving the object from the database.

If the received value is not a model instance, it is treated as a standard JSON object.

This process ensures that Django objects can be reconstructed properly when handling HTMX requests.

Object scoping (``get_queryset`` / ``model``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The instance is resolved through the model's **default manager** — not
``_base_manager``. Any scoping expressed on the default manager (soft-delete
filters, tenant boundaries) is therefore honored automatically: an object the
default manager hides cannot be resolved.

For row-level authorization, override :meth:`get_queryset` on the
:code:`HxRequest` (or set :attr:`model`), exactly as you would on a Django
:code:`UpdateView`. Resolution runs through that queryset, and a primary key
outside it raises :code:`Http404` rather than silently loading another user's
row:

.. code-block:: python

    class EditInvoiceHx(FormModalHxRequest):
        name = "edit_invoice"

        def get_queryset(self):
            # A user can only resolve invoices they own.
            return Invoice.objects.filter(owner=self.request.user)

Because the round-trip is signed, the object reference cannot be *forged*; the
:code:`get_queryset` seam is what stops a *replayed* reference (a token minted
for one user's page, sent by another) from resolving out-of-scope data.

Handling kwargs Serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each keyword argument is prefixed with :code:`___` inside the token so it can be
told apart from any loose query parameters. When deserializing, the prefix is
removed, and values are restored to their original form.

This allows :code:`hx_requests` to safely pass complex parameters in HTMX requests.

.. note::

    Kwargs live *inside* the signed token, not on the query string — so a kwarg
    is never read as a standard GET parameter.
    If you need to pass a real GET parameter through an HTMX request, use the
    :code:`hx-include` or :code:`hx-vals` attribute instead of passing it as a :code:`kwarg`.
    For example, when implementing pagination, the :code:`page` parameter must be sent as a standard GET parameter. Passing it as a :code:`kwarg` will bury it in the token and it will be ignored by the request handler.
