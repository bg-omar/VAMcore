# Installing swirl-string-core on Google Colab

## Important Note

**Google Colab uses Python 3.12 on Linux.** Currently, there are no pre-built Linux wheels for Python 3.12 on PyPI, so the package will be built from source. This requires a C++ compiler.

## Quick Install (Builds from Source)

```python
# Install build dependencies first
!apt-get update
!apt-get install -y build-essential g++

# Then install the package (will build from source)
!pip install swirl-string-core
```

**Note**: Building from source takes 2-5 minutes on Colab.

## If Build Fails

If you encounter build errors, try installing build dependencies first:

```python
# Install build dependencies
!apt-get update
!apt-get install -y build-essential g++

# Then install the package
!pip install swirl-string-core
```

## Alternative: Install from Source with Verbose Output

If you need to see the actual error messages:

```python
!pip install swirl-string-core --verbose --no-cache-dir
```

## Common Issues

### Issue: C++ Compiler Not Found
**Solution**: Install build tools:
```python
!apt-get update && apt-get install -y build-essential g++
```

### Issue: C++ Standard Not Supported
**Solution**: The package uses C++20. If your compiler is too old, you may need to update it:
```python
!apt-get update && apt-get install -y g++-11
```

### Issue: Memory Errors During Build
**Solution**: Colab may run out of memory. Try:
```python
# Restart runtime and try again
!pip install swirl-string-core --no-cache-dir
```

## Verify Installation

```python
try:
    import swirl_string_core
    print("✓ swirl_string_core imported successfully")
    
    # Test embedded knots
    from swirl_string_core import VortexKnotSystem
    system = VortexKnotSystem()
    system.initialize_knot_from_name('3_1', resolution=100)
    print(f"✓ Loaded knot with {len(system.get_positions())} points")
except Exception as e:
    print(f"✗ Error: {e}")
```

## Using the Package

```python
import swirl_string_core
from swirl_string_core import VortexKnotSystem
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Initialize a knot
system = VortexKnotSystem()
system.initialize_knot_from_name('3_1', resolution=1000)

# Get positions
positions = system.get_positions()

# Plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot(positions[:, 0], positions[:, 1], positions[:, 2])
ax.set_title('Trefoil Knot (3_1)')
plt.show()
```

