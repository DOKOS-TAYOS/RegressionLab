#!/bin/bash
# ============================================================================
# RegressionLab - Installation Script for Termux (Android)
# ============================================================================
# This script clones the repository and runs the setup for Termux
# ============================================================================

set -e  # Exit on error

echo ""
echo "===================================="
echo "   RegressionLab - Termux (Android)"
echo "===================================="
echo ""

# Check if running in Termux
if [ -z "$PREFIX" ] || [[ "$PREFIX" != *"com.termux"* ]]; then
    echo "WARNING: This script is designed for Termux on Android."
    echo "If you are not in Termux, consider using install.sh instead."
    read -p "Continue anyway? (y/N): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# [1/3] Check Git
echo "[1/3] Checking Git..."
if ! command -v git &> /dev/null; then
    echo "      Installing Git..."
    pkg update
    pkg install -y git
    echo "      Git installed"
fi
git --version

# Set repository URL
REPO_URL="https://github.com/DOKOS-TAYOS/RegressionLab.git"
REPO_NAME="regressionlab"

# Check if directory already exists
if [ -d "$REPO_NAME" ]; then
    echo ""
    echo "WARNING: Directory '$REPO_NAME' already exists"
    read -p "Do you want to remove it and clone again? (y/N): " OVERWRITE
    if [[ "$OVERWRITE" =~ ^[Yy]$ ]]; then
        echo "      Removing existing directory..."
        rm -rf "$REPO_NAME"
    else
        echo "      Using existing directory..."
        cd "$REPO_NAME"
        chmod +x setup_termux.sh 2>/dev/null || true
        ./setup_termux.sh
        exit 0
    fi
fi

# [2/3] Clone repository
echo ""
echo "[2/3] Cloning repository..."
if ! git clone "$REPO_URL" "$REPO_NAME"; then
    echo "ERROR: Failed to clone repository"
    echo "Please check your internet connection and try again"
    exit 1
fi
echo "      Repository cloned successfully"

# Change to repository directory
cd "$REPO_NAME" || {
    echo "ERROR: Failed to change to repository directory"
    exit 1
}

# [3/3] Run Termux setup
echo ""
echo "[3/3] Running Termux setup..."
chmod +x setup_termux.sh
./setup_termux.sh

echo ""
echo "===================================="
echo "   Installation Complete!"
echo "===================================="
echo ""
echo "The RegressionLab repository has been cloned and set up."
echo "You can now run the application from: $(pwd)"
echo ""
