#!/usr/bin/env python3
"""
Helper script to build wheels for multiple Python versions locally.
Requires multiple Python versions to be installed (via pyenv, conda, or system).

Usage:
    python build_wheels_local.py
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

# Python versions to build for
PYTHON_VERSIONS = ["3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]

def find_python_executable(version):
    """Find Python executable for given version."""
    # Try common names
    names = [
        f"python{version}",
        f"python{version.replace('.', '')}",  # python312
        f"py -{version}",  # Windows py launcher
    ]
    
    for name in names:
        try:
            result = subprocess.run(
                [name, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return name
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    return None

def build_wheel(python_exe):
    """Build wheel using specified Python executable."""
    print(f"\n{'='*60}")
    print(f"Building wheel with {python_exe}")
    print(f"{'='*60}")
    
    # Install build dependencies
    print("Installing build dependencies...")
    subprocess.run(
        [python_exe, "-m", "pip", "install", "--upgrade", "pip", "build", "wheel", "setuptools", "pybind11", "numpy"],
        check=True
    )
    
    # Clean previous builds (optional)
    # shutil.rmtree("build", ignore_errors=True)
    # shutil.rmtree("dist", ignore_errors=True)
    
    # Build wheel
    print("Building wheel...")
    subprocess.run(
        [python_exe, "-m", "build", "--wheel"],
        check=True
    )
    
    print(f"✓ Successfully built wheel with {python_exe}")

def main():
    print("Building wheels for multiple Python versions")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("setup.py"):
        print("Error: setup.py not found. Run this script from the project root.")
        sys.exit(1)
    
    # Find available Python versions
    available = {}
    missing = []
    
    for version in PYTHON_VERSIONS:
        exe = find_python_executable(version)
        if exe:
            available[version] = exe
            print(f"✓ Found Python {version}: {exe}")
        else:
            missing.append(version)
            print(f"✗ Python {version} not found")
    
    if not available:
        print("\nError: No Python versions found!")
        print("Install Python versions using:")
        print("  - pyenv: pyenv install 3.7 3.8 3.9 ...")
        print("  - conda: conda create -n py37 python=3.7")
        print("  - Or download from python.org")
        sys.exit(1)
    
    if missing:
        print(f"\nWarning: Missing Python versions: {', '.join(missing)}")
        print("Wheels will only be built for available versions.")
    
    # Build wheels
    print(f"\nBuilding wheels for {len(available)} Python version(s)...")
    
    for version, exe in available.items():
        try:
            build_wheel(exe)
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to build wheel for Python {version}: {e}")
            continue
    
    # Summary
    print(f"\n{'='*60}")
    print("Build Summary")
    print(f"{'='*60}")
    
    dist_files = list(Path("dist").glob("*.whl")) if os.path.exists("dist") else []
    
    if dist_files:
        print(f"\n✓ Built {len(dist_files)} wheel(s):")
        for wheel in sorted(dist_files):
            print(f"  - {wheel.name}")
        print(f"\nWheels are in: {Path('dist').absolute()}")
        print("\nTo upload to PyPI:")
        print("  twine upload dist/*.whl")
    else:
        print("\n✗ No wheels were built successfully.")
    
    print()

if __name__ == "__main__":
    main()


