Object Serialization
--------------------

Serialization in :code:`hx_requests` ensures that Django model instances and other data types
can be safely passed through HTMX requests. The serialization process takes place in the :ref:`template tag <Hx Tags>`.

Since HTMX requests don’t natively support passing complex Python objects,
:code:`hx_requests` provides a custom serialization method that allows Django models
and additional data to be included in GET and POST requests.

Serializing Model Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a model instance is serialized, it is converted into a structured string format
that includes the prefix :code:`model_instance`, to differentiate from other URL parameters, the app label, model name, and primary key.

For example, a :code:`User` instance with :code:`pk=5` in the :code:`auth` app
would be represented as:

.. code-block:: text

    model_instance__auth__user__5

This ensures that objects can be passed in requests without requiring JSON encoding.

If the value being serialized is not a Django model instance,
it is simply converted to JSON.

Deserializing Model Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a serialized object is received, it needs to be converted back into a Django model instance.
This is done by extracting the app label, model name, and primary key,
then retrieving the object from the database.

If the received value is not a model instance, it is treated as a standard JSON object.

This process ensures that Django objects can be reconstructed properly when handling HTMX requests.

Handling kwargs Serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each keyword argument is prefixed with :code:`___` to differentiate it from standard query parameters.
When deserializing, the prefix is removed, and values are restored to their original form.

This allows :code:`hx_requests` to safely pass complex parameters in HTMX requests.

.. note::

    Since keyword arguments (:code:`kwargs`) are prefixed with :code:`___` during serialization, they are not recognized as standard query parameters.
    If you need to pass a GET parameter through an HTMX request, use the :code:`hx-include` or :code:`hx-vals` attribute instead of a passing as a :code:`kwarg`.
    For example, when implementing pagination, the :code:`page` parameter must be sent as a standard GET parameter. Passing it as a :code:`kwarg` will result in it being prefixed and ignored by the request handler.
