#!/usr/bin/env python3
"""
Simple test script to verify embedded knots are accessible.
This tests that knots can be loaded by name without needing .fseries files.
"""

# Try to import the compiled library
import sys
import os

# Add build directory to path if needed
build_dir = os.path.join(os.path.dirname(__file__), 'build', 'Release')
if os.path.exists(build_dir):
    sys.path.insert(0, build_dir)

try:
    import swirl_string_core
    from swirl_string_core import VortexKnotSystem
    print("✓ Successfully imported swirl_string_core")
except ImportError:
    try:
        import sstbindings as swirl_string_core
        from sstbindings import VortexKnotSystem
        print("✓ Successfully imported sstbindings (fallback)")
    except ImportError:
        print("✗ ERROR: Could not import swirl_string_core or sstbindings")
        print("  Make sure you've built the C++ module first!")
        print(f"  Tried to load from: {build_dir}")
        exit(1)

print("\n" + "=" * 70)
print("Testing Embedded Knot Access")
print("=" * 70)

# List of known knot IDs to test
test_knots = ['3_1', '3_1p','3_1u', '4_1', '5_1', '5_2', '6_1', '7_1']

print(f"\nTesting {len(test_knots)} knots...\n")

success_count = 0
failed_knots = []

for knot_id in test_knots:
    try:
        print(f"Testing knot '{knot_id}'...", end=" ")
        
        # Create a VortexKnotSystem and initialize the knot by name
        system = VortexKnotSystem()
        system.initialize_knot_from_name(knot_id, resolution=100)
        
        # Get the positions to verify it loaded
        positions = system.get_positions()
        
        if positions is not None and len(positions) > 0:
            print(f"✓ SUCCESS - Loaded {len(positions)} points")
            print(f"  First point: ({positions[0][0]:.3f}, {positions[0][1]:.3f}, {positions[0][2]:.3f})")
            print(f"  Last point:  ({positions[-1][0]:.3f}, {positions[-1][1]:.3f}, {positions[-1][2]:.3f})")
            success_count += 1
        else:
            print(f"✗ FAILED - No positions returned")
            failed_knots.append(knot_id)
            
    except Exception as e:
        print(f"✗ FAILED - Error: {str(e)}")
        failed_knots.append(knot_id)
    
    print()

print("=" * 70)
print(f"Results: {success_count}/{len(test_knots)} knots loaded successfully")
print("=" * 70)

if failed_knots:
    print(f"\nFailed knots: {', '.join(failed_knots)}")
    print("\nThis might mean:")
    print("  1. The knot ID doesn't exist in the embedded files")
    print("  2. The embedded files weren't generated correctly")
    print("  3. There's an issue with the knot loading code")
    exit(1)
else:
    print("\n✓ All knots loaded successfully!")
    print("✓ Embedded knots are working correctly!")
    print("\nYou can now use knots programmatically without .fseries files:")
    print("  system = VortexKnotSystem()")
    print("  system.initialize_knot_from_name('3_1', resolution=1000)")
    exit(0)