# SPDX-FileCopyrightText: 2021 - 2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import datetime
import os
import sys


# -- Project information -----------------------------------------------------


def doc_target_version(semantic_version: str) -> str:
    if not semantic_version:
        return ""
    major_version = semantic_version.split(".", 1)[0]
    return f"{major_version}.x"


def read_version_from_ci() -> str:
    """Read the version for the documentation from the pipeline definition."""
    doc_target_key = os.environ.get("DOC_TARGET_VERSION")
    if doc_target_key:
        return doc_target_version(doc_target_key)

    semantic_version = os.environ.get("SEMANTIC_VERSION")
    if semantic_version:
        return doc_target_version(semantic_version)

    return ""


release = doc_target_version(read_version_from_ci())
version = release
project = f"SCIM Client for Nubus documentation {release}".rstrip()
author = "Univention GmbH"
year_range = datetime.datetime.now(tz=datetime.UTC).date().year
start_year = 2026
if year_range > start_year:
    year_range = f"{start_year}-{year_range}"
copyright = f"{year_range}, {author}"
html_show_copyright = True
language = "en"

html_title = project

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_copybutton",
    "sphinxcontrib.spelling",
    "univention_sphinx_extension",
    "sphinx_last_updated_by_git",
    "sphinx.ext.intersphinx",
    "sphinx_design",
]

# For more configuration options of Sphinx-copybutton, see the documentation
# https://sphinx-copybutton.readthedocs.io/en/latest/index.html
copybutton_prompt_text = r"\$ "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "univention_sphinx_book_theme"

doc_base = os.path.basename(os.path.dirname(__file__))

html_theme_options = {
    "show_source_license": True,
    "typesense_search": True,
    "typesense_document": doc_base,
    "typesense_document_version": release,
    "univention_matomo_tracking": True,
    "univention_docs_deployment": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []  # value is usually ['_static']

git_last_updated_timezone = "Europe/Berlin"

numfig = True

suppress_warnings = ["git.too_shallow"]

if "spelling" in sys.argv:
    spelling_lang = "en"
    spelling_show_suggestions = True
    spelling_word_list_filename = ["spelling_wordlist"]

root_doc = "contents"

intersphinx_mapping = {
    "uv-nubus-kubernetes-operation": (
        "https://docs.software-univention.de/nubus-kubernetes-operation/1.x/en/",
        None,
    ),
}

linkcheck_ignore = [
    r"http://provisioning-api",  # From SCIM Client Helm Chart reference
    r"http://scim-server",  # From SCIM Client Helm Chart reference
]

git_untracked_show_sourcelink = True
# See Univention Sphinx Extension for its options.
# https://git.knut.univention.de/univention/documentation/univention_sphinx_extension
# Information about the feedback link.
univention_feedback = True
# Information about the license statement for the source files
univention_pdf_show_source_license = True
univention_doc_basename = doc_base
univention_use_doc_base = True
univention_project_basename = doc_base
univention_release_language_scheme = "{release}/{language}"
