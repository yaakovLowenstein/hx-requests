How To delete
-------------

This how-to demonstrates how to delete an object using :code:`hx-requests`. It follows the same structure as
Django's `DeleteView <https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/#deleteview>`_.


.. code-block:: html+django

    {% load hx_tags %}
    <div id="object_target">{{object}}</div>
    <button {% hx_post 'delete_object' object=object %}
            hx-swap="outerHTML"
            hx-target="#object_target"
            type="button">
        Delete
    </button>

Notes
    - The object passed in to the :code:`hx_post` is a Django model instance and will be deleted

.. code-block:: python

    class Delete(DeleteHxRequest):
        name = "delete_object"
        return_empty = True

Notes
    - The :code:`return_empty` attribute ensures that an empty response is returned after deletion which effectively removes the :code:`#object_target` div from the DOM.
    - If you prefer to update the DOM instead of removing the element, you can use :code:`POST_template`.
