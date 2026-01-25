#!/bin/bash
# ============================================================================
# RegressionLab - Setup Script for Unix/Mac
# ============================================================================
# This script sets up the development environment for RegressionLab
# ============================================================================

set -e  # Exit on error

echo ""
echo "===================================="
echo "   RegressionLab Setup (Unix/Mac)"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    echo "Python 3.12 is recommended for best performance"
    exit 1
fi

echo "[1/7] Checking Python version..."
python3 --version

# Check Python version is 3.10 or higher
python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" || {
    echo "ERROR: Python 3.10 or higher is required"
    echo "Python 3.12 is recommended for best performance"
    exit 1
}

# Check if Python version is 3.12 or higher (recommended)
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
    echo "      Python version OK (recommended version)"
else
    echo "WARNING: Python 3.12 or higher is recommended for best performance"
    echo "      Current version will work, but 3.12+ is preferred"
fi

echo ""
echo "[2/7] Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "      Virtual environment already exists, skipping creation"
else
    python3 -m venv .venv
    echo "      Virtual environment created"
fi

echo ""
echo "[3/7] Activating virtual environment..."
source .venv/bin/activate

echo ""
echo "[4/7] Upgrading pip..."
python -m pip install --upgrade pip

echo ""
echo "[5/7] Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "[6/7] Setting up environment file..."
if [ -f ".env" ]; then
    echo "      .env file already exists, skipping"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "      .env file created from .env.example"
    else
        echo "      Warning: .env.example not found, skipping .env creation"
    fi
fi

echo ""
echo "[7/7] Creating desktop shortcut..."

# Determine desktop path based on OS
if [ -d "$HOME/Desktop" ]; then
    DESKTOP_DIR="$HOME/Desktop"
elif [ -d "$HOME/desktop" ]; then
    DESKTOP_DIR="$HOME/desktop"
elif [ -d "$HOME/Escritorio" ]; then
    DESKTOP_DIR="$HOME/Escritorio"
else
    DESKTOP_DIR="$HOME"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="$DESKTOP_DIR/RegressionLab.desktop"
ICON_PATH="$SCRIPT_DIR/images/RegressionLab_icon_low_res.ico"

# Create .desktop file
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=$(grep -E '^APP_VERSION=' "$SCRIPT_DIR/.env" | cut -d '=' -f2 | tr -d '"')
Type=Application
Name=RegressionLab
Comment=RegressionLab - Quick Launch
Exec=$SCRIPT_DIR/bin/run.sh
Path=$SCRIPT_DIR
Icon=$ICON_PATH
Terminal=true
Categories=Utility;Science;
EOF

# Make it executable
chmod +x "$DESKTOP_FILE"

if [ -f "$DESKTOP_FILE" ]; then
    echo "      Desktop shortcut created successfully at: $DESKTOP_FILE"
else
    echo "      Warning: Could not create desktop shortcut"
fi

echo ""
echo "===================================="
echo "   Setup Complete!"
echo "===================================="
echo ""
echo "To run RegressionLab:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Run the program: python main_program.py"
echo ""
echo "Or simply use: ./bin/run.sh"
echo "Or double-click the desktop shortcut: RegressionLab.desktop"
echo ""
echo "To configure the application:"
echo "  1. Edit .env with your preferences (already created during setup)"
echo ""
