How To Scope The hx_object Queryset
-----------------------------------

When an :code:`HxRequest` carries an object, the round-trip reference is resolved
through :code:`get_queryset`. By default that queryset is the object's **model
default manager**, so any scoping expressed there (soft-delete filters, tenant
boundaries) is honored automatically, and a primary key outside the queryset
raises :code:`Http404` instead of loading the row.

That default is deliberately narrow. This guide shows how to resolve the object
through **a different queryset** — a custom manager, a broader lookup, or a
per-request scope.

For *why* resolution is scoped and how it relates to signing, see
:ref:`Object Serialization`.


Set ``model``
~~~~~~~~~~~~~

The simplest override. Point the handler at a model and resolution runs through
that model's default manager, mirroring Django's :code:`SingleObjectMixin`:

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class EditInvoiceHx(BaseHxRequest):
        name = "edit_invoice"
        model = Invoice


Override ``get_queryset``
~~~~~~~~~~~~~~~~~~~~~~~~~~

For anything beyond the default manager, override :code:`get_queryset` and return
the queryset you want the object resolved through. Whatever you return is the
authoritative lookup — a pk outside it is a :code:`Http404`.

**Resolve through a custom manager.**
Use a manager other than the default — for example one that widens the lookup
back to rows the default manager hides:

.. code-block:: python

    class RestoreInvoiceHx(BaseHxRequest):
        name = "restore_invoice"

        def get_queryset(self):
            # Include soft-deleted rows the default manager filters out.
            return Invoice.all_objects.all()

**Broaden for privileged users.**
:code:`get_queryset` runs per request, so you can widen or narrow the scope based
on who is asking:

.. code-block:: python

    class EditInvoiceHx(BaseHxRequest):
        name = "edit_invoice"

        def get_queryset(self):
            if self.request.user.is_staff:
                return Invoice.objects.all()
            return Invoice.objects.filter(owner=self.request.user)

.. note::

    Returning :code:`None` from :code:`get_queryset` (the default when no
    :attr:`model` is set) falls back to the resolved object's own model default
    manager. Return an explicit queryset only when you need a scope other than
    that.

.. warning::

    Widening the queryset widens what a replayed reference can resolve. A token
    minted for one user's page can be sent by another; :code:`get_queryset` is
    the boundary that keeps resolution in scope. Only broaden it — for example
    with :code:`all_objects` or an unfiltered :code:`objects.all()` — where the
    handler's own checks make that safe.
