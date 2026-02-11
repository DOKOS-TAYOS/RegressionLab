# RegressionLab Documentation

This directory contains the complete documentation for RegressionLab. The documentation is organized to serve both end users and developers.

## Documentation Structure

### User Documentation

**Getting Started**
- [`index.md`](index.md) - Main documentation index and overview
- [`introduction.md`](introduction.md) - Project introduction, objectives, and benefits
- [`installation.md`](installation.md) - Installation instructions for all platforms
- [`usage.md`](usage.md) - General user guide covering all operation modes

**Configuration & Customization**
- [`configuration.md`](configuration.md) - Complete guide to `.env` configuration options
- [`streamlit-guide.md`](streamlit-guide.md) - Detailed guide for the web interface
- [`tkinter-guide.md`](tkinter-guide.md) - Detailed guide for the desktop interface

**Developer Documentation**
- [`extending.md`](extending.md) - How to add new fitting functions
- [`customization.md`](customization.md) - How to replace the fitting core (SciPy alternatives)
- [`api/`](api/) - Technical API documentation for developers

**Reference & Support**
- [`troubleshooting.md`](troubleshooting.md) - Known issues, solutions, and roadmap
- [`contributing.md`](contributing.md) - Contributing guidelines
- [`license.md`](license.md) - MIT License and copyright information

## Quick Navigation

### I want to...

**...get started quickly**
→ Start with [Introduction](introduction.md), then [Installation](installation.md)

**...learn how to use RegressionLab**
→ Read the [User Guide](usage.md), then interface-specific guides:
  - [Streamlit Guide](streamlit-guide.md) for web version
  - [Tkinter Guide](tkinter-guide.md) for desktop version

**...customize the appearance**
→ See [Configuration Guide](configuration.md)

**...add a new equation**
→ Follow [Extending RegressionLab](extending.md)

**...use a different optimization library**
→ Read [Customizing the Fitting Core](customization.md)

**...contribute to the project**
→ Check [Contributing Guidelines](contributing.md)

**...fix a problem**
→ Search [Troubleshooting Guide](troubleshooting.md)

**...understand the code**
→ Browse [API Documentation](api/index.md)

## For ReadTheDocs / Sphinx

This documentation is designed to be compatible with ReadTheDocs and Sphinx. To build the documentation with Sphinx:

### Setup

```bash
cd sphinx-docs
pip install -r requirements.txt
```

### Build

**Linux/macOS:**
```bash
./build_docs.sh
```

**Windows:**
```batch
build_docs.bat
```

### View

**Linux/macOS:**
```bash
./open_docs.sh
```

**Windows:**
```batch
open_docs.bat
```

The built documentation will be in `sphinx-docs/build/html/`.

## Markdown Features Used

This documentation uses standard Markdown with these extensions:

- **Code blocks** with syntax highlighting
- **Tables** for structured data
- **Links** (internal and external)
- **Images** (stored in `images/` subdirectory)
- **Admonitions** (Note, Warning, etc. - for Sphinx)
- **Math** (LaTeX syntax - for Sphinx)

## Documentation Standards

When contributing to documentation:

### Style Guide

1. **Be clear and concise**: Use simple language.
2. **Use examples**: Code examples, screenshots, workflows.
3. **Link related content**: Cross-reference other documentation.
4. **Stay up-to-date**: Update docs when code changes.
5. **Test examples**: Ensure code examples actually work.

### File Naming

- Use lowercase with hyphens: `configuration-guide.md`.
- Be descriptive: `installation.md` not `install.md`.
- Group related files: `api/` directory for API docs.

### Structure

Each document should have:

1. **Title** (H1): Clear, descriptive.
2. **Introduction**: What this document covers.
3. **Table of contents** (for long docs).
4. **Sections** (H2, H3): Logical organization.
5. **Examples**: Where appropriate.
6. **Cross-references**: Links to related docs.
7. **Navigation**: "Next steps" or "See also".

### Code Examples

```python
# Always include:
# 1. Comments explaining what the code does
# 2. Expected output or behavior
# 3. Complete, runnable examples when possible

import numpy as np
from fitting.fitting_functions import func_lineal

# Example: Calculate y values for linear function
x = np.array([1, 2, 3, 4, 5])
m = 2.5
y = func_lineal(x, m)

print(y)  # Output: [ 2.5  5.   7.5 10.  12.5]
```

### Screenshots

- Store in `docs/images/`.
- Use descriptive filenames: `tkinter-main-menu-spanish.png`.
- Include in both languages if UI differs.
- Optimize file size (< 500 KB per image).
- Use PNG for UI screenshots, JPEG for photos.

## Building Locally

### Preview Markdown

Use a Markdown previewer:

- **VS Code**: Built-in Markdown preview (Ctrl+Shift+V)
- **Typora**: WYSIWYG Markdown editor
- **Grip**: GitHub-flavored Markdown preview
  ```bash
  pip install grip
  grip docs/index.md
  ```

### Build Sphinx Documentation

From project root:

```bash
cd sphinx-docs
make html          # Linux/macOS
.\make.bat html    # Windows
```

View at: `sphinx-docs/build/html/index.html`

## Documentation Checklist

When adding or updating documentation:

- [ ] Content is accurate and up-to-date
- [ ] Examples are tested and work
- [ ] Screenshots are current (if applicable)
- [ ] Links work (internal and external)
- [ ] Spelling and grammar checked
- [ ] Code blocks have syntax highlighting
- [ ] Cross-references added where helpful
- [ ] Updated table of contents (if applicable)
- [ ] Follows style guide
- [ ] Builds successfully with Sphinx (no warnings)

## Localization

Currently, documentation is in English only. To add translations:

1. Create language subdirectory: `docs/es/` for Spanish.
2. Translate all markdown files.
3. Update links to point to translated versions.
4. Add language selector to index.
5. Update Sphinx configuration.

## Feedback

Documentation feedback is welcome!

- **Typos/errors**: Open a pull request with fixes.
- **Missing content**: Open an issue describing what's needed.
- **Unclear sections**: Open an issue with suggestions.
- **Questions**: Use GitHub Discussions.

## Maintenance

Documentation should be reviewed and updated:

- **With each release**: Update version numbers, screenshots.
- **When code changes**: Update affected sections.
- **Quarterly**: Review for accuracy and completeness.
- **When issues reported**: Fix problems promptly.

## Resources

### Markdown

- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)

### Sphinx

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [ReadTheDocs](https://docs.readthedocs.io/)

### Writing

- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Write the Docs](https://www.writethedocs.org/)

---

**Documentation Version**: 0.9.2  
**Last Updated**: February 2026  
**Maintainer**: Alejandro Mata Ali
