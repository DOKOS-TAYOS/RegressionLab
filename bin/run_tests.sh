#!/bin/bash
# Run all tests for RegressionLab project

set -e  # Exit on error

# Change to project root directory (parent of bin)
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run setup.sh first"
    exit 1
fi

source .venv/bin/activate
echo "Running RegressionLab tests..."
python tests/run_tests.py
