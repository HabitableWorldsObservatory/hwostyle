"""Sphinx configuration for hwostyle documentation."""

from importlib.metadata import version as get_version

project = "hwostyle"
release = get_version("hwostyle")
version = ".".join(release.split(".")[:2])
copyright = "2026, Corey Spohn"
author = "Corey Spohn"

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "IPython.sphinxext.ipython_console_highlighting",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autoapi_dirs = ["../src"]
autoapi_ignore = ["**/*version.py"]
autodoc_typehints = "description"
# AutoAPI already indexes fields; Napoleon should render their descriptions only.
napoleon_use_ivar = True

myst_enable_extensions = ["amsmath", "dollarmath"]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_book_theme"
html_static_path = []
master_doc = "index"
html_title = "hwostyle"

html_theme_options = {
    "repository_url": "https://github.com/HabitableWorldsObservatory/hwostyle",
    "repository_branch": "main",
    "use_repository_button": True,
    "show_toc_level": 2,
}
html_context = {
    "default_mode": "dark",
}
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst-nb",
}

nb_execution_mode = "off"
