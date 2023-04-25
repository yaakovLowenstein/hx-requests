# hx-requests
<br>

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Code style: djlint](https://img.shields.io/badge/html%20style-djlint-blue.svg)](https://www.djlint.com)

Hx-requests is a package to simplify the usage of htmx with Django.
It enables an application to make asyncronous requests without clogging up
views and urls with extra code. It simplifies making django forms post asyncronously
with htmx, and many other awesome features.

The idea of hx-requests is that `HXRequests` absorb all htmx requests.
Define an `HXRequest` and
observe the magic of `hx-requests`.

- No need to define extra urls to handle these requests
- No need to add anything extra in views
- Reusable `HXRequests` across views
- Built in `HXReuqests` to reduce boilerplate code

# Installation

```python
pip install hx-requests
```

```python
INSTALLED_APPS = (
    ...
    'hx_requests',
)
 ```

**Note**
It's assumed that htmx is already included in the base html file. It's also recommended to include hyperscript.
Htmx: `<script src="https://unpkg.com/htmx.org@1.8.6"></script>`
Hyperscript: `<script src="https://unpkg.com/hyperscript.org@0.9.8"></script>`

# Contributing to this repository

**Warning CI is not setup yet, but will be at a later date.**
## Getting setup


```bash
# If your system has python3.10 installed make sure the virtual environment is using 3.8
poetry env use python3.8

# Install packages
poetry install

# Install pre-commit hooks
pre-commit install -t pre-commit -t pre-push -t commit-msg

# Activate the virtual environment
poetry shell
```


## Committing

Must follow Conventional Commit
https://www.conventionalcommits.org/en/v1.0.0/
