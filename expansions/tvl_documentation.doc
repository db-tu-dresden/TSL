# OUTPUT: docs_out_path: library_root_path.joinpath(docs)
# INPUT: library_root_path
# PROJECT_NAME: tvl_lib_name

doxygen tvl.doxy

xml/index.rst:
Welcome to TEST's documentation!
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
.. highlight:: cpp
.. doxygenindex::
.. doxygenfunction::
.. doxygenstruct::
.. doxygenenum::
.. doxygentypedef::
.. doxygenclass::


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



xml/conf.py
project = 'TEST'
copyright = '2022, TEST'
author = 'ABX'

extensions = ['sphinx.ext.todo', 'breathe' ]
breathe_projects = { "TEST": "/home/jpietrzyk/Own/Work/TVL/lib/docs/xml" }
breathe_default_project = "TEST"

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


sphinx-build ./xml ./sphinx


breathe-apidoc -o ./breathe ./xml