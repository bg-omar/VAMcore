# Quick Start: Publishing to PyPI

## 1. Update Your Information

Edit these files and replace placeholder values:
- `setup.py`: Update `author_email`, `url`, and `project_urls`
- `pyproject.toml`: Update `authors`, `maintainers`, and `urls`

## 2. Install Build Tools

```bash
pip install build twine
```

## 3. Build the Package

```bash
python -m build
```

This creates `dist/` with:
- Source distribution (`.tar.gz`)
- Wheel files (`.whl`) for different platforms

## 4. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ swirl-string-core
```

## 5. Publish to PyPI

```bash
twine upload dist/*
```

You'll need:
- PyPI username and password, OR
- API token (recommended): https://pypi.org/manage/account/token/

## 6. Verify

```bash
pip install swirl-string-core
python -c "import swirl_string_core; print('Success!')"
```

## Next Steps

- Update version in `setup.py` and `pyproject.toml` for new releases
- Tag your git repository: `git tag v0.1.0`
- See `PUBLISHING.md` for detailed instructions

