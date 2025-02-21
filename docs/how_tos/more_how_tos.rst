More How Tos
------------


What Is no_swap For?
~~~~~~~~~~~~~~~~~~~~

When :code:`no_swap` is set, no HTML is swapped into the DOM. A common use case is a button that submits a POST request.
If the form is valid, you may want to swap in updated content to reflect the changes.
However, if the form is invalid, you may only want to display error messages without modifying the page structure.

.. code-block:: python

    class MyHxRequest(FormHxRequest):
        ...

        def form_invalid(self,kwargs):
            self.no_swap = True
            self.messages.error("Sorry there was an error")
            return super().form_invalid(kwargs)


How Do I Add Form Errors To The Error Message?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting :code:`add_form_errors_to_error_message` to True will add a Django form's errors into the error message.

.. code-block:: python

    class MyHxRequest(FormHxRequest):
        ...
        add_form_errors_to_error_message = True
