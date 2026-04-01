#!/usr/bin/env node
// prebuild.js - Pre-build script to generate embedded knot files

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Running pre-build steps...');

// Ensure build/generated directory exists
const generatedDir = path.join(__dirname, '..', 'build', 'generated');
if (!fs.existsSync(generatedDir)) {
    fs.mkdirSync(generatedDir, { recursive: true });
}

// Run CMake to generate embedded knot files
try {
    const buildDir = path.join(__dirname, '..', 'build_node');
    if (!fs.existsSync(buildDir)) {
        fs.mkdirSync(buildDir, { recursive: true });
    }
    
    // Configure CMake (this will generate the embedded files)
    execSync('cmake ..', {
        cwd: buildDir,
        stdio: 'inherit'
    });
    
    console.log('Pre-build completed successfully');
} catch (err) {
    console.warn('Pre-build step failed (this is okay if CMake is not available):', err.message);
    // Don't fail the install if prebuild fails
}

