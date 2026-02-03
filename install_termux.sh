#!/data/data/com.termux/files/usr/bin/bash
# ============================================================================
# RegressionLab - Installation Script for Termux (Android)
# ============================================================================
#
# INSTALLATION: you only need this file. No need to clone the repo.
#
#  1) Download install_termux.sh (just this file) to your device.
#  2) In Termux run:  bash install_termux.sh
#
#  (If you have it in the current folder)
#     bash install_termux.sh
#
#  (If you downloaded it to Downloads)
#     bash ~/storage/downloads/install_termux.sh
#
#  One-line INTERACTIVE (prompts work; use this to choose options):
#     bash <(curl -sL https://raw.githubusercontent.com/DOKOS-TAYOS/RegressionLab/dev/install_termux.sh | sed 's/\r$//')
#
#  One-line NON-INTERACTIVE (no prompts, uses defaults):
#     curl -sL https://raw.githubusercontent.com/DOKOS-TAYOS/RegressionLab/dev/install_termux.sh | sed 's/\r$//' | bash
#
# Requires: Termux (recommended from F-Droid).
#
# PKG INSTALLS (script runs these; for reference if you need them manually):
#   pkg install git
#   pkg install python
#   pkg install tur-repo
#   pkg install python-numpy python-scipy python-pandas python-pyarrow matplotlib
#   pkg install python-tkinter
# ============================================================================

set -e

REPO_URL="https://github.com/DOKOS-TAYOS/RegressionLab.git"
REPO_NAME="RegressionLab"
BASE_DIR="$HOME/python_materials"

# When run as "curl ... | bash", stdin is a pipe: use defaults, no prompts
if [ ! -t 0 ]; then
    NONINTERACTIVE=1
    echo "Running in non-interactive mode (e.g. curl | bash). Using defaults."
    echo "To choose options, save the file and run: bash install_termux.sh"
    echo ""
fi

echo ""
echo "===================================="
echo "   RegressionLab - Termux Installer"
echo "===================================="
echo ""

# ----------------------------------------------------------------------------
# 1. Go to home and create python_materials
# ----------------------------------------------------------------------------
cd ~ || exit 1
if [ ! -d "python_materials" ]; then
    echo "[1/11] Creating directory python_materials..."
    mkdir -p python_materials
else
    echo "[1/11] Directory python_materials already exists."
fi
cd python_materials || exit 1

# ----------------------------------------------------------------------------
# 2. Check Git
# ----------------------------------------------------------------------------
echo ""
echo "[2/11] Checking for Git..."
if ! command -v git &> /dev/null; then
    echo "Git is not installed."
    if [ -n "${NONINTERACTIVE}" ]; then
        INSTALL_GIT=y
        echo "Non-interactive: installing Git (default)."
    else
        echo -n "Do you want to install Git now? (y/n): "
        if [ -t 0 ]; then read -r INSTALL_GIT; else read -r INSTALL_GIT < /dev/tty; fi
    fi
    if [[ "$INSTALL_GIT" =~ ^[Yy]$ ]]; then
        echo "Installing Git (pkg install git)..."
        pkg install -y git
        echo "Git installed successfully."
    else
        echo "Git is required to clone the repository."
        echo "Install it later with: pkg install git"
        exit 1
    fi
else
    echo "Git found: $(git --version)"
fi

# ----------------------------------------------------------------------------
# 3. Check Python 3.12 (or python3)
# ----------------------------------------------------------------------------
echo ""
echo "[3/11] Checking for Python 3..."
PYTHON_CMD=""
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "Python 3 is not installed."
    if [ -n "${NONINTERACTIVE}" ]; then
        INSTALL_PY=y
        echo "Non-interactive: installing Python (default)."
    else
        echo -n "Do you want to install Python now? (y/n): "
        if [ -t 0 ]; then read -r INSTALL_PY; else read -r INSTALL_PY < /dev/tty; fi
    fi
    if [[ "$INSTALL_PY" =~ ^[Yy]$ ]]; then
        echo "Installing Python (pkg install python)..."
        pkg install -y python
        PYTHON_CMD="python3"
        echo "Python installed successfully."
    else
        echo "Python is required. Install it later with: pkg install python"
        exit 1
    fi
else
    echo "Python found: $($PYTHON_CMD --version)"
fi

# ----------------------------------------------------------------------------
# 3b. Termux: install scientific packages via pkg (evita compilar numpy con pip)
# ----------------------------------------------------------------------------
echo ""
echo "[3b/11] Scientific packages (numpy, scipy, matplotlib, pandas)..."
echo "In Termux it is better to install them with pkg to avoid pip building for a long time."
if [ -n "${NONINTERACTIVE}" ]; then
    INSTALL_PKG=y
    echo "Non-interactive: installing scientific packages with pkg (default)."
else
    echo -n "Install scientific packages with pkg now? (y/n, default y): "
    if [ -t 0 ]; then read -r INSTALL_PKG; else read -r INSTALL_PKG < /dev/tty; fi
fi
INSTALL_PKG="${INSTALL_PKG:-y}"
if [[ "$INSTALL_PKG" =~ ^[Yy]$ ]]; then
    echo "Adding TUR repo (needed for python-scipy and python-pandas)..."
    pkg install -y tur-repo || true
    echo "Installing python-numpy, python-scipy, python-pandas, python-pyarrow, matplotlib..."
    pkg install -y python-numpy python-scipy python-pandas python-pyarrow matplotlib || true
    echo "Scientific packages installed (or already present)."
else
    echo "Skipped. Pip may compile numpy/scipy later (can take a long time on device)."
fi

# Tkinter is required for the GUI (shortcut runs Tkinter version)
echo "Installing python-tkinter (required for GUI)..."
pkg install -y python-tkinter || true

# ----------------------------------------------------------------------------
# 4. Clone repository
# ----------------------------------------------------------------------------
echo ""
echo "[4/11] Cloning repository..."

if [ -d "$REPO_NAME" ]; then
    echo "Directory $REPO_NAME already exists."
    if [ -n "${NONINTERACTIVE}" ]; then
        OVERWRITE=n
        echo "Non-interactive: keeping existing directory (default)."
    else
        echo -n "Do you want to remove it and clone again? (y/N): "
        if [ -t 0 ]; then read -r OVERWRITE; else read -r OVERWRITE < /dev/tty; fi
    fi
    if [[ "$OVERWRITE" =~ ^[Yy]$ ]]; then
        rm -rf "$REPO_NAME"
    else
        echo "Using existing directory. Skipping clone."
    fi
fi

if [ ! -d "$REPO_NAME" ]; then
    if ! git clone -b dev "$REPO_URL"; then
        echo "ERROR: Failed to clone repository. Check your internet connection."
        exit 1
    fi
    echo "Repository cloned successfully."
fi

# ----------------------------------------------------------------------------
# 5. Enter RegressionLab
# ----------------------------------------------------------------------------
echo ""
echo "[5/11] Entering $REPO_NAME..."
cd "$REPO_NAME" || exit 1
INSTALL_DIR="$(pwd)"

# ----------------------------------------------------------------------------
# 6. Create and activate venv
# ----------------------------------------------------------------------------
echo ""
echo "[6/11] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "venv already exists."
else
    if [[ "$INSTALL_PKG" =~ ^[Yy]$ ]]; then
        $PYTHON_CMD -m venv venv --system-site-packages
        echo "Virtual environment created (with access to pkg-installed packages)."
    else
        $PYTHON_CMD -m venv venv
        echo "Virtual environment created."
    fi
fi

echo "Activating virtual environment..."
# shellcheck source=/dev/null
source venv/bin/activate

# ----------------------------------------------------------------------------
# 7. Install Python dependencies (no build of numpy/pandas; rest may use source)
# ----------------------------------------------------------------------------
echo ""
echo "[7/11] Installing dependencies..."
pip install --upgrade pip

# Critical Streamlit deps first (so a later failure does not leave them missing)
pip install "blinker>=1.0,<2" "cachetools>=4.0,<6" "click>=7.0,<9" "requests>=2.27,<3" "protobuf>=3.20,<5" "typing-extensions>=4.3,<5" "tornado>=6.0,<7"

# Scientific stack: wheels only (never build numpy/pandas on device)
export PIP_ONLY_BINARY=:all:
if pip install "numpy>=2.0,<3.0" "scipy>=1.17,<2.0" "pandas>=2.3,<3.0" "matplotlib>=3.10,<4.0" 2>/dev/null; then
    HAVE_SCIENTIFIC_WHEELS=1
else
    echo "No binary wheels for numpy/scipy/pandas/matplotlib; using pkg-installed versions."
    HAVE_SCIENTIFIC_WHEELS=
fi
unset PIP_ONLY_BINARY 2>/dev/null || true

# Rest: allow wheels or source (Pillow etc. may have no wheel on Termux)
if [ -n "$HAVE_SCIENTIFIC_WHEELS" ]; then
    pip install "openpyxl>=3.1,<4.0" "Pillow>=8.0" "python-dotenv>=1.0,<2.0" "colorama>=0.4,<1.0" "streamlit>=1.31,<2.0"
else
    pip install "openpyxl>=3.1,<4.0" "Pillow>=8.0" "python-dotenv>=1.0,<2.0" "colorama>=0.4,<1.0"
    pip install --no-deps "streamlit>=1.31,<2.0"
    # pyarrow from pkg (avoid slow build); rest via pip
    pip install "altair>=4.0,<6" "blinker>=1.0,<2" "cachetools>=4.0,<6" "click>=7.0,<9" "importlib-metadata>=1.4,<8" "packaging>=16.8,<24" "protobuf>=3.20,<5" "python-dateutil>=2.7,<3" "requests>=2.27,<3" "rich>=10.14,<14" "tenacity>=8.1,<9" "toml>=0.10,<2" "typing-extensions>=4.3,<5" "tzlocal>=1.1,<6" "validators>=0.2,<1" "watchdog>=2.1" "gitpython>=3.0.7,<4" "tornado>=6.0,<7" || true
fi
# Ensure all Streamlit deps + transitive deps (numpy/pandas/pyarrow from pkg when no wheels)
pip install \
  "altair>=4.0,<6" "blinker>=1.0,<2" "cachetools>=4.0,<6" "click>=7.0,<9" \
  "importlib-metadata>=1.4,<8" "packaging>=16.8,<24" "protobuf>=3.20,<5" \
  "python-dateutil>=2.7,<3" "requests>=2.27,<3" "rich>=10.14,<14" "tenacity>=8.1,<9" \
  "toml>=0.10,<2" "typing-extensions>=4.3,<5" "tzlocal>=1.1,<6" "validators>=0.2,<1" \
  "watchdog>=2.1" "gitpython>=3.0.7,<4" "tornado>=6.0,<7" "pydeck>=0.8.0b4,<1" \
  "urllib3>=1.26" "certifi" "charset-normalizer" "idna>=2.0" "Jinja2>=2.0" \
  || true
# rpds-py may fail on Termux (no wheel); try separately so it does not block the rest
pip install rpds-py 2>/dev/null || true
echo "Dependencies installed."

# ----------------------------------------------------------------------------
# 8. Copy .env_mobile.example to .env
# ----------------------------------------------------------------------------
echo ""
echo "[8/11] Configuring .env..."
if [ -f ".env_mobile.example" ]; then
    cp .env_mobile.example .env
    echo ".env created from .env_mobile.example"
else
    echo "WARNING: .env_mobile.example not found. Creating minimal .env"
    touch .env
fi

# ----------------------------------------------------------------------------
# 9. Ask user for input/output paths and update .env
# ----------------------------------------------------------------------------
echo ""
echo "[9/11] File paths for datasets and outputs"
echo "You can use absolute paths (e.g. $HOME/storage/dcim/Datasets) or names relative to the project (e.g. input)."
echo -n "Directory for input datasets [default: input]: "
if [ -t 0 ]; then read -r USER_INPUT_DIR; else read -r USER_INPUT_DIR < /dev/tty; fi
echo -n "Directory for output files [default: output]: "
if [ -t 0 ]; then read -r USER_OUTPUT_DIR; else read -r USER_OUTPUT_DIR < /dev/tty; fi

USER_INPUT_DIR="${USER_INPUT_DIR:-input}"
USER_OUTPUT_DIR="${USER_OUTPUT_DIR:-output}"

# Create directories if they are relative (so they live inside the project)
case "$USER_INPUT_DIR" in
    /*) ;;
    *) mkdir -p "$USER_INPUT_DIR" ;;
esac
case "$USER_OUTPUT_DIR" in
    /*) ;;
    *) mkdir -p "$USER_OUTPUT_DIR" ;;
esac

# Update .env: set FILE_INPUT_DIR and FILE_OUTPUT_DIR
if [ -f ".env" ]; then
    if grep -q "^FILE_INPUT_DIR=" .env 2>/dev/null; then
        sed -i "s|^FILE_INPUT_DIR=.*|FILE_INPUT_DIR=\"$USER_INPUT_DIR\"|" .env
    else
        echo "FILE_INPUT_DIR=\"$USER_INPUT_DIR\"" >> .env
    fi
    if grep -q "^FILE_OUTPUT_DIR=" .env 2>/dev/null; then
        sed -i "s|^FILE_OUTPUT_DIR=.*|FILE_OUTPUT_DIR=\"$USER_OUTPUT_DIR\"|" .env
    else
        echo "FILE_OUTPUT_DIR=\"$USER_OUTPUT_DIR\"" >> .env
    fi
    echo "Paths saved in .env: INPUT=$USER_INPUT_DIR, OUTPUT=$USER_OUTPUT_DIR"
fi

# ----------------------------------------------------------------------------
# 10. Shortcut in Downloads (if possible)
# ----------------------------------------------------------------------------
echo ""
echo "[10/11] Creating shortcut..."

RUN_SCRIPT="$INSTALL_DIR/run_regressionlab_termux.sh"
cat > "$RUN_SCRIPT" << 'RUNEOF'
#!/data/data/com.termux/files/usr/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting RegressionLab (Streamlit)..."
echo "Open in browser: http://localhost:8501"
exec streamlit run src/streamlit_app/app.py --server.headless true
RUNEOF
chmod +x "$RUN_SCRIPT"

DOWNLOADS="$HOME/storage/downloads"
if [ -d "$DOWNLOADS" ]; then
    SHORTCUT="$DOWNLOADS/run_regressionlab.sh"
    cat > "$SHORTCUT" << SHORTCUTEOF
#!/data/data/com.termux/files/usr/bin/bash
# RegressionLab launcher (Streamlit) - run from Termux: bash run_regressionlab.sh
cd "$INSTALL_DIR" || exit 1
source venv/bin/activate
echo "Starting RegressionLab (Streamlit)..."
echo "Open in browser: http://localhost:8501"
exec streamlit run src/streamlit_app/app.py --server.headless true
SHORTCUTEOF
    chmod +x "$SHORTCUT"
    echo "Shortcut created: $SHORTCUT"
    echo "From Termux you can run: bash ~/storage/downloads/run_regressionlab.sh"
else
    echo "Downloads folder not found (run 'termux-setup-storage' if you want to use it)."
    echo "To start RegressionLab from anywhere, run:"
    echo "  bash $RUN_SCRIPT"
fi

# ----------------------------------------------------------------------------
# 11. Done
# ----------------------------------------------------------------------------
echo ""
echo "[11/11] Installation complete."
echo ""
echo "===================================="
echo "   RegressionLab - Ready in Termux"
echo "===================================="
echo ""
echo "Installation directory: $INSTALL_DIR"
echo ""
echo "To run RegressionLab (Streamlit):"
echo "  bash $RUN_SCRIPT"
echo "  Or: cd $INSTALL_DIR && source venv/bin/activate && streamlit run src/streamlit_app/app.py"
echo ""
if [ -f "$RUN_SCRIPT" ]; then
    echo "Or run: bash $RUN_SCRIPT"
fi
echo ""
