@echo off
REM ============================================================================
REM RegresionLab - Setup Script for Windows
REM ============================================================================
REM This script sets up the development environment for RegresionLab
REM ============================================================================

echo.
echo ====================================
echo    RegresionLab Setup (Windows)
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

REM Check Python version is 3.11 or higher
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11 or higher is required
    pause
    exit /b 1
)
echo       Python version OK

echo.
echo [2/5] Creating virtual environment...
if exist .venv (
    echo       Virtual environment already exists, skipping creation
) else (
    python -m venv .venv
    echo       Virtual environment created
)

echo.
echo [3/5] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [5/5] Installing dependencies...
pip install -r requirements.txt

echo.
echo ====================================
echo    Setup Complete!
echo ====================================
echo.
echo To run RegresionLab:
echo   1. Activate the virtual environment: .venv\Scripts\activate.bat
echo   2. Run the program: python main_program.py
echo.
echo Or simply use: run.bat
echo.
echo To configure the application:
echo   1. Copy .env.example to .env
echo   2. Edit .env with your preferences
echo.

pause
