Configuration
=============

Settings that need to be set in :code:`settings.py`.

| :code:`HX_REQUESTS_CUSTOM_VIEWS_SETUP` : *Default=None*
| Dict of custom views to a corrensponding get function that mimics the view's get EXCEPT that it does not return a response (see :ref:`Context setup by get`.)
| For example:

.. code-block:: python

    HX_REQUESTS_CUSTOM_VIEWS_SETUP = {
        'my_app.views.my_custom_view': 'my_app.view_get_functions.custom_view_get',
    }

Messages Configuration
----------------------

| :code:`HX_REQUESTS_USE_HX_MESSAGES` : *Default=False*
| Set this to True to use messages in :code:`hx-requests`. If this is False :code:`hx-requests` messages will not be displayed even if you set messages.

| :code:`HX_REQUESTS_HX_MESSAGES_TEMPLATE` : *No Default*
|
| Template to be used for displaying the messages. The context in this template has access to the :code:`messages`. Same as Django's `Messages <https://docs.djangoproject.com/en/5.0/ref/contrib/messages/#displaying-messages>`_.

Modal Configuration
-------------------
.. note::

    See :ref:`Defining a Modal Template` for a guide on overriding the default modal template.

| :code:`HX_REQUESTS_MODAL_TEMPLATE` : *Default=None*
|
| Template to be used for modals. Set to the path of your modal template.

| :code:`HX_REQUESTS_MODAL_BODY_ID` : *Default='#hx_modal_body'*
|
| A CSS selector for the modal body. This only needs to be set if :code:`HX_REQUESTS_MODAL_TEMPLATE` is overridden and '.modal-body' is not a valid selector for it.
