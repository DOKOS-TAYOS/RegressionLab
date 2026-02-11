#!/bin/bash
# Build RegressionLab Documentation

echo "Building RegressionLab documentation..."
echo

# Clean previous build
make clean

# Build HTML documentation (parallel jobs for faster build)
make html SPHINXOPTS="-j auto"

echo
echo "Documentation build complete!"
echo
echo "Open build/html/index.html in your browser to view the documentation."
echo
