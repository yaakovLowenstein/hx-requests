HX Tags
=======

There are two template tags to use to setup :code:`HXRequests`: :code:`hx_get` and :code:`hx_post`. They are identical except that one makes a get request and one makes a post request.

hx_get
------

*Example from quickstart*

.. code-block:: html

    {% load hx_tags %}
    <div id="user_info_target"></div>
    <button {% hx_get 'get_user_info' %}
            hx-target="#user_info_target"
            type="button">
        Click Me
    </button>

- :code:`hx_get` takes in:
    - The name of the :code:`HXRequest` that is being used
    - An object if there is one that is associted with the :code:`HXRequest` (similar to Django's `UpdateView <https://docs.djangoproject.com/en/4.2/ref/class-based-views/generic-editing/#django.views.generic.edit.UpdateView>`_ )
    - And kwargs

Notes:
    - If an object is passed in it is added as an attribute to the :code:`HXRequest` as :code:`hx_object` and can be accessed as :code:`self.hx_object`
    - If :code:`hx_object_name` is not set on the :code:`HXRequest`, the object is passed into the template (:code:`GET_template` for :code:`get` requests or :code:`POST_template` for :code:`post` requests) as :code:`hx_object` and can be accessed in the template as :code:`{{ hx_object }}`
    - Kwargs that are passed in are accessible in the :code:`HXRequest` (through :code:`**kwargs` in each method). They get passed into the template as :code:`hx_kwargs` and can be accessed as :code:`{{ hx_kwargs.key }}`
    - Besides for primitive types the object and the kwargs can be a :code:`model_instance` (an instance of a Django model) because a :code:`model_instance` gets serialized by :code:`hx_get`.

.. warning::

    Objects passed into :code:`hx_get`, whether as the 'object' or in kwargs must be Django :code:`model_instance`. Other objects will not be serialized/ deserialized (primitives are of course okay).

hx_post
-------

Same as above except that a post request will be made instead of a get request.
