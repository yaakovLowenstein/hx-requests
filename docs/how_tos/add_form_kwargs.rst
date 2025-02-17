How To Add Form Kwargs
----------------------

In a Django view, form kwargs are added by overriding the :code:`get_form_kwargs` method.
Similarly, :code:`HxRequest` provides a :code:`get_form_kwargs` method that allows you to pass additional information to the form that is not part of the request.

Adding Form Kwargs
~~~~~~~~~~~~~~~~~~

Override :code:`get_form_kwargs` in your `HxRequest` to add custom kwargs to the form.


.. code-block:: python

    from hx_requests.hx_requests import FormHxRequest

    class MyHxRequest(FormHxRequest):
        # Set attributes

        def get_form_kwargs(self,**kwargs):
            kwargs = super().get_form_kwargs(**kwargs)

            # Add the user to the form
            kwargs['user'] = self.request.user
            return kwargs

        def get_initial(**kwargs):
            initial = super().get_initial(**kwargs)

            # Set the initial value of 'created_by' field
            initial['created_by'] = self.request.user
            return initial

Adding An Instance To A Model Form
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to pass an instance to a model form, you can do so directly from the template tag.
When using :code:`hx_get` or :code:`hx_post`, pass the instance using the :code:`object` parameter.
If the form is a model form, the `object` will be passed as the instance.

.. code-block:: html+django

    <button {% hx_get 'my_hx_request' object=my_instance %}></button>
    <button {% hx_post 'my_hx_request' object=my_instance %}></button>

Adding Initial Form Values From The Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To automatically populate initial values from kwargs passed in the template tag, set :code:`set_initial_from_kwargs = True` on the :code:`HxRequest`.
If a kwarg passed into the template tag matches a form field name, it will be set as the initial value for that field.

.. code-block:: html+django

    <button {% hx_get 'my_hx_request' created_by=user %}></button>
