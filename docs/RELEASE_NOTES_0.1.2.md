# Release Notes for v0.1.2

## swirl-string-core v0.1.2

### Features
- Embedded 42 knot `.fseries` files directly in the C++ library
- All knots accessible via `VortexKnotSystem.initialize_knot_from_name()`
- No external `.fseries` files required for Python users

### Improvements
- Renamed module from `sstcore` to `swirl_string_core` for better branding
- Backwards compatibility: `sstbindings` module still available
- Optimized C++20 build configuration for better compatibility
- Added Linux compiler flags for cross-platform builds

### Supported Platforms
- Windows: Python 3.9, 3.10, 3.11, 3.12, 3.13
- Linux: Build from source (wheels coming soon)
- macOS: Build from source (wheels coming soon)

### Installation
```bash
pip install swirl-string-core
```

### Usage
```python
import swirl_string_core
from swirl_string_core import VortexKnotSystem

# Initialize any embedded knot
system = VortexKnotSystem()
system.initialize_knot_from_name('3_1', resolution=1000)  # Trefoil
positions = system.get_positions()
```

### Available Knots
All knots from `src/knot_fseries/` are now built-in, including:
- 3_1 (Trefoil/Electron)
- 4_1 (Dark Knot)
- 5_1 (Muon)
- 5_2 (Up Quark)
- 6_1 (Down Quark)
- 7_1 (Tau)
- And 36 more...

### Documentation
- GitHub: https://github.com/Swirl-String-Theory/SSTcore
- PyPI: https://pypi.org/project/swirl-string-core/

