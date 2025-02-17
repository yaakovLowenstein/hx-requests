How To Add Context To HX Requests
---------------------------------

There are times when you need to pass additional context to the template that is being swapped in, beyond the context that is provided by the view.
This can be done in multiple ways, depending on your needs.

Adding Context
~~~~~~~~~~~~~~

Overriding the :code:`get_context_data` method in the :code:`HxRequest` is the easiest way to add context to the template that is being swapped in.

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class MyHxRequest(BaseHxRequest):
        ....

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["important_var"] = "I am important"
            return context

This context will get passed to both the :code:`GET_template` and the :code:`POST_template`.


Adding Context Only On GET
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you only want to add context on the :code:`GET_template`, you can override :code:`get_context_on_GET`.
This is useful when fetching the context is an expensive operation and is not needed in the :code:`POST_template`.

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class MyHxRequest(BaseHxRequest):
        ....

        def get_context_on_GET(self, **kwargs):
            context = super().get_context_on_GET(**kwargs)
            context["important_var"] = "I am important"
            return context

Adding Context Only On POST
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handling context on POST is slightly different because context often needs to be updated based on the form submission.
For example, if a user's email is updated in a form, the email displayed in the template should also reflect this change.
By default, :code:`hx_object` is refreshed, so if the user is the :code:`hx_object`, their updated email will be reflected.
However, there are cases where you need to update additional context as well.

There are 2 ways refresh the context on POST:

#. Override :code:`get_post_context_data` to add context only on POST.

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class MyHxRequest(BaseHxRequest):
        ....

        def get_context_on_POST(self, **kwargs):
            context = super().get_context_on_POST(**kwargs)
            context["updated_context"] = "This was updated and now needs to be updated in context"
            return context


#. Set :code:`refresh_views_context_on_POST` to :code:`True` in the :code:`HxRequest`. This will refresh all the context from the view with updated data.

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class MyHxRequest(BaseHxRequest):
        ....
        refresh_views_context_on_POST = True
