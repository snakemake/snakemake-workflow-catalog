# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "snakemake-workflow-catalog"
copyright = "2025, The Snakemake team."
author = "Johannes Koester, Michael Jahn"

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from build_wf_pages import build_wf_pages
from build_wf_tables import build_wf_tables
from sphinxawesome_theme.postprocess import Icons

build_wf_pages()
build_wf_tables()

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinxcontrib.jquery",
    "sphinx_datatables",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinxawesome_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "logo_light": "_static/logo-snake.svg",
    "logo_dark": "_static/logo-snake.svg",
    "show_breadcrumbs": True,
    "globaltoc_includehidden": True,
    "show_prev_next": True,
    "main_nav_links": {
        "GitHub page": "https://github.com/snakemake/snakemake-workflow-catalog",
        "Snakemake homepage": "https://snakemake.github.io",
        "Snakemake documentation": "https://snakemake.readthedocs.io",
    },
}
html_title = "Snakemake workflow catalog"
pygments_style = "sphinx"
html_permalinks_icon = Icons.permalinks_icon
suppress_warnings = ["myst.xref_missing", "myst.header"]
myst_enable_extensions = ["colon_fence", "attrs_block"]
myst_heading_anchors = 2
html_sidebars = {
    "**": ["globaltoc.html"],
}

# -- Settings for data-tables plugin -----------------------------------------
# for all settings see https://datatables.net/reference/option/
datatables_version = "1.13.4"
datatables_class = "sphinx-datatable"
datatables_options = {
    "order": [[4, "desc"]],
}

# -- Manage redirection of old to new wf pages -------------------------------
html_js_files = [
    "redirect.js",
]
