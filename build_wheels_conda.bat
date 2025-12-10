@echo off
REM Build wheels for multiple Python versions using conda environments
REM This is a Windows batch script version

echo Building wheels for multiple Python versions using conda
echo ============================================================

REM Check if conda is available
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: conda not found. Please install conda or add it to PATH.
    exit /b 1
)

REM Check if setup.py exists
if not exist setup.py (
    echo Error: setup.py not found. Run this script from the project root.
    exit /b 1
)

REM Create dist directory
if not exist dist mkdir dist

REM Python versions to build for
set PYTHON_VERSIONS=3.7 3.8 3.9 3.10 3.11 3.12 3.13

echo.
echo Creating conda environments (if needed)...
for %%v in (%PYTHON_VERSIONS%) do (
    set ENV_NAME=py%%v
    set ENV_NAME=!ENV_NAME:.=!
    
    echo.
    echo Checking environment py!ENV_NAME!...
    conda env list | findstr /C:"py!ENV_NAME!" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Creating conda environment py!ENV_NAME! with Python %%v...
        conda create -n py!ENV_NAME! python=%%v -y
    ) else (
        echo Environment py!ENV_NAME! already exists
    )
)

echo.
echo Building wheels...
for %%v in (%PYTHON_VERSIONS%) do (
    set ENV_NAME=py%%v
    set ENV_NAME=!ENV_NAME:.=!
    
    echo.
    echo ============================================================
    echo Building wheel in conda environment py!ENV_NAME! (Python %%v)
    echo ============================================================
    
    REM Activate environment and build
    call conda activate py!ENV_NAME!
    if %ERRORLEVEL% EQU 0 (
        python -m pip install --upgrade pip build wheel setuptools pybind11 numpy
        python -m build --wheel
        call conda deactivate
    ) else (
        echo Failed to activate environment py!ENV_NAME!
    )
)

echo.
echo ============================================================
echo Build Summary
echo ============================================================
echo.
dir /b dist\*.whl 2>nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Wheels are in: %CD%\dist
    echo.
    echo To upload to PyPI:
    echo   twine upload dist\*.whl
) else (
    echo No wheels were built.
)

pause

