# RegressionLab Documentation

This directory contains the project documentation for RegressionLab.

The current primary desktop frontend is **Electron + React**, backed by the existing Python fitting core. Streamlit remains available as an optional web frontend. The older Tkinter desktop frontend is still documented as legacy reference material.

## Main Documents

### Getting started

- [index.md](index.md) - documentation index
- [introduction.md](introduction.md) - project overview
- [installation.md](installation.md) - current installation guide for Electron desktop and optional Streamlit
- [usage.md](usage.md) - how to use RegressionLab

### Configuration and customization

- [configuration.md](configuration.md) - `.env` configuration reference
- [streamlit-guide.md](streamlit-guide.md) - web frontend guide
- [tkinter-guide.md](tkinter-guide.md) - legacy Tkinter frontend guide

### Developer reference

- [extending.md](extending.md) - adding fitting functions
- [customization.md](customization.md) - replacing or adapting the fitting core
- [api/index.md](api/index.md) - API/module documentation

### Support

- [troubleshooting.md](troubleshooting.md)
- [contributing.md](contributing.md)
- [license.md](license.md)

## Suggested Reading Order

1. [Introduction](introduction.md)
2. [Installation](installation.md)
3. [Usage](usage.md)
4. [Configuration](configuration.md)

## Notes

- For this desktop branch, prefer the Electron flow documented in [installation.md](installation.md).
- Keep documentation aligned with code changes, especially launch scripts, dependency requirements, and UI workflow changes.
