Messages
========

:code:`hx-requests` leverages Django's messaging framework and turns them into asynchronous messages. It's very convenient for notifying the user when the form is valid/ invalid.

Setup
-----

1. In :code:`settings.py` set :code:`HX_REQUESTS_USE_HX_MESSAGES`: bool that defines whether or not :code:`hx-messages` should be used (default is False)
2. In :code:`settings.py` set :code:`HX_REQUESTS_HX_MESSAGES_TEMPLATE`: path to a template to be used for the messages. The context in the template has access to :code:`messages`.

*example-message-template.html*

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
   - The same template can be used for Django's messages framework and for :code:`hx-requests`

3. An empty div (or any Html element) with the same id as the one in the messages template needs to be put in your base Html file. (:code:`hx-messages` leverages Htmx's :code:`hx-swap-oob`)

.. code-block:: html

    <div id="hx_messages" hx-swap-oob='true'></div>

Setting a Message
-----------------

You can set a message anywhere within an :code:`HxRequest` the same way you would set a message in Django.

.. code-block:: python

    def form_valid(self, **kwargs) -> str:
        self.form.save()

        # Set a message
        messages.success(self.request, "Form saved successfully")

        return ...

Disabling Messages
------------------

If :code:`HX_REQUESTS_USE_HX_MESSAGES`  is set to True, there are some default messages set in some of the :code:`HxRequests`.
To disable messages on any :code:`HxRequest` set :code:`show_messages` to False

.. code-block:: python

    class MyHxRequest(BaseHxRequest):
        ...
        show_messages = False

Tip
---

.. tip::

    Toasts are a good template to use for asynchronous messages because the page doesn't reload. A user may not see a message banner that is set on the top of the page, but a toast that is fixed to the top right cornder of the page will always be visible.
