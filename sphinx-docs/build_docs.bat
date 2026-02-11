@echo off
REM Build RegressionLab Documentation

echo ========================================
echo Building RegressionLab documentation...
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Clean previous build
echo Cleaning previous build...
call make.bat clean
if errorlevel 1 (
    echo ERROR: Failed to clean build directory
    pause
    exit /b 1
)
echo.

REM Build HTML documentation (parallel jobs for faster build)
echo Building HTML documentation...
echo.
set SPHINXOPTS=-j auto
call make.bat html
if errorlevel 1 (
    echo.
    echo ERROR: Documentation build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Documentation build complete!
echo ========================================
echo.
if exist "build\html\index.html" (
    echo SUCCESS: Documentation generated successfully!
    echo.
    echo Output location: %CD%\build\html\index.html
    echo.
    echo You can open it in your browser or run open_docs.bat
) else (
    echo WARNING: index.html not found in build\html\
    echo Build may have failed. Check the output above for errors.
)
echo.

pause
