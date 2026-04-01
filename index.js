// index.js - Main entry point for swirl-string-core npm package
// Auto-detects environment and loads appropriate module (native addon or WASM)

'use strict';

let nativeModule = null;
let wasmModule = null;

// Detect environment
const isNode = typeof process !== 'undefined' && process.versions && process.versions.node;
const isBrowser = typeof window !== 'undefined' || (typeof self !== 'undefined' && typeof importScripts === 'function');

// Try to load native Node.js addon
function loadNativeModule() {
    if (!isNode) {
        return null;
    }
    try {
        // Try to load the native addon
        nativeModule = require('./build/Release/swirl_string_core.node');
        return nativeModule;
    } catch (err) {
        // Native module not available, fall back to WASM
        console.warn('Native addon not available, falling back to WASM:', err.message);
        return null;
    }
}

// Try to load WASM module
function loadWasmModule() {
    if (isBrowser) {
        // In browser, WASM should be loaded via script tag or dynamic import
        // The WASM build will create swirl_string_core_wasm.js
        try {
            // Dynamic import for ES modules (using Function to avoid syntax error in non-ESM contexts)
            const dynamicImport = new Function('specifier', 'return import(specifier)');
            return dynamicImport('./dist/swirl_string_core_wasm.js').then(module => {
                wasmModule = module;
                return module;
            }).catch(err => {
                console.warn('WASM module not available:', err.message);
                return null;
            });
        } catch (err) {
            console.warn('WASM module not available:', err.message);
            return null;
        }
    } else if (isNode) {
        // In Node.js, can load WASM as fallback
        try {
            wasmModule = require('./dist/swirl_string_core_wasm.js');
            return wasmModule;
        } catch (err) {
            console.warn('WASM module not available:', err.message);
            return null;
        }
    }
    return null;
}

// Main module loader
let loadedModule = null;

if (isNode) {
    // Try native first, then WASM
    loadedModule = loadNativeModule();
    if (!loadedModule) {
        loadedModule = loadWasmModule();
    }
} else if (isBrowser) {
    // Browser: use WASM
    loadedModule = loadWasmModule();
}

// Create exports object - handle all cases safely
let exportsObj = {};

// If module is not available, export a stub with error
if (!loadedModule) {
    exportsObj.version = '0.1.3';
    exportsObj.error = 'No module available. Please build the native addon or WASM module.';
    exportsObj.isAvailable = false;
    exportsObj.isNative = false;
    exportsObj.isWasm = false;
    module.exports = exportsObj;
} else if (typeof loadedModule.then === 'function') {
    // Async module (WASM in browser) - return a promise
    // For synchronous access, provide a stub
    exportsObj.version = '0.1.3';
    exportsObj.isAvailable = false;
    exportsObj.isNative = false;
    exportsObj.isWasm = false;
    exportsObj.error = 'WASM module is loading asynchronously. Use await or .then() on the module.';
    // Set up the promise-based export
    const promiseExports = loadedModule.then(module => {
        const asyncExports = Object.assign({}, module || {});
        asyncExports.version = '0.1.3';
        asyncExports.isAvailable = true;
        asyncExports.isNative = false;
        asyncExports.isWasm = true;
        return asyncExports;
    });
    // Export both the stub and the promise
    module.exports = exportsObj;
    module.exports.load = promiseExports;
} else {
    // Sync module (native or WASM in Node.js)
    Object.assign(exportsObj, loadedModule || {});
    exportsObj.version = '0.1.3';
    exportsObj.isAvailable = true;
    exportsObj.isNative = !!nativeModule;
    exportsObj.isWasm = !!wasmModule;
    module.exports = exportsObj;
}

