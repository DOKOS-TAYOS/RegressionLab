#!/bin/bash
# ============================================================================
# RegressionLab - Installation Script for Unix/Mac
# ============================================================================
# This script clones the repository and runs the setup automatically
# ============================================================================

set -e  # Exit on error

# Detect Linux and package manager (for optional auto-install of dependencies)
is_linux_with_pkg_manager() {
    [ "$(uname -s)" = "Linux" ] || return 1
    command -v apt-get &> /dev/null || command -v dnf &> /dev/null || \
    command -v yum &> /dev/null || command -v zypper &> /dev/null || \
    command -v pacman &> /dev/null
}

install_git_linux() {
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y git
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y git
    elif command -v yum &> /dev/null; then
        sudo yum install -y git
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y git
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm git
    else
        return 1
    fi
}

echo ""
echo "===================================="
echo "   RegressionLab Installation"
echo "===================================="
echo ""

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed."
    if is_linux_with_pkg_manager; then
        read -p "Do you want to install Git now? (y/N): " INSTALL_GIT
        if [[ "$INSTALL_GIT" =~ ^[Yy]$ ]]; then
            echo "Installing Git..."
            if install_git_linux; then
                echo "Git installed successfully."
            else
                echo "ERROR: Failed to install Git automatically."
                echo "Please install Git manually:"
                echo "  - Ubuntu/Debian: sudo apt-get install git"
                echo "  - Fedora/RHEL: sudo dnf install git"
                echo "  - openSUSE: sudo zypper install git"
                echo "  - Arch: sudo pacman -S git"
                exit 1
            fi
        else
            echo "Please install Git and run this script again:"
            echo "  - Ubuntu/Debian: sudo apt-get install git"
            echo "  - macOS: git is included with Xcode Command Line Tools"
            echo "  - Or download from: https://git-scm.com/downloads"
            exit 1
        fi
    else
        echo "ERROR: Git is not installed"
        echo "Please install Git:"
        echo "  - Ubuntu/Debian: sudo apt-get install git"
        echo "  - macOS: git is included with Xcode Command Line Tools"
        echo "  - Or download from: https://git-scm.com/downloads"
        exit 1
    fi
fi

echo "[1/3] Git found:"
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
        chmod +x setup.sh
        ./setup.sh
        exit 0
    fi
fi

echo ""
echo "[2/3] Cloning repository..."
if ! git clone "$REPO_URL"; then
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

echo ""
echo "[3/3] Running setup..."
echo ""

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh

echo ""
echo "===================================="
echo "   Installation Complete!"
echo "===================================="
echo ""
echo "The RegressionLab repository has been cloned and set up."
echo "You can now run the application from: $(pwd)"
echo ""
