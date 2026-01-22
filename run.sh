#!/bin/bash
# ============================================================================
# RegresionLab - Quick Launch Script for Unix/Mac
# ============================================================================
# This script activates the virtual environment and runs RegresionLab
# ============================================================================

set -e  # Exit on error

# Language Configuration (Uncomment and modify to set language)
# export LANGUAGE=es    # For Spanish (default)
# export LANGUAGE=en    # For English

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run setup.sh first"
    exit 1
fi

# Activate virtual environment and run the program
source .venv/bin/activate && python src/main_program.py
