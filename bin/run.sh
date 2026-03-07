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

# Check for --dev flag (run with terminal visible)
DEV_MODE=false
if [[ "${1:-}" == "--dev" ]]; then
    DEV_MODE=true
    shift
fi

if $DEV_MODE; then
    # Dev mode: run with terminal (foreground)
    python -m regressionlab.main_program "$@"
else
    # Default: run without terminal (background), exit immediately so terminal closes
    nohup python -m regressionlab.main_program > /dev/null 2>&1 &
    disown
    exit 0
fi
