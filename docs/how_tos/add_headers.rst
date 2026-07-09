How To Add Headers To Responses
-------------------------------


There are times when you need to add headers to the response returned from the server.
HTMX uses specific headers to modify behavior when certain headers are present.

Common HTMX response headers include:

* **`HX-Trigger`** - Triggers client-side events when the response is returned.
* **`HX-Redirect`** - Redirects the user to a new page.
* **`HX-Refresh`** - Refreshes the page.


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

Hx-Trigger With Details
~~~~~~~~~~~~~~~~~~~~~~~

You can pass details along with a trigger by using a dict instead of a string.
When any trigger carries details, the header is automatically formatted as a JSON object
per the `HX-Trigger spec <https://htmx.org/headers/hx-trigger/>`_.

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class MyHxRequest(BaseHxRequest):
        ....

        def get_triggers(self, **kwargs):
            triggers = super().get_triggers(**kwargs)
            triggers.append({"showMessage": {"level": "info", "message": "Saved!"}})
            return triggers

You can also mix plain triggers and triggers with details:

.. code-block:: python

    def get_triggers(self, **kwargs):
        triggers = super().get_triggers(**kwargs)
        triggers.append("refreshList")
        triggers.append({"showMessage": "Item saved successfully"})
        return triggers

This produces the header: ``HX-Trigger: {"refreshList": true, "showMessage": "Item saved successfully"}``

Targeting Trigger Phases (After-Settle / After-Swap)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default all triggers are emitted on the ``HX-Trigger`` header (fired as soon
as the response is received). To fire events at a later htmx phase, return a
**dict** from :code:`get_triggers` keyed by phase. Each value is a list of the
same shape as above (plain strings and/or detail dicts):

.. code-block:: python

    def get_triggers(self, **kwargs):
        return {
            "trigger": ["eventA"],                                  # HX-Trigger
            "after_settle": ["eventB"],                             # HX-Trigger-After-Settle
            "after_swap": [{"showMessage": {"message": "Done"}}],   # HX-Trigger-After-Swap
        }

The recognized phase keys are :code:`trigger`, :code:`after_settle`, and
:code:`after_swap` (see :code:`BaseHxRequest.trigger_header_map`). Phases with no
triggers are omitted.

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
            return super().form_invalid(**kwargs)
