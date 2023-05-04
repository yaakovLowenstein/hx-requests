# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# sys.path.insert(0, os.path.abspath("."))
# sys.path.insert(0, os.path.abspath("../"))
# sys.path.insert(0, os.path.abspath("../hx_requests/"))

project = "hx-requests"
copyright = "2023, Yaakov Lowenstein"
author = "Yaakov Lowenstein"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autosectionlabel", "sphinx.ext.autodoc", "autoapi.extension"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

root_doc = "index"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

autoapi_dirs = ["../hx_requests"]
# autoapi_root = "reference/"
autoapi_add_toctree_entry = False
autoapi_keep_files = True
# autoapi_generate_api_docs = False
