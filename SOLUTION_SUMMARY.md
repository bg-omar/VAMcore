# Solution Summary: pkg_resources ModuleNotFoundError

## Problem Statement
When attempting to install dependencies from `requirements.txt`, the following error occurred:
```
ModuleNotFoundError: No module named 'pkg_resources'
ERROR: Failed to build 'pandas' when getting requirements to build wheel
```

## Root Cause
The issue occurs when:
1. A package in requirements.txt tries to be built from source instead of installed from a pre-built wheel
2. Old packages (like `pandas==1.5.3` from 2022) have setup scripts that directly import `pkg_resources`
3. In pip's isolated build environment, `setuptools` (which provides `pkg_resources`) isn't automatically available
4. The build subprocess fails because it can't find `pkg_resources`

## Solutions Implemented

### 1. Updated `pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=65.0", "wheel", "pybind11>=2.6.0", "numpy>=1.19.0", "packaging"]
build-backend = "setuptools.build_meta"
```
- Increased setuptools requirement from >=45 to >=65.0
- Added `packaging` to ensure full setuptools functionality

### 2. Updated `requirements.txt`
Changed `pandas==1.5.3` to `pandas>=2.0.0` 
- Newer versions have better binary wheel support
- Modern versions work better with current setuptools

### 3. Created Installation Scripts
- **install.bat**: Batch script for Windows Command Prompt
- **install.ps1**: PowerShell script for Windows PowerShell
- **install_requirements.py**: Python script that works cross-platform

All scripts follow this pattern:
```bash
pip install --upgrade setuptools wheel packaging
pip install --prefer-binary -r requirements.txt
# Falls back to --no-build-isolation if needed
```

## Installation Instructions

### Option A: Using Python Script (Recommended)
```bash
python install_requirements.py
```

### Option B: Using PowerShell
```powershell
.\install.ps1
```

### Option C: Using Command Prompt
```cmd
install.bat
```

### Option D: Manual Installation
```bash
pip install --upgrade setuptools wheel packaging
pip install --prefer-binary -r requirements.txt
```

## Key Flags Explained

### `--prefer-binary`
- Tells pip to prefer pre-built wheels (.whl files) over source distributions
- Avoids compilation issues with old packages
- Significantly faster installation

### `--no-build-isolation` (fallback)
- Uses the system's setuptools instead of creating an isolated build environment
- Only used if `--prefer-binary` fails
- Ensures setuptools is available for packages that require it

## Files Modified/Created

1. **Modified**: `pyproject.toml` - Updated build system requirements
2. **Modified**: `requirements.txt` - Updated pandas version constraint
3. **Created**: `install_requirements.py` - Automated installation script
4. **Created**: `install.bat` - Windows batch installer
5. **Created**: `install.ps1` - Windows PowerShell installer
6. **Created**: `test_install2.py` - Verification script
7. **Created**: `INSTALL_INSTRUCTIONS.md` - Installation guide
8. **Created**: `check_modules.py` - Module availability checker

## Verification

Run the verification script:
```bash
python test_install2.py
```

Expected output:
```
pandas version: 3.0.1
setuptools version: 82.0.0
setuptools: OK
All checks successful!
```

## Notes

- The installation may take some time due to the large number of dependencies
- Some packages may show warnings about deprecated modules - these are normal
- If installation still fails, check your internet connection and PyPI availability
- For conda users, consider using: `conda install --file requirements-conda.txt`

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [pip Documentation](https://pip.pypa.io/)