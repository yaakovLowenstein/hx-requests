Quickstart
==========

The idea of hx-requests is that :code:`HXRequests` absorb all htmx requests.
Define an :code:`HXRequest` (we'll get into how to do that in just a sec) and
observe the magic of :code:`hx-requests`.

- No need to define extra urls to handle these requests
- No need to add anything extra in views
- Reusable :code:`HXRequests` across views
- Built in :code:`HXReuqests` to reduce boilerplate code (Forms, Deleting, Modals)

Making a GET Request (hx-get)
---------------------------------

The View
~~~~~~~~

The view requires :code:`HtmxViewMixin`

.. code-block:: python

    from hx_requests.views import HtmxViewMixin

    class MyView(HtmxViewMixin):
        pass

The HTML
~~~~~~~~


.. code-block:: html

    {% load hx_tags %}
    <div id="user_info_target"></div>
    <button {% hx_get 'get_user_info' %}
            hx-target="#user_info_target"
            type="button">
        Click Me
    </button>

Notes:
    - Using the :ref:`hx_get <hx_get>` template tag signifies that it's an :code:`hx-get`
    - The goal of this :code:`hx-get` is to render a user info card into the empty div


Create the HXRequest
~~~~~~~~~~~~~~~~~~~~

Create an :code:`hx_requests.py` file

.. warning::

    All :code:`HXRequests` must be defined inside an :code:`hx_requests.py` file, and the :code:`hx_requests.py`
    files must live inside an app that's included in Django's :code:`INSTALLED_APPS`.

| Create the HXRequest.
| The :code:`hx-get` will get directed to this :code:`HXRequest`.

.. code-block:: python

    from hx_requests.hx_requests import BaseHXRequest

    class GetUserInfo(BaseHXRequest):
        name = "get_user_info"
        GET_template = "user_info_card.html"

Notes:
    - :code:`GetUserInfo` will return the HTML from the :code:`GET_template` (:code:`user_info_card.html`)

*user_info_card.html*

.. code-block:: html

    <div>
        <p>Username:{{request.user.username}}</p>
        <p>Email:{{request.user.email}}</p>
    </div>

Summary
~~~~~~~

| Htmx requests are routed to the :code:`HXRequest` that matches the name (1st argument) passed into the :code:`hx_get` template tag. In this example 'get_user_info'. That's how the :code:`hx-get` is routed to :code:`GetUserInfo`.
|
| The request returns the html of the :code:`GET_template`.

.. note::

    The :code:`GET_template` has access to all of the context that is in the view.



Making a POST Request (hx-post)
---------------------------------

Alomost exactly the same as the :code:`GET` request above.

.. note::

    Working with a form? See :ref:`Using Forms`

The View
~~~~~~~~

The view requires :code:`HtmxViewMixin`

.. code-block:: python

    from hx_requests.views import HtmxViewMixin

    class MyView(HtmxViewMixin):
        pass

The HTML
~~~~~~~~

.. code-block:: html

    {% load hx_tags %}
    <div id="email_display">{{request.user.email}}</div>
    <input type="text" name="email" id='email_input'/>
    <button {% hx_post 'change_email' %}
            hx-target="#email_display"
            hx-include="#email_input"
            type="button">
        Save
    </button>

Notes:
    - Using the :ref:`hx_post <hx_post>` template tag signifies that it's an :code:`hx-post`
    - The goal of this :code:`hx-post` is to change the signed in user's email to the value of the input and display the email in the div.


Create the HXRequest
~~~~~~~~~~~~~~~~~~~~

Create an :code:`hx_requests.py` file

.. warning::

    All :code:`HXRequests` must be defined inside an :code:`hx_requests.py` file, and the :code:`hx_requests.py`
    files must live inside an app that's included in Django's :code:`INSTALLED_APPS`.

| Create the HXRequest.
| The :code:`hx-post` will get directed to this :code:`HXRequest`.

.. code-block:: python

    from hx_requests.hx_requests import BaseHXRequest

    class ChangeEmail(BaseHXRequest):
        name = "change_email"
        POST_template = "email.html"

        def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user = request.user
            user.email = request.POST.get("email")
            user.save()
            return super().post(request, *args, **kwargs)

Notes:
    - :code:`ChangeEmail` will return the HTML from the :code:`POST_template` (:code:`email.html`)

*email.html*

.. code-block:: html

    <span>{{request.user.email}}</span>

Summary
~~~~~~~

| Htmx requests are routed to the :code:`HXRequest` that matches the name (1st argument) passed into the :code:`hx_post` template tag. In this example 'change_email'. That's how the :code:`hx-post` is routed to :code:`ChangeEmail`.
|
| The request returns the html of the :code:`POST_template`.

.. note::

    The :code:`POST_template` has access to all of the context that is in the view.

Rendering Blocks
----------------

Thanks to `django-render-block <https://github.com/clokep/django-render-block>`_ there is a way to reduce using :code:`includes`. Instead of needing to
split out templates into includes to use them for partials, you can specify a block from the template to use and that block will be rendered by the
:code:`HXRequest`.

Example
~~~~~~~

*HXRequest*

.. code-block:: python

    class UpdateUser(FormHXRequest):
        name = "update_user"
        form_class = UpdateUserForm # Form with a username field
        GET_template = "user_form.html"
        POST_template = "big_template.html"
        POST_block = "table" # This is the block that will be rendered on POST

*big_template.html*

.. code-block:: html

    {% load hx_tags %}
    ....

    {% block table %}
        <table>
            <th>Username</th>
            <tr>
                <td>{{ request.user.username }}</td>
                <td >
                    <button{% hx_get 'update_user' object=request.user %}
                    hx-target="closest tr">Edit user</button>
                </td>
            </tr>
        </table>
    {% endblock table %}

    ...

*user_form.html*

.. code-block:: html

    {% load hx_tags %}
    <td colspan="2">
        <form action="">
            {{ form.username }}
            <button {% hx_post 'update_user' object=hx_object %}
                    hx-target="closest table">Save</button>
        </form>
    </td>

Notes:

    - This is a :code:`FormHXRequest` that replaces a row of the table with a form to edit the contents of the row (i.e. username)
    - On post the :code:`HXRequest` will return just the table because the :code:`POST_block` was set to table and in :code:`big_template.html` that
      block contains the table. This is helpful because the only thing on the page that should be updated on post is the table.
    - If not for :code:`django-render-block` the table would have to be a separate include so that you could specifiy the table template as the :code:`POST_template`
