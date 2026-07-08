.. _how-to-mount-on-urls:

How To Mount HxRequests on URLs
-------------------------------

By default, :code:`hx-requests` routes every request through the page view that
carries :code:`HtmxViewMixin`: the handler name rides inside the signed
:code:`hx` token and the mixin dispatches to it. The **URL router** is an
additive alternative that gives every registered handler its own real Django
URL (:code:`/hx/<name>/`), so :code:`reverse()`, URL-level decorators and
middleware, per-endpoint caching, and :code:`show_urls` all work.

It is **opt-in and additive**: until you wire it up nothing changes, and once
you do, your templates need no edits — the :code:`hx_get` / :code:`hx_post` tags
start emitting the router URL automatically.

Wiring it up
~~~~~~~~~~~~~

Add the generated patterns to your root URLconf once. The registry builds one
:code:`path()` per registered handler *name* — you never hand-author a URL per
handler:

.. code-block:: python

    # urls.py
    from django.urls import include, path

    from hx_requests.hx_registry import HxRequestRegistry

    urlpatterns = [
        # ... your other URLs ...
        path("hx/", include((HxRequestRegistry.get_urls(), "hx_requests"), namespace="hx")),
    ]

:code:`HxRequestRegistry.get_urls()` returns the URL patterns. Handler classes
are **not** imported when the URLs are built — only their names are needed — so
lazy loading is preserved. The patterns are a snapshot taken when the URLconf is
built, so **adding a new handler needs a server restart** (the same as any
URLconf change).

That is all. :code:`reverse("hx:edit_widget")` now resolves to
:code:`/hx/edit_widget/`, and the template tags reverse it for you.

.. note::

    The namespace is the fixed string :code:`hx`, so handlers reverse as
    :code:`hx:<name>`.

Templates are unchanged
~~~~~~~~~~~~~~~~~~~~~~~~~

You do not touch your templates. :code:`{% hx_get %}`, :code:`{% hx_post %}` and
:code:`{% hx_url %}` prefer the router URL when it is installed and fall back to
the current page's path (legacy dispatch) when it is not:

.. code-block:: html

    <!-- Emits hx-get="/hx/edit_widget/?hx=<token>" when the router is wired,
         or hx-get="<current-path>?hx=<token>" when it is not. -->
    <button {% hx_get 'edit_widget' widget %}>Edit</button>

The signed :code:`hx` token still carries the handler name, object, and kwargs,
so request signing composes with the router unchanged.

Path binding (a security bonus)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the router the handler name comes from the **URL path**, not from a client
parameter. The endpoint checks that the token's name matches the URL it arrived
on, so a token minted for :code:`edit_widget` **cannot be replayed** against
:code:`delete_widget`'s URL — the mismatch is rejected with :code:`Http404`.
Per-handler authorization (:code:`login_required` / :code:`permission_required`
/ :code:`has_permission`) runs exactly as it does on the legacy path.

Because the endpoint is a real Django :code:`View`, Django's own
:code:`login_required` decorator and :code:`LoginRequiredMixin` compose natively
with it, and the :code:`hx_requests.W001` mixin-ordering trap does not apply on
this path (there is no page view to short-circuit).

Sharing page-view context
~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the legacy path a handler implicitly inherits the page view's context
(:code:`get_context_data`). On the router there is **no page view in the request
cycle**, so that implicit context is gone. Two options:

#. **Declare where the context comes from** with
   :code:`shares_context_from = SomeView`. The endpoint stands that view up and
   merges its context, reproducing the old behavior with one line:

   .. code-block:: python

       class EditWidgetHx(FormHxRequest):
           name = "edit_widget"
           GET_template = "widgets/_edit_form.html"
           shares_context_from = WidgetListView  # its get_context_data() is merged in

#. **Extract the shared context into a mixin** that both the page view and the
   handler inherit — the cleaner long-term pattern, with no cross-view
   instantiation.

Two things to keep in mind on the router path:

- A router handler must declare its own :code:`GET_template` / :code:`POST_template`.
  There is no page-view :code:`template_name` to fall back to.
- :code:`shares_context_from` fits context-only views such as
  :code:`TemplateView` and :code:`ListView`. A :code:`DetailView` /
  :code:`UpdateView` that needs a pk from the URL is out of scope for the
  additive router — resolve the object through the signed token instead (it is
  available as :code:`self.hx_object`).

A handler with no :code:`shares_context_from` simply gets no page-view context;
:code:`get_context_on_GET` / :code:`get_context_on_POST` and :code:`hx_object`
still work as usual.
