Modals
======

| Modals are a very useful component when designing web pages. :code:`hx-requests` has a built in modal to reduce boilerplate code.
| To use the build in modal functionality, you need to define a modal tempalte and set :code:`HX_REQUESTS_MODAL_TEMPLATE` in settings to the path of the template.

Using Modals
------------

.. code-block:: python

    class ModalExample(HXModal):
        name = "modal_example"
        body_template = "modal_body.html"

Notes:
    - :code:`body_template` is used with modals instead of :code:`GET_template` since the :code:`GET_template` is acutally the the entire modal
    - HxModal's return the entire modal not just the body template

.. code-block:: html+django

    <button {% hx_get 'modal_example' %}
            hx-trigger="click"
            hx-target="#hx_modal_container"
            >
            Open Modal
    </button>

Notes:
    - The :code:`hx-target` is the id of the div where the modal will be rendered. Makes sense to put an empty div with the id :code:`hx_modal_container` in the base template of your project.

Defining a Modal Template
-------------------------

To customize a modal, there are a few steps that need to be followed.

#. Override :code:`HX_REQUESTS_MODAL_TEMPLATE` in settings and set it to the path of the modal template.
#. Set the id of you modal to :code:`hx_modal_body` or set :code:`HX_REQUESTS_MODAL_BODY_ID` (a :code:`css` id for the modal body) in settings.
#. Use an include for the body and add the title and modal_size_classes to the template. See the example below.
#. Set a way for the modal to open when the modal template is rendered. See the modal example below.
#. Set a way for the modal to close using the :code:`closeHxModal` event. See the modal example below
#. Set a div with the id :code:`hx_modal_container` in the body of the page, this is where the modal will be rendered (the :code:`hx-target` of the request)

.. tip::

    Put :code:`<div id="hx_modal_container"></div>` in the base template of your project.

Custom Modal Example
~~~~~~~~~~~~~~~~~~~~

.. code-block:: html+django

    <div class="modal fade"
        {% comment %} Using Alpine.js for close, but vanilla JS can be used as well to do this {% endcomment %}
        x-on:close-hx-modal.camel="$('#hx_modal').modal('hide')"
        id="hx_modal"
        tabindex="-1"
        role="dialog"
        aria-hidden="true"
        style="display:block">
        {% comment %} Modal size classes {% endcomment %}
        <div role="document" class="modal-dialog {{ modal_size_classes }}">
            <div class="modal-content">
                <div class="modal-header">
                    {% comment %} Title {% endcomment %}
                    <h5 id="hx-modal-title" class="modal-title">{{ title|default_if_none:""|safe }}</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                {% comment %} Modal body id {% endcomment %}
                <div class="modal-body" id="hx_modal_body" >
                    {% comment %} How to include the body {% endcomment %}
                    <p >{% include body %}</p>
                </div>
            </div>
        </div>
    </div>
    {% comment %} Opens the modal when this template is rendered {% endcomment %}
    <script>$('#hx_modal').modal();</script>


.. note::

    - `Alpine.js <https://alpinejs.dev/>`_ works very nicely with Htmx


Form Modals
-----------

:code:`hx-requests` has a built in form modal, :ref:`HXFormModal`. It takes care of the boilerplate needed to put a form in a modal.
Additionally, it has features like keeping the modal open when the form in invalid so that the errors are displayed to the user.

The page HTML

.. code-block:: html

    <button {% hx_get 'edit_user_modal' object=request.user %}
            hx-trigger="click"
            hx-target="#hx_modal_container"
            >
            Open Modal
    </button>

Notes:
    - This is a button for triggering a modal
    - The object is passed in here becasue it is the model instance of the model form and it's the instance that's used for initializing the form
    - The :code:`hx-target` is the id of the div where the modal will be rendered. Makes sense to put an empty div with the id :code:`hx_modal_container` in the base template of your project.

.. code-block:: python

    class EditUserModal(HXFormModal):
        name = "edit_user_modal"
        form_class = UserInfoForm
        body_template = 'form.html' # Used as the body of the modal
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
    - The object is passed in here becasue it is the model instance of the model form and it's the instance getting updated by the form
