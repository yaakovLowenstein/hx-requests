Rendering Blocks
================

Thanks to `django-render-block <https://github.com/clokep/django-render-block>`_ there is a way to reduce using :code:`includes`. Instead of needing to
split out templates into includes to use them for partials, you can specify a block from the template to use and that block will be rendered by the
:code:`HXRequest`.

Example
-------

Using the example from :ref:`forms <HTML>`, instead of using an :code:`include`, we can replace that with a block

*user_info_page.html* (what it originally was)

.. code-block:: html

    {% load hx_tags %}
    <div id="user_info">
        {% include 'user_info.html' %}
    </div>
    <form method="post">
        <div hx-trigger='load'
            {% hx_get 'user_info_form' object=request.user %}>
        </div>
        <button type="submit"
                hx-target="#user_info"
                {% hx_post 'user_info_form' object=request.user %}>
                Submit
        </button>
    </form>

*user_info_page.html* (modified to use block rendering)

.. code-block:: html

    {% load hx_tags %}
    <div id="user_info">
        {% block user_info %}
            {{ user.email }}
            {{ user.first_name }}
            {{ user.last_name }}
        {% endblock user_info %}
    </div>
    <form method="post">
        <div hx-trigger='load'
            {% hx_get 'user_info_form' object=request.user %}>
        </div>
        <button type="submit"
                hx-target="#user_info"
                {% hx_post 'user_info_form' object=request.user %}>
                Submit
        </button>
    </form>

And the :code:`HXRequest`:

.. code-block:: python

    from hx_requests.hx_requests import FormHXRequest

    class UserInfoHXRequest(FormHXRequest):
        ...
        # Instead of this (which was the include)
        POST_template = 'user_info.html'

        # We can do this
        POST_template = 'user_info_page.html'
        POST_block = 'user_info'



Another Example
---------------


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
        <form method="post">
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
