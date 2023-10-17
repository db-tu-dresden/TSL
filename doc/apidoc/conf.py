# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import textwrap
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Template SIMD Library'
copyright = '2023, me'
author = 'me'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
	'breathe',
	'exhale'
]
breathe_projects = {
    "My Project": "./_doxygen/xml"
}
breathe_default_project = "My Project"
exhale_args = {
    # These arguments are required
    "containmentFolder":     "./api",
    "rootFileName":          "library_root.rst",
    "rootFileTitle":         "Library API",
    "doxygenStripFromPath":  "../../tsl_lib",
    # Suggested optional arguments
    "createTreeView":        True,
    # TIP: if using the sphinx-bootstrap-theme, you need
    # "treeViewIsBootstrap": True,
    "exhaleExecutesDoxygen": True,
    "exhaleDoxygenStdin": textwrap.dedent('''
        EXTRACT_ALL = YES
        SOURCE_BROWSER = YES
        EXTRACT_STATIC = YES
        OPTIMIZE_OUTPUT_FOR_C  = YES
        HIDE_SCOPE_NAMES = YES
        QUIET = YES
        INPUT = ../../tsl_lib/include
        FILE_PATTERNS = *.c *.h *.cpp *.hpp
        EXAMPLE_RECURSIVE = YES
        GENERATE_TREEVIEW = YES
        RECURSIVE = YES
    ''')
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Tell sphinx what the primary language being documented is.
primary_domain = 'cpp'

# Tell sphinx what the pygments highlight language should be.
highlight_language = 'cpp'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
