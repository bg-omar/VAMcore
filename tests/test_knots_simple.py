#!/usr/bin/env python3
"""Simple test to verify embedded knots"""

import sys
import os

# Force reload if already loaded
if 'sstbindings' in sys.modules:
    del sys.modules['sstbindings']

try:
    import sstbindings
except ImportError:
    # Try adding build directory to path
    build_dir = os.path.join(os.path.dirname(__file__), 'build', 'Release')
    if os.path.exists(build_dir):
        sys.path.insert(0, build_dir)
    import sstbindings

print("Available VortexKnotSystem methods:")
methods = [m for m in dir(sstbindings.VortexKnotSystem) if not m.startswith('_')]
for m in sorted(methods):
    print(f"  - {m}")

if 'initialize_knot_from_name' in methods:
    print("\n✓ initialize_knot_from_name is available!")
    print("\nTesting knot loading...")
    try:
        system = sstbindings.VortexKnotSystem()
        system.initialize_knot_from_name('3_1', resolution=100)
        positions = system.get_positions()
        print(f"✓ Successfully loaded knot 3_1 with {len(positions)} points")
        print(f"  First point: {positions[0]}")
    except Exception as e:
        print(f"✗ Error loading knot: {e}")
else:
    print("\n✗ initialize_knot_from_name is NOT available")
    print("  The module may need to be rebuilt")

