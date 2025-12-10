# Building Wheels for Multiple Python Versions

## Why Multiple Wheels Are Needed

Pybind11 extensions are compiled for specific Python versions. A wheel built for Python 3.12 will **not** work with Python 3.11 or 3.13. Therefore, you need to build separate wheels for each Python version you want to support.

## Supported Python Versions

- Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Platforms: Linux (manylinux), macOS (universal2), Windows (win_amd64)

## Building Wheels Locally

### For Your Current Python Version

```bash
# Install build tools
pip install build wheel

# Build wheel for current Python version
python -m build --wheel
```

### For Multiple Python Versions

You'll need multiple Python installations. Using `pyenv` (Linux/macOS) or multiple Python installers (Windows):

```bash
# Example: Build for Python 3.12
python3.12 -m pip install build wheel
python3.12 -m build --wheel

# Example: Build for Python 3.11
python3.11 -m pip install build wheel
python3.11 -m build --wheel
```

## Using GitHub Actions (Recommended)

The `.github/workflows/build-wheels.yml` workflow automatically builds wheels for all supported Python versions and platforms when you:

1. **Push a tag** (e.g., `v0.1.0`)
2. **Create a release** on GitHub
3. **Manually trigger** the workflow

### Setting Up GitHub Actions

1. Create a PyPI API token: https://pypi.org/manage/account/token/
2. Add it as a GitHub secret:
   - Go to: Settings → Secrets and variables → Actions
   - Add secret: `PYPI_API_TOKEN` with your token value
3. Push the workflow file to your repository
4. Create a release or push a tag to trigger builds

### Downloading Built Wheels

After the workflow runs, download the wheel artifacts from the Actions page and upload them to PyPI:

```bash
# Download all wheels from GitHub Actions artifacts
# Then upload to PyPI
twine upload dist/*.whl dist/*.tar.gz
```

## Building for Google Colab

Google Colab uses **Python 3.12** on **Linux x86_64**. You need:

- A wheel built for: `cp312-cp312-manylinux*_x86_64.whl` (Linux, Python 3.12)

Or users can build from source:

```python
!apt-get update && apt-get install -y build-essential g++
!pip install swirl-string-core
```

## Building Linux Wheels on Windows/macOS

You cannot build Linux wheels on Windows or macOS directly. Options:

1. **Use GitHub Actions** (recommended) - builds on Linux runners
2. **Use Docker** with manylinux images:
   ```bash
   docker run --rm -v $(pwd):/io quay.io/pypa/manylinux2014_x86_64 bash -c \
     "pip install build && python -m build --wheel"
   ```
3. **Use a Linux VM or WSL2** (Windows)

## Uploading to PyPI

After building wheels for all platforms and Python versions:

```bash
# Upload all wheels and source distribution
twine upload dist/*.whl dist/*.tar.gz
```

PyPI will serve the appropriate wheel based on the user's Python version and platform.

## Verifying Wheel Compatibility

Check which Python versions a wheel supports:

```bash
# Inspect wheel tags
python -m pip show swirl-string-core
# Or
unzip -l dist/swirl_string_core-0.1.0-cp312-cp312-win_amd64.whl
```

The wheel filename format is:
```
{package}-{version}-{python_tag}-{abi_tag}-{platform_tag}.whl
```

Example: `swirl_string_core-0.1.0-cp312-cp312-win_amd64.whl`
- `cp312`: Python 3.12
- `win_amd64`: Windows 64-bit

## Current Status

Currently, you have wheels for:
- ✅ Windows: Python 3.12, 3.13
- ❌ Linux: None (needs to be built)
- ❌ macOS: None (needs to be built)

**Next Steps**: Use GitHub Actions or build Linux/macOS wheels manually and upload to PyPI.

