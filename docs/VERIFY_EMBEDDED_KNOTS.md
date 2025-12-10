# Verifying Embedded Knots

After compiling the C++ library, you can verify that embedded knots are accessible.

## Quick Test

Run the test script:

```bash
python test_embedded_knots.py
```

Or use Python directly:

```python
import sstbindings  # or swirl_string_core

# Create a vortex knot system
system = sstbindings.VortexKnotSystem()

# Initialize a knot by name (no .fseries file needed!)
system.initialize_knot_from_name('3_1', resolution=1000)

# Get the positions
positions = system.get_positions()
print(f"Loaded knot with {len(positions)} points")
print(f"First point: {positions[0]}")
```

## Available Knot IDs

- `'3_1'` - Electron / Positron (canon)
- `'4_1'` - Dark Knot (research)
- `'5_1'` - Muon (research)
- `'5_2'` - Up Quark (canon)
- `'6_1'` - Down Quark (canon)
- `'7_1'` - Tau (research)

## What This Verifies

1. ✓ The `.fseries` files were embedded into the C++ library during build
2. ✓ The `initialize_knot_from_name()` method can access embedded knots
3. ✓ Knots can be loaded programmatically without external files
4. ✓ The library is self-contained and ready for distribution

## Troubleshooting

### Module Not Found

If you get `ModuleNotFoundError`, make sure:
- The Python module was built: `cmake --build . --config Release --target sstbindings`
- You're using the correct Python version (the module is built for a specific Python version)
- The `.pyd` file is in your Python path or current directory

### Method Not Found

If `initialize_knot_from_name` is not available:
- Rebuild the Python bindings: `cmake --build . --config Release --target sstbindings`
- Make sure `py_knot.cpp` is included in the build
- Check that the binding code in `src_bindings/py_knot.cpp` includes the method

### Knot Not Found

If a knot ID is not found:
- Check that the `.fseries` file exists in `src/knot_fseries/`
- Verify the file was embedded during CMake configuration (check build output for "Embedded X .fseries files")
- The knot ID should match the filename: `knot.{knot_id}.fseries`

