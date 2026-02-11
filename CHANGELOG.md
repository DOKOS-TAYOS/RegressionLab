# Changelog

All notable changes to RegressionLab are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.1] - 2026-02-11

### Fixed

- **Streamlit Cloud**: Hotfix to repair Streamlit Cloud deployment that was not working due to a tkinter dependency that could not be resolved.

---

## [0.9.0] - 2026-02-07

### Fixed

- **Binaries**: Binaries corrected.

### Changed

- **Python**: Only Python 3.12+ is now supported.
- **Estimators**: Estimator improvements.
- **Imports and maintainability**: Improved imports and maintainability. New functions can now be defined more easily.
- **run.bat / run.sh**: When using `run.bat` and `run.sh`, the command console is no longer shown.
- **User interface**: Completely modernized UI across the application (layouts, styles, and controls updated).
- **User experience**: Improved UX with better controls, configuration options, and visualizations for fitting and analysis.
- **Streamlit app**: Refined Streamlit UI and behavior; current design is considered stable with no further near-term changes planned.
- **Documentation and docstrings**: Many docstrings updated and expanded; user and API documentation completed and brought in line with the current behavior.
- **Environment variables**: Improved loading, validation, and defaults when reading environment variables.
- **Dialogs**: Dialog layout, wording, and behavior improved for a more consistent user experience.
- **Misc**: Minor changes and optimizations.

---

## [0.8.3] - 2026-02-06

### Fixed

- **Languages**: Minor language fixes in translations and UI messages.

### Added

- **.env validations**: New validations for `.env` values to ensure correct configuration.
- **RMSE**: Added RMSE (Root Mean Square Error) to fit results and statistics.

### Changed

- **Python**: Project requirement updated from Python 3.10+ to Python 3.12 only. All config (pyproject.toml, setup scripts, docs, installers) now require Python 3.12 or higher.
- **Tests**: Tests updated to reflect recent changes and new validations.
- **Documentation**: Docs submodules updated.
- **Imports**: Improved relative imports across the project.
- **Fitting functions**: Reference to existing functions moved to a `.yaml` file for better maintainability.
- **Environment variables**: When invalid values are set in the environment variables, the system now detects them and applies the default values at the conflicting points.
- **Style and architecture**: Minor style and architecture changes.

---

## [0.8.2] - 2026-02-04

### Fixed

- **Closing with X**: Corrected behavior when closing dialogs or the main window with the window close button (X). All Tkinter dialogs (equation type, file type, file name, variables, parameter configuration, custom formula, number of fits, config, data preview) now use `WM_DELETE_WINDOW` so that closing with X is treated as cancel and returns the appropriate signal. Main window closing with X shows the exit confirmation dialog (same as the Exit button); in the exit confirmation dialog, closing with X cancels exit.
- **Custom function unicode symbols**: Fixed bugs where unicode symbols were not being read correctly in custom functions, ensuring proper parsing and evaluation of mathematical expressions with special characters.

### Added

- **Parameter estimates and bounds**: In Tkinter, you can configure initial parameter values and bounds before fitting via the "Configure initial parameters" dialog. Dialog columns: initial value, range start, range end per parameter; empty fields use the automatic estimator. All built-in fitting functions support `initial_guess_override` and `bounds_override` (with `merge_initial_guess` and `merge_bounds` utilities).
- **Extra information in results**: Fit results can include additional statistical and fit information (e.g. χ², R², confidence intervals) in the result text and display.
- **Data visualization modes**: Table view and pair plots (scatter matrix) for datasets. In Streamlit: expander "Data visualization" with dataframe and optional "Visualize variable pairs"; in Tkinter: data preview with optional pair-plot button that opens a scaled image window.
- **Configuration**: Configuration dialog (Tkinter) with grouped sections: language, UI appearance, plots, fonts, paths, links, logging. All `ENV_SCHEMA` options are editable from the application and persisted to `.env`; closing the dialog with X cancels without saving.
- **Termux / mobile installer**: First trial installer for Android via Termux (`install_termux.sh`). Installs Git and Python if needed; uses TUR repo and `pkg` for numpy, scipy, pandas, matplotlib and python-tkinter to avoid long pip builds. Clones the repo into `~/python_materials/RegressionLab`, creates a venv (with `--system-site-packages` when using pkg packages), installs Streamlit and remaining dependencies, configures `.env` from `.env_mobile.example`, prompts for input/output paths, and creates a run script that starts the Streamlit app in headless mode (`http://localhost:8501`). Optional shortcut in `~/storage/downloads/run_regressionlab.sh` when storage is set up. Recommended Termux from F-Droid.
- **TXT data files**: Support for loading data from `.txt` files (tab or comma-separated; delimiter auto-detected). File type selector in Tkinter and Streamlit includes CSV, XLSX and TXT.
- **Plot output format**: The output format for saved plots can be chosen in the configuration dialog (Tkinter) or via `.env`: `FILE_PLOT_FORMAT` with options `png`, `jpg` or `pdf`. Plots are saved in the selected format in the output directory.
- **Example datasets**: Added more example datasets to the `input/` directory for testing and demonstration purposes.

### Changed

- **Config**: `src/config.py` refactored into package `src/config/` with modules `constants.py`, `env.py`, `paths.py`, `theme.py`. Public API preserved via `config/__init__.py` re-exports.
- **Fitting functions**: `src/fitting/fitting_functions.py` split into `src/fitting/fitting_functions/` and `src/fitting/functions/`. Model functions grouped by family in `functions/`: `polynomials.py`, `trigonometric.py`, `inverse.py`, `special.py`, plus `_base.py` for shared types.
- **Frontend (Tkinter)**: `src/frontend/ui_dialogs.py` refactored into package `src/frontend/ui_dialogs/` with modules: `config_dialog.py`, `data_selection.py`, `equation.py`, `help.py`, `result.py`, `tooltip.py`.
- **Streamlit app**: Application logic moved into `src/streamlit_app/sections/` with modules: `data.py`, `fitting.py`, `help_section.py`, `modes.py`, `results.py`, `sidebar.py`. `app.py` delegates to these sections.
- **Imports**: `main_program.py`, `streamlit_app/app.py` and `utils/validators.py` updated to use the new package layout.
- **Excel input**: Support for legacy XLS (Excel 97-2003) has been removed; only XLSX is supported for Excel files.
- **Code refactoring**: Continued refactoring of code and structures to improve maintainability, organization, and code quality.

---

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

[0.9.1]: https://github.com/DOKOS-TAYOS/RegressionLab/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/DOKOS-TAYOS/RegressionLab/compare/v0.8.3...v0.9.0
[0.8.3]: https://github.com/DOKOS-TAYOS/RegressionLab/compare/v0.8.2...v0.8.3
[0.8.2]: https://github.com/DOKOS-TAYOS/RegressionLab/compare/v0.8.1...v0.8.2
[0.8.1]: https://github.com/DOKOS-TAYOS/RegressionLab/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/DOKOS-TAYOS/RegressionLab/releases/tag/v0.8.0
