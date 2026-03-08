# RegressionLab Documentation

Welcome to the RegressionLab documentation.

RegressionLab combines:

- a Python scientific backend for loading, fitting, analysis, plotting, and configuration
- an Electron + React desktop frontend
- an optional Streamlit frontend

## Start Here

### Core guides

1. [Introduction](introduction.md)
2. [Installation Guide](installation.md)
3. [Usage Guide](usage.md)
4. [Configuration Guide](configuration.md)

### Interface-specific guides

- [Streamlit Guide](streamlit-guide.md)
- [Tkinter Guide](tkinter-guide.md) - legacy reference

### Developer guides

- [Extending RegressionLab](extending.md)
- [Customizing the Fitting Core](customization.md)
- [API Documentation](api/index.md)

### Support and project docs

- [Troubleshooting](troubleshooting.md)
- [Contributing](contributing.md)
- [License](license.md)

## Notes For This Branch

- The main desktop interface is now Electron-based.
- Installation requires both Python and Node.js.
- `install.*` and `setup.*` still help with Python setup, but the Electron frontend also requires `npm install --prefix desktop`.

## External Links

- [GitHub repository](https://github.com/DOKOS-TAYOS/RegressionLab)
- [Issue tracker](https://github.com/DOKOS-TAYOS/RegressionLab/issues)
- [Streamlit demo](https://regressionlab.streamlit.app/)
