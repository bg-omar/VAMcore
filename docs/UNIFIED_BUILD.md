# Unified Build: Python + npm in One Action

The `setup.py` file has been enhanced to automatically build both the Python package and the npm package in a single action.

## How It Works

When you run:

```bash
python setup.py build
# or
pip install .
# or
pip install -e .
```

The build process will:

1. **Build Python extensions** (swirl_string_core and sstbindings)
2. **Build npm package** (Node.js native addon) automatically

## Build Steps

The unified build performs these steps in order:

### Python Build (Standard)
- Generates embedded knot files
- Compiles C++ extensions with pybind11
- Creates Python `.pyd` (Windows) or `.so` (Linux/macOS) modules

### npm Build (Automatic)
1. **Checks prerequisites**:
   - Verifies `package.json` exists
   - Checks if Node.js is installed
   - Checks if npm is installed

2. **Installs dependencies**:
   - Runs `npm install` to get node-addon-api and other dependencies

3. **Generates embedded files**:
   - Runs CMake to generate embedded knot files for Node.js build

4. **Builds native addon**:
   - Runs `npm run build:node` to compile the Node.js native addon
   - Creates `build/Release/swirl_string_core.node`

## Behavior

### If Node.js/npm is Available
- Builds both Python and npm packages
- Outputs progress messages for each step
- Continues even if npm build has warnings

### If Node.js/npm is NOT Available
- Builds Python package normally
- Prints warnings but doesn't fail
- Python package still works (npm package just won't be built)

## Usage Examples

### Standard Build
```bash
python setup.py build
```

### Install (Development)
```bash
pip install -e .
```

### Install (Production)
```bash
pip install .
```

### Build Wheel
```bash
python setup.py bdist_wheel
```

All of these will automatically build the npm package if Node.js is available.

## Output

You'll see output like:

```
Building Python extensions...
...

============================================================
Building npm package (Node.js native addon)...
============================================================

Found Node.js: v20.10.0
Found npm: 10.2.3

[1/3] Installing npm dependencies...
...

[2/3] Generating embedded knot files for Node.js...
✓ Embedded knot files generated

[3/3] Building Node.js native addon...
✓ Node.js native addon built successfully

============================================================
npm package build completed
============================================================
```

## Skipping npm Build

If you want to skip the npm build (e.g., in CI where you only need Python):

```bash
# Set environment variable
SKIP_NPM_BUILD=1 python setup.py build
```

Or modify `setup.py` to check for this variable in the `build_npm_package` method.

## Troubleshooting

### npm Build Fails But Python Build Succeeds
- This is expected if Node.js/npm is not installed
- Python package will still work
- Install Node.js if you need the npm package

### CMake Not Found During npm Build
- The build will continue with a warning
- Node.js addon may not build correctly
- Install CMake for full functionality

### Build Takes Longer
- This is normal - it's building both packages
- npm build typically adds 1-3 minutes
- You can skip it if not needed (see above)

## Benefits

1. **Single command**: Build everything with one action
2. **Consistent builds**: Both packages use the same embedded knot files
3. **CI/CD friendly**: One build step for both distributions
4. **Developer friendly**: No need to remember separate build commands

## See Also

- `BUILD_NPM.md` - Manual npm build instructions
- `BUILDING_WHEELS.md` - Python wheel building guide
- `SETUP_NPM_PUBLISHING.md` - npm publishing setup

