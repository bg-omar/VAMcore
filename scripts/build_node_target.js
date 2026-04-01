#!/usr/bin/env node

// Helper script to conditionally build the CMake Node addon target.
// It reads build_node/CMakeCache.txt and only invokes
//   cmake --build build_node --target swirl_string_core_node
// if HAVE_SWIRL_STRING_CORE_NODE is ON. This avoids MSBuild errors
// when the target is not generated (e.g., node-addon-api missing).

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const repoRoot = path.join(__dirname, '..');
const buildDir = path.join(repoRoot, 'build_node');
const cachePath = path.join(buildDir, 'CMakeCache.txt');

if (!fs.existsSync(buildDir) || !fs.existsSync(cachePath)) {
  console.log('[swirl-string-core] build_node directory or CMakeCache.txt not found; skipping CMake Node target build');
  process.exit(0);
}

const cache = fs.readFileSync(cachePath, 'utf8');
const hasNodeTarget = /HAVE_SWIRL_STRING_CORE_NODE:BOOL=ON/.test(cache);

if (!hasNodeTarget) {
  console.log('[swirl-string-core] CMake reports no Node addon target (HAVE_SWIRL_STRING_CORE_NODE=OFF); skipping swirl_string_core_node build');
  process.exit(0);
}

console.log('[swirl-string-core] Building CMake Node addon target swirl_string_core_node...');

const result = spawnSync('cmake', ['--build', 'build_node', '--target', 'swirl_string_core_node'], {
  cwd: repoRoot,
  stdio: 'inherit',
  shell: true,
});

if (result.error) {
  console.error('[swirl-string-core] Error spawning cmake:', result.error.message);
}

process.exit(result.status ?? 1);