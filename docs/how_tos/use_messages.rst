How To Set Messages
-------------------

:code:`hx-requests` leverages Django's messaging framework to deliver asynchronous messages.
This is a convenient way to notify users when a form is valid or invalid, or to display any other message without requiring a full page reload.

Add Settings to settings.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| Set :code:`HX_REQUESTS_USE_HX_MESSAGES`: to True (default is False)
| Define :code:`HX_REQUESTS_HX_MESSAGES_TEMPLATE` in settings to the path of the messages template. The context in the template has access to :code:`messages`.

.. code-block:: python

    HX_REQUESTS_USE_HX_MESSAGES = True # Default is False
    HX_REQUESTS_HX_MESSAGES_TEMPLATE = "path/to/your/messages_template.html"

*messages_template.html*

.. code-block:: html

    <div id="hx_messages" hx-swap-oob='true'>
        <ul class="messages">
            {% for message in messages %}
                <li class="alert {{ message.tags }}">{{ message|safe }}</li>
            {% endfor %}
        </ul>
    </div>

Notes:
   - This follows the same structure as Django's `Messages <https://docs.djangoproject.com/en/5.0/ref/contrib/messages/#displaying-messages>`_

.. tip::

    The same template can be used for Django's messages framework and for :code:`hx-requests` (:code:`hx-swap-oob` is required)

Add A Div to the Base Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is where the messages will be rendered. Htmx's :code:`hx-swap-oob` is leveraged to swap in the messages. This ensures that messages can be swapped in with other Html snippets.

.. code-block:: html

    <div id="hx_messages" hx-swap-oob='true'></div>

Setting a Message
~~~~~~~~~~~~~~~~~

You can set a message anywhere within an :code:`HxRequest` the same way you would set a message in Django.

.. code-block:: python

    from django.contrib import messages

    def form_valid(self, **kwargs):
        self.form.save()

        # Set a message
        messages.success(self.request, "Form saved successfully")

    def form_invalid(self, **kwargs):
        # Set a message
        messages.error(self.request, "Form is invalid")

:code:`form_valid` and :code:`form_invalid` do not need to return anything. When they
return :code:`None` the response is built for you. Return an :code:`HttpResponse` only
if you need to short-circuit with custom output.

Disabling Messages
~~~~~~~~~~~~~~~~~~

If :code:`HX_REQUESTS_USE_HX_MESSAGES`  is set to True, there are some default messages set in some of the :code:`HxRequests`.
To disable messages on any :code:`HxRequest` set :code:`show_messages` to False

.. code-block:: python

    class MyHxRequest(BaseHxRequest):
        ...
        show_messages = False

On a :code:`FormHxRequest`, an error message is set by default when the form is invalid.
If the form already renders inline field errors this banner can be redundant. Set
:code:`show_form_invalid_message` to False to suppress it without overriding :code:`form_invalid`.

.. code-block:: python

    class MyHxRequest(FormHxRequest):
        ...
        show_form_invalid_message = False

Tip
~~~

.. tip::

    Toasts are an effective template for asynchronous messages because the page doesn't reload.
    While a user might miss a message banner displayed at the top of the page, a toast fixed to the top-right corner will always be visible.
