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

REM Activate virtual environment and run the program (start = console closes after launch)
call .venv\Scripts\activate.bat
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"

REM Precheck import so pythonw failures do not remain silent
"%PYTHON_EXE%" -c "import regressionlab.main_program" >nul 2>&1
if errorlevel 1 (
    echo ERROR: RegressionLab precheck failed.
    echo Running in console mode to show details...
    "%PYTHON_EXE%" -m regressionlab.main_program
    pause
    exit /b 1
)

REM Run in console mode so startup errors are visible instead of silent.
"%PYTHON_EXE%" -m regressionlab.main_program
if errorlevel 1 (
    echo.
    echo ERROR: RegressionLab failed to start.
    pause
    exit /b 1
)

exit /b 0
