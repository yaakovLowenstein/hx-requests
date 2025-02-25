Hx Tags
=======

:code:`hx_get` and :code:`hx_post` are template tags for setting up :code:`HxRequests`.
They function identically, except :code:`hx_get` makes a GET request, while :code:`hx_post` makes a POST request.

Parameters
~~~~~~~~~~
    - :code:`HxRequest` Name (required) – The name of the HxRequest being used.
    - Object (optional) - If provided, this object is associated with the :code:`HxRequest` (similar to Django's `UpdateView <https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/#django.views.generic.edit.UpdateView>`_ )
    - use_full_path (optional) - If set to True, the full path of the :code:`url` is used. See :ref:`How To Add GET Parameters To POST Requests`
    - Keyword Arguments (:code:`kwargs`) - Additional arguments passed into the :code:`HxRequest`. These can be Django :code:`Model` objects because they are serialized.

Behavior
~~~~~~~~
    - If an object is passed in:
        - It is added as :code:`hx_object` inside the HxRequest and accessible as :code:`self.hx_object`.
        - If :code:`hx_object_name` is not set on the :code:`HxRequest`, the object is available in the template as :code:`hx_object`, accessible with :code:`{{ hx_object }}`.
        - If :code:`hx_object_name` is set, the object is available in the template as what :code:`hx_object_name` is set to.

    - Kwargs
        - Accessible in the :code:`HxRequest` through :code:`**kwargs` in each method.
        - Available in the template as context variables, unless :code:`kwargs_as_context = False` is set on the :code:`HxRequest`, in which case they are stored in :code:`hx_kwargs`, accessible as {{ hx_kwargs.key }}.


Example
~~~~~~~

.. code-block:: html+django

    <button {% hx_get 'my_hx_request' object=my_instance %}></button>


Is equal to:

.. code-block:: html+django

    <button hx-get="my-website/current-page?hx_request_name=my_hx_request&object=model_instance__app_name__model__id_of_my_instance"></button>

.. note::

    See :ref:`Object Serialization` for more information on how objects are serialized.
`
