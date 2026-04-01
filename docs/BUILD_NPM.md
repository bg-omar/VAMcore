# Building swirl-string-core for npm

This guide explains how to build the npm package for local use or publication.

## Prerequisites

### Required
- **Node.js** 14.0 or higher
- **npm** (comes with Node.js)
- **CMake** 3.23 or higher
- **C++ Compiler**:
  - **Windows**: Visual Studio 2019+ with C++ tools, or Build Tools for Visual Studio
  - **Linux**: GCC 9+ or Clang 10+
  - **macOS**: Xcode Command Line Tools (`xcode-select --install`)

### Optional (for WASM)
- **Emscripten SDK** (for browser/WebAssembly builds)
# Still inside the session that has EMSDK set
$env:EMSCRIPTEN = "$env:EMSDK\upstream\emscripten"

# Sanity check: toolchain file should exist
Test-Path "$env:EMSCRIPTEN\cmake\Modules\Platform\Emscripten.cmake"

# Also quickly print to be sure
echo "EMSCRIPTEN=$env:EMSCRIPTEN"
## Quick Start

### 1. Install Dependencies

```bash
cd SSTcore
npm install
```

This will install:
- `node-addon-api` (required dependency)
- `node-gyp` (dev dependency for building native addons)
- `typescript` (dev dependency)

### 2. Build the Native Addon (Node.js)

```bash
npm run build:node
```

This command:
1. Runs CMake to generate embedded knot files and configure the Node addon target
2. Uses a helper script (`scripts/build_node_target.js`) to **only** build the CMake Node addon target if it was generated (i.e., `HAVE_SWIRL_STRING_CORE_NODE=ON`)
3. Builds the addon using node-gyp (creates `build/Release/swirl_string_core.node`)

If `node-addon-api` is not available or CMake cannot detect it, the CMake Node addon target is skipped and the helper script will log a message and continue without failing the build. In that case, `node-gyp rebuild` will still attempt to build the native addon using `binding.gyp`.

> **Windows note:** If CMake has trouble locating `node-addon-api`, you can override the include path explicitly when configuring:
>
> ```powershell
> $nodeAddonApiInclude = node -p "require('node-addon-api').include"
> cmake -B build_node -S . "-DNODE_ADDON_API_INCLUDE_DIR=$nodeAddonApiInclude"
> ```
>
> Then re-run `npm run build:node`.

**Note**: The first build may take several minutes as it compiles all C++ sources.

### 3. Test the Build

```bash
npm test
```

Or test manually:
```bash
node tests/test_basic.js
```

### 4. Build WASM (Optional, for Browser)

If you want to build the WebAssembly version for browser use:

```bash
# First, install Emscripten SDK (if not already installed)
# See: https://emscripten.org/docs/getting_started/downloads.html

npm run build:wasm
```

This creates WASM files in the `dist/` directory.

### 5. Build Everything

To build both native addon and WASM:

```bash
npm run build:all
```

## Build Outputs

After building, you should have:

### Native Addon (Node.js)
- `build/Release/swirl_string_core.node` - The compiled native addon
- `build_node/` - CMake build directory with generated files

### WASM (Browser)
- `dist/swirl_string_core_wasm.js` - WASM loader
- `dist/swirl_string_core_wasm.wasm` - Compiled WebAssembly binary

## Using the Package Locally

### Option 1: npm link (Development)

```bash
# In SSTcore directory
npm link

# In your Angular/Node.js project
npm link swirl-string-core
```

### Option 2: Install from Local Path

```bash
# In your project directory
npm install /path/to/SSTcore
```

### Option 3: Use in Angular Project

```bash
# In your Angular project
npm install /path/to/SSTcore

# Then import in your TypeScript files
import * as sst from 'swirl-string-core';
```

## Publishing to npm

### 1. Prepare for Publishing

Ensure you have:
- ✅ Built both native addon and WASM (`npm run build:all`)
- ✅ Tested the package (`npm test`)
- ✅ Updated version in `package.json`
- ✅ Updated `README_NPM.md` with any changes

### 2. Create npm Account (if needed)

```bash
npm adduser
# or
npm login
```

### 3. Check Package Contents

```bash
npm pack
```

This creates a `.tgz` file showing what will be published. Check that all necessary files are included.

### 4. Publish

```bash
# Dry run (test without publishing)
npm publish --dry-run

# Actually publish
npm publish
```

**Note**: The `prepublishOnly` script will automatically run `npm run build:all` before publishing.

### 5. Publish with Tags (Optional)

```bash
# Publish as beta
npm publish --tag beta

# Publish as latest (default)
npm publish --tag latest
```

## Troubleshooting

### Build Fails: "CMake not found"

**Solution**: Install CMake and ensure it's in your PATH.
- Windows: Download from https://cmake.org/download/
- macOS: `brew install cmake`
- Linux: `sudo apt-get install cmake` or `sudo yum install cmake`

### Build Fails: "C++ compiler not found"

**Solution**: Install a C++ compiler:
- Windows: Install Visual Studio Build Tools
- macOS: `xcode-select --install`
- Linux: `sudo apt-get install build-essential`

### Build Fails: "node-addon-api not found"

**Solution**: 
```bash
npm install node-addon-api
```

### Native Addon Build Fails on Windows

**Solution**: 
1. Install Visual Studio 2019+ with "Desktop development with C++" workload
2. Or install "Build Tools for Visual Studio"
3. Run from "Developer Command Prompt for VS" or ensure `vcvarsall.bat` is sourced

### WASM Build Fails

**Solution**: 
1. Install Emscripten SDK: https://emscripten.org/docs/getting_started/downloads.html
2. Ensure `emcc` is in your PATH
3. Run `emsdk activate latest` if using emsdk

### Module Not Found After Install

**Solution**: 
1. Ensure the native addon was built: `npm run build:node`
2. Check that `build/Release/swirl_string_core.node` exists
3. The package will fall back to WASM if native addon is unavailable

## Platform-Specific Notes

### Windows

- Use PowerShell or Command Prompt (not Git Bash for builds)
- May need to run as Administrator for some operations
- Visual Studio Build Tools must be installed

### macOS

- May need to accept Xcode license: `sudo xcodebuild -license accept`
- If using Homebrew, ensure paths are correct

### Linux

- May need additional packages: `sudo apt-get install python3 make g++`
- For some distributions, use `gcc-c++` instead of `g++`

## Continuous Integration

For CI/CD pipelines, you can use:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: npm install

- name: Build native addon
  run: npm run build:node

- name: Test
  run: npm test
```

## Next Steps

- See `README_NPM.md` for usage examples
- See `index.d.ts` for TypeScript API documentation
- Check `tests/test_basic.js` for example usage