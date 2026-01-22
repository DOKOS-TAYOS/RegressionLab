@echo off
REM ============================================================================
REM RegresionLab - Quick Launch Script for Windows
REM ============================================================================
REM This script activates the virtual environment and runs RegresionLab
REM ============================================================================

REM Language Configuration (Uncomment and modify to set language)
REM set LANGUAGE=es    REM For Spanish (default)
REM set LANGUAGE=en    REM For English

REM Check if virtual environment exists
if not exist .venv (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment and run the program
call .venv\Scripts\activate.bat && python src\main_program.py
