How To Access hx_object In Template
-----------------------------------


To access the :code:`hx_object` in a template, use it as you would any other context variable:
it will be available in the template as :code:`hx_object`.

If you want to rename it to have it accessible as something else, override the :code:`hx_object_name` attribute in your :code:`HxRequest` class.

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class MyHxRequest(BaseHxRequest):
        hx_object_name = "my_object" # in the template: {{ my_object }}



The hx object is the object passed into tmeplate tag

    .. code-block:: html+django

        <button {% hx_get 'my_hx_request' object=my_instance %}></button>
        <button {% hx_post 'my_hx_request' object=my_instance %}></button>


Kwargs
~~~~~~

Any kwargs passed to the :code:`hx_get` or :code:`hx_post` template tag will be available in the template as context variables by default.

.. code-block:: html+django

    <button {% hx_get 'my_hx_request' my_kwarg="my_value" %}></button>

In the template, you can access the kwarg as you would any other context variable:

.. code-block:: html+django

    <p>{{ my_kwarg }}</p>


If you want to prevent possible collisions between kwargs and existing context variables,
set :code:`kwargs_as_context = False` in your `HxRequest`.
This will make the kwargs available as a dictionary called :code:`kwargs` in the template.

.. code-block:: python

    from hx_requests.hx_requests import BaseHxRequest

    class MyHxRequest(BaseHxRequest):
        kwargs_as_context = False # in the template: {{ kwargs.my_kwarg }}
