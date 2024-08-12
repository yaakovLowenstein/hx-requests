Deleting
========

:code:`hx-requests` has a build in **Delete** :code:`HXRequest` which makes it really easy to asyncronously delete something.

.. code-block:: html

     <button {% hx_post 'delete_user' object=user  %}
            hx-trigger='confirmed'
            _="on click call Swal.fire({ text:'Are you sure you want to delete this user?',showCancelButton: true,confirmButtonText: 'Yes'  }) if result.isConfirmed trigger confirmed">
        Delete
    </button>

Notes:
    - The delete button is using Hyperscript with `Sweet Alert <https://sweetalert2.github.io/>`_ to ask the user for confirmation before deleting
    - User is an object in the context coming from the view


.. code-block:: python

    class DeleteUser(DeleteHXRequest):
        name = "delete_user"
        POST_template = "..." # html returned on post (used to update DOM)

        def delete(self, **kwargs) -> str:
            # This is the default delete

            self.hx_object.delete()
            return self.get_response(**kwargs)

Notes:
    - Very simple way to delete asyncronously.
    - Use the :code:`POST_template` to update the DOM after the deletion
    - If using :ref:`Messages`, by default the message is set to '{model name} deleted successfully`.
