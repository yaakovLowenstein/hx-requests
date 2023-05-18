Modals
======

| Modals are a very useful component when designing web pages. :code:`hx-requests` has a built in modal to reduce boilerplate code.
| :code:`hx-requests` comes with two flavors of a modal. `A custom Htmx modal <https://htmx.org/examples/modal-custom/>`_  and a `bootstrap modal <https://htmx.org/examples/modal-bootstrap/>`_ . You can also override these and use your own modal.

| To select which of the two modals to use, set :code:`HX_REQUSTS_MODAL_TEMPLATE` to 'hx_requests/modal.html' (this is the default), or to 'hx_requests/bootstrap_modal.html' or :ref:`override the modal <Overriding the built-in Modal>`

| The default modal and the bootstrap modal differ in how to use them and override them. Both are documented below.

.. warning::

    Hyperscript is used for both modals. To use either of them you will need to load Hyperscript (see :ref:`Installation`)

Using a Modal
-------------

Default Modal
~~~~~~~~~~~~~

HTML to load the modal

.. code-block:: html

    {% load hx_tags %}
    <button
        {% hx_get 'hx_modal' body='modal_body.html' title='My Modal' %}
        hx-target="body"
        hx-swap="beforeend"
    >
        Open Modal
    </buton>

Notes:
    - The body and title of the modal are passed in as kwargs. The body could be an html file OR just raw html (i.e. :code:`body=<h1>Hello</h1>`)

.. note::

    Any context needed for the modal body can be passed into the template tag as kwargs and can be accessed in the body template as :code:`hx_kwargs.{context_var_name}`

Bootstrap Modal
~~~~~~~~~~~~~~~

1. The page using the modal needs to define a container for the modal to be rendered in.

.. code-block:: html

    <div id="hx_modal_container"></div>

If you change the :code:`id` of the modal container, you need to set :code:`HX_REQUSTS_MODAL_CONTAINER_ID` in settings to that :code:`id`.


.. tip::

    Put the :code:`div` in your base html file so it can be used on any page easily

2. HTML to load the modal

.. code-block:: html

    {% load hx_tags %}
    <button
        {% hx_get 'hx_modal' body='modal_body.html' title='My Modal' %}
        hx-target="#hx_modal_container"
        _="on htmx:afterOnLoad wait 10ms then add .show to #hx_modal then add .show to #hx_modal_backdrop">
        Open Modal
    </buton>

Notes:
    - The body and title of the modal are passed in as kwargs. The body could be an html file OR just raw html (i.e. :code:`body=<h1>Hello</h1>`)
    - Hyperscript is used here to load the modal, it can be done using JavaScript, but it's recommended to use Hyperscript
    - :code:`hx_modal_container`, :code:`hx_modal_backdrop`, and :code:`hx_modal` are the ids when using the modal provided by :code:`hx-requests`. If you are not using the default modal and you change the ids, these values would need to reflect that.

.. note::

    Any context needed for the modal body can be passed into the template tag as kwargs and can be accessed in the body template as :code:`hx_kwargs.{context_var_name}`


Overriding the built-in Modal
-----------------------------

To use a custom modal instead of the built-in one, there are a few steps that need to be followed.

Default Modal
~~~~~~~~~~~~~

#. Override :code:`HX_REQUSTS_MODAL_TEMPLATE` in settings and set it to the template of your modal.
#. Make sure the hyperscript for closing the modal is set correctly.

    - The modal's close button has hyperscript that triggers the modal to close
    - For :ref:`Form Modals` on submit the modal only closes when the :code:`modalFormValid` event is triggered. When a form is invalid the modal stays open so the user can see the form errors. There is hyperscript that triggers the modal to close on :code:`modalFormValid`.

*modal.html*

.. code-block:: html

    {% load static %}
    <div id="modal"
        _="on closeModal add .closing then wait for animationend then remove me"
        _="on modalFormValid add .closing then wait for animationend then remove me"
    >
        <div class="modal-underlay" _="on click trigger closeModal"></div>
        <div class="modal-content">
            <h1>{{title}}</h1>
            {{body}}
            <br>
            <br>
            <button _="on click trigger closeModal">Close</button>
        </div>
    </div>
    <link href="{% static 'hx_requests/css/modal.css' %}" rel="stylesheet">



Bootstrap Modal
~~~~~~~~~~~~~~~

#. Override :code:`HX_REQUSTS_MODAL_TEMPLATE` in settings and set it to the template of your modal.
#. Set HX_REQUSTS_MODAL_BODY_SELECTOR (a :code:`css` selector for the modal body container) in settings.
#. Set your own 'close modal' function. See below for built in modal html and JavaScript that handles the closing of the modal.

    - The modal's close button has onclick set to :code:`closeHXModal()`
    - For :ref:`Form Modals` on submit the modal only closes when the :code:`modalFormValid` event is triggered. When a form is invalid the modal stays open so the user can see the form errors. By default the event handler for closing the modal on :code:`modalFormValid` is set for the built-in modal. When overriding the modal, make sure to add that event handler if you want the modal to stay open when the form is invalid.

*bootstrap_modal.html*

.. code-block:: html

    <div id="hx_modal_backdrop"
        class="modal-backdrop fade show"
        style="display:block"></div>
    <div id="hx_modal"
        class="modal fade show"
        tabindex="-1"
        style="display:block">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{{ title }}</h5>
                </div>
                <div class="modal-body">
                    <p>{{ body }}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeHXModal()">Close</button>
                </div>
            </div>
        </div>
    </div>
    <script>
        function closeHXModal() {
            const container = document.getElementById('{{modal_container_id}}')
            const backdrop = document.getElementById("hx_modal_backdrop")
            const modal = document.getElementById("hx_modal")

            modal.classList.remove("show")
            backdrop.classList.remove("show")

            setTimeout(function () {
                container.innerHTML = ''
            }, 200)
    }
        document.addEventListener('modalFormValid',closeHXModal)
    </script>

Form Modals
-----------

:code:`hx-requests` has a built in form modal, :ref:`HXFormModal`

The page HTML

.. code-block:: html

    <button {% hx_get 'edit_user_modal' object=request.user %}
            hx-trigger="click"
            hx-target="#hx_modal_container"
            _="on htmx:afterOnLoad wait 10ms then add .show to #hx_modal then add .show to #hx_modal_backdrop">
            Open Modal
    </button>

Notes:
    - Hyperscript is used here to load the modal, it can be done using JavaScript, but it's recommended to use Hyperscript
    - :code:`hx_modal_container`, :code:`hx_modal_backdrop`, and :code:`hx_modal` are the ids when using the modal provided by :code:`hx-requests`. If you are not using the default modal and you change the ids, these values would need to reflect that.

.. code-block:: python

    class EditUserModal(HXFormModal):
        name = "edit_user_modal"
        form_class = UserInfoForm
        GET_template = 'form.html' # Used as the body of the modal
        POST_template = '...' # This works the same as any POST_template

Notes:
    - When the form is valid the modal will close
    - When the form is invalid the modal will stay open and contain the validation errors

*form.html*

.. code-block:: html

    {% load hx_tags %}
    <div>
        {{ # Render fom fields }}
        <button hx-include="closest div"
                {% hx_post 'edit_user_modal' hx_object %}>
            Save
        </button>
    </div>

Notes:
    - The object is in this context as :code:`hx_object` because :code:`hx_object_name` is not set in the :code:`HXRequest` above
