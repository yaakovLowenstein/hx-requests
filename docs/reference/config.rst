Configuration
=============

These settings should be added to :code:`settings.py` to control :code:`hx-requests` behavior.

Messages Configuration
----------------------

HX_REQUESTS_USE_HX_MESSAGES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** `False`

Set this to `True` to enable `hx-requests` messages.
If `False`, messages will not be displayed, even if they are set.

HX_REQUESTS_HX_MESSAGES_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** *No Default*

Path to the template used for displaying messages.
The context in this template has access to :code:`messages`, following the same behavior as Django’s
`Messages framework <https://docs.djangoproject.com/en/5.0/ref/contrib/messages/#displaying-messages>`_.

Modal Configuration
-------------------

HX_REQUESTS_MODAL_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** `None`

Path to the template used for modals.

HX_REQUESTS_MODAL_BODY_ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Default:** `#hx_modal_body`

A CSS selector for the modal body.
Set this only if :code:`HX_REQUESTS_MODAL_TEMPLATE` is overridden.

.. note::
    See :ref:`How To Use Modals` for details on overriding the default modal template.
