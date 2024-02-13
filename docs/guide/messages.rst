Messages
========

:code:`hx-requests` has an asyncronous messaging framework, :code:`hx-messages`. It's very convenient for notifiying the user when the form is valid/ invalid.

.. note::

    :code:`hx_message` framework is based on `Django's messages framework <https://docs.djangoproject.com/en/4.2/ref/contrib/messages/>`_
Setup
-----

To use :code:`hx-messages` a few things need to be set...

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

3. An empty div (or any Html element) with the same id as the one in the messages template needs to be put in your base Html file. (:code:`hx-messages` leverages Htmx's :code:`hx-swap-oob`)

.. code-block:: html

    <div id="hx_messages" hx-swap-oob='true'></div>

3. In :code:`settings.py` set :code:`HX_REQUESTS_USE_DJANGO_MESSAGE_TAGS` : bool that defines whether or not :code:`hx_messages` should use Django's message tags. If set to True then there is no need to set :code:`HX_REQUESTS_HX_MESSAGE_TAGS` (default is False)
4. If  :code:`HX_REQUESTS_USE_DJANGO_MESSAGE_TAGS` is False, in :code:`settings.py` set :code:`HX_REQUESTS_HX_MESSAGE_TAGS`: dict just like Django's `message tags <https://docs.djangoproject.com/en/4.2/ref/contrib/messages/#message-tags>`_

.. code-block:: python

    from hx_requests.hx_messages import HXMessageTags

    HX_REQUESTS_HX_MESSAGE_TAGS = {
        HXMessageTags.DEBUG: "alert-info",
        HXMessageTags.INFO: "alert-info",
        HXMessageTags.SUCCESS: "alert-success",
        HXMessageTags.WARNING: "alert-warning",
        HXMessageTags.ERROR: "alert-danger",
    }


Setting a Message
-----------------

You can set a message anywhere within an :code:`HXRequest` by doing the following:

.. code-block:: python

    def form_valid(self, **kwargs) -> str:
        self.form.save()

        # Set a message
        self.messages.success("Form was successfully saved!")

        return ...

Notes:
    - Sucess is the level of the message and is used to retrive the tag from :code:`HX_REQUESTS_HX_MESSAGE_TAGS`
    - can also set :code:`self.messages.error()`, :code:`self.messages.warning()`, :code:`self.messages.info()` and :code:`self.messages.debug()`

Disabling Messages
------------------

If :code:`HX_REQUESTS_USE_HX_MESSAGES`  is set to True, there are some default messages set in some of the :code:`HXRequests`.
To disable messages on any :code:`HXRequest` set :code:`show_messages` to False

.. code-block:: python

    class MyHXRequest(BaseHXRequest):
        ...
        show_messages = False

Tip
---

.. tip::

    Toasts are a good template to use for :code:`hx_messages`. Because the messages are asyncronous and the page doesn't reload, a user may not see a message banner that is set on the top of the page, but a toast that is fixed to the top right cornder of the page will always be visible.
