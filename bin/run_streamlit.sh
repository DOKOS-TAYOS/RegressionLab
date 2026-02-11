#!/bin/bash
# Streamlit launcher for RegressionLab (Unix/Linux/macOS)
# This script starts the Streamlit web application

set -e  # Exit on error

# Change to project root directory (parent of bin)
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run setup.sh first"
    exit 1
fi

echo "Starting RegressionLab Streamlit Application..."
echo ""
source .venv/bin/activate

# Run Streamlit application
streamlit run src/streamlit_app/app.py
