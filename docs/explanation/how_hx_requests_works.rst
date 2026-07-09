How Do HxRequests Work?
-----------------------

Instead of routing HTMX requests to a Django view like a normal request,
:code:`hx_requests` intercepts them and sends them to a dedicated HxRequest class.

How It Works
~~~~~~~~~~~~

When using the :ref:`hx_get <Hx Tags>` and :ref:`hx_post <Hx Tags>` template tags:


#. The URL of the request is set to the current page's URL.
#. A single :code:`hx` GET parameter is added to the request URL. It carries the
   :code:`HxRequest` name (along with the serialized object and kwargs).
#. When the request reaches the view, :code:`HtmxViewMixin` reads the name from
   the :code:`hx` parameter and routes the request to the :code:`HxRequest` with
   the matching name.
#. The :code:`HxRequest` processes the request and returns an Html response.

.. note::

    The :code:`hx` parameter is a signed token, not loose query params — see
    :ref:`Object Serialization` for what it packs and
    :ref:`Why HxRequest Security Is Needed` for why it is signed.


Why Not Just Use A URL Router?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At first glance, this might seem like something a URL router should handle. But using a view mixin instead has a couple of key advantages:

Access to View Context
^^^^^^^^^^^^^^^^^^^^^^

Since the request first reaches the view, the :code:`HxRequest` has access to everything the view provides.
This is especially useful because you don’t have to duplicate context logic in the :code:`HxRequest`.

In many cases, the HTML snippet being swapped in depends on context from the view—particularly with Django class-based views like :code:`ListView`.
Using a mixin ensures that context is automatically available without extra work.

Permissions Work Automatically
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because :code:`HxRequests` run through the view, any permissions applied to the view also apply to the :code:`HxRequest` by default.
If a user can’t access the view, they also can’t access the :code:`HxRequest`, eliminating the need to duplicate permission logic.

Of course, there may be cases where this isn’t the behavior you want. If needed, you can override permissions inside the :code:`HxRequest` itself.

.. warning::

    This depends on mixin ordering. On the HxRequest handoff,
    :code:`HtmxViewMixin.dispatch` does **not** call :code:`super().dispatch()`,
    so a dispatch-based auth mixin (:code:`LoginRequiredMixin`,
    :code:`PermissionRequiredMixin`) only gates the HxRequest when it is placed
    *before* :code:`HtmxViewMixin` in the class's MRO. hx_requests raises a
    startup system check (W001) when an auth mixin is ordered after
    :code:`HtmxViewMixin`. For robust control, authorize on the HxRequest itself.

.. warning::

    If an `HxRequest` is used across multiple views, it's permissions depend on the view handling the request.
