# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Standard library
import logging
import os
import re
import sys
import urllib.parse
import warnings

from docutils import nodes

try:
    from sphinx.addnodes import pending_xref
except ImportError:
    pending_xref = None

# Patch sphinxcontrib.relativeinclude.LinkTranslator to handle URL fragments (#anchor).
# The stock LinkTranslator treats reftarget as a file path and fails for links like
# configuration.md#update-check-tkinter or fragment-only refs like update-check-tkinter.
def _patch_link_translator() -> None:
    from os.path import relpath

    from sphinxcontrib import relativeinclude

    _logger = logging.getLogger("sphinxcontrib.relativeinclude")
    _identify = getattr(relativeinclude, "_identify", lambda o: f"{type(o).__name__}")

    def _patched_visit(self: "relativeinclude.LinkTranslator", node: nodes.Node) -> None:
        if not isinstance(node, nodes.Element) or (
            hasattr(node, "resolved") and getattr(node, "resolved", False)
        ):
            return
        for attr in ("reftarget", "uri"):
            if attr not in node.attributes:
                continue
            old_target = node[attr]
            if any(old_target.startswith(s) for s in ("http", "https", "data")):
                continue
            # Split path and fragment
            if "#" in old_target:
                path_part, frag = old_target.split("#", 1)
                fragment = "#" + frag if frag else ""
            else:
                path_part, fragment = old_target, ""
            # Skip fragment-only (same-doc anchor)
            if not path_part.strip():
                if hasattr(node, "resolved"):
                    node.resolved = True  # type: ignore[attr-defined]
                continue
            # Resolve path part only
            try:
                new_abs = (self.rel_base / path_part).resolve()
            except Exception:
                continue
            if new_abs.exists():
                node[attr] = relpath(new_abs, self.abs_base) + fragment
                if hasattr(node, "resolved"):
                    node.resolved = True  # type: ignore[attr-defined]
                continue
            # Path doesn't exist: skip without warning if it looks like a fragment (no extension)
            if "." not in path_part and "/" not in path_part and "\\" not in path_part:
                if hasattr(node, "resolved"):
                    node.resolved = True  # type: ignore[attr-defined]
                continue
            # Otherwise warn (original behavior)
            _logger.warning(
                f"{_identify(self)}: couldn't resolve {_identify(node)} "
                f"target path {new_abs} derived from {old_target}. Skipping!"
            )
        if hasattr(node, "resolved"):
            node.resolved = True  # type: ignore[attr-defined]

    relativeinclude.LinkTranslator.default_visit = _patched_visit

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
    'saving_utils.md': 'modules/loaders.html',
    'data_analysis.md': 'modules/data_analysis.html',
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


def _get_fragment(raw: str) -> str:
    """Extract fragment (#anchor) from raw ref if present."""
    if '#' in raw and not raw.startswith('#'):
        part = raw.split('#', 1)[1].strip()
        if part:
            return '#' + urllib.parse.unquote(part)
    return ''


# Docname (no extension) for each .md key, for get_relative_uri
_DOC_HTML_TO_DOCNAME = {v: v.replace('.html', '') for v in _DOC_MD_TO_HTML.values()}


def _images_path_to_static(uri: str) -> str:
    """Convert ../images/... or ../../../images/... to _static/... for ReadTheDocs.

    On ReadTheDocs, Spanish docs are at /es/latest/; relative paths like ../../../images/
    escape the site root and break. Using _static/ (copied via html_static_path) works
    for all URL depths (en/latest/, es/latest/, etc.).
    """
    for prefix in ('../images/', '../../images/', '../../../images/'):
        if uri.startswith(prefix):
            return '_static/' + uri[len(prefix):]
    return uri


def _rewrite_locale_asset_paths(doctree: nodes.document, language: str = "en") -> None:
    """Rewrite image paths so they work on ReadTheDocs for both en and es builds.

    Use _static/ for doc images (copied via html_static_path) so paths work regardless
    of URL depth (/es/latest/, /en/latest/, etc.).
    For Spanish (es), replace en_documentation with es_documentation so locale-specific
    images are used.
    """
    use_es_images = language == "es"
    for node in doctree.traverse(nodes.image):
        uri = node.get('uri', '')
        if use_es_images and 'en_documentation' in uri:
            uri = uri.replace('en_documentation', 'es_documentation')
        new_uri = _images_path_to_static(uri)
        if new_uri != node.get('uri', ''):
            node['uri'] = new_uri
        if 'candidates' in node:
            node['candidates'] = {'*': node['uri']}


# Regex for paragraphs that are only markdown image or link (locale builds sometimes
# inject translated strings as literal text instead of parsed nodes).
# Match both ../images/ and ../../images/ (path may vary by context)
_IMAGE_MARKDOWN_RE = re.compile(
    r'^!\s*\[([^\]]*)\]\s*\(\s*((?:\.\./)+images/[^)]+)\s*\)\s*$',
    re.DOTALL,
)
_LINK_MARKDOWN_RE = re.compile(
    r'^\[([^\]]*)\]\s*\(\s*([^)]+)\s*\)\s*$',
    re.DOTALL,
)
# Link inside a paragraph: [text](url) or [text] (url) - allow space between ] and (
_LINK_INLINE_RE = re.compile(
    r'\[([^\]]*)\]\s*\(\s*([^)]+)\s*\)',
)
# Inline image inside a paragraph: ![alt](path) - path may be ../images/...
_IMAGE_INLINE_RE = re.compile(
    r'!\s*\[([^\]]*)\]\s*\(\s*((?:\.\./)+images/[^)]+)\s*\)',
)
_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')


def _is_image_path(target: str) -> bool:
    """Return True if target is an image path (e.g. ../images/.../file.png)."""
    t = target.strip().lower()
    return any(t.endswith(ext) for ext in _IMAGE_EXTENSIONS) or (
        'images/' in t and any(ext in t for ext in _IMAGE_EXTENSIONS)
    )


def _image_uri_from_path(path: str) -> str:
    """Normalize image path to _static/ for ReadTheDocs compatibility."""
    if "images/" in path:
        return "_static/" + path.split("images/", 1)[1]
    return path


def _convert_literal_markdown_paragraphs(app, doctree: nodes.document, docname: str) -> None:
    """Convert paragraphs/literal_blocks that are literal markdown image/link into proper nodes.

    In gettext builds, translated content can be inserted as plain text; the result
    is raw markdown like ![alt](../images/...) or [text](installation.md) shown
    on the page. Replace such nodes with image and reference nodes.
    """
    # Only needed for non-English builds (gettext injects literal strings)
    if getattr(app.config, "language", "en") == "en":
        return

    builder = getattr(app, "builder", None)
    get_uri = getattr(builder, "get_relative_uri", None) if builder else None

    # Handle both paragraph and literal_block (gettext may put content in either)
    for node in list(doctree.traverse(nodes.paragraph)) + list(
        doctree.traverse(nodes.literal_block)
    ):
        text = node.astext().strip()
        if not text:
            continue

        # Whole paragraph is a markdown image: ![alt](../images/...) or ![alt](../../images/...)
        match = _IMAGE_MARKDOWN_RE.match(text)
        if match:
            alt = match.group(1).strip()
            path = match.group(2).strip()
            uri = _image_uri_from_path(path) if "images/" in path else path
            img = nodes.image(uri=uri, alt=alt)
            # Sphinx post_process_images expects image nodes to have 'candidates'
            img["candidates"] = {"*": uri}
            node.replace_self(img)
            continue

        # Whole paragraph is a markdown link: [text](url) or [text](installation.md)
        match = _LINK_MARKDOWN_RE.match(text)
        if match:
            link_text = match.group(1).strip()
            target = match.group(2).strip()
            # If target is an image path, render as img not link
            if _is_image_path(target):
                uri = _image_uri_from_path(target)
                from html import escape
                raw = nodes.raw(
                    "",
                    f'<img src="{escape(uri)}" alt="{escape(link_text)}" />',
                    format="html",
                )
                node.replace_self(raw)
                continue
            if any(target.startswith(s) for s in ("http://", "https://", "mailto:")):
                refuri = target
            elif get_uri:
                base = _norm_base(target)
                fragment = _get_fragment(target)
                html = _DOC_MD_TO_HTML.get(base)
                if html:
                    target_doc = _DOC_HTML_TO_DOCNAME.get(html) or html.replace(
                        ".html", ""
                    )
                    refuri = get_uri(docname, target_doc) + fragment
                else:
                    refuri = target
            else:
                refuri = target
            # Use raw HTML to avoid Sphinx HTML5 writer assertion on reference+single child
            from html import escape
            escaped_text = escape(link_text)
            escaped_uri = escape(refuri)
            raw = nodes.raw("", f'<a href="{escaped_uri}">{escaped_text}</a>', format="html")
            node.replace_self(raw)
            continue

        # Paragraph contains inline image: "text ![alt](../images/...)" - render img
        match_img = _IMAGE_INLINE_RE.search(text)
        if match_img and _IMAGE_INLINE_RE.search(text, match_img.end()) is None:
            from html import escape
            before = text[: match_img.start()]
            alt = match_img.group(1).strip()
            path = match_img.group(2).strip()
            uri = _image_uri_from_path(path)
            after = text[match_img.end() :]
            new_children = []
            if before:
                new_children.append(nodes.Text(before))
            new_children.append(
                nodes.raw("", f'<img src="{escape(uri)}" alt="{escape(alt)}" />', format="html")
            )
            if after:
                new_children.append(nodes.Text(after))
            node.clear()
            for c in new_children:
                node += c
            continue

        # Paragraph contains one markdown link in the middle (e.g. "Consulta la [Guía](installation.md) para...")
        match_inline = _LINK_INLINE_RE.search(text)
        if match_inline and _LINK_INLINE_RE.search(text, match_inline.end()) is None:
            # Exactly one link in the paragraph
            from html import escape
            before = text[: match_inline.start()]
            link_text = match_inline.group(1).strip()
            target = match_inline.group(2).strip()
            after = text[match_inline.end() :]
            # If target is an image path, render as img not link
            if _is_image_path(target):
                uri = _image_uri_from_path(target)
                new_children = []
                if before:
                    new_children.append(nodes.Text(before))
                new_children.append(
                    nodes.raw("", f'<img src="{escape(uri)}" alt="{escape(link_text)}" />', format="html")
                )
                if after:
                    new_children.append(nodes.Text(after))
                node.clear()
                for c in new_children:
                    node += c
                continue
            if any(target.startswith(s) for s in ("http://", "https://", "mailto:")):
                refuri = target
            elif get_uri:
                base = _norm_base(target)
                fragment = _get_fragment(target)
                html = _DOC_MD_TO_HTML.get(base)
                if html:
                    target_doc = _DOC_HTML_TO_DOCNAME.get(html) or html.replace(".html", "")
                    refuri = get_uri(docname, target_doc) + fragment
                else:
                    refuri = target
            else:
                refuri = target
            new_children = []
            if before:
                new_children.append(nodes.Text(before))
            new_children.append(
                nodes.raw(
                    "",
                    f'<a href="{escape(refuri)}">{escape(link_text)}</a>',
                    format="html",
                )
            )
            if after:
                new_children.append(nodes.Text(after))
            node.clear()
            for c in new_children:
                node += c
            continue


def _rewrite_doc_md_links(app, doctree, docname):
    """Rewrite links to docs/*.md so they point to the built .html (works in both .md and Sphinx)."""
    # Fix image paths for locale builds (content from .po resolves paths from source/)
    language = getattr(app.config, 'language', 'en')
    _rewrite_locale_asset_paths(doctree, language)
    # Convert paragraphs that are literal markdown image/link (gettext can emit raw text)
    _convert_literal_markdown_paragraphs(app, doctree, docname)

    builder = getattr(app, 'builder', None)
    get_uri = getattr(builder, 'get_relative_uri', None) if builder else None

    def refuri_for(base: str) -> str:
        html = _DOC_MD_TO_HTML.get(base) or (base if base.endswith('.html') else None)
        if not html or not get_uri:
            return html or ''
        target_doc = _DOC_HTML_TO_DOCNAME.get(html) or (base.replace('.html', '') if base.endswith('.html') else None)
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
            if base in _DOC_MD_TO_HTML or (base.endswith('.html') and base.replace('.html', '') in {v.replace('.html', '') for v in _DOC_MD_TO_HTML.values()}):
                node['refuri'] = refuri_for(base) + _get_fragment(raw)
                if attr == 'refid' and 'refid' in node:
                    del node['refid']
                break
    # Replace unresolved pending_xref that point to our .md docs with a proper reference node
    if pending_xref is not None:
        doc_to_html = {
            **_DOC_MD_TO_HTML,
            'configuration': 'configuration.html', 'configuration.html': 'configuration.html',
            'configuration.md': 'configuration.html', 'usage': 'usage.html',
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
                uri = (get_uri(docname, target_doc) if get_uri else html) + _get_fragment(reftarget)
                ref = nodes.reference(
                    '', '', *node.children, refuri=uri, internal=True
                )
                ref['classes'] = node.get('classes', [])
                node.replace_self(ref)


def _on_missing_reference(app, env, node, contnode):
    """Resolve doc links like configuration.md#anchor that Sphinx/MyST cannot resolve."""
    reftarget = node.get('reftarget', '')
    if not reftarget or '#' not in reftarget:
        return None
    base = _norm_base(reftarget)
    fragment = _get_fragment(reftarget)
    doc_to_html = {
        'configuration.md': 'configuration.html', 'configuration.html': 'configuration.html',
        'configuration': 'configuration.html', 'installation.md': 'installation.html',
        'usage.md': 'usage.html', 'troubleshooting.md': 'troubleshooting.html',
        'introduction.md': 'introduction.html', 'streamlit-guide.md': 'streamlit-guide.html',
        'tkinter-guide.md': 'tkinter-guide.html', 'extending.md': 'extending.html',
        'customization.md': 'customization.html', 'contributing.md': 'contributing.html',
        'license.md': 'license.html',
    }
    if base not in doc_to_html:
        return None
    html = doc_to_html[base]
    target_doc = html.replace('.html', '')
    try:
        uri = app.builder.get_relative_uri(env.docname, target_doc) + fragment
    except Exception:
        uri = html + fragment
    ref = nodes.reference(
        '', '', *contnode.children, refuri=uri, internal=True
    )
    ref['classes'] = contnode.get('classes', [])
    return ref


def setup(app):  # noqa: D103
    """Register filter to suppress duplicate object description warnings and rewrite doc links."""
    _patch_link_translator()

    def add_filters(_app):
        # Attach at source so duplicate-object warnings from Python domain never reach handlers
        logging.getLogger('sphinx.domains.python').addFilter(_DuplicateObjectFilter())
        # Also on sphinx handlers in case propagation path differs
        for handler in logging.getLogger('sphinx').handlers:
            handler.addFilter(_DuplicateObjectFilter())

    app.connect('builder-inited', add_filters)
    app.connect('autodoc-skip-member', _skip_imported_member)
    app.connect('doctree-resolved', _rewrite_doc_md_links, priority=900)
    app.connect('missing-reference', _on_missing_reference)
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

release = '1.0.0'
version = '1.0.0'

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

# Language: use READTHEDOCS_LANGUAGE when building on ReadTheDocs (en/es), else default to English
language = os.environ.get('READTHEDOCS_LANGUAGE', 'en')

# Localization: required for Spanish builds. Translations live in sphinx-docs/locale/<lang>/LC_MESSAGES/
locale_dirs = ['../locale']
gettext_uuid = True
gettext_compact = False

# The root toctree document (replaces deprecated master_doc)
root_doc = 'index'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
# Ensure _static exists (Sphinx does not create it)
_static_dir = os.path.join(os.path.dirname(__file__), '_static')
os.makedirs(_static_dir, exist_ok=True)
# Doc images from project root: copied to _static/ so paths work on ReadTheDocs (/es/latest/, etc.)
_images_src = os.path.join(os.path.dirname(__file__), '..', '..', 'images')
html_static_path = ['_static', _images_src] if os.path.isdir(_images_src) else ['_static']

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

# Autodoc settings (module .rst files can omit these options for brevity)
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
    'imported-members': True,
}
# Hide types in documentation for cleaner reading (docstrings are sufficient)
autodoc_typehints = 'none'

# Only link to source for directly documented modules (faster viewcode)
viewcode_follow_imported_members = False

# Todo extension: hide TODOs on ReadTheDocs (cleaner production docs, slightly faster)
todo_include_todos = not os.environ.get('READTHEDOCS', '')
