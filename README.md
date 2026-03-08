<div align="center">

![RegressionLab Logo](images/RegressionLab_logo.png)

# RegressionLab

Curve fitting and data analysis with a desktop frontend built in **Electron + React** and the existing scientific backend in **Python**.

[Documentation](docs/index.md) • [Issues](https://github.com/DOKOS-TAYOS/RegressionLab/issues) • [Web demo](https://regressionlab.streamlit.app/)

</div>

---

## Overview

RegressionLab provides:

- multiple fitting modes: normal, multiple datasets, checker, and total fitting
- interactive desktop plots with Plotly
- data inspection, transform, cleaning, save, and pair plots in a dedicated data view
- batch result galleries with thumbnail previews and side-by-side comparison
- live prediction and copyable solution text in the fit results
- configuration via `.env` and the desktop UI
- shared Python fitting core for desktop and Streamlit

The main desktop application in this branch is:

- **Electron + React + TypeScript** for the frontend
- **FastAPI** as a local desktop sidecar
- the same existing **Python backend** for loading, fitting, analysis, plotting, and configuration

`src/streamlit_app` is still present, but it is optional and is not the main desktop workflow.

## Requirements

- Python 3.12 or newer
- Node.js 20 or newer
- npm
- Windows 10/11, macOS, or Linux

## Desktop Installation

### Recommended

1. Clone the repository:

```bash
git clone https://github.com/DOKOS-TAYOS/RegressionLab.git
cd RegressionLab
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Install the desktop frontend dependencies:

```bash
npm install --prefix desktop
```

5. Run the desktop app:

Windows:

```powershell
.\bin\run.bat
```

macOS/Linux:

```bash
./bin/run.sh
```

The normal launcher now reuses the existing desktop build. It only recompiles if the build files are missing or if the Electron/frontend sources changed.

### Development mode

Windows:

```powershell
.\bin\run.bat --dev
```

macOS/Linux:

```bash
./bin/run.sh --dev
```

### Force a rebuild manually

If you want to rebuild the desktop frontend explicitly before launching:

Windows:

```powershell
.\bin\run.bat --build
```

macOS/Linux:

```bash
./bin/run.sh --build
```

### Using `install.*` / `setup.*`

The scripts `install.bat`, `install.sh`, `setup.bat`, and `setup.sh` install everything needed:

- Python (with optional install via winget on Windows)
- Node.js (with optional install if not present)
- `npm install --prefix desktop` for the Electron frontend

If Node.js is not installed, the setup will ask whether to install it.

## Optional Streamlit Run

Windows:

```powershell
.\bin\run_streamlit.bat
```

macOS/Linux:

```bash
./bin/run_streamlit.sh
```

Or directly:

```bash
streamlit run src/streamlit_app/app.py
```

## Verification

Python:

```bash
python -m pytest tests/test_desktop_api.py tests/test_import_hygiene.py -q
```

Desktop frontend:

```bash
npm --prefix desktop test
npm --prefix desktop run build
```

## Main Dependencies

### Python runtime

- NumPy
- SciPy
- Matplotlib
- Pandas
- OpenPyXL
- Pillow
- PyYAML
- FastAPI
- Uvicorn
- Streamlit

### Desktop frontend runtime

- Electron
- React
- React Router
- Plotly
- Zustand

## Documentation

- [Documentation index](docs/index.md)
- [Installation guide](docs/installation.md)
- [Usage guide](docs/usage.md)
- [Configuration guide](docs/configuration.md)
- [License guide](docs/license.md)

## License

RegressionLab is licensed under the MIT License. See [LICENSE](LICENSE).

Third-party dependency licenses are summarized in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
