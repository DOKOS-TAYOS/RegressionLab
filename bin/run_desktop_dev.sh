#!/bin/bash
set -e

cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run setup.sh first"
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "ERROR: npm was not found in PATH"
    echo "Install Node.js 20+ and run: npm install --prefix desktop"
    exit 1
fi

source .venv/bin/activate
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
export REGRESSIONLAB_PYTHON="$PWD/.venv/bin/python"

npm --prefix desktop run dev
