How To Register hx-requests
---------------------------

There are two ways to register :code:`hx_requests`.

Using a File
~~~~~~~~~~~~

#. Create an :code:`hx_requests.py` file in your app.
#. Add your :code:`hx_requests` there.

Example directory structure:

.. code-block:: text

    my_app/
    |── __init__.py
    |── models.py
    |── views.py
    |── hx_requests.py  # This file contains your hx_requests
    |── urls.py
    |── templates/
    |── static/

Using a Directory
~~~~~~~~~~~~~~~~~

#. Add an :code:`hx_requests` directory to your installed app.
#. Add an :code:`__init__.py` file to the :code:`hx_requests` directory.
#. Add a file, which can be named anything, to the :code:`hx_requests` directory.
#. Add your :code:`hx_requests` to the file.

Example directory structure:

.. code-block:: text

    my_app/
    |── __init__.py
    |── models.py
    |── views.py
    |── hx_requests/
    |   |── __init__.py  # Ensures the directory is treated as a package
    |   |── my_requests.py  # Contains your hx_requests
    |── urls.py
    |── templates/
    |── static/
