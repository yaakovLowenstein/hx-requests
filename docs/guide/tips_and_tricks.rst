Tips and Tricks
===============

**How do I make the page refresh when using an HXRequest?**

Set :code:`refresh_page` to True.

.. code-block:: python

    class MyHXRequest(FormHXRequest):
        ...
        refresh_page = True


**How do I redirect to a new page when using an HXRequest?**

Set redirect to the URL the :code:`HXRequest` should redirect to.

.. code-block:: python

    class MyHXRequest(FormHXRequest):
        ...
        redirect = "my-website/home"

**What if I only want the page to refresh/ redirect when the form is valid but if the form is invlalid I want the errors to show and the page not to refresh/ redirect?**

Set :code:`refresh` or :code:`redirect` in form_invalid.


.. code-block:: python

    class MyHXRequest(FormHXRequest):
        ...
        refresh=True # or redirect = "my-website/home"

        def form_invalid(self,**kwargs):
            self.refresh = False # or self.redirect = None
            return super().form_invalid(**kwargs)

**What is return_empty for?**

:code:`return_empty` returns an empty :code:`HttpResponse` from the :code:`HXRequest`. An example of where it may be used is a 'save for later'
button in a shopping cart. The item needs to disappear from the cart, but there is nothing on the page that needs to be updated. Therfore you
want to return an empty :code:`HTTPResponse`. Another example is a delete where nothing on the page needs to be updated.

**What is no_swap for?**

When :code:`no_swap` is set no html is swapped into the DOM. An example where to use this would be a button that submits a post request.
If there is validation and the form is valid, you may want to do a swap in the DOM to update part of the page. However,
when the form in invalid, you may want to just set a message with the errors.

.. code-block:: python

    class MyHXRequest(FormHXRequest):
        ...

        def form_invalid(self,**kwargs):
            self.no_swap = True
            self.messages.error("Sorry there was an error")
            return super().form_invalid(**kwargs)


**How do I put the form errors into the error message when using a FormHXRequest?**

Setting :code:`add_form_errors_to_error_message` to True will put the form's errors into the error message.


**How do I change the name of the context variable that hx_object is passed into the context with?**

If you want to put the :code:`hx_object` into the context with a different name, set :code:`hx_object_name`.

.. code-block:: python

    class MyHXRequest(FormHXRequest):
        ...
        hx_object_name = "my_object"

*and in the template*

.. code-block:: html

    {{my_object}}


**How do I use asyncronous Htmx requests with Bootstrap's tooltips (and selectpicker)?**

This is a tip for using Htmx in general with Bootstrap. Because tooltips are initialized on page load, Html loaded
asyncronously will not have them initialized. To fix this you can set an event listener on :code:`htmx:afterRequest`.

.. code-block:: JavaScript

    document.addEventListener('htmx:afterRequest', (e) => {
        // For Tooltips
        $('[data-bs-toggle="tooltip"]').tooltip();

        // For Bootstrap's selectpicker
        $('.selectpicker').selectpicker();

    })
