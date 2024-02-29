Out of Band
===========

How to update more than one part of the page using hx-requests?
What if you want to return a response that has the Html from two templates or you want to return two separate blocks from the same template, or maybe
even blocks from all different templates?

Setting template to a list
--------------------------


.. code-block:: python

    from hx_requests.hx_requests import FormHXRequest

    class UserInfoHXRequest(FormHXRequest):
        name = "user_info_form"
        form_class = UserInfoForm
        GET_template = 'form.html'
        POST_template = ['user_info_1.html', 'user_info_2.html']
        hx_object_name = "user"


Notes:
    - The POST will return the Html from both :code:`user_info_1.html` and :code:`user_info_2.html`
    - Cannot set blocks when using a list of templates because it is not clear which template the block is coming from
    - The main use of this is for doing out-of-band swaps so that other parts of the page could be updated as well
    - This can also be done with GET_template

.. note::

    The Html mark up for the template being used out-of-band would need to use :code:`hx-swap-oob` or :code:`hx-select-oob`

Setting block to a list
-----------------------


.. code-block:: python

    from hx_requests.hx_requests import FormHXRequest

    class UserInfoHXRequest(FormHXRequest):
        name = "user_info_form"
        form_class = UserInfoForm
        GET_template = 'form.html'
        POST_template = 'user_info_1.html'
        POST_block = ['block_1', 'block_2']
        hx_object_name = "user"


Notes:
    - The POST will return the Html from both :code:`block_1` and :code:`block_2`
    - :code:`POST_template` must be a string when using a list of blocks so that it is clear all the blocks defined are coming from the same template
    - The main use of this is for doing out-of-band swaps so that other parts of the page could be updated as well
    - This can also be done with GET_block

.. note::

    The Html mark up for the template being used out-of-band would need to use :code:`hx-swap-oob` or :code:`hx-select-oob`

Setting block to a dict
-----------------------


.. code-block:: python

    from hx_requests.hx_requests import FormHXRequest

    class UserInfoHXRequest(FormHXRequest):
        name = "user_info_form"
        form_class = UserInfoForm
        GET_template = 'form.html'
        POST_template = '' # This is needed because the default is the view's template
        POST_block = {
            'user_info_1.html': ['block_1', 'block_2'],
            'user_info_2.html': ['block_3', 'block_4']
        }
        hx_object_name = "user"


Notes:
    - The POST will return the Html from all 4 blocks across the two templates
    - Using a dict allows you to define which blocks are coming from which template
    - If :code:`POST_template` is defined as a string, it will also return the Html from the template along with the blocks
    - If :code:`POST_template` is defined as a list, it will also return the Html from all the templates along with the blocks
    - The main use of this is for doing out-of-band swaps so that other parts of the page could be updated as well
    - This can also be done with GET_block

.. warning::

    If you don't want the Html from the view's template to be returned, you must set :code:`POST_template` to an empty string
    because the default is the view's template

.. note::

    The Html mark up for the template being used out-of-band would need to use :code:`hx-swap-oob` or :code:`hx-select-oob`