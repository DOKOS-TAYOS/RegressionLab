# Changelog

All notable changes to RegressionLab are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.1] - 2026-02-02

### Fixed

- **Custom function fitting**: Corrected failure when using custom functions due to parameter initialization. When `*params` was not provided, the code now initializes parameters with ones to handle the indeterminate number of parameters.
- **Tests**: One test was fixed to align with the above behavior.

### Added

- **German (Deutsch)**: Full locale support for German (`de`) added (translations in `src/locales/de.json`).
- **Statistical values**: Improved syntax for including statistical values in results; new statistical values were added.
- **Donation / channel link**: Optional donations button in the Help window (Tkinter and Streamlit). Configure via `DONATIONS_URL` in `.env`; if set, a button linking to that URL is shown. Documented in `.env.example`.

### Changed

- **Documentation**: Version references and docs updated for 0.8.1 (README, docs, Sphinx).
- **Configuration**: `DONATIONS_URL` support added in `config.py`; optional in `.env.example`.

---

## [0.8.0]

Initial 0.8.x release. See repository history and documentation for features and changes prior to 0.8.1.

[0.8.1]: https://github.com/DOKOS-TAYOS/RegressionLab/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/DOKOS-TAYOS/RegressionLab/releases/tag/v0.8.0
