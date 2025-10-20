import os

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Dyablo'
copyright = '2025, The Dyablo Team'
author = 'The Dyablo Team'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.imgmath', 'breathe']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = [
    'css/custom.css',
]

# -- Sphinx math configuration
imgmath_image_format = 'svg'
imgmath_font_size = 16


# -- Breathe - Doxygen/Sphinx connection -------------------------------------
## Only include Breathe if the doxygen path has been imported into the project
if os.path.exists('../doxygen'):
    extensions.append('breathe')
    breathe_projects = {
        "reference": "../doxygen"
    }
    breathe_default_project = "reference"