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
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo "[1/5] Checking Python version..."
python3 --version

# Check Python version is 3.11 or higher
python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" || {
    echo "ERROR: Python 3.11 or higher is required"
    exit 1
}
echo "      Python version OK"

echo ""
echo "[2/5] Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "      Virtual environment already exists, skipping creation"
else
    python3 -m venv .venv
    echo "      Virtual environment created"
fi

echo ""
echo "[3/5] Activating virtual environment..."
source .venv/bin/activate

echo ""
echo "[4/5] Upgrading pip..."
python -m pip install --upgrade pip

echo ""
echo "[5/5] Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "===================================="
echo "   Setup Complete!"
echo "===================================="
echo ""
echo "To run RegressionLab:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Run the program: python main_program.py"
echo ""
echo "Or simply use: ./run.sh"
echo ""
echo "To configure the application:"
echo "  1. Copy .env.example to .env: cp .env.example .env"
echo "  2. Edit .env with your preferences"
echo ""
