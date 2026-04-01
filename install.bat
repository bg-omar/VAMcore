@echo off
REM Installation script for Swirl-String-Core
REM This script handles the pkg_resources error that occurs when installing dependencies

echo.
echo ========================================
echo Swirl-String-Core Installation Script
echo ========================================
echo.

REM Step 1: Upgrade pip, setuptools, and wheel
echo Step 1: Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel packaging
if %errorlevel% neq 0 (
    echo Error upgrading pip/setuptools/wheel
    exit /b 1
)

REM Step 2: Install requirements with binary preference
echo.
echo Step 2: Installing dependencies with binary preference...
python -m pip install --prefer-binary -r requirements.txt
if %errorlevel% neq 0 (
    echo Binary installation failed, trying with --no-build-isolation...
    python -m pip install --no-build-isolation -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error installing requirements
        exit /b 1
    )
)

REM Step 3: Verify installation
echo.
echo Step 3: Verifying installation...
python test_install2.py
if %errorlevel% neq 0 (
    echo Verification failed
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================