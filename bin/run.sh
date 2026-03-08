#!/bin/bash
# ============================================================================
# RegressionLab - Quick Launch Script for Unix/Mac
# ============================================================================
# This script activates the virtual environment and runs RegressionLab
# ============================================================================

set -e  # Exit on error

# Language Configuration (Uncomment and modify to set language)
# export LANGUAGE=es    # For Spanish (default)
# export LANGUAGE=en    # For English

# Change to project root directory (parent of bin)
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run setup.sh first"
    exit 1
fi

# Activate virtual environment and run the program
source .venv/bin/activate
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
export REGRESSIONLAB_PYTHON="$PWD/.venv/bin/python"

if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: Node.js was not found in PATH"
    echo "Install Node.js 20+ and run: npm install --prefix desktop"
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "ERROR: npm was not found in PATH"
    echo "Install Node.js 20+ and run: npm install --prefix desktop"
    exit 1
fi

if [ ! -d "desktop/node_modules" ]; then
    echo "ERROR: desktop dependencies are not installed"
    echo "Run: npm install --prefix desktop"
    exit 1
fi

# Check for --dev flag (run with terminal visible)
DEV_MODE=false
if [[ "${1:-}" == "--dev" ]]; then
    DEV_MODE=true
    shift
fi

if $DEV_MODE; then
    # Dev mode: Vite + Electron
    npm --prefix desktop run dev
else
    # Default: build renderer/electron and start the desktop app
    npm --prefix desktop run start
fi
