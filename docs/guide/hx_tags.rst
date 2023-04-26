HX Tags
=======

:code:`render_hx` is the template tag used to setup :code:`HXReuqests` in the template.

*Example from quickstart*

.. code-block:: html

    {% load hx_tags %}
    <div id="user_info_target"></div>
    <button {% render_hx 'get_user_info' 'get' %}
            hx-target="#user_info_target"
            type="button">
        Click Me
    </button>

- :code:`render_hx` takes in:
    - The name of the :code:`HXRequest` that is being used
    - The type of request, :code:`get` or :code:`post`
    - An object if there is one that is associted with the :code:`HXRequest` (similar to Django's `UpdateView <https://docs.djangoproject.com/en/4.2/ref/class-based-views/generic-editing/#django.views.generic.edit.UpdateView>`_ )
    - And kwargs

Notes:
    - If an object is passed in it is saved as :code:`hx_object` and can be accessed as :code:`self.hx_object`
    - If :code:`hx_object_name` is not set on the :code:`HXRequest`, the object is passed into the template (:code:`GET_template` for :code:`get` requests or :code:`POST_template` for :code:`post` requests) as :code:`hx_object` and can be accessed in the template as :code:`{{ hx_object }}`
    - Kwargs that are passed in are accessible in the :code:`HXRequest`(through :code:`**kwargs` in each method). THey get passed into the template as :code:`hx_kwargs` and can be accessed as :code:`{{ hx_kwargs.key }}`
    - Besides for primitive types the object and the kwargs can be a :code:`model_instance` (an instance of a Django model) because a :code:`model_instance` gets serialized by :code:`render_hx`.

.. warning::

    Objects passed into :code:`render_hx`, whether as the 'object' or in kwargs must be Django :code:`model_instance`. Other objects will not be serialized/ deserialized (primitives are of course okay).
