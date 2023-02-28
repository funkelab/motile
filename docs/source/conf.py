# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os

here = os.path.abspath(os.path.dirname(__file__))
version_info = {}
with open(os.path.join(here, '..', '..', 'motile', 'version_info.py')) as fp:
    exec(fp.read(), version_info)
motile_version = version_info['_version']

project = 'motile'
copyright = '2023, Jan Funke, Ana Cristina Pascual Ramos'
author = 'Jan Funke, Ana Cristina Pascual Ramos'
version = u'{}.{}'.format(motile_version.major(), motile_version.minor())
release = str(motile_version)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
        'jupyter_sphinx',
        'sphinx.ext.autodoc',
        'sphinx.ext.githubpages',
        'sphinx.ext.mathjax',
        'sphinx_rtd_theme',
        'sphinx_togglebutton',
        'sphinxcontrib.jquery'
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'logo_only': True
}
html_logo = 'motile.svg'
html_static_path = ['_static']
html_css_files = [
    'css/custom.css'
]
html_show_sourcelink = False

togglebutton_hint = ""
togglebutton_hint_hide = ""

pygments_style = 'lovelace'
