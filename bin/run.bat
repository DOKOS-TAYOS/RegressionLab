@echo off
setlocal
REM ============================================================================
REM RegressionLab - Quick Launch Script for Windows
REM ============================================================================
REM This script activates the virtual environment and runs RegressionLab
REM ============================================================================

REM Language Configuration (Uncomment and modify to set language)
REM set LANGUAGE=es    REM For Spanish (default)
REM set LANGUAGE=en    REM For English

REM Change to project root directory (parent of bin)
cd /d "%~dp0.."

REM Check if virtual environment exists
if not exist .venv (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment and run the program
call .venv\Scripts\activate.bat
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"
set "REGRESSIONLAB_PYTHON=%PYTHON_EXE%"

where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js was not found in PATH
    echo Install Node.js 20+ and run: npm install --prefix desktop
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm was not found in PATH
    echo Install Node.js 20+ and run: npm install --prefix desktop
    pause
    exit /b 1
)

if not exist desktop\node_modules (
    echo ERROR: desktop dependencies are not installed
    echo Run: npm install --prefix desktop
    pause
    exit /b 1
)

REM Check for --dev flag (run with terminal visible)
set "DEV_MODE=0"
if "%~1"=="--dev" (
    set "DEV_MODE=1"
    shift
)

if "%DEV_MODE%"=="1" (
    REM Dev mode: start Vite + Electron
    npm --prefix desktop run dev
    exit /b 0
)

REM Default: build renderer/electron and launch desktop app
npm --prefix desktop run start
exit /b 0
