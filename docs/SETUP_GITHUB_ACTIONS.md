# Setting Up GitHub Actions for Automated Wheel Building

This guide will help you set up GitHub Actions to automatically build wheels for all Python versions and platforms.

## Step 1: Create the Workflow File

The workflow file is already created at `.github/workflows/build-wheels.yml`. Just make sure it's committed to your repository:

```bash
git add .github/workflows/build-wheels.yml
git commit -m "Add GitHub Actions workflow for building wheels"
git push
```

## Step 2: Create a PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Choose:
   - **Token name**: `GitHub Actions` (or any descriptive name)
   - **Scope**: 
     - For testing: "Project: swirl-string-core" (project-specific)
     - For production: "Entire account" (can publish any project)
   - **Expiration**: Set as needed (or leave blank for no expiration)
4. Click "Add token"
5. **Copy the token immediately** - it starts with `pypi-` and you won't be able to see it again!

## Step 3: Add Token as GitHub Secret

**Quick Path**: https://github.com/Swirl-String-Theory/SSTcore/settings/secrets/actions

**Step-by-step**:
1. Go to your GitHub repository: https://github.com/Swirl-String-Theory/SSTcore
2. Click **Settings** (top menu bar, next to "Insights")
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** button (top right)
5. Fill in:
   - **Name**: `PYPI_API_TOKEN` (must match exactly)
   - **Secret**: Paste your PyPI API token (starts with `pypi-`)
6. Click **Add secret**

**See detailed guide**: `GITHUB_SECRETS_GUIDE.md` for screenshots and troubleshooting

## Step 4: Test the Workflow

### Option A: Manual Trigger (Recommended for First Test)

1. Go to **Actions** tab in your GitHub repository
2. Click **Build Wheels** workflow (on the left)
3. Click **Run workflow** (on the right)
4. Select branch (usually `main` or `master`)
5. Click **Run workflow** button

This will build wheels for all Python versions and platforms. It takes about 20-30 minutes.

### Option B: Create a Release

1. Create a git tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. Go to GitHub → **Releases** → **Draft a new release**
3. Choose tag `v0.1.0`
4. Add release notes
5. Click **Publish release**

This will trigger the workflow automatically.

## Step 5: Download and Upload Wheels

After the workflow completes:

1. Go to **Actions** tab
2. Click on the completed workflow run
3. Scroll down to **Artifacts**
4. Download all wheel artifacts:
   - `wheel-ubuntu-latest-py3.7`
   - `wheel-ubuntu-latest-py3.8`
   - ... (one for each Python version and platform)
   - `sdist` (source distribution)

5. Extract all artifacts to a `dist/` folder

6. Upload to PyPI:
   ```bash
   twine upload dist/*.whl dist/*.tar.gz
   ```

## Step 6: Automatic Upload (Optional)

To automatically upload to PyPI when you create a release, the workflow is already configured. Just make sure:

1. The `PYPI_API_TOKEN` secret is set (Step 3)
2. The workflow's `upload-pypi` job will run automatically on releases

The workflow will:
- Build wheels for all platforms/Python versions
- Build source distribution
- Upload everything to PyPI automatically

## Troubleshooting

### Workflow Fails to Build

- Check the workflow logs in the **Actions** tab
- Common issues:
  - Missing dependencies (should be handled by workflow)
  - C++ compiler errors (check build logs)
  - Path issues with embedded files

### Upload Fails

- Verify `PYPI_API_TOKEN` secret is set correctly
- Check token hasn't expired
- Verify token has correct scope (project vs. entire account)
- Check PyPI for existing package version (increment version if needed)

### Wheels Not Compatible

- Verify the wheel tags match your Python version
- Check `python -m pip debug --verbose` to see supported tags
- Ensure you're building for the correct platform (manylinux for Linux, etc.)

## Manual Building (Alternative)

If you prefer to build manually or GitHub Actions isn't working:

See `BUILDING_WHEELS.md` for instructions on building wheels locally or using Docker.

## Next Steps

Once wheels are built and uploaded:

1. Test installation on different platforms:
   ```bash
   # Linux
   pip install swirl-string-core
   
   # Windows
   pip install swirl-string-core
   
   # macOS
   pip install swirl-string-core
   ```

2. Update your README with installation instructions

3. Test on Google Colab (should work without building from source once Linux wheels are available)


