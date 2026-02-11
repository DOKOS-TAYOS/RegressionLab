@echo off
REM Streamlit launcher for RegressionLab (Windows)
REM This script starts the Streamlit web application

REM Change to project root directory (parent of bin)
cd /d "%~dp0.."

REM Check if virtual environment exists
if not exist .venv (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo Starting RegressionLab Streamlit Application...
echo.
call .venv\Scripts\activate.bat

REM Run Streamlit application
streamlit run src\streamlit_app\app.py

pause
