# Uploading Wheels to PyPI

## Current Status

You have successfully built:
- ✅ **5 Windows wheels**: Python 3.9, 3.10, 3.11, 3.12, 3.13
- ⚠️ **Failed**: Python 3.7, 3.8 (may be due to C++20 compatibility or compiler issues)

**Note**: Having 5 Python versions is excellent coverage! Most users are on Python 3.9+.

## Step 1: Build Source Distribution

The source distribution allows users to build from source if no wheel matches their platform:

```bash
python -m build --sdist
```

This creates: `swirl_string_core-0.1.0.tar.gz`

## Step 2: Verify Files

Check what you're about to upload:

```bash
# Windows
dir dist\*.whl dist\*.tar.gz

# Linux/macOS
ls -lh dist/*.whl dist/*.tar.gz
```

You should see:
- `swirl_string_core-0.1.0-cp39-cp39-win_amd64.whl`
- `swirl_string_core-0.1.0-cp310-cp310-win_amd64.whl`
- `swirl_string_core-0.1.0-cp311-cp311-win_amd64.whl`
- `swirl_string_core-0.1.0-cp312-cp312-win_amd64.whl`
- `swirl_string_core-0.1.0-cp313-cp313-win_amd64.whl`
- `swirl_string_core-0.1.0.tar.gz` (source distribution)

## Step 3: Test on TestPyPI (Recommended)

Before uploading to production PyPI, test on TestPyPI:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*.whl dist/*.tar.gz

# When prompted:
# Username: __token__
# Password: pypi-YourTestPyPIToken
```

Then test installation:

```bash
pip install --index-url https://test.pypi.org/simple/ swirl-string-core
```

## Step 4: Upload to Production PyPI

Once tested, upload to the real PyPI:

```bash
# Upload to PyPI
twine upload dist/*.whl dist/*.tar.gz

# When prompted:
# Username: __token__
# Password: pypi-YourProductionToken
```

Or use environment variables:

```bash
# Windows PowerShell
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-YourTokenHere"
twine upload dist/*.whl dist/*.tar.gz

# Linux/macOS
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-YourTokenHere"
twine upload dist/*.whl dist/*.tar.gz
```

## Step 5: Verify Upload

After uploading, wait 1-5 minutes, then verify:

```bash
# Check package page
# https://pypi.org/project/swirl-string-core/

# Test installation
pip install swirl-string-core

# Test import
python -c "import swirl_string_core; print('Success!')"
```

## What Happens Next

After uploading:

1. **PyPI processes** the files (1-5 minutes)
2. **Package becomes available** at: https://pypi.org/project/swirl-string-core/
3. **Users can install** with: `pip install swirl-string-core`
4. **Google Colab users** will need to build from source (no Linux wheels yet)

## Next Steps: Build Linux Wheels

To make the package work on Google Colab and Linux without building from source:

1. **Use GitHub Actions** (recommended):
   - Push the workflow file to GitHub
   - Create a release to trigger builds
   - Linux wheels will be built automatically

2. **Or build manually**:
   - Use Docker with manylinux images
   - See `BUILDING_WHEELS.md` for details

## Troubleshooting

### Upload Fails: "File already exists"

- Increment version number in `setup.py` and `pyproject.toml`
- Rebuild wheels
- Upload again

### Upload Fails: "Authentication failed"

- Check your PyPI token is correct
- Verify token hasn't expired
- Make sure username is `__token__` (with underscores)

### Python 3.7/3.8 Build Failed

This is okay! Common reasons:
- C++20 features not fully supported in older compilers
- Python 3.7/3.8 are end-of-life or near end-of-life
- Most users are on Python 3.9+

You can:
- Skip them (you have 5 versions which is great coverage)
- Or investigate the build errors if you want to support them

## Quick Upload Command

```bash
# One-liner (Windows PowerShell)
$env:TWINE_USERNAME="__token__"; $env:TWINE_PASSWORD="pypi-YourToken"; twine upload dist/*.whl dist/*.tar.gz
```

