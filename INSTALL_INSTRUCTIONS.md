# Installation Instructions - Fixing pkg_resources Error

## Problem
When installing dependencies, you may encounter:
```
ModuleNotFoundError: No module named 'pkg_resources'
ERROR: Failed to build 'pandas' when getting requirements to build wheel
```

This occurs because:
1. Old packages (like pandas==1.5.3) try to build from source
2. Their build scripts require `pkg_resources` which is from the setuptools package
3. In isolated build environments, setuptools isn't available

## Solution

### Method 1: Install with --prefer-binary flag (RECOMMENDED)
This tells pip to prefer pre-built wheels over compiling from source:

```bash
pip install --upgrade setuptools wheel
pip install --prefer-binary -r requirements.txt
```

### Method 2: Use --no-build-isolation flag
This uses the system setuptools instead of creating an isolated build environment:

```bash
pip install --upgrade setuptools wheel
pip install --no-build-isolation -r requirements.txt
```

### Method 3: Ensure setuptools is properly installed
Sometimes setuptools gets corrupted. Reinstall it:

```bash
pip uninstall setuptools -y
pip install setuptools wheel packaging
pip install --prefer-binary -r requirements.txt
```

## Key Changes Made

1. **Updated pyproject.toml**: Increased setuptools requirement from >=45 to >=65.0 and added `packaging` to build requirements
2. **Updated requirements.txt**: Changed `pandas==1.5.3` to `pandas>=2.0.0` for better wheel availability
3. **Provided install script**: Use `python install_requirements.py` for automated installation

## Installation via Script
Run the provided installation script which handles all these issues automatically:

```bash
python install_requirements.py
```

This script will:
- Ensure setuptools, wheel, and packaging are up-to-date
- Install all requirements with binary preference
- Fall back to --no-build-isolation if needed

## Verification
After installation, verify everything works:

```bash
python test_install2.py
```

This should show:
- pandas version (3.0.0 or later)
- setuptools version (82.0.0 or later)
- All checks successful!