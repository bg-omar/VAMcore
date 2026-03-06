#!/usr/bin/env python
import sys
try:
    import pandas
    print(f"pandas version: {pandas.__version__}")
except ImportError as e:
    print(f"pandas import failed: {e}")
    sys.exit(1)

try:
    import pkg_resources
    print("pkg_resources: OK")
except ImportError as e:
    print(f"pkg_resources import failed: {e}")
    sys.exit(1)

try:
    from setuptools import setup
    print("setuptools: OK")
except ImportError as e:
    print(f"setuptools import failed: {e}")
    sys.exit(1)

print("All imports successful!")