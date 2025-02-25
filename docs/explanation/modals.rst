Modals
------

Modals are a common UI pattern, and this document explains how :code:`hx-requests`
makes them easier to use.

Why Does :code:`hx-requests` Have A Modal Class?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The primary reason for having a built-in modal class is to reduce boilerplate code.
Instead of manually handling modal rendering, :code:`ModalHxRequest` allows you to
define a template, and it will automatically render it within the modal body.
If you were to do this manually, you would need to write additional code to
handle rendering, swapping content, and managing the modal state.

Another key advantage of :code:`ModalHxRequest` is that it always returns the full modal.
This means that the modal's title and size can be updated dynamically.
If only the modal body were returned, you would have no control over elements
like the title or size.

The biggest benefit of using the built-in modals is how they handle forms.
When a form is submitted, :code:`ModalHxRequest` simplifies handling validation.
If the form is invalid, it automatically re-renders the modal with the form
and validation errors. If the form is valid, it submits the form and returns
a trigger to close the modal.

.. note::
    The :code:`GET_template` is rendered inside the modal body,
    but the response includes the entire modal template.

.. note::
    See :ref:`How To Use Modals` for details on using modals.
