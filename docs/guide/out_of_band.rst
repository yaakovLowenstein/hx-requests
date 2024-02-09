Out of Band
===========

How to update more than one part of the page using hx-requests?
What if you want to return a response that has the Html from two templates or you want to return two separate blocks from the same template?

Setting template/ block to lists
--------------------------------


.. code-block:: python

    from hx_requests.hx_requests import FormHXRequest

    class UserInfoHXRequest(FormHXRequest):
        name = "user_info_form"
        form_class = UserInfoForm
        GET_template = 'form.html'
        POST_template = ['user_info_1.html', 'user_info_2.html']
        # POST_block = ['block_1', 'block_2'] # Cannot use lists for both at the same time
        hx_object_name = "user"


Notes:
    - This will return the Html from both :code:`user_info_1.html` and :code:`user_info_2.html`
    - The main use of this is for doing out-of-band swaps so that other parts of the page could be updated as well

.. note::

    The Html mark up for the template being used out-of-band would need to use :code:`hx-swap-oob` or :code:`hx-select-oob`
