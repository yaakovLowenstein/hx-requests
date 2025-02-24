What Are FormHxRequests?
------------------------


The :code:`FormHxRequest` is modeled after Django's :code:`FormView`, :code:`CreateView` and :code:`UpdateView`.
If the package was being rewritten it coulde be there would be three separate classes, but for now they are all combined into one.
Which on one hand makes it easier to use, but on the other hand can make it a little more coupled.

The :code:`FormHxRequest` uses a :code:`form_class` attribute to set which form to use. This could be a regular form or a model form.
On GET the form is accessible in the context as :code:`form` and the template defined in :code:GET_template has access to it..
On POST the form is validated and if it is valid the :code:`form_valid` method is called, if it is invalid the :code:`form_invalid` method is called just
like in Django's :code:`FormView`.

If the form is a model form and :code:`hx_object` (object is the parameter in the :ref:`tags <Hx Tags>` is passed in to the template tags on GET/ POST then the
:code:`FormHxRequest` is treated like a :code:`UpdateView` and the object is passed in to the form as an instance.
If the form is a model form and the object is not passed in then the :code:`FormHxRequest` is treated like a :code:`CreateView` and a model instance is created from the form.

:code:`form_valid` by default calls the save method of the form and sets a success :ref:`message <How To Set Messages>`.
If you want to do something else you can override the :code:`form_valid` method, ie like sending an email.

:code:`form_invalid` by default sets a :ref:`message <How To Set Messages>` and returns the form with the errors and it does this by changing the template
rendered back to the :code:`GET_template` so that the form will be still visible but now with the errors.

Other built in behavior includes support for setting :ref:`form_kwargs <How To Add Form Kwargs>` (even the ability to automatically set from the :ref:`template tag <Adding Initial Form Values From The Template>`),

hx_object
~~~~~~~~~

The :code:`hx_object` is the object passed into the template tag and as mentioned above is used as the instance for the form if the form is a model form.
It is accessible in the templates (:code:`GE_tempalte` and :code:`POST_template`) as :code:`hx_object` by default, but can be :ref:`renamed <How To Access hx_object In Template>` by setting :code:`hx_object_name` in the :code:`FormHxRequest` class.

This can be a little confusing, for example

you have a page that has the object passed in fomr the view's context as :code:`user`

.. code-block:: html+django

    <button {% hx_get 'my_form_request' object=user %}></button>

But in the :code:`GET_template` you need to access the object as :code:`hx_object` because that is the default

.. code-block:: html+django

    <p>{{ hx_object.username }}</p>
    <p>{{ hx_object.email }}</p>

    <form>
        {{ form.as_p }}
        <button {% hx_post 'my_form_request' object=hx_object %}>Submit</button>

        >Submit</button>
    </form>

.. tip::

    Most of the time you will want the :code:`hx_object_name` to match the context of the view so that when the :code:`GET_template`
    is the same as the view's template you can just use the same context variable name.
