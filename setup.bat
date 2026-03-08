@echo off
setlocal enabledelayedexpansion
REM ============================================================================
REM RegressionLab - Setup Script for Windows
REM ============================================================================
REM This script sets up the development environment for RegressionLab
REM ============================================================================

REM Change to project root directory (where this script lives)
cd /d "%~dp0"

echo.
echo ====================================
echo    RegressionLab Setup (Windows)
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    set /p INSTALL_PYTHON="Do you want to install Python 3.12 now? (y/N): "
    if /i "!INSTALL_PYTHON!"=="y" (
        echo Installing Python via winget...
        winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        if errorlevel 1 (
            echo ERROR: Failed to install Python via winget.
            echo Please install Python 3.12 from https://www.python.org/
            pause
            exit /b 1
        )
        echo Python installed. Please restart this script in a new terminal.
        pause
        exit /b 0
    ) else (
        echo ERROR: Python 3.12 or higher is required.
        echo Please install from https://www.python.org/
        pause
        exit /b 1
    )
)

echo [1/8] Checking Python version...
python --version

REM Check Python version is 3.12 or higher
python -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.12 or higher is required
    pause
    exit /b 1
)
echo       Python version OK

echo.
echo [2/8] Creating virtual environment...
if exist .venv (
    echo       Virtual environment already exists, skipping creation
) else (
    python -m venv .venv
    echo       Virtual environment created
)

echo.
echo [3/8] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [4/8] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [5/8] Installing dependencies...
pip install -r requirements.txt

echo.
echo [6/8] Setting up environment file...
if exist .env (
    echo       .env file already exists, skipping
) else (
    if exist .env.example (
        copy .env.example .env >nul
        echo       .env file created from .env.example
    ) else (
        echo       Warning: .env.example not found, skipping .env creation
    )
)

echo.
echo [7/8] Checking Node.js (required for desktop app)...
node --version >nul 2>&1
if errorlevel 1 (
    echo       Node.js is not installed.
    set /p INSTALL_NODE="Do you want to install Node.js LTS now? (y/N): "
    if /i "!INSTALL_NODE!"=="y" (
        echo       Installing Node.js via winget...
        winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
        if errorlevel 1 (
            echo       ERROR: Failed to install Node.js via winget.
            echo       Please install Node.js 20+ manually from https://nodejs.org/
            echo       Then run: npm install --prefix desktop
            goto :skip_npm
        ) else (
            echo       Node.js installed. Adding to PATH for this session...
            set "PATH=%ProgramFiles%\nodejs;%PATH%"
        )
    ) else (
        echo       Skipping Node.js. You will need to install it manually and run:
        echo         npm install --prefix desktop
        goto :skip_npm
    )
) else (
    echo       Node.js found:
    node --version
)

REM Ensure Node is in PATH (e.g. after fresh winget install)
if not defined PATH (
    set "PATH=%ProgramFiles%\nodejs"
) else (
    echo %PATH% | findstr /i "nodejs" >nul 2>&1
    if errorlevel 1 (
        set "PATH=%ProgramFiles%\nodejs;%PATH%"
    )
)

echo       Installing desktop frontend dependencies...
call npm install --prefix desktop
if errorlevel 1 (
    echo       WARNING: npm install failed. Run manually: npm install --prefix desktop
) else (
    echo       Desktop dependencies installed successfully
)

:skip_npm
echo.
echo [8/8] Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT_NAME=RegressionLab.lnk"
set "TARGET_PATH=%~dp0bin\run.bat"
set "WORKING_DIR=%~dp0"
set "ICON_PATH=%~dp0images\RegressionLab_icon_low_res.ico"

REM Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\%SHORTCUT_NAME%'); $Shortcut.TargetPath = '%TARGET_PATH%'; $Shortcut.WorkingDirectory = '%WORKING_DIR%'; $Shortcut.IconLocation = '%ICON_PATH%'; $Shortcut.Description = 'RegressionLab - Quick Launch'; $Shortcut.Save()" >nul 2>&1

if errorlevel 1 (
    echo       Warning: Could not create desktop shortcut
) else (
    echo       Desktop shortcut created successfully
)

echo.
echo ====================================
echo    Setup Complete!
echo ====================================
echo.
echo To run RegressionLab:
echo   1. Activate the virtual environment: .venv\Scripts\activate.bat
echo   2. Run the program: python main_program.py
echo.
echo Or simply use: bin\run.bat
echo Or double-click the desktop shortcut: RegressionLab.lnk
echo.
echo To configure the application:
echo   1. Edit .env with your preferences (already created during setup)
echo.

pause
