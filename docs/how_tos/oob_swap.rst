How To Do OOB Swaps
-------------------

Out-of-band (OOB) swaps are useful for updating multiple parts of a page without returning the entire page each time.
hx-requests provides an easy way to return multiple HTML snippets, each performing an OOB swap efficiently.

Using Multiple Templates
~~~~~~~~~~~~~~~~~~~~~~~~

If the HTML snippets you want to return are in separate templates, the code would look like this:

.. code-block:: python

    class MyHxRequest(BaseHxRequest):
        name ="my_hx_request"
        GET_template = ["target_template.html","oob_template.html"]


Using Multiple Blocks (Same Template)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the HTML snippets are in separate blocks within the same template, the code would look like this:

.. code-block:: python

    class MyHxRequest(BaseHxRequest):
        name ="my_hx_request"
        GET_template = "template.html"
        GET_block = ["block","oob_block"]

Using Multiple Blocks (Different Templates)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the HTML snippets are in separate blocks across different templates, the code would look like this:

.. code-block:: python

    class MyHxRequest(BaseHxRequest):
        name ="my_hx_request"
        GET_block = {
            "template1.html": "block",
            "template2.html": ["oob_block1","oob_block2"]
        }

.. note::

    All the above examples work the same way with :code:`POST_template` and :code:`POST_block` as well.

.. note::

    Ensure that all top level blocks or templates have :code:`hx-swap-oob=True` in the html tag, excluding the one being swapped into the :code:`hx-target`.

More On Blocks:

    | :ref:`Basic Tutorial <Step 8: Use Blocks (Optional)>`
    | :ref:`Form Tutorial <Step 8: Create The HxRequest>`
    | `Django Render Block <https://github.com/clokep/django-render-block>`_
