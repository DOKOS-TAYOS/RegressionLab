#!/bin/bash
# ============================================================================
# RegressionLab - Setup Script for Unix/Mac
# ============================================================================
# This script sets up the development environment for RegressionLab
# ============================================================================

set -e  # Exit on error

# Change to project root directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detect Linux and package manager (for optional auto-install of dependencies)
is_linux_with_pkg_manager() {
    [ "$(uname -s)" = "Linux" ] || return 1
    command -v apt-get &> /dev/null || command -v dnf &> /dev/null || \
    command -v yum &> /dev/null || command -v zypper &> /dev/null || \
    command -v pacman &> /dev/null
}

install_python312_linux() {
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu: use deadsnakes PPA for Python 3.12
        sudo apt-get update
        if ! apt-cache show python3.12 &> /dev/null; then
            sudo add-apt-repository -y ppa:deadsnakes/ppa
            sudo apt-get update
        fi
        sudo apt-get install -y python3.12 python3.12-venv python3.12-pip
        sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 2
        sudo update-alternatives --set python3 /usr/bin/python3.12
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3.12 python3.12-pip
        if command -v python3.12 &> /dev/null; then
            sudo alternatives --set python3 /usr/bin/python3.12 2>/dev/null || true
        fi
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3.12 python3.12-pip 2>/dev/null || \
        { echo "Python 3.12 may not be in default repos. Try: sudo yum install python3.12"; return 1; }
        if command -v python3.12 &> /dev/null; then
            sudo alternatives --set python3 /usr/bin/python3.12 2>/dev/null || true
        fi
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y python312 python312-pip python312-venv 2>/dev/null || \
        sudo zypper install -y python3.12 python3.12-pip 2>/dev/null || return 1
        if command -v python3.12 &> /dev/null; then
            sudo update-alternatives --set python3 /usr/bin/python3.12 2>/dev/null || true
        fi
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm python python-pip
        # Arch uses 'python' for latest (3.12+); ensure python3 exists
        if ! command -v python3 &> /dev/null && command -v python &> /dev/null; then
            sudo ln -sf "$(command -v python)" /usr/local/bin/python3 2>/dev/null || true
        fi
    else
        return 1
    fi
}

echo ""
echo "===================================="
echo "   RegressionLab Setup (Unix/Mac)"
echo "===================================="
echo ""

# Resolve Python command (python3 preferred; on Arch/Linux sometimes only 'python' is available)
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null && python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_CMD="python"
    echo "Note: Using 'python' as Python 3 (python3 not in PATH)."
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "Python 3 is not installed."
    if is_linux_with_pkg_manager; then
        read -p "Do you want to install Python 3.12 now? (y/N): " INSTALL_PYTHON
        if [[ "$INSTALL_PYTHON" =~ ^[Yy]$ ]]; then
            echo "Installing Python 3.12..."
            if install_python312_linux; then
                echo "Python 3.12 installed successfully."
                # On Arch, 'python' is the command; ensure python3 exists
                if ! command -v python3 &> /dev/null && command -v python &> /dev/null; then
                    echo "Note: On this system Python 3 is run as 'python'. Creating python3 symlink if possible..."
                    if [ -x "$(command -v python)" ]; then
                        sudo ln -sf "$(command -v python)" /usr/local/bin/python3 2>/dev/null || true
                    fi
                fi
            else
                echo "ERROR: Failed to install Python 3.12 automatically."
                echo "Please install Python 3.12 manually."
                exit 1
            fi
        else
            echo "Please install Python 3.12 and run this script again."
            exit 1
        fi
    else
        echo "ERROR: Python 3 is not installed"
        echo "Please install Python 3.12"
        exit 1
    fi
fi
# Use python3 after a fresh install if PYTHON_CMD was not set
[ -z "$PYTHON_CMD" ] && PYTHON_CMD="python3"

echo "[1/7] Checking Python version..."
$PYTHON_CMD --version

# Check Python version is 3.12 or higher
$PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" || {
    echo "ERROR: Python 3.12 or higher is required"
    exit 1
}
echo "      Python version OK"

echo ""
echo "[2/7] Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "      Virtual environment already exists, skipping creation"
else
    $PYTHON_CMD -m venv .venv
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

DESKTOP_FILE="$DESKTOP_DIR/RegressionLab.desktop"
ICON_PATH="$SCRIPT_DIR/images/RegressionLab_icon_low_res.ico"

# Get version from .env (APP_VERSION) or pyproject.toml, default 1.0
APP_VER="$(grep -E '^APP_VERSION=' "$SCRIPT_DIR/.env" 2>/dev/null | cut -d '=' -f2 | tr -d '"')"
if [ -z "$APP_VER" ] && [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    APP_VER="$(grep -E '^version[[:space:]]*=' "$SCRIPT_DIR/pyproject.toml" | head -1 | sed -nE 's/^version[[:space:]]*=[[:space:]]*"([^"]*)".*/\1/p')"
fi
[ -z "$APP_VER" ] && APP_VER="1.0"

# Create .desktop file
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=$APP_VER
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
