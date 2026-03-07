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

# Activate virtual environment and run the program (background + nohup = terminal can close)
source .venv/bin/activate
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
nohup python -m regressionlab.main_program > /dev/null 2>&1 &
exit 0
