@echo off
setlocal

cd /d "%~dp0.."

if not exist .venv (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    exit /b 1
)

call .venv\Scripts\activate.bat
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"

python -m regressionlab.desktop_api %*
