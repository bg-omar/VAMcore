# Setting Up npm Publishing with GitHub Actions

This guide explains how to set up automated npm publishing using GitHub Actions.

## Overview

The repository includes two GitHub Actions workflows:

1. **`test-npm.yml`** - Runs on every push/PR to test the package on multiple platforms
2. **`publish-npm.yml`** - Publishes to npm when you create a release or push a version tag

## Prerequisites

### 1. npm Account

1. Create an account at https://www.npmjs.com/signup (if you don't have one)
2. Verify your email address

### 2. npm Package Name

The package name is set in `package.json` as `swirl-string-core`. Make sure this name is available on npm:

```bash
npm search swirl-string-core
```

If the name is taken, update `package.json`:
```json
{
  "name": "@your-org/swirl-string-core"  // Use scoped package
}
```

## Step 1: Create npm Access Token

1. Go to https://www.npmjs.com/settings/YOUR_USERNAME/tokens
2. Click **"Generate New Token"**
3. Choose:
   - **Token type**: "Automation" (for CI/CD)
   - **Expiration**: Set as needed (or leave blank for no expiration)
4. Click **"Generate Token"**
5. **Copy the token immediately** - it starts with `npm_` and you won't be able to see it again!

## Step 2: Add Token as GitHub Secret

1. Go to your GitHub repository: https://github.com/Swirl-String-Theory/SSTcore
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Fill in:
   - **Name**: `NPM_TOKEN` (must match exactly)
   - **Secret**: Paste your npm token (starts with `npm_`)
5. Click **"Add secret"**

## Step 3: Test the Workflow

### Option A: Manual Trigger

1. Go to **Actions** tab in your GitHub repository
2. Click **"Build and Publish npm Package"** workflow
3. Click **"Run workflow"** (on the right)
4. Select branch (usually `main` or `master`)
5. Optionally enter a version number
6. Click **"Run workflow"**

This will build and test the package but won't publish (since no tag/release exists).

### Option B: Create a Test Release

1. Create a git tag:
   ```bash
   git tag v0.1.3-test
   git push origin v0.1.3-test
   ```

2. The workflow will run automatically and attempt to publish

**Note**: For test releases, you might want to use a scoped package name like `@your-org/swirl-string-core-test` to avoid polluting the main package.

## Step 4: Publish a Real Release

### Method 1: Using Git Tags (Recommended)

1. **Update version in package.json**:
   ```bash
   # Edit package.json and change version to, e.g., "0.1.3"
   ```

2. **Commit and push**:
   ```bash
   git add package.json
   git commit -m "Bump version to 0.1.3"
   git push
   ```

3. **Create and push a tag**:
   ```bash
   git tag v0.1.3
   git push origin v0.1.3
   ```

4. The workflow will automatically:
   - Build the package
   - Run tests
   - Publish to npm
   - Create a GitHub release

### Method 2: Using GitHub Releases

1. Go to **Releases** → **Draft a new release**
2. Choose or create a tag (e.g., `v0.1.3`)
3. Add release notes
4. Click **"Publish release"**

The workflow will automatically publish to npm.

## Workflow Details

### Test Workflow (`test-npm.yml`)

Runs on:
- Every push to `main`, `master`, or `develop`
- Every pull request to these branches

Tests on:
- Ubuntu, Windows, macOS
- Node.js 18.x and 20.x

### Publish Workflow (`publish-npm.yml`)

Runs on:
- Push of tags starting with `v` (e.g., `v0.1.3`)
- GitHub releases (published)
- Manual trigger via workflow_dispatch

Steps:
1. Builds and tests on multiple platforms
2. Builds WASM version
3. Publishes to npm (only on tags/releases)
4. Creates GitHub release (if tag pushed)

## Version Management

### Version Format

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Updating Version

1. Update `package.json`:
   ```json
   {
     "version": "0.1.4"
   }
   ```

2. Commit:
   ```bash
   git add package.json
   git commit -m "Bump version to 0.1.4"
   git push
   ```

3. Create tag:
   ```bash
   git tag v0.1.4
   git push origin v0.1.4
   ```

## Troubleshooting

### Workflow Fails: "NPM_TOKEN not found"

**Solution**: Ensure the secret is named exactly `NPM_TOKEN` in GitHub repository settings.

### Publish Fails: "Package name already exists"

**Solution**: 
- The version already exists on npm - increment the version
- Or the package name is taken - use a scoped package name

### Build Fails: "CMake not found"

**Solution**: The workflow installs CMake automatically. If it fails:
- Check the workflow logs
- Ensure the system dependencies step completed successfully

### Publish Fails: "Invalid token"

**Solution**:
- Verify the npm token is correct
- Check token hasn't expired
- Ensure token has "Automation" type (not "Publish")

### Version Mismatch Warning

If you see a warning about version mismatch:
- The tag version (e.g., `v0.1.3`) should match `package.json` version (`0.1.3`)
- Update `package.json` before creating the tag

## Manual Publishing (Alternative)

If you prefer to publish manually:

```bash
# 1. Build
npm run build:all

# 2. Test
npm test

# 3. Check what will be published
npm pack --dry-run

# 4. Publish
npm publish
```

## Verifying Publication

After publishing, verify on npm:

1. Go to https://www.npmjs.com/package/swirl-string-core
2. Check the version appears in the package page
3. Test installation:
   ```bash
   npm install swirl-string-core
   ```

## Best Practices

1. **Always test before publishing**: The test workflow runs automatically on PRs
2. **Use semantic versioning**: Follow MAJOR.MINOR.PATCH format
3. **Update CHANGELOG**: Document changes in `RELEASE_NOTES_X.X.X.md`
4. **Tag releases**: Always create git tags for published versions
5. **Test locally first**: Run `npm test` before pushing tags

## Next Steps

- See `BUILD_NPM.md` for local build instructions
- See `README_NPM.md` for package usage
- Check npm package page: https://www.npmjs.com/package/swirl-string-core

