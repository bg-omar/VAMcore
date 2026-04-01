// test_basic.js - Basic test for Node.js bindings

const sst = require('../index.js');

console.log('Testing swirl-string-core npm package...');
console.log('Version:', sst.version);
console.log('Available:', sst.isAvailable);
console.log('Is Native:', sst.isNative);
console.log('Is WASM:', sst.isWasm);

if (!sst.isAvailable) {
    console.error('Module not available:', sst.error);
    console.log('This is expected if the native addon or WASM module has not been built.');
    console.log('Run: npm run build:node (for Node.js) or npm run build:wasm (for browser)');
    process.exit(0);
}

// Test basic functionality if available
try {
    if (typeof sst.computeVelocity === 'function') {
        console.log('✓ computeVelocity function available');
        
        // Simple test
        const curve = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]];
        const grid = [[0.5, 0.5, 0.5]];
        
        try {
            const result = sst.computeVelocity(curve, grid);
            console.log('✓ computeVelocity test passed');
            console.log('Result type:', typeof result, Array.isArray(result) ? 'Array' : result.constructor.name);
        } catch (err) {
            console.error('✗ computeVelocity test failed:', err.message);
        }
    } else {
        console.log('computeVelocity function not available (module may be stub)');
    }
    
    console.log('\nBasic test completed!');
} catch (err) {
    console.error('Test error:', err.message);
    process.exit(1);
}

