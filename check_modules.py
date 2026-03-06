#!/usr/bin/env python
"""Test if key dependencies are installed"""
import sys

modules_to_test = [
    'pandas',
    'numpy',
    'scipy',
    'sklearn',
    'matplotlib',
    'torch',
]

failed = []
for module in modules_to_test:
    try:
        __import__(module)
        print(f"✓ {module}")
    except ImportError as e:
        print(f"✗ {module}: {e}")
        failed.append(module)

if failed:
    print(f"\nFailed to import: {', '.join(failed)}")
    print("\nTrying to install failed modules...")
    import subprocess
    for mod in failed:
        subprocess.call([sys.executable, "-m", "pip", "install", "--prefer-binary", mod])
else:
    print("\nAll key modules are installed!")