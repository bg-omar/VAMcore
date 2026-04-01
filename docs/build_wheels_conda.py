#!/usr/bin/env python3
"""
Build wheels for multiple Python versions using conda environments.

This script:
1. Creates conda environments for each Python version (if they don't exist)
2. Builds wheels in each environment
3. Collects all wheels in the dist/ folder

Usage:
    python build_wheels_conda.py

Requirements:
    - conda installed and in PATH
    - conda activate command available
"""

import subprocess
import sys
import os
from pathlib import Path

# Python versions to build for
PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]

# Environment names (conda env names can't have dots)
ENV_NAMES = {v: f"py{v.replace('.', '')}" for v in PYTHON_VERSIONS}

def run_command(cmd, check=True, shell=True):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(
        cmd,
        shell=shell,
        capture_output=True,
        text=True,
        check=check
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
    return result

def conda_env_exists(env_name):
    """Check if a conda environment exists."""
    try:
        result = run_command(f"conda env list", check=False)
        return env_name in result.stdout
    except:
        return False

def create_conda_env(env_name, python_version):
    """Create a conda environment with specified Python version."""
    if conda_env_exists(env_name):
        print(f"✓ Conda environment '{env_name}' already exists")
        return True
    
    print(f"Creating conda environment '{env_name}' with Python {python_version}...")
    try:
        run_command(f"conda create -n {env_name} python={python_version} -y")
        print(f"✓ Created conda environment '{env_name}'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create conda environment '{env_name}': {e}")
        return False

def build_wheel_in_env(env_name, python_version):
    """Build wheel in a conda environment."""
    print(f"\n{'='*60}")
    print(f"Building wheel in conda environment '{env_name}' (Python {python_version})")
    print(f"{'='*60}")
    
    # Get conda base path
    try:
        result = run_command("conda info --base", check=True)
        conda_base = result.stdout.strip()
    except:
        print("Error: Could not find conda base path")
        return False
    
    # Determine activation script based on OS
    if sys.platform == "win32":
        activate_script = os.path.join(conda_base, "Scripts", "activate.bat")
        python_exe = os.path.join(conda_base, "envs", env_name, "python.exe")
        pip_exe = os.path.join(conda_base, "envs", env_name, "Scripts", "pip.exe")
    else:
        activate_script = os.path.join(conda_base, "etc", "profile.d", "conda.sh")
        python_exe = os.path.join(conda_base, "envs", env_name, "bin", "python")
        pip_exe = os.path.join(conda_base, "envs", env_name, "bin", "pip")
    
    # Check if environment exists
    if not os.path.exists(python_exe):
        print(f"✗ Python executable not found: {python_exe}")
        print(f"  Environment '{env_name}' may not exist. Creating it...")
        if not create_conda_env(env_name, python_version):
            return False
    
    try:
        # Install build dependencies
        print("Installing build dependencies...")
        run_command(f'"{pip_exe}" install --upgrade pip build wheel setuptools pybind11 numpy')
        
        # Build wheel
        print("Building wheel...")
        run_command(f'"{python_exe}" -m build --wheel')
        
        print(f"✓ Successfully built wheel in '{env_name}'")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build wheel in '{env_name}': {e}")
        return False

def main():
    print("Building wheels for multiple Python versions using conda")
    print("=" * 60)
    
    # Check if conda is available
    try:
        run_command("conda --version", check=True)
    except:
        print("Error: conda not found. Please install conda or add it to PATH.")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not os.path.exists("setup.py"):
        print("Error: setup.py not found. Run this script from the project root.")
        sys.exit(1)
    
    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    
    # Create conda environments and build wheels
    print(f"\nWill build wheels for {len(PYTHON_VERSIONS)} Python version(s):")
    for version in PYTHON_VERSIONS:
        print(f"  - Python {version} (env: {ENV_NAMES[version]})")
    
    print("\nCreating conda environments (if needed)...")
    for version in PYTHON_VERSIONS:
        env_name = ENV_NAMES[version]
        if not conda_env_exists(env_name):
            create_conda_env(env_name, version)
    
    # Build wheels
    print(f"\nBuilding wheels...")
    success_count = 0
    failed = []
    
    for version in PYTHON_VERSIONS:
        env_name = ENV_NAMES[version]
        if build_wheel_in_env(env_name, version):
            success_count += 1
        else:
            failed.append(version)
    
    # Summary
    print(f"\n{'='*60}")
    print("Build Summary")
    print(f"{'='*60}")
    
    dist_files = list(Path("dist").glob("*.whl")) if os.path.exists("dist") else []
    
    if dist_files:
        print(f"\n✓ Built {len(dist_files)} wheel(s) successfully:")
        for wheel in sorted(dist_files):
            print(f"  - {wheel.name}")
        print(f"\nWheels are in: {Path('dist').absolute()}")
    else:
        print("\n✗ No wheels were built successfully.")
    
    if failed:
        print(f"\n⚠ Failed to build wheels for: {', '.join(failed)}")
    
    print(f"\n✓ Successfully built wheels for {success_count}/{len(PYTHON_VERSIONS)} Python versions")
    
    if success_count > 0:
        print("\nTo upload to PyPI:")
        print("  twine upload dist/*.whl")
    
    print()

if __name__ == "__main__":
    main()