How To Add Headers To Respones
------------------------------


There are times when you need to add headers to the response returned from the server.
HTMX uses specific headers to modify behavior when certain headers are present.

Common HTMX response headers include:
- **`Hx-Triggers`** - Triggers client-side events when the response is returned.
- **`Hx-Redirect`** - Redirects the user to a new page.
- **`Hx-Refresh`** - Refreshes the page.


Adding Headers
~~~~~~~~~~~~~~

The easiest way to add headers to a response is by overriding the :code:`get_headers` method in an :code:`HxRequest`.

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class MyHxRequest(BaseHxRequest):
        ....

        def get_headers(self, **kwargs):
            headers = super().get_headers(**kwargs)
            headers["Some-Header"] = "Some Value"
            return headers

Hx-Trigger
~~~~~~~~~~

Since triggers are commonly used, a helper method is available to add them to the headers.

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class MyHxRequest(BaseHxRequest):
        ....

        def get_triggers(self, **kwargs):
            triggers = super().get_triggers(**kwargs)
            triggers.append("some_trigger")
            return triggers

Refresh and Redirect
~~~~~~~~~~~~~~~~~~~~

If you need to refresh the page or redirect to another page, use the :code:`refresh_page` or :code:`redirect` attributes.

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class MyHxRequest(BaseHxRequest):
        ....
        refresh_page = True # This will refresh the page
        redirect = "some_url" # This will redirect to some_url



If you need to set :code:`refresh_page` or :code:`redirect` dynamically, you can modify them anywhere in the request lifecycle.

.. code-block:: python

    from hx_requests.hx_requests import FormHxRequest

    class MyHxRequest(FormHxRequest):
        ....
        refresh_page = True

        def form_invalid(self, **kwargs):
            self.refresh_page = False
            return super().form_invalid(form)
