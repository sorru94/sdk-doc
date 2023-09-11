# Copyright 2024 SECO Mind Srl
#
# SPDX-License-Identifier: CC0-1.0

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Astarte SDKs'
copyright = '2024 SECO Mind Srl'
author = 'Simone Orru'
release = ''

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser', 'sphinx_copybutton']
templates_path = ['_templates']
exclude_patterns = []

# -- Options for myst-parser ----------------------------------------------------------

myst_heading_anchors = 3

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_title = f"{project} documentation"
html_static_path = ['_static']
html_favicon = '_static/mascotte.svg'
