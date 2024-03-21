Quickstart
==========

The idea of hx-requests is that :code:`HXRequests` absorb all htmx requests.
Define an :code:`HXRequest` (we'll get into how to do that in just a sec) and
observe the magic of :code:`hx-requests`.

- No need to define extra urls to handle these requests
- No need to add anything extra in views
- Reusable :code:`HXRequests` across views
- Built in :code:`HXReuqests` to reduce boilerplate code (Forms, Deleting, Modals)

Making a GET Request (hx-get)
---------------------------------

The View
~~~~~~~~

The view requires :code:`HtmxViewMixin`

.. code-block:: python

    from hx_requests.views import HtmxViewMixin
    from django.views.generic.base import View

    class MyView(HtmxViewMixin, View):
        pass

The HTML
~~~~~~~~


.. code-block:: html+django

    {% load hx_tags %}
    <div id="user_info_target"></div>
    <button {% hx_get 'get_user_info' %}
            hx-target="#user_info_target"
            type="button">
        Click Me
    </button>

Notes:
    - Using the :ref:`hx_get <hx_get>` template tag signifies that it's an :code:`hx-get`
    - 'get_user_info' is the name of this :code:`HXRequest`. See below to understand what that means
    - The goal of this :code:`hx-get` is to render a user info card into the empty div


Create the HXRequest
~~~~~~~~~~~~~~~~~~~~

Create an :code:`hx_requests.py` file

.. warning::

    All :code:`HXRequests` must be defined inside an :code:`hx_requests.py` file, and the :code:`hx_requests.py`
    files must live inside an app that's included in Django's :code:`INSTALLED_APPS`.

| Create the HXRequest.
| The :code:`hx-get` will get directed to this :code:`HXRequest`.

.. code-block:: python

    from hx_requests.hx_requests import BaseHXRequest

    class GetUserInfo(BaseHXRequest):
        name = "get_user_info"
        GET_template = "user_info_card.html"

Notes:
    - :code:`GetUserInfo` will return the HTML from the :code:`GET_template` (:code:`user_info_card.html`)

*user_info_card.html*

.. code-block:: html+django

    <div>
        <p>Username:{{request.user.username}}</p>
        <p>Email:{{request.user.email}}</p>
    </div>

Summary
~~~~~~~

| Htmx requests are routed to the :code:`HXRequest` that matches the name (1st argument) passed into the :code:`hx_get` template tag. In this example 'get_user_info'. That's how the :code:`hx-get` is routed to :code:`GetUserInfo`.
|
| The request returns the html of the :code:`GET_template`.

.. note::

    The :code:`GET_template` has access to all of the context that is in the view.



Making a POST Request (hx-post)
---------------------------------

Alomost exactly the same as the :code:`GET` request above.

.. note::

    Working with a form? See :ref:`Using Forms`

The View
~~~~~~~~

The view requires :code:`HtmxViewMixin`

.. code-block:: python

    from hx_requests.views import HtmxViewMixin
    from django.views.generic.base import View

    class MyView(HtmxViewMixin, View):
        pass

The HTML
~~~~~~~~

.. code-block:: html+django

    {% load hx_tags %}
    <div id="email_display">{{request.user.email}}</div>
    <input type="text" name="email" id='email_input'/>
    <button {% hx_post 'change_email' %}
            hx-target="#email_display"
            hx-include="#email_input"
            type="button">
        Save
    </button>

Notes:
    - Using the :ref:`hx_post <hx_post>` template tag signifies that it's an :code:`hx-post`
    - The goal of this :code:`hx-post` is to change the signed in user's email to the value of the input replace the email address in the div with the updated email


Create the HXRequest
~~~~~~~~~~~~~~~~~~~~

Create an :code:`hx_requests.py` file

.. warning::

    All :code:`HXRequests` must be defined inside an :code:`hx_requests.py` file, and the :code:`hx_requests.py`
    files must live inside an app that's included in Django's :code:`INSTALLED_APPS`.

| Create the HXRequest.
| The :code:`hx-post` will get directed to this :code:`HXRequest`.

.. code-block:: python

    from hx_requests.hx_requests import BaseHXRequest

    class ChangeEmail(BaseHXRequest):
        name = "change_email"
        POST_template = "email.html"

        def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user = request.user
            user.email = request.POST.get("email")
            user.save()
            return super().post(request, *args, **kwargs)

Notes:
    - :code:`ChangeEmail` will return the HTML from the :code:`POST_template` (:code:`email.html`)

*email.html*

.. code-block:: html+django

    <span>{{request.user.email}}</span>

Summary
~~~~~~~

| Htmx requests are routed to the :code:`HXRequest` that matches the name (1st argument) passed into the :code:`hx_post` template tag. In this example 'change_email'. That's how the :code:`hx-post` is routed to :code:`ChangeEmail`.
|
| The request returns the html of the :code:`POST_template`.

.. note::

    The :code:`POST_template` has access to all of the context that is in the view.

Adding context to the templates
-------------------------------

Many times you may need additional context in the :code:`GET_template` or :code:`POST_template`. Luckily, there is
a simple way to add context to them.

.. code-block:: python

    from hx_requests.hx_requests import BaseHXRequest

    class MyHXRequest(BaseHXRequest):
        ...

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["important_var"] = "I am important"
            return context

Additionally, if you only want the contex added on post (i.e. you want one of the form values in the :code:`POST_template`), you can
instead override :code:`get_post_context_data`

.. code-block:: python

    from hx_requests.hx_requests import BaseHXRequest

    class MyHXRequest(BaseHXRequest):
        ...

        def get_post_context_data(self, **kwargs):
            context = super().get_post_context_data(**kwargs)
            context["important_var"] = "I am important"
            return context


.. note::

    The :code:`GET_template` and the :code:`POST_template` have access to :code:`hx_obect` (or the name it's given by setting :code:`hx_object_name`)
    and the kwargs passed into :code:`hx_get` or :code:`hx_post`.

    For example:

    .. code-block:: html+django

        {% hx_get 'my_hx_request' object=object my_awesome_kwarg="I am awesome" %}

    In the :code:`GET_template`, 'my_awesome_kwarg' can be accessed as :code:`my_awesome_kwarg` unless :code:`kwargs_as_context` is set to False then it can be accessed as :code:`{{ hx_kwargs.my_awesome_kwarg }}`

Context setup by get
--------------------

One key feature of :code:`hx-requests` is that the :code:`HxRequest` class grants access to the context of the view it is associated with.
However, a common issue arises when the view sets up attributes within its :code:`get` method that the context relies on.
This poses a challenge because :code:`HXRequest` does not directly invoke the view's :code:`get` method, potentially resulting in an error where
:code:`self.{var}` is inaccessible.

To mitigate this issue, :code:`hx-requests` automatically resolves Django's views and invokes the :code:`get` method on your behalf.
Notably, it does so without returning the response immediately. This approach minimizes performance overhead,
as returning the response entails the view evaluating the entire response, which can be detrimental to performance.

Additionally, :code:`hx-requests` offers the flexibility to configure :code:`get` behavior for custom views through settings,
as detailed in the :ref:`settings <Configuration>`.

Example of the get for a :code:`UpdateView`:

.. code-block:: python

    def update_view_get(self, request, *args, **kwargs):
        self.object = self.get_object()

Notes:
 - :code:`UpdateView` relys on the get setting the :code:`self.object` attribute. :code:`hx-requests` will call the :code:`get` method
   and set the :code:`self.object` attribute for you.
 - The function takes the same arguments as the :code:`get` method of the view.

Example of setting up a custom view's get:

.. code-block:: python

    def my_custom_view_get(self, request, *args, **kwargs):
        self.my_custom_attribute = "I am custom"

    # In settings.py
    HX_REQUESTS_CUSTOM_VIEWS_SETUP = {
        'my_app.views.my_custom_view' : 'my_app.view_get_functions.custom_view_get',
        }

.. note::

    A good example of a use case is if you are using django-filters. The :code:`FilterView` sets up attributes in the :code:`get` method
    and also passes them to the context. To use :code:`FilterView` with :code:`hx-requests`, you would need to setup the :code:`get` method
    to match the :code:`get` method of the :code:`FilterView` and return the extra context instead of the response.

    .. code-block:: python

        def filter_view_get(self,request,*args,**kwargs):
            filterset_class = self.get_filterset_class()
            self.filterset = self.get_filterset(filterset_class)

            if (
                not self.filterset.is_bound
                or self.filterset.is_valid()
                or not self.get_strict()
            ):
                self.object_list = self.filterset.qs
            else:
                self.object_list = self.filterset.queryset.none()

            # Return the extra context
            return {'filter': self.filterset, 'object_list': self.object_list}
