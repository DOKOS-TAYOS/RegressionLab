# Installation Guide

This guide covers the **current** installation flow for the main desktop application in this branch:

- **Electron + React + TypeScript** frontend
- **FastAPI** local sidecar
- existing **Python** scientific backend

Streamlit is still available, but it is optional and is not the primary workflow described here.

## Prerequisites

### Required software

- **Python 3.12+**
- **Node.js 20+**
- **npm**
- **Git** (recommended)

### Quick checks

```bash
python --version
node --version
npm --version
git --version
```

If your system uses `python3` instead of `python`, replace commands accordingly.

## Important Note About The Existing Setup Scripts

The repository still contains:

- `install.bat` / `install.sh`
- `setup.bat` / `setup.sh`

Those scripts currently prepare the **Python environment** only. They do **not** yet:

- install Node.js
- install the Electron frontend dependencies
- run `npm install --prefix desktop`

So the desktop frontend requires one extra manual step after the Python setup.

## Recommended Installation

### Windows

1. Clone the repository:

```powershell
git clone https://github.com/DOKOS-TAYOS/RegressionLab.git
cd RegressionLab
```

2. Install Node.js 20+ if needed.

Using `winget`:

```powershell
winget install OpenJS.NodeJS.LTS
```

3. Create the virtual environment:

```powershell
python -m venv .venv
```

4. Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

5. Install Python dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

6. Create `.env` if needed:

```powershell
Copy-Item .env.example .env
```

7. Install the desktop frontend dependencies:

```powershell
npm install --prefix desktop
```

8. Run the desktop application:

```powershell
.\bin\run.bat
```

### macOS / Linux

1. Clone the repository:

```bash
git clone https://github.com/DOKOS-TAYOS/RegressionLab.git
cd RegressionLab
```

2. Install Node.js 20+ if needed.

3. Create the virtual environment:

```bash
python3 -m venv .venv
```

4. Activate it:

```bash
source .venv/bin/activate
```

5. Install Python dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

6. Create `.env` if needed:

```bash
cp .env.example .env
```

7. Install the desktop frontend dependencies:

```bash
npm install --prefix desktop
```

8. Run the desktop application:

```bash
./bin/run.sh
```

## Using `setup.*` First

If you prefer the existing scripts, you can still use:

Windows:

```powershell
.\setup.bat
```

macOS/Linux:

```bash
./setup.sh
```

After that, you still need:

```bash
npm install --prefix desktop
```

before `bin/run.bat` or `./bin/run.sh` will work for the desktop app.

## Development Mode

The development launcher starts:

- the Vite dev server
- Electron
- the Python desktop API sidecar

Windows:

```powershell
.\bin\run.bat --dev
```

macOS/Linux:

```bash
./bin/run.sh --dev
```

## Running Only The Desktop API

Windows:

```powershell
.\bin\run_desktop_api.bat
```

macOS/Linux:

```bash
./bin/run_desktop_api.sh
```

## Optional Streamlit Run

Windows:

```powershell
.\bin\run_streamlit.bat
```

macOS/Linux:

```bash
./bin/run_streamlit.sh
```

Or:

```bash
streamlit run src/streamlit_app/app.py
```

## Verification

### Python checks

```bash
python -m pytest tests/test_desktop_api.py tests/test_import_hygiene.py -q
```

### Desktop frontend checks

```bash
npm --prefix desktop test
npm --prefix desktop run build
```

## Common Problems

### `node` or `npm` not found

Install Node.js 20+ and reopen the terminal.

### `desktop dependencies are not installed`

Run:

```bash
npm install --prefix desktop
```

### PowerShell cannot activate `.venv`

Run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### `.venv` does not exist

Create it first:

```bash
python -m venv .venv
```

or:

```bash
python3 -m venv .venv
```

## Updating

If you installed from Git:

```bash
git pull
pip install -r requirements.txt --upgrade
pip install -r requirements-dev.txt --upgrade
npm install --prefix desktop
```

## See Also

- [Usage Guide](usage.md)
- [Configuration Guide](configuration.md)
- [Troubleshooting](troubleshooting.md)
