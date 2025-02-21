How To Add GET Parameters To POST Requests
------------------------------------------

There are times when you need to pass GET parameters to a POST request.
A common example is when you have a page with filters applied, and after submitting a form via POST,
you want to refresh part of the page while preserving those filters.

`HxRequest` provides a way to include GET parameters in a POST request.

Passing GET Parameters in a POST Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To include GET parameters in a POST request, set :code:`use_full_path=True` in the :ref:`template tags <Hx Tags>`.

.. code-block:: html+django

    <button {% hx_post 'my_hx_request' use_full_path=True %}></button>


Why Is This Needed
~~~~~~~~~~~~~~~~~~

:code:`hx-requests` does not provide direct access to the current URL when using :code:`hx_get` or :code:`hx_post`.
This means you cannot manually append :code:`?param=value` to the request URL in the template (though that isnt pretty anyway).
