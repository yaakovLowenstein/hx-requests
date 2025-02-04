# hx-requests

Full documentation: https://hx-requests.readthedocs.io/en/latest/#

<br>

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-blue.svg)](https://docs.astral.sh/ruff/formatter/)
[![Code style: djlint](https://img.shields.io/badge/html%20style-djlint-blue.svg)](https://www.djlint.com)

Overview
==========

What Are hx-requests?
---------------------

To start with a high level explanation, :code:`hx-requests` are quasy Django + Htmx views.
They mimic Django's class based views, but with the added functionality to work
seamlessly with Htmx. Using a View mixin, it elegantly handles multiple Htmx requests on a single page. Each Htmx request is routed to a specific hx-request (think of it as a view), which returns the
necessary HTML to update the DOM. A more detailed explanation can be found :ref:`below <Why Use hx-requests?>`.


Why The Name?
-------------

Excellent question! The package was named early on in the development process when the behavior wasn't exactly clear.
All that was clear was that there needed to be an easier way to work with Htmx in Django.
Hx comes from Htmx, and requests because every use of Htmx is a request to the server.
If it was named today, it would probably be named something like Django-Htmx-Views, but :code:`hx-requests` has stuck.


Why Use hx-requests?
--------------------

This is where we will get into the weeds a little to explain why :code:`hx-requests` is needed.

There are multiple ways of integrating Htmx in a Django project.

1. **Using The Page View**

The most common way seems to be re-hitting the view that loaded the page.

The base view:

.. code-block:: python

    class MyView(View):
        def get(self, request):
            return render(request, "my_template.html")


The template:

.. code-block:: html+django

    <div hx-get="{% url 'my_view' %}">
        <p>Click me to use hx-get</p>
    </div>

Handling the request:

.. code-block:: python

    class MyView(View):
        def get(self, request):
            if request.headers.get("HX-Request"):
                return render(request, "my_template.html")
            return render(request, "my_template.html")


This, along with help from some other packages out there, seems to be the most common way to use Htmx in Django.
However, this works well for views with one Htmx request, but what if you have multiple Htmx requests on the same page?

View handling multiple Htmx requests:

.. code-block:: python

    class MyView(View):
        def get(self, request):
            if request.headers.get("HX-Request"):
                if request.headers.get("Unique-Identifier") == "get_user_info":
                    return render(request, "user_info_card.html")
                if request.headers.get("Unique-Identifier") == "get_user_profile":
                    return render(request, "user_profile_card.html")
            return render(request, "my_template.html")

Issues with this:

* This already isn't great, but now imagine this with 10 Htmx requests on the same page. It's a mess. Additionally, if they are POST requests and specfic
  logic needs to be run (and it needs to be dynamic based on whether the form is valid or not), it's even more of a mess.
* The logic for the Htmx request is tied to the view and therefore a duplicate request for this cannot be used on a different page
  without duplicating all the logic.

This brings us to the 2nd way of using Htmx in Django.

2. **Using Separate Views**

Every Htmx request is routed to a separate view.

.. code-block:: python

    # Page View
    class MyView(View):
        def get(self, request):
            # Do some logic to set up context
            context['complex-context'] = "This is a complex context"
            return render(request, "my_template.html", context)

    # Htmx Request 1
    class GetUserInfo(View):
        def get(self, request):
            return render(request, "user_info_card.html")

    # Htmx Request 2
    class GetUserProfile(View):
        def get(self, request):
            return render(request, "user_profile_card.html")


Issues with this:

* There's a lot of extra URL handling, as every Htmx request needs a url.
* The context is not shared across views. This is a major issue because if the parent page view does some logic to set up context,
  that context is not available in the Htmx request views and would need to be duplicated. In the contrived example above, a mixin or helper
  function could be used to set up the context, but in a real world application, this would be a nightmare. Especially with Django's built in
  views. Think of the ListView, If there is an Htmx request that needs to return a list of objects (i.e. a filter form), the ListView would need to be duplicated
  in the view setup for the Htmx request view.



**Hx-requests**

:code:`hx-requests` solves all of these issues. It allows for multiple Htmx requests on the same page, and the context is shared across all of the Htmx requests.
Every Htmx request routes to an :ref:`hx-request <What Are hx-requests?>`.

Therefore:

* The parent view is not clogged up with extra logic to handle many Htmx requests
* Reusable HXRequests across views. Since they are not directly tied to the view (even though they can use the view's context) they can be reused across views.
* No extra urls are needed
* The view's context is shared across all Htmx requests because the parent view routes the Htmx request to the correct hx-request giving the hx-request access to the all the view's attributes and context.

Additionally, :code:`hx-requests` has built in functionality that helps with common Htmx use cases.

* When a form is posted, the form is validated and the form is returned with errors if it is not valid.
  This is done by default when using :code:`FormHxRequest`.
* Easy integration with Django's messages framework.
* Easy integration with `django-render-block <https://github.com/clokep/django-render-block>`_ to reduce the need for includes and instead
  use blocks to render partials.
* A built in way to use modals with Htmx.

Full documentation: https://hx-requests.readthedocs.io/en/latest/#

# Contributing to this repository

## Getting setup

- This project is using poetry
- pre-commit is used for CI (code formatting, linting, etc...)
- There is a dev container that can be used with vs-code


## Committing

Must follow Conventional Commit
https://www.conventionalcommits.org/en/v1.0.0/
