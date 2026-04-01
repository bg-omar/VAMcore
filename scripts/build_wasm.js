#!/usr/bin/env node
// build_wasm.js - Script to build WASM module using Emscripten

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Building WASM module with Emscripten...');

// Check if Emscripten is available
try {
    execSync('emcc --version', { stdio: 'ignore' });
} catch (err) {
    console.error('Error: Emscripten (emcc) not found. Please install Emscripten SDK.');
    console.error('See: https://emscripten.org/docs/getting_started/downloads.html');
    process.exit(1);
}

// Create dist directory if it doesn't exist
const distDir = path.join(__dirname, '..', 'dist');
if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
}

// Build WASM using CMake with Emscripten toolchain
const buildDir = path.join(__dirname, '..', 'build_wasm');
if (!fs.existsSync(buildDir)) {
    fs.mkdirSync(buildDir, { recursive: true });
}

try {
    // Configure with Emscripten
    execSync(`cmake -DCMAKE_TOOLCHAIN_FILE=${process.env.EMSCRIPTEN}/cmake/Modules/Platform/Emscripten.cmake -DCMAKE_BUILD_TYPE=Release ..`, {
        cwd: buildDir,
        stdio: 'inherit'
    });
    
    // Build
    execSync('cmake --build . --target swirl_string_core_wasm', {
        cwd: buildDir,
        stdio: 'inherit'
    });
    
    console.log('WASM build completed successfully!');
} catch (err) {
    console.error('WASM build failed:', err.message);
    process.exit(1);
}

