More How Tos
------------


What Is no_swap For?
~~~~~~~~~~~~~~~~~~~~

When :code:`no_swap` is set, no HTML is swapped into the DOM. A common use case is a button that submits a POST request.
If the form is valid, you may want to swap in updated content to reflect the changes.
However, if the form is invalid, you may only want to display error messages without modifying the page structure.

Set it statically with the :code:`no_swap` attribute, or compute it per request
by overriding :code:`get_no_swap` — cleaner than flipping :code:`self.no_swap`
inside :code:`form_valid` / :code:`form_invalid` just to change the swap:

.. code-block:: python

    class MyHxRequest(FormHxRequest):
        ...

        def get_no_swap(self, **kwargs):
            # Swap in updated content when the form saves; leave the page
            # untouched (errors show via messages) when it doesn't.
            return not self.form.is_valid()

There is a matching :code:`get_return_empty` hook for computing :code:`return_empty` the same way.


How Do I Submit A Formset Alongside The Form?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A :code:`FormHxRequest` takes in :code:`self.form`, but a handler may submit more
than that — an extra formset, a second form. Override :code:`form_is_valid` so one
answer covers the whole submission:

.. code-block:: python

    class MyHxRequest(FormModalHxRequest):
        ...

        @cached_property
        def formset(self):
            return MyFormSet(data=self.request.POST if self.is_post_request else None)

        def form_is_valid(self, **kwargs) -> bool:
            return super().form_is_valid(**kwargs) and self.formset.is_valid()

        def form_valid(self, **kwargs):
            response = super().form_valid(**kwargs)
            self.formset.save()
            return response

Everything on the save path reads through that hook: :code:`post` picks
:code:`form_valid` / :code:`form_invalid`, :code:`get_response_html` chooses the GET
template so the errors come back, and :code:`FormModalHxRequest` decides whether to
close the modal or retarget the errors into its body. Without the override those
disagree with the handler, and a submission that failed only in the formset reads as
a save — the modal closes, taking the errors and everything typed with it.

:code:`form_is_valid` is called several times while the response is built, so keep
an override free of side effects, or memoize them.


How Do I Add Form Errors To The Error Message?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting :code:`add_form_errors_to_error_message` to True will add a Django form's errors into the error message.

.. code-block:: python

    class MyHxRequest(FormHxRequest):
        ...
        add_form_errors_to_error_message = True


How To Opt Out Of The View's Context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default :code:`HxRequests` include the view's context so that you can access the view's context in your template.
However, there may be cases where you want to opt out of this behavior (slow performance, security concerns, etc).

.. code-block:: python

    class MyHxRequest(BaseHxRequest):
        get_views_context = False

.. note::

    The view's context is only harvested when the response actually renders it.
    A POST that renders nothing from the view (:code:`refresh_page`,
    :code:`redirect`, or :code:`return_empty`) skips running the view's
    :code:`get()` entirely, so you don't pay its query cost on those paths.
    Setting :code:`get_views_context = False` is therefore mainly useful for
    handlers that *do* render a template but don't need the view's context.
