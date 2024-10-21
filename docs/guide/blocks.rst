Rendering Blocks
================

Thanks to `django-render-block <https://github.com/clokep/django-render-block>`_ there is a way to reduce using :code:`includes`. Instead of needing to
split out templates into includes to use them for partials, you can specify a block from the template to use and that block will be rendered by the
:code:`HXRequest`.

Example
-------

Using the example from :ref:`forms <HTML>`, instead of using an :code:`include`, we can replace that with a block

*user_info_page.html* (what it originally was)

.. code-block:: html+django

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

.. code-block:: html+django

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

.. code-block:: html+django

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

.. code-block:: html+django

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

Formats for Using `POST_block`
------------------------------

The `POST_block` attribute in an `HXRequest` can be used in various formats depending on how you want to render blocks in your templates. Below are the different ways to use it:

1. **Single Block from a Template**
   When you want to render just one specific block from the template on POST:

   .. code-block:: python

       class UpdateUser(FormHXRequest):
           POST_template = "big_template.html"
           POST_block = "table"  # Renders the 'table' block from the template

   In this case, after the form submission (POST), only the content inside the block labeled `table` in `big_template.html` will be rendered.

2. **Multiple Blocks from a Single Template**
   If you need to render multiple blocks from a single template, you can pass a list of blocks:

   .. code-block:: python

       class UpdateUser(FormHXRequest):
           POST_template = "big_template.html"
           POST_block = ["table", "summary"]  # Renders both 'table' and 'summary' blocks

   This allows you to return multiple sections of the page. Both blocks `table` and `summary` from `big_template.html` will be rendered and combined in the response.

3. **Different Blocks from Multiple Templates**
   If you are rendering blocks from different templates, you can use a dictionary to map templates to their respective blocks:

   .. code-block:: python

       class UpdateUser(FormHXRequest):
           POST_template = "additional_template_to_render.html"
           POST_block = {
               "big_template.html": "table",
               "summary_template.html": "summary"
           }

   Here, the `table` block from `big_template.html` and the `summary` block from `summary_template.html` will both be rendered on POST.

4. **No Specific Block (Rendering Entire Template)**
   If you want to render the entire template and not just a block, you can omit the `POST_block` attribute:

   .. code-block:: python

       class UpdateUser(FormHXRequest):
           POST_template = "big_template.html"
           # POST_block is omitted to render the entire template

   This will render the whole `big_template.html` without focusing on any specific block.

These formats provide flexibility in determining how much content should be returned after a POST request, whether it's a single block, multiple blocks, or an entire template.
