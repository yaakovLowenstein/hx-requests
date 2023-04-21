Deleting
========

:code:`hx-requests` has a build in **Delete** :code:`HXRequest` which makes it really easy to asyncronously delete something.

.. code-block:: html

     <button {% render_hx 'delete_user' 'post' object=user  %}
            hx-trigger='confirmed'
            _="on click call Swal.fire({ text:'Are you sure you want to delete this dish?',showCancelButton: true,confirmButtonText: 'Yes'  }) if result.isConfirmed trigger confirmed">
        Delete
    </button>

Notes:
    - The delete button is using Hyperscript with `Sweet Alert <https://sweetalert2.github.io/>`_ to ask the user for confirmation before deleting
    - User is an object in the context


.. code-block:: python

    class DeleteUser(DeleteHXRequest):
        name = "delete_user"
        POST_template = "..." # html returned on post (used to update DOM)

        def handle_delete(self, **kwargs) -> str:
            # This is the default handle_delete

            self.hx_object.delete()
            return self.get_POST_response(**kwargs)

Notes:
    - Very simple way to delete asyncronously.
    - If using :ref:`Messages`, by default the message is set to '{...} deleted successfully`.
