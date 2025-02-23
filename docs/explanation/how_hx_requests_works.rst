How Do HxRequests Work?
-----------------------

Instead of routing HTMX requests to a Django view like a normal request,
:code:`hx_requests` intercepts them and sends them to a dedicated HxRequest class.

How It Works
~~~~~~~~~~~~

When using the :ref:`hx_get <Hx Tags>` and :ref:`hx_post <Hx Tags>` template tags:


#. The URL of the request is set to the current page's URL.
#. An :code:`hx_request_name`` GET parameter is added to the request URL (based on the name passed to the template tag).
#. When the request reaches the view, :code:`HtmxViewMixin` checks if the request is an HTMX request and if the :code:`hx_request_name` is in the request
   and routes the request to the :code:`HxRequest` with the matching name.
#. The :code:`HxRequest` processes the request and returns an Html response.


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

    If an `HxRequest` is used across multiple views, it's permissions depend on the view handling the request.
