#!/usr/bin/env python
import sys

try:
    import pandas
    print(f"pandas version: {pandas.__version__}")
except ImportError as e:
    print(f"pandas import failed: {e}")
    sys.exit(1)

# Try importlib.metadata first (modern approach for Python 3.8+)
try:
    from importlib.metadata import distribution
    dist = distribution('setuptools')
    print(f"setuptools version: {dist.version}")
except ImportError:
    # Fall back to pkg_resources
    try:
        import pkg_resources
        version = pkg_resources.get_distribution('setuptools').version
        print(f"setuptools version: {version}")
    except Exception as e:
        print(f"Failed to get setuptools version: {e}")

try:
    from setuptools import setup
    print("setuptools: OK")
except ImportError as e:
    print(f"setuptools import failed: {e}")
    sys.exit(1)

print("All checks successful!")