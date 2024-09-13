# hx-requests

Full documentation: https://hx-requests.readthedocs.io/en/latest/#

<br>

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-blue.svg)](https://docs.astral.sh/ruff/formatter/)
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
- Built in `HXRequests` to reduce boilerplate code

See full documentation here: https://hx-requests.readthedocs.io/en/latest/#

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
</br>
Hyperscript: `<script src="https://unpkg.com/hyperscript.org@0.9.8"></script>`

# Contributing to this repository

## Getting setup

- This project is using poetry
- pre-commit is used for CI (code formatting, linting, etc...)
- There is a dev container that can be used with vs-code


## Committing

Must follow Conventional Commit
https://www.conventionalcommits.org/en/v1.0.0/
