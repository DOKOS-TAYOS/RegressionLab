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
#  One-line option (download and run without saving the file):
#     curl -sL https://raw.githubusercontent.com/DOKOS-TAYOS/RegressionLab/dev/install_termux.sh | bash
#
# Requires: Termux (recommended from F-Droid).
# ============================================================================

set -e

REPO_URL="https://github.com/DOKOS-TAYOS/RegressionLab.git"
REPO_NAME="RegressionLab"
BASE_DIR="$HOME/python_materials"

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
    echo -n "Do you want to install Git now? (y/n): "
    if [ -t 0 ]; then read -r INSTALL_GIT; else read -r INSTALL_GIT < /dev/tty; fi
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
    echo -n "Do you want to install Python now? (y/n): "
    if [ -t 0 ]; then read -r INSTALL_PY; else read -r INSTALL_PY < /dev/tty; fi
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
echo -n "Install scientific packages with pkg now? (y/n, default y): "
if [ -t 0 ]; then read -r INSTALL_PKG; else read -r INSTALL_PKG < /dev/tty; fi
INSTALL_PKG="${INSTALL_PKG:-y}"
if [[ "$INSTALL_PKG" =~ ^[Yy]$ ]]; then
    echo "Installing python-numpy, matplotlib, python-pandas (main repo)..."
    pkg install -y python-numpy matplotlib python-pandas 2>/dev/null || true
    if ! pkg show python-scipy &>/dev/null; then
        echo "Adding TUR repo for python-scipy..."
        pkg install -y tur-repo 2>/dev/null || true
    fi
    echo "Installing python-scipy..."
    pkg install -y python-scipy 2>/dev/null || true
    echo "Scientific packages installed (or already present)."
else
    echo "Skipped. Pip may compile numpy/scipy later (can take a long time on device)."
fi

# ----------------------------------------------------------------------------
# 4. Clone repository
# ----------------------------------------------------------------------------
echo ""
echo "[4/11] Cloning repository..."

if [ -d "$REPO_NAME" ]; then
    echo "Directory $REPO_NAME already exists."
    echo -n "Do you want to remove it and clone again? (y/N): "
    if [ -t 0 ]; then read -r OVERWRITE; else read -r OVERWRITE < /dev/tty; fi
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
# 7. Install Python dependencies
# ----------------------------------------------------------------------------
echo ""
echo "[7/11] Installing dependencies..."
pip install --upgrade pip
if [[ "$INSTALL_PKG" =~ ^[Yy]$ ]]; then
    # numpy/scipy/matplotlib/pandas from pkg; only install the rest via pip
    pip install "openpyxl>=3.1,<4.0" "Pillow>=10.0,<11.0" "python-dotenv>=1.0,<2.0" "colorama>=0.4,<1.0" "streamlit>=1.31,<2.0"
    echo "Dependencies installed."
else
    echo "Installing full requirements (numpy/scipy may take 15-30 min to build on device)..."
    pip install -r requirements.txt
    echo "Dependencies installed."
fi

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
streamlit run src/streamlit_app/app.py --server.headless true
RUNEOF
chmod +x "$RUN_SCRIPT"

DOWNLOADS="$HOME/storage/downloads"
if [ -d "$DOWNLOADS" ]; then
    SHORTCUT="$DOWNLOADS/run_regressionlab.sh"
    cat > "$SHORTCUT" << SHORTCUTEOF
#!/data/data/com.termux/files/usr/bin/bash
# RegressionLab launcher - run from Termux: bash run_regressionlab.sh
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
echo "To run RegressionLab:"
echo "  cd $INSTALL_DIR"
echo "  source venv/bin/activate"
echo "  streamlit run src/streamlit_app/app.py"
echo ""
if [ -f "$RUN_SCRIPT" ]; then
    echo "Or run: bash $RUN_SCRIPT"
fi
echo ""
