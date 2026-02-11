# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Standard library
import logging
import os
import sys
import urllib.parse
import warnings

from docutils import nodes

try:
    from sphinx.addnodes import pending_xref
except ImportError:
    pending_xref = None

# -- Path setup --------------------------------------------------------------
# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath('../../src'))

# Silence Streamlit "No runtime found" when autodoc imports streamlit_app (no server running).
# Set level before any streamlit import so the warning is never emitted.
logging.getLogger('streamlit').setLevel(logging.ERROR)
logging.getLogger('streamlit.runtime').setLevel(logging.ERROR)
logging.getLogger('streamlit.runtime.caching').setLevel(logging.ERROR)
logging.getLogger('streamlit.runtime.caching.cache_data_api').setLevel(logging.ERROR)


class _DuplicateObjectFilter(logging.Filter):
    """Hide Sphinx "duplicate object description" warnings (no type/subtype set by Python domain)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, 'levelno', 0) != logging.WARNING:
            return True
        try:
            msg = record.getMessage()
        except Exception:
            msg = str(getattr(record, 'msg', ''))
        if 'duplicate object description' in msg and 'use :no-index:' in msg:
            return False
        return True


def _skip_imported_member(app, what: str, name: str, obj: object, skip: bool, options: dict) -> bool:
    """Skip members that are not defined in the module being documented.

    Only the module that *defines* a symbol should document it. So we skip:
    - Imports from other packages (e.g. Path from pathlib)
    - Re-exports from other modules of the same project (e.g. t from utils in main_program)
    """
    if skip:
        return True
    if what != 'module':
        return skip
    # Current module being documented (set by ModuleDocumenter.document_members)
    current_module = getattr(
        getattr(app.env, 'current_document', None), 'autodoc_module', None
    )
    if current_module is None:
        return skip
    obj_module = getattr(obj, '__module__', None)
    if obj_module is None:
        return skip
    # Skip if the object is defined in a different module (external or same project)
    if obj_module != current_module:
        return True
    return skip


# Map .md link targets (from docs/*.md) to Sphinx document names (output .html)
# Top-level docs
_DOC_MD_TO_HTML = {
    'introduction.md': 'introduction.html',
    'installation.md': 'installation.html',
    'usage.md': 'usage.html',
    'configuration.md': 'configuration.html',
    'streamlit-guide.md': 'streamlit-guide.html',
    'tkinter-guide.md': 'tkinter-guide.html',
    'extending.md': 'extending.html',
    'customization.md': 'customization.html',
    'troubleshooting.md': 'troubleshooting.html',
    'contributing.md': 'contributing.html',
    'license.md': 'license.html',
}
# API index.md links to docs/api/*.md; Sphinx builds API ref from modules/*.rst → map to module pages
_API_MD_TO_MODULE_HTML = {
    'config.md': 'modules/core.html',
    'i18n.md': 'modules/core.html',
    'fitting_functions.md': 'modules/fitting.html',
    'fitting_utils.md': 'modules/fitting.html',
    'workflow_controller.md': 'modules/fitting.html',
    'custom_function_evaluator.md': 'modules/fitting.html',
    'estimators.md': 'modules/fitting.html',
    'data_loader.md': 'modules/loaders.html',
    'loading_utils.md': 'modules/loaders.html',
    'plot_utils.md': 'modules/plotting.html',
    'ui_main_menu.md': 'modules/frontend.html',
    'ui_dialogs.md': 'modules/frontend.html',
    'image_utils.md': 'modules/frontend.html',
    'keyboard_nav.md': 'modules/frontend.html',
    'streamlit_app.md': 'modules/streamlit_app.html',
    'exceptions.md': 'modules/utils.html',
    'logger.md': 'modules/utils.html',
    'validators.md': 'modules/utils.html',
}
_DOC_MD_TO_HTML = {**_DOC_MD_TO_HTML, **_API_MD_TO_MODULE_HTML}


def _norm_base(raw: str) -> str:
    path_part = raw[1:] if raw.startswith('#') else raw.split('#')[0]
    path_part = urllib.parse.unquote(path_part).replace('\\', '/')
    return os.path.basename(path_part)


# Docname (no extension) for each .md key, for get_relative_uri
_DOC_HTML_TO_DOCNAME = {v: v.replace('.html', '') for v in _DOC_MD_TO_HTML.values()}


def _rewrite_doc_md_links(app, doctree, docname):
    """Rewrite links to docs/*.md so they point to the built .html (works in both .md and Sphinx)."""
    builder = getattr(app, 'builder', None)
    get_uri = getattr(builder, 'get_relative_uri', None) if builder else None

    def refuri_for(base: str) -> str:
        html = _DOC_MD_TO_HTML.get(base)
        if not html or not get_uri:
            return html or ''
        target_doc = _DOC_HTML_TO_DOCNAME.get(html)
        if target_doc:
            return get_uri(docname, target_doc)
        return html

    # Fix reference nodes (resolved or failed refs that became reference with wrong refuri/refid)
    for node in doctree.traverse(nodes.reference):
        for attr in ('refuri', 'refid'):
            raw = node.get(attr, '')
            if not raw:
                continue
            base = _norm_base(raw)
            if base in _DOC_MD_TO_HTML:
                node['refuri'] = refuri_for(base)
                if attr == 'refid' and 'refid' in node:
                    del node['refid']
                break
    # Replace unresolved pending_xref that point to our .md docs with a proper reference node
    if pending_xref is not None:
        doc_to_html = {
            **_DOC_MD_TO_HTML,
            'configuration': 'configuration.html', 'usage': 'usage.html',
            'installation': 'installation.html', 'troubleshooting': 'troubleshooting.html',
            'introduction': 'introduction.html', 'streamlit-guide': 'streamlit-guide.html',
            'tkinter-guide': 'tkinter-guide.html', 'extending': 'extending.html',
            'customization': 'customization.html', 'contributing': 'contributing.html',
            'license': 'license.html',
        }
        for node in list(doctree.traverse(pending_xref)):
            reftarget = node.get('reftarget', '')
            base = _norm_base(reftarget) if reftarget else (str(reftarget).strip() or '')
            if base in doc_to_html:
                html = doc_to_html[base]
                target_doc = html.replace('.html', '')
                uri = get_uri(docname, target_doc) if get_uri else html
                ref = nodes.reference(
                    '', '', *node.children, refuri=uri, internal=True
                )
                ref['classes'] = node.get('classes', [])
                node.replace_self(ref)


def setup(app):  # noqa: D103
    """Register filter to suppress duplicate object description warnings and rewrite doc links."""
    def add_filters(_app):
        # Attach at source so duplicate-object warnings from Python domain never reach handlers
        logging.getLogger('sphinx.domains.python').addFilter(_DuplicateObjectFilter())
        # Also on sphinx handlers in case propagation path differs
        for handler in logging.getLogger('sphinx').handlers:
            handler.addFilter(_DuplicateObjectFilter())

    app.connect('builder-inited', add_filters)
    app.connect('autodoc-skip-member', _skip_imported_member)
    app.connect('doctree-resolved', _rewrite_doc_md_links)
    return {'version': '0.1', 'parallel_read_safe': True}


# Silence deprecation from myst_parser (RemovedInSphinx10Warning) until they fix it
warnings.filterwarnings('ignore', category=DeprecationWarning, module='myst_parser')

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'RegressionLab'
copyright = '2026, Alejandro Mata Ali'
author = 'Alejandro Mata Ali'
# Third-party packages (optional for ReadTheDocs)
try:
    from dotenv import load_dotenv
    env_path = os.path.abspath('../../.env')
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # dotenv not required for documentation build

release = '0.9.1'
version = '0.9.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',          # Auto-generate documentation from docstrings
    'sphinx.ext.napoleon',         # Support for NumPy and Google style docstrings
    'sphinx.ext.viewcode',         # Add links to highlighted source code
    'sphinx.ext.githubpages',      # Create .nojekyll file for GitHub Pages
    'sphinx.ext.intersphinx',      # Link to other projects' documentation
    'sphinx.ext.todo',             # Support for TODO items
    'sphinx.ext.coverage',         # Check documentation coverage
    'sphinx.ext.mathjax',          # Math support via MathJax
    'myst_parser',                 # Markdown support
    'sphinxcontrib.relativeinclude',  # Resolve image paths relative to included file (e.g. docs/)
    # 'sphinx_autodoc_typehints' disabled: hide types for cleaner documentation
]

# MyST Parser configuration
myst_heading_anchors = 2  # Generate anchors for h1 and h2 for in-doc links
myst_enable_extensions = [
    "colon_fence",      # ::: fences for directives
    "deflist",          # Definition lists
    "dollarmath",       # Math with $ and $$
    "fieldlist",        # Field lists
    "html_admonition",  # HTML admonitions
    "html_image",       # HTML images
    "linkify",          # Auto-detect URLs
    "replacements",     # Text replacements
    "smartquotes",      # Smart quotes
    "strikethrough",    # ~~strikethrough~~
    "substitution",     # Variable substitution
    "tasklist",         # Task lists with [ ] and [x]
]

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['README.md']  # Exclude README.md from docs if present

# Reduce noise: ambiguous cross-refs, missing file refs (duplicate object is filtered in setup())
suppress_warnings = [
    'ref.python',
    'ref.doc',
    'myst.xref_missing',  # e.g. THIRD_PARTY_LICENSES.md (file outside doc tree)
    'myst.iref_ambiguous',  # extending/contributing matched by intersphinx (numpy, pandas, etc.)
]

language = 'en'

# The root toctree document (replaces deprecated master_doc)
root_doc = 'index'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
# Create _static directory if it doesn't exist
import os
static_path = os.path.join(os.path.dirname(__file__), '_static')
if not os.path.exists(static_path):
    os.makedirs(static_path, exist_ok=True)
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'vcs_pageview_mode': '',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add logo if available
html_logo = '_static/RegressionLab_logo.png'

# Add favicon if available
# html_favicon = '_static/favicon.ico'

# Add custom CSS files
# html_css_files = [
#     'custom.css',
# ]

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'preamble': '',
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files
latex_documents = [
    (root_doc, 'RegressionLab.tex', 'RegressionLab Documentation',
     'Alejandro Mata Ali', 'manual'),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    (root_doc, 'regressionlab', 'RegressionLab Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (root_doc, 'RegressionLab', 'RegressionLab Documentation',
     author, 'RegressionLab', 'Scientific curve fitting application with GUI',
     'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------
epub_title = project
epub_exclude_files = ['search.html']

# -- Extension configuration -------------------------------------------------

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = False  # Don't show type annotations in attributes

# Use legacy class-based autodoc so autodoc-skip-member is applied to module members
# (Sphinx 5+ uses a new implementation that may not emit skip-member for all members)
autodoc_use_legacy_class_based = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
# Hide types in documentation for cleaner reading (docstrings are sufficient)
autodoc_typehints = 'none'

# Todo extension
todo_include_todos = True
