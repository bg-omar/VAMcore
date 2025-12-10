# Downloading and Installing swirl-string-core

## After Publishing to PyPI

Once you've published the package to PyPI, it will be available for download **within a few minutes** (usually 1-5 minutes).

## Installation Methods

### Standard Installation (Recommended)

```bash
pip install swirl-string-core
```

This will:
- Download the latest version from PyPI
- Install all dependencies (pybind11, numpy)
- Compile the C++ extensions for your platform
- Make the package available for import

### Install Specific Version

```bash
pip install swirl-string-core==0.1.0
```

### Install from TestPyPI (Before Official Release)

```bash
pip install --index-url https://test.pypi.org/simple/ swirl-string-core
```

Note: You may need to also include the main PyPI index for dependencies:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ swirl-string-core
```

## Package URLs After Publishing

Once published, your package will be available at:

- **PyPI Package Page**: https://pypi.org/project/swirl-string-core/
- **Download Page**: https://pypi.org/project/swirl-string-core/#files
- **Simple Index**: https://pypi.org/simple/swirl-string-core/

## Timeline

1. **Upload**: `twine upload dist/*` (takes ~30 seconds)
2. **Processing**: PyPI processes the package (1-5 minutes)
3. **Available**: Package appears on PyPI and can be installed via pip

## Verification

After publishing, verify it's available:

```bash
# Check if package exists
pip search swirl-string-core  # (if search is enabled)
# Or visit: https://pypi.org/project/swirl-string-core/

# Try installing
pip install swirl-string-core

# Verify import works
python -c "import swirl_string_core; print('Success!')"
```

## Using the Package

Once installed:

```python
import swirl_string_core
# or
import sstbindings  # backwards compatibility

# Use embedded knots
from swirl_string_core import VortexKnotSystem

system = VortexKnotSystem()
system.initialize_knot_from_name('3_1', resolution=1000)
positions = system.get_positions()
print(f"Loaded knot with {len(positions)} points")
```

## Troubleshooting

### Package Not Found

If `pip install` fails with "Could not find a version":
- Wait a few more minutes for PyPI to process
- Check the package name is correct: `swirl-string-core` (with hyphens)
- Verify the package was uploaded successfully

### Installation Fails

If installation fails:
- Ensure you have a C++ compiler installed
- Check Python version compatibility (requires Python 3.7+)
- Verify dependencies are available: `pip install pybind11 numpy`


