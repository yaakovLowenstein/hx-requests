Installation
============

::

    pip install hx-requests

Once installed add :code:`hx_requests` to your :code:`INSTALLED_APPS` in settings.py::

    INSTALLED_APPS = (
        ...
        'hx_requests',
    )

.. note::

    | It's assumed that htmx is already included in the base html file. It's also recommended to include hyperscript.
    | Htmx: :code:`<script src="https://unpkg.com/htmx.org@1.8.6"></script>`
    | Hyperscript: :code:`<script src="https://unpkg.com/hyperscript.org@0.9.8"></script>`
