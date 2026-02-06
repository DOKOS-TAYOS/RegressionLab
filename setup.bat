@echo off
REM ============================================================================
REM RegressionLab - Setup Script for Windows
REM ============================================================================
REM This script sets up the development environment for RegressionLab
REM ============================================================================

echo.
echo ====================================
echo    RegressionLab Setup (Windows)
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.12 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/7] Checking Python version...
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
echo [2/7] Creating virtual environment...
if exist .venv (
    echo       Virtual environment already exists, skipping creation
) else (
    python -m venv .venv
    echo       Virtual environment created
)

echo.
echo [3/7] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [4/7] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [5/7] Installing dependencies...
pip install -r requirements.txt

echo.
echo [6/7] Setting up environment file...
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
echo [7/7] Creating desktop shortcut...
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
