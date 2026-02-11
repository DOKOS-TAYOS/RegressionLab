@echo off
REM Run all tests for RegressionLab project

REM Change to project root directory (parent of bin)
cd /d "%~dp0.."

if not exist .venv (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
echo Running RegressionLab tests...
python tests\run_tests.py
pause
