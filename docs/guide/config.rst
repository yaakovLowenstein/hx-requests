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
| Set this to True to use :code:`hx-requests` messaging framework. If this is False :code:`hx-requests` messages will not be displayed even if you set messages.

| :code:`HX_REQUESTS_USE_DJANGO_MESSAGE_TAGS` : *Default=False*
| Set this to True to use Django's :code:`MESSAGE_TAGS` setting for tags.

| :code:`HX_REQUESTS_HX_MESSAGE_TAGS` : *No Default*
| If you are not using Django's :code:`MESSAGE_TAGS` set this to a dict of tags.
|
| *Example*

.. code-block:: python

    MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
    }

| :code:`HX_REQUESTS_HX_MESSAGES_TEMPLATE` : *No Default*
|
| Template to be used for displaying the messages. The context in this template has access to the :code:`messages`.

Modal Configuration
-------------------
.. note::

    See :ref:`Overriding the built-in Modal` for a guide on overriding the default modal template.

| :code:`HX_REQUESTS_MODAL_TEMPLATE` : *Default='hx_requests/modal.html'*
|
| Template to be used for modals. There are two that :code:`hx-requests` comes with: 'hx_requests/modal.html' and 'hx_requests/bootstrap_modal.html. Additionally you can set this to any template you want. The context in this template has access to the modal's 'title' and 'body'.

| :code:`HX_REQUESTS_MODAL_CONTAINER_ID` : *Default='hx_modal_container'*
|
| Id of the container the modal is rendered in.

| :code:`HX_REQUESTS_MODAL_BODY_SELECTOR` : *Default='.modal-body'*
|
| A CSS selector for the modal body. This only needs to be set if :code:`HX_REQUESTS_MODAL_TEMPLATE` is overridden and '.modal-body' is not a valid selector for it.
