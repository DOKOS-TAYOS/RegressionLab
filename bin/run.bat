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
set "PYTHONW_EXE=%CD%\.venv\Scripts\pythonw.exe"

REM Check for --dev flag (run with terminal visible)
set "DEV_MODE=0"
if "%~1"=="--dev" (
    set "DEV_MODE=1"
    shift
)

if "%DEV_MODE%"=="1" (
    REM Dev mode: run with console visible
    "%PYTHON_EXE%" -m regressionlab.main_program %*
    exit /b 0
)

REM Default: run with pythonw (no console), start without waiting so terminal closes
start "" "%PYTHONW_EXE%" -m regressionlab.main_program
exit /b 0
