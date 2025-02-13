How To Use Modals
-----------------


This how-to demonstrates how to use the built-in modal functionality in hx-requests to load content asynchronously into the modal.
The built-in modal reduces boilerplate code and simplifies common tasks like handling forms, validation, and dynamic content
updates—without full page reloads.



Define a Modal Template
~~~~~~~~~~~~~~~~~~~~~~~

To use the built in modal functionality, you need to define a modal template and set :code:`HX_REQUESTS_MODAL_TEMPLATE` in settings to the path of the template.

.. code-block:: html+django

    <div class="modal fade"
         id="hx_modal"
         tabindex="-1"
         role="dialog"
         aria-hidden="true"
         style="display:block"
         @close-hx-modal.camel="bootstrap.Modal.getOrCreateInstance(document.getElementById('hx_modal')).hide()"
        >
        <div role="document" class="modal-dialog {{ modal_size_classes }}">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{{ title|default_if_none:""|safe }}</h5>
                    <button type="button"
                            class="btn-close"
                            data-bs-dismiss="modal"
                            aria-label="Close"></button>
                </div>
                <div class="modal-body" id="hx_modal_body">
                    <p>{{ body }}</p>
                </div>
            </div>
        </div>
    </div>
    <script>
        bootstrap.Modal.getOrCreateInstance(document.getElementById('hx_modal')).show();
    </script>



Notes:
    - This is using a bootstrap modal, but any modal can be used.
    - The title, modal_size_classes and body are passed in as context from the :code:`HxRequest` that is being rendered.
    - The :code:`closeHxModal` (:code:`close-hx-modal` in the Html above) event is used to close the modal - this is triggered by the :code:`HxModalHxRequest` (the code above is using `Alpine.js <https://alpinejs.dev/>`_ to close the modal).


Add Settings to settings.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| Define :code:`HX_REQUESTS_MODAL_TEMPLATE` in settings to the path of the modal template.
| Define :code:`HX_REQUESTS_MODAL_BODY_ID` in settings to the id of the modal body (default is :code:`hx_modal_body`)

.. code-block:: python

    HX_REQUESTS_MODAL_TEMPLATE = "path/to/your/modal_template.html"
    HX_REQUESTS_MODAL_BODY_ID = "hx_modal_body" # Default is hx_modal_body

Add A Div to the Base Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is where the modal will be rendered.

.. code-block:: html+django

    <div id="hx_modal_container"></div>

Notes:
    - The id of the div can be anything, this is just the :code:`hx-target` of the request.


Create a ModalHxRequest
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class ModalExample(ModalHxRequest):
        name = "modal_example"
        GET_template = "modal_body.html" # A template to be used as the body of the modal


Trigger the Modal
~~~~~~~~~~~~~~~~~

.. code-block:: html+django

    <button {% hx_get "modal_example" %} hx-target="#hx_modal_container">Open Modal</button>


.. note::

        This is using a bootstrap 5 modal and therefore needs bootstrap 5 to be included in the project.


Using Forms in Modals
~~~~~~~~~~~~~~~~~~~~~

To use a form in a modal, you can use the :code:`FormModalHxRequest` class. This class is a subclass of :code:`ModalHxRequest`
and has the same functionality as the :ref:`FormHxRequest<Form Tutorial>`.


.. code-block:: python

    class UserFormModal(FormModalHxRequest):
        name = "user_form_modal"
        GET_template = "user_form.html" # This will be rendered as the body of the modal
        POST_template = "user_display.html"
        form_class = UserForm

Notes:
    - This is all that is needed to use a form in a modal.
    - The form will be validated and the form will be re-rendered in the modal if there are errors.
    - If the form is valid, the form will be submitted and the modal will close.


Manually Triggering The Modal To Close
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to manually close the modal, you can return the :code:`closeHxModal` trigger from the :code:`get_triggers` method.

.. code-block:: python

    class UserFormModal(FormModalHxRequest):
        name = "user_form_modal"
        GET_template = "user_form.html" # This will be rendered as the body of the modal
        POST_template = "user_display.html"
        form_class = UserForm

        def get_triggers(self, **kwargs) -> list:
            triggers = super().get_triggers(**kwargs)
            if some_condition:
                triggers.append("closeHxModal")
            return triggers
