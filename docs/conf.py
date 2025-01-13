# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import json
import os
import sys
from datetime import date

project = "rtfm"

version = "0.0.0"
author = "Unknown Author"
try:
    with open("../plugin.json") as f:
        data = json.load(f)
        version = data["Version"]
        author = data["Author"]
except Exception:
    pass

release = version
author = author

current_year = date.today().year
copyright = f"{current_year}, {author}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))
sys.path.append(os.path.abspath("extensions"))

extensions = [
    "list_presets",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
# html_css_files = ["style.css"]
# html_js_files = ["custom.js"]
# html_favicon = "./images/flow_logo.ico"
