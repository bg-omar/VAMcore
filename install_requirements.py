#!/usr/bin/env python
"""
Install script to handle pkg_resources issue by using --prefer-binary flag
"""
import subprocess
import sys

# First, ensure setuptools is properly installed
print("Ensuring setuptools is installed...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel", "packaging"])

# Now install all requirements with binary preference to avoid source compilation
print("\nInstalling requirements with binary preference...")
try:
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "--prefer-binary",  # Prefer binary wheels over source compilation
        "-r", "requirements.txt"
    ])
    print("\nSuccessfully installed all requirements!")
except subprocess.CalledProcessError as e:
    print(f"\nError installing requirements: {e}")
    print("\nTrying with --no-build-isolation flag...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "--no-build-isolation",  # Use system setuptools instead of isolated build env
            "-r", "requirements.txt"
        ])
        print("\nSuccessfully installed all requirements!")
    except subprocess.CalledProcessError as e2:
        print(f"\nFailed even with --no-build-isolation: {e2}")
        sys.exit(1)