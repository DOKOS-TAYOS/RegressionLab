#!/bin/bash
# ============================================================================
# RegressionLab - Setup Script for Termux (Android)
# ============================================================================
# This script sets up the development environment for RegressionLab in Termux
# ============================================================================

set -e  # Exit on error

# Change to project root directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Paths for Android storage (Downloads folder) - absolute paths
# /storage/downloads = Downloads (en algunos dispositivos puede ser /storage/emulated/0/Download)
INPUT_DIR="/storage/downloads/input"
OUTPUT_DIR="/storage/downloads/output"

echo ""
echo "===================================="
echo "   RegressionLab Setup (Termux)"
echo "===================================="
echo ""

# [1/8] Check Python
echo "[1/8] Checking Python..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "      Installing Python..."
    pkg update
    pkg install -y python
    echo "      Python installed"
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

$PYTHON_CMD --version

# Check Python version is 3.12 or higher (flexible for Termux)
$PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" || {
    echo "ERROR: Python 3.10 or higher is required"
    exit 1
}
echo "      Python version OK"

echo ""
echo "[2/8] Ensuring tkinter is available (required for GUI)..."
if ! $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    echo "      Tkinter not found. Installing X11 packages..."
    pkg update
    pkg install -y x11-repo 2>/dev/null || true
    pkg install -y python-tkinter 2>/dev/null || {
        echo "      WARNING: Could not install python-tkinter automatically."
        echo "      Try: pkg install x11-repo && pkg install python-tkinter"
    }
else
    echo "      Tkinter already available"
fi

echo ""
echo "[3/8] Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "      Virtual environment already exists, skipping creation"
else
    $PYTHON_CMD -m venv .venv
    echo "      Virtual environment created"
fi

echo ""
echo "[4/8] Activating virtual environment..."
source .venv/bin/activate

echo ""
echo "[5/8] Upgrading pip..."
python -m pip install --upgrade pip

echo ""
echo "[6/8] Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "[7/8] Setting up environment file..."
if [ -f ".env" ]; then
    echo "      .env file already exists, skipping"
else
    if [ -f ".env_mobile.example" ]; then
        cp .env_mobile.example .env
        # Override paths with absolute storage paths
        sed -i "s|^FILE_INPUT_DIR=.*|FILE_INPUT_DIR=\"${INPUT_DIR}\"|" .env
        sed -i "s|^FILE_OUTPUT_DIR=.*|FILE_OUTPUT_DIR=\"${OUTPUT_DIR}\"|" .env
        echo "      .env file created from .env_mobile.example"
        echo "      Input:  ${INPUT_DIR}"
        echo "      Output: ${OUTPUT_DIR}"
        echo "      (Si no existe /storage/downloads, edita .env y usa /storage/emulated/0/Download/input y output)"
    else
        echo "      Warning: .env_mobile.example not found, skipping .env creation"
    fi
fi

echo ""
echo "[8/8] Creating shortcut in storage/downloads..."

# Ensure termux-setup-storage has been run (creates ~/storage/downloads symlink)
if [ ! -d "$HOME/storage/downloads" ]; then
    echo "      Running termux-setup-storage to enable access to Downloads..."
    termux-setup-storage 2>/dev/null || true
fi

SHORTCUT_DIR="$HOME/storage/downloads"
if [ -d "$SHORTCUT_DIR" ]; then
    SHORTCUT_FILE="$SHORTCUT_DIR/RegressionLab.sh"
    cat > "$SHORTCUT_FILE" << EOF
#!/bin/bash
# RegressionLab - Quick Launch for Termux
# Run from Termux: bash ~/storage/downloads/RegressionLab.sh
# IMPORTANT: Start Termux:X11 first (see instructions below)

cd "$SCRIPT_DIR" || { echo "ERROR: RegressionLab dir not found"; exit 1; }

if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found. Run setup_termux.sh first."
    exit 1
fi

export DISPLAY=:0
source .venv/bin/activate
python src/main_program.py
EOF
    chmod +x "$SHORTCUT_FILE"
    echo "      Shortcut created at: $SHORTCUT_FILE"
else
    echo "      Warning: Could not create shortcut (run 'termux-setup-storage' first)"
fi

# Create input/output directories in storage if possible
if [ -d "$HOME/storage/downloads" ]; then
    mkdir -p "$INPUT_DIR" 2>/dev/null || mkdir -p "$HOME/storage/downloads/input" 2>/dev/null || true
    mkdir -p "$OUTPUT_DIR" 2>/dev/null || mkdir -p "$HOME/storage/downloads/output" 2>/dev/null || true
fi

echo ""
echo "===================================="
echo "   Setup Complete!"
echo "===================================="
echo ""
echo "To run RegressionLab:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Run the program: python src/main_program.py"
echo ""
echo "Or use the shortcut: bash ~/storage/downloads/RegressionLab.sh"
echo ""
echo "===================================="
echo "   COMO USAR LA INTERFAZ TKINTER"
echo "===================================="
echo ""
echo "La interfaz gráfica (tkinter) requiere un servidor X11 en Android."
echo "Sigue estos pasos:"
echo ""
echo "1. Instala la app Termux:X11 desde:"
echo "   https://github.com/termux/termux-x11/releases (descarga app-*-debug.apk)"
echo ""
echo "2. En Termux, instala el paquete companion:"
echo "   pkg install x11-repo"
echo "   pkg install termux-x11-nightly"
echo ""
echo "3. Instala python-tkinter si no lo tienes:"
echo "   pkg install python-tkinter"
echo ""
echo "4. Antes de ejecutar RegressionLab, inicia Termux:X11:"
echo "   - Abre la app Termux:X11 en tu teléfono"
echo "   - En Termux, ejecuta: termux-x11 :0 &"
echo "   - O: termux-x11 :0 -xstartup 'sleep infinity' &"
echo ""
echo "5. Luego ejecuta RegressionLab:"
echo "   export DISPLAY=:0"
echo "   source .venv/bin/activate"
echo "   python src/main_program.py"
echo ""
echo "Nota: Si ves pantalla negra, prueba: termux-x11 :0 -legacy-drawing &"
echo "      Si los colores se ven mal: termux-x11 :0 -force-bgra &"
echo ""
echo "Para configurar la aplicación, edita el archivo .env"
echo ""
