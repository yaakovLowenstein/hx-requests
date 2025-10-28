# hx-requests

Full documentation: [hx-requests Documentation](https://hx-requests.readthedocs.io/en/latest/#)
Demo Website: https://hx-requests-demo.com/

<br>

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-blue.svg)](https://docs.astral.sh/ruff/formatter/)
[![Code style: djlint](https://img.shields.io/badge/html%20style-djlint-blue.svg)](https://www.djlint.com)

## Overview

### What Are hx-requests?

To start with a high-level explanation, `hx-requests` are quasi Django + Htmx views.
They mimic Django's class-based views but with added functionality to work seamlessly with Htmx. Using a View mixin, it elegantly handles multiple Htmx requests on a single page. Each Htmx request is routed to a specific hx-request (think of it as a view), which returns the necessary HTML to update the DOM. A more detailed explanation can be found [below](#why-use-hx-requests).

### Why The Name?

Excellent question! The package was named early on in the development process when the behavior wasn't exactly clear.
All that was clear was that there needed to be an easier way to work with Htmx in Django.
**Hx** comes from Htmx, and **requests** because every use of Htmx is a request to the server.
If it was named today, it would probably be called something like `Django-Htmx-Views`, but `hx-requests` has stuck.

### Why Use hx-requests?

This is where we will get into the details of why `hx-requests` is needed.

There are multiple ways of integrating Htmx in a Django project.

#### 1. Using The Page View

The most common way is re-hitting the view that loaded the page.

The base view:

```python
class MyView(View):
    def get(self, request):
        return render(request, "my_template.html")
```

The template:

```html
<div hx-get="{% url 'my_view' %}">
    <p>Click me to use hx-get</p>
</div>
```

Handling the request:

```python
class MyView(View):
    def get(self, request):
        if request.headers.get("HX-Request"):
            return render(request, "my_template.html")
        return render(request, "my_template.html")
```

This approach works well for views with one Htmx request, but what if you have multiple Htmx requests on the same page?

Handling multiple Htmx requests:

```python
class MyView(View):
    def get(self, request):
        if request.headers.get("HX-Request"):
            if request.headers.get("Unique-Identifier") == "get_user_info":
                return render(request, "user_info_card.html")
            if request.headers.get("Unique-Identifier") == "get_user_profile":
                return render(request, "user_profile_card.html")
        return render(request, "my_template.html")
```

**Issues with this approach:**

- It gets messy if there are multiple Htmx requests on the same page.
- Handling POST requests with specific logic dynamically adds complexity.
- The logic for handling Htmx requests is tightly coupled to the view, making reuse difficult.

#### 2. Using Separate Views

Each Htmx request is routed to a separate view.

```python
# Page View
class MyView(View):
    def get(self, request):
        context = {'complex-context': "This is a complex context"}
        return render(request, "my_template.html", context)

# Htmx Request 1
class GetUserInfo(View):
    def get(self, request):
        return render(request, "user_info_card.html")

# Htmx Request 2
class GetUserProfile(View):
    def get(self, request):
        return render(request, "user_profile_card.html")
```

**Issues with this approach:**

- Each Htmx request requires a separate URL.
- Context is not shared across views, leading to code duplication.
- Using Django's built-in `ListView`, duplicating logic for Htmx requests becomes a nightmare.

### hx-requests: The Solution

`hx-requests` solves all of these issues. It allows multiple Htmx requests on the same page while sharing context across requests. Every Htmx request routes to an [`hx-request`](#what-are-hx-requests).

**Advantages:**

- The parent view is not cluttered with extra logic for handling multiple Htmx requests.
- HxRequests are reusable across views, reducing duplication.
- No extra URLs are needed.
- The view's context is shared across all Htmx requests, making it easier to manage.

Additionally, `hx-requests` includes built-in functionality to help with common Htmx use cases:

- Form validation and automatic return of errors when using `FormHxRequest`.
- Easy integration with Django's messages framework.
- Compatibility with [`django-render-block`](https://github.com/clokep/django-render-block) for partial template rendering.
- Built-in support for handling modals with Htmx.

Full documentation: [hx-requests Documentation](https://hx-requests.readthedocs.io/en/latest/#)

---

# Contributing to this repository

## Getting setup

- This project is using poetry
- pre-commit is used for CI (code formatting, linting, etc...)
- There is a dev container that can be used with vs-code

## Committing

Must follow [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/)
