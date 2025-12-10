# Building Wheels Using Conda Environments

This is the **easiest way** to build wheels for multiple Python versions on Windows, macOS, or Linux.

## Quick Start

### Windows (PowerShell - Recommended)

```powershell
# Run the PowerShell script
.\build_wheels_conda.ps1
```

### Windows (Batch)

```batch
# Run the batch script
build_wheels_conda.bat
```

### Linux/macOS/Windows (Python script)

```bash
python build_wheels_conda.py
```

## How It Works

1. **Creates conda environments** for each Python version:
   - `py37` (Python 3.7)
   - `py38` (Python 3.8)
   - `py39` (Python 3.9)
   - `py310` (Python 3.10)
   - `py311` (Python 3.11)
   - `py312` (Python 3.12)
   - `py313` (Python 3.13)

2. **Builds wheels** in each environment

3. **Collects all wheels** in the `dist/` folder

## Manual Method (Step by Step)

If you prefer to run commands manually in separate terminals:

### Terminal 1: Python 3.7

```bash
conda create -n py37 python=3.7 -y
conda activate py37
pip install build wheel setuptools pybind11 numpy
python -m build --wheel
conda deactivate
```

### Terminal 2: Python 3.8

```bash
conda create -n py38 python=3.8 -y
conda activate py38
pip install build wheel setuptools pybind11 numpy
python -m build --wheel
conda deactivate
```

### Terminal 3: Python 3.9

```bash
conda create -n py39 python=3.9 -y
conda activate py39
pip install build wheel setuptools pybind11 numpy
python -m build --wheel
conda deactivate
```

... and so on for each Python version.

## Advantages

✅ **Simple**: No Docker needed  
✅ **Works on Windows**: Native conda support  
✅ **Isolated**: Each Python version in its own environment  
✅ **Fast**: Can run multiple builds in parallel (different terminals)  
✅ **Reliable**: Uses conda's Python installations

## Requirements

- **Conda** installed (Miniconda or Anaconda)
- Conda in PATH
- Enough disk space (~500MB per environment)

## After Building

All wheels will be in the `dist/` folder. Upload them to PyPI:

```bash
twine upload dist/*.whl dist/*.tar.gz
```

## Troubleshooting

### Conda Not Found

```bash
# Add conda to PATH (Windows)
# Add to PATH: C:\Users\YourName\miniconda3\Scripts
# Or: C:\Users\YourName\anaconda3\Scripts

# Linux/macOS
export PATH="$HOME/miniconda3/bin:$PATH"
```

### Environment Already Exists

The script will skip creating environments that already exist. To recreate:

```bash
conda env remove -n py37
conda create -n py37 python=3.7 -y
```

### Build Fails

Check the error message. Common issues:
- Missing C++ compiler (install Visual Studio Build Tools on Windows)
- Missing dependencies (should be handled by script)
- Disk space issues

### Parallel Building

You can speed things up by running multiple builds in parallel:

1. Open multiple terminals
2. Run the build command for different Python versions in each terminal
3. All wheels will end up in the same `dist/` folder

## Example: Building in Parallel

**Terminal 1:**
```bash
conda activate py37 && python -m build --wheel && conda deactivate
```

**Terminal 2:**
```bash
conda activate py38 && python -m build --wheel && conda deactivate
```

**Terminal 3:**
```bash
conda activate py39 && python -m build --wheel && conda deactivate
```

All three can run simultaneously!

