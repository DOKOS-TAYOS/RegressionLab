@echo off
setlocal

cd /d "%~dp0.."

if not exist .venv (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm was not found in PATH
    echo Install Node.js 20+ and run: npm install --prefix desktop
    exit /b 1
)

call .venv\Scripts\activate.bat
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
set "REGRESSIONLAB_PYTHON=%CD%\.venv\Scripts\python.exe"

npm --prefix desktop run dev
