# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'exax'
copyright = '2023, abcd'
author = 'abcd'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
			  'sphinx.ext.autosummary',
			  'sphinx.ext.autosectionlabel',
			  'sphinxarg.ext']

autosectionlabel_prefix_document = True  # Make sure the target is unique

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'nature'  # 'classic', 'alabaster'
html_static_path = ['_static']
