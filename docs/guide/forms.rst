Using Forms
===========

| Probably the most common thing to use :code:`HXRequests` with is forms. :code:`HXRequests` gives a simple way to post data and update the page asyncronously.
|
| Using a :code:`FormHXRequest` the form is fetched asyncronously using the :code:`GET_template`, the form is saved and then it returns the :code:`POST_template`


Basic Form
----------

Form
~~~~

.. code-block:: python

    from django import forms

    class UserInfoForm(forms.ModelForm):

        class Meta:
            model = User
            fields = ['email', 'first_name', 'last_name']

HTML
~~~~
*user_info_page.html*

.. code-block:: html+django

    {% load hx_tags %}
    <div id="user_info">
        {% include 'user_info.html' %}
    </div>
    <form method="post">
        <div hx-trigger='load'
            {% hx_get 'user_info_form' object=request.user %}>
        </div>
        <button type="submit"
                hx-target="#user_info"
                {% hx_post 'user_info_form' object=request.user %}>
                Submit
        </button>
    </form>

*user_info.html*

.. code-block:: html+django

    {{ user.email }}
    {{ user.first_name }}
    {{ user.last_name }}

Notes:
    - 'user_info_form' in the template tags is the name of the :code:`HXRequest` that these requests will be routed to (see below)
    - :code:`object` is equivalent to an instance in a Django form. In the :code:`get` it's used to set the initial of the fields. In the :code:`post` it's the object that is getting updated.
    - An :code:`include` is used so that it can be reused below as the :code:`POST_template` in the :code:`HXRequest`.
    - The user in :code:`user_info.html` comes from the context of the view.

.. tip::

    :code:`includes` are very helpful when using htmx, because it gives an easy way to load part of the html.

HXRequest
~~~~~~~~~

.. code-block:: python

    from hx_requests.hx_requests import FormHXRequest

    class UserInfoHXRequest(FormHXRequest):
        name = "user_info_form"
        form_class = UserInfoForm
        GET_template = 'form.html' # Renders the form
        POST_template = 'user_info.html' # The 'include' in the HTML above
        hx_object_name = "user"


        def form_valid(self,**kwargs):
            # This is the default form_valid
            self.form.save()
            return self.get_response(**kwargs)

        def form_invalid(self, **kwargs) -> str:
            # This is the default form_invalid
            return self.get_response(**kwargs)

Notes:
    - :code:`form_valid` by default calls :code:`form.save()` and returns the :code:`POST_template`
    - :code:`form_invalid` by default returns the :code:`GET_template`. The purpose of this is to show the error messages. Because :code:`is_valid` was called (:code:`is_valid` is called in the :code:`post` method), the form now contains the errors, which gives you asyncronous validation of the form.
    - The :code:`GET_template` (*form.html*) has access to the form as 'form' in the context
    - :code:`hx_object_name` is the name given to the object when it's passed into the context. Above in :code:`user_info.html` (the :code:`POST_template`), on :code:`POST` the user in that context is the object that was passed in to the :code:`hx_post` template tag (although now it was updated by the form). If :code:`hx_object_name` was not set, instead of referencing the object as 'user' in :code:`user_info.html`, it would be referenced as :code:`hx_object` (i.e. :code:`hx_object.username`)
    - The object is saved as an attribute on the :code:`HXRequest` as :code:`hx_object`, so it can be referenced anywhere in the class as :code:`self.hx_object`

Setting Form Kwargs
-------------------

| To add kwargs to the form, override :code:`get_form_kwargs`.
| To set initial values of form fields, override :code:`get_initial`.

.. code-block:: python

    from hx_requests.hx_requests import FormHXRequest

    class MyHXRequest(FormHXRequest):
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

You can also set the initial from the kwargs by setting :code:`set_initial_from_kwargs` to :code:`True`.
This setting allows the initial value to be automatically populated from the kwargs.
As long as the key in the kwargs matches the name of a field in the form, it will be assigned as the initial value for that field.

.. code-block:: python

    from hx_requests.hx_requests import FormHXRequest

    class MyForm(forms.ModelForm):

        class Meta:
            model = MyModel
            fields = ['field1', 'field2']

    class MyHXRequest(FormHXRequest):
        name='my_hx_request'
        set_initial_from_kwargs = True


.. code-block:: html+django

        <button {% hx_get 'my_hx_request' field1="Cool Initial Value" %}></button>

Notes:
    - The initial value of :code:`field1` will be set to :code:`"Cool Initial Value"`

Setting :ref:`Messages`
-----------------------

.. note::

    See :ref:`Messages` for more details and for config settings.

In a :code:`FormHXRequest` success and error messages can be set by overriding :code:`get_success_message` and :code:`get_error_message`

.. code-block:: python

    class MyHXRequest(FormHXRequest):
        # Set attributes

        def get_success_message(self, **kwargs) -> str:
            # This is not the default
            return "Form saved sucessfully"

        def get_error_message(self, **kwargs) -> str:
            # This is not the default
            return "Did not save due to errors in the form"

Notes:
    - Set :code:`add_form_errors_to_error_message` to :code:`True` to add the form errors to the error message automatically. But then do not override :code:`get_error_message`.

.. note::

    Messages can be set in any :code:`HXRequest` at any point like this:

    .. code-block:: python

        self.messages.success("Hooray!")

    Message types are: debug, info, succes  s, warning and error.

Forms in Modals
---------------

See :ref:`Form Modals`
