Quickstart
==========

The idea of hx-requests is that :code:`HXRequests` absorb all htmx requests.
Define an :code:`HXRequest` (we'll get into how to do that in just a sec) and
observe the magic of :code:`hx-requests`.

- No need to define extra urls
- No need to add anything extra in the view
- Reusable :code:`HXRequests` across views

Setting up a GET Request (hx-get)
---------------------------------

The View
~~~~~~~~

The view requires :code:`HtmxViewMixin`

.. code-block:: python

    from hx_requests.views import HtmxViewMixin

    class MyView(HtmxViewMixin):
        pass

The HTML markup
~~~~~~~~~~~~~~~


.. code-block:: html

    {% load hx_tags %}
    <div id="user_info_target"></div>
    <button {% render_hx 'get_user_info' 'get' %}
            hx-target="#user_info_target"
            type="button">
        Click Me
    </button>

- The 'get' in the :code:`render_hx` template tag signifies that it's an :code:`hx-get`
- The goal of this :code:`hx-get` is to render a user info card into the empty div.
- The :code:`render_hx` template tag will be discussed in depth later.


Create the HXRequest
~~~~~~~~~~~~~~~~~~~~

Create an :code:`hx_requests.py` file

.. warning::

    All :code:`HXRequests` must be defined inside an :code:`hx_requests.py` file, and the :code:`hx_requests.py`
    files must live inside an app that's included in Django's :code:`INSTALLED_APPS`.

| Create the HXRequest.
| The :code:`hx-get` will get directed to this :code:`HXRequest`.

.. code-block:: python

    from hx_requests.hx_requests import HXRequestGET

    class GetUserInfo(HXRequestGET):
        name = "get_user_info"
        GET_template = "user_info_card.html"

:code:`GetUserInfo` will return the HTML from the :code:`GET_template` (:code:`user_info_card.html`)

.. code-block:: html

    <div>
        <p>Username:{{request.user.username}}</p>
        <p>Email:{{request.user.email}}</p>
    </div>

Summary
~~~~~~~

| Htmx requests are routed to the :code:`HXRequest` that matches the name (1st argument) passed into the :code:`render_hx` template tag. In this example 'get_user_info'. That's how the :code:`hx-get` is routed to :code:`GetUserInfo`.
|
| The request returns the html of the :code:`GET_template`.

.. note::

    The :code:`GET_template` has access to all of the context that is in the view.



Setting up a POST Request (hx-post)
---------------------------------

Very similar to the :code:`GET` request above.

.. note::

    Working with a form? See :ref:`Using Forms`

The View
~~~~~~~~

The view requires :code:`HtmxViewMixin`

.. code-block:: python

    from hx_requests.views import HtmxViewMixin

    class MyView(HtmxViewMixin):
        pass

The HTML markup
~~~~~~~~~~~~~~~


.. code-block:: html

    {% load hx_tags %}
    <div id="email_display">{{request.user.email}}</div>
    <input type="text" name="email" id='email_input'/>
    <button {% render_hx 'change_email' 'post' %}
            hx-target="#email_display"
            hx-include="#email_input"
            type="button">
        Save
    </button>

- The 'post' in the :code:`render_hx` template tag signifies that it's an :code:`hx-post`
- The goal of this :code:`hx-post` is to change the signed in user's email to the value of the input and display the email in the div.
- The :code:`render_hx` template tag will be discussed in depth later.


Create the HXRequest
~~~~~~~~~~~~~~~~~~~~

Create an :code:`hx_requests.py` file

.. warning::

    All :code:`HXRequests` must be defined inside an :code:`hx_requests.py` file, and the :code:`hx_requests.py`
    files must live inside an app that's included in Django's :code:`INSTALLED_APPS`.

| Create the HXRequest.
| The :code:`hx-post` will get directed to this :code:`HXRequest`.

.. code-block:: python

    from hx_requests.hx_requests import HXRequestPOST

    class ChangeEmail(HXRequestPOST):
        name = "change_email"
        POST_template = "email.html"

        def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user = request.user
            user.email = request.POST.get("email")
            user.save()
            return super().post(request, *args, **kwargs)

:code:`ChangeEmail` will return the HTML from the :code:`POST_template` (:code:`email.html`)

.. code-block:: html

    <span>{{request.user.email}}</span>

Summary
~~~~~~~

| Htmx requests are routed to the :code:`HXRequest` that matches the name (1st argument) passed into the :code:`render_hx` template tag. In this example 'change_email'. That's how the :code:`hx-post` is routed to :code:`ChangeEmail`.
|
| The request returns the html of the :code:`POST_template`.

.. note::

    The :code:`POST_template` has access to all of the context that is in the view.
