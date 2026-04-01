# Build wheels for multiple Python versions using conda environments
# PowerShell script for Windows

Write-Host "Building wheels for multiple Python versions using conda" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Check if conda is available
try {
    $condaVersion = conda --version 2>&1
    Write-Host "Found: $condaVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: conda not found. Please install conda or add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if setup.py exists
if (-not (Test-Path "setup.py")) {
    Write-Host "Error: setup.py not found. Run this script from the project root." -ForegroundColor Red
    exit 1
}

# Create dist directory
if (-not (Test-Path "dist")) {
    New-Item -ItemType Directory -Path "dist" | Out-Null
}

# Python versions to build for
$pythonVersions = @("3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13")

Write-Host ""
Write-Host "Creating conda environments (if needed)..." -ForegroundColor Yellow

foreach ($version in $pythonVersions) {
    $envName = "py$($version.Replace('.', ''))"
    
    Write-Host "Checking environment $envName..." -ForegroundColor Gray
    
    $envExists = conda env list | Select-String -Pattern "^$envName\s" -Quiet
    
    if (-not $envExists) {
        Write-Host "Creating conda environment $envName with Python $version..." -ForegroundColor Yellow
        conda create -n $envName python=$version -y
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Created environment $envName" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to create environment $envName" -ForegroundColor Red
        }
    } else {
        Write-Host "✓ Environment $envName already exists" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Building wheels..." -ForegroundColor Yellow

$successCount = 0
$failed = @()

foreach ($version in $pythonVersions) {
    $envName = "py$($version.Replace('.', ''))"
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Building wheel in conda environment $envName (Python $version)" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    
    # Get conda base path
    $condaBase = (conda info --base).Trim()
    
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        $pythonExe = Join-Path $condaBase "envs\$envName\python.exe"
        $pipExe = Join-Path $condaBase "envs\$envName\Scripts\pip.exe"
    } else {
        $pythonExe = Join-Path $condaBase "envs\$envName\bin\python"
        $pipExe = Join-Path $condaBase "envs\$envName\bin\pip"
    }
    
    if (-not (Test-Path $pythonExe)) {
        Write-Host "✗ Python executable not found: $pythonExe" -ForegroundColor Red
        $failed += $version
        continue
    }
    
    try {
        Write-Host "Installing build dependencies..." -ForegroundColor Gray
        & $pipExe install --upgrade pip build wheel setuptools pybind11 numpy
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
        
        Write-Host "Building wheel..." -ForegroundColor Gray
        & $pythonExe -m build --wheel
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Successfully built wheel in $envName" -ForegroundColor Green
            $successCount++
        } else {
            throw "Build failed"
        }
    } catch {
        Write-Host "✗ Failed to build wheel in $envName : $_" -ForegroundColor Red
        $failed += $version
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Build Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$wheels = Get-ChildItem -Path "dist" -Filter "*.whl" -ErrorAction SilentlyContinue

if ($wheels) {
    Write-Host "✓ Built $($wheels.Count) wheel(s) successfully:" -ForegroundColor Green
    foreach ($wheel in $wheels | Sort-Object Name) {
        Write-Host "  - $($wheel.Name)" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Wheels are in: $(Resolve-Path 'dist')" -ForegroundColor Green
} else {
    Write-Host "✗ No wheels were built successfully." -ForegroundColor Red
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠ Failed to build wheels for: $($failed -join ', ')" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✓ Successfully built wheels for $successCount/$($pythonVersions.Count) Python versions" -ForegroundColor Green

if ($successCount -gt 0) {
    Write-Host ""
    Write-Host "To upload to PyPI:" -ForegroundColor Cyan
    Write-Host "  twine upload dist\*.whl" -ForegroundColor Gray
}

Write-Host ""

