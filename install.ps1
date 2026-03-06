#!/usr/bin/env powershell
<#
.SYNOPSIS
    Installation script for Swirl-String-Core that handles pkg_resources errors
.DESCRIPTION
    This script automates the installation process, ensuring setuptools is available
    and using binary wheels to avoid source compilation issues.
#>

Write-Host "========================================"
Write-Host "Swirl-String-Core Installation Script"
Write-Host "========================================"
Write-Host ""

# Step 1: Upgrade pip, setuptools, and wheel
Write-Host "Step 1: Upgrading pip, setuptools, and wheel..."
& python -m pip install --upgrade pip setuptools wheel packaging
if ($LASTEXITCODE -ne 0) {
    Write-Error "Error upgrading pip/setuptools/wheel"
    exit 1
}

# Step 2: Install requirements with binary preference
Write-Host ""
Write-Host "Step 2: Installing dependencies with binary preference..."
& python -m pip install --prefer-binary -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Binary installation failed, trying with --no-build-isolation..."
    & python -m pip install --no-build-isolation -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error installing requirements"
        exit 1
    }
}

# Step 3: Verify installation
Write-Host ""
Write-Host "Step 3: Verifying installation..."
& python test_install2.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Verification failed"
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "Installation completed successfully!"
Write-Host "========================================"