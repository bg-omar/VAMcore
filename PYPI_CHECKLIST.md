# PyPI Publishing Checklist

Use this checklist before publishing to PyPI.

## Pre-Publishing

- [ ] **Update Metadata**
  - [ ] Author name and email in `setup.py`
  - [ ] Author name and email in `pyproject.toml`
  - [ ] Repository URL in both files
  - [ ] License information (add LICENSE file if missing)
  - [ ] Project URLs (GitHub, documentation, etc.)

- [ ] **Version Management**
  - [ ] Update `__version__` in `setup.py`
  - [ ] Update `version` in `pyproject.toml`
  - [ ] Create git tag: `git tag v0.1.0`

- [ ] **Documentation**
  - [ ] `Readme.md` is complete and well-formatted
  - [ ] All examples work correctly
  - [ ] Installation instructions are clear

- [ ] **Testing**
  - [ ] Build succeeds: `python -m build`
  - [ ] Wheel installs: `pip install dist/swirl_string_core-*.whl`
  - [ ] Import works: `import swirl_string_core`
  - [ ] Embedded knots work: Run `test_embedded_knots.py`

## Build Process

- [ ] Install build tools: `pip install build twine`
- [ ] Clean previous builds: `rm -rf build/ dist/ *.egg-info`
- [ ] Build package: `python -m build`
- [ ] Verify dist/ contains:
  - [ ] Source distribution (`.tar.gz`)
  - [ ] Wheel files (`.whl`)

## TestPyPI (Recommended First Step)

- [ ] Create TestPyPI account: https://test.pypi.org/account/register/
- [ ] Upload to TestPyPI: `twine upload --repository testpypi dist/*`
- [ ] Test installation: `pip install --index-url https://test.pypi.org/simple/ swirl-string-core`
- [ ] Verify functionality works from TestPyPI

## PyPI Publishing

- [ ] Create PyPI account: https://pypi.org/account/register/
- [ ] Create API token: https://pypi.org/manage/account/token/
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Wait a few minutes for processing

## Post-Publishing

- [ ] Verify installation: `pip install swirl-string-core`
- [ ] Test import: `python -c "import swirl_string_core; print('Success!')"`
- [ ] Update repository README with PyPI installation instructions
- [ ] Create GitHub release with version tag
- [ ] Add PyPI badge to README (optional)

## Common Issues

- **Build fails**: Check C++ compiler is installed
- **Upload fails**: Verify credentials or API token
- **Package too large**: Check file sizes, PyPI has 100MB limit
- **Version conflict**: Increment version number

