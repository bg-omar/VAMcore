#!/usr/bin/env python3
"""
Comprehensive test suite for Field Operations bindings.
Tests all functions with LaTeX formulas, inputs, and results logged.
"""

import sys
import os
import numpy as np

# Add build directory to path
build_dir = os.path.join(os.path.dirname(__file__), "../build/Debug")
if os.path.exists(build_dir):
    sys.path.insert(0, build_dir)

try:
    import swirl_string_core
    HAS_SST = True
except ImportError:
    try:
        import sstbindings as swirl_string_core
        HAS_SST = True
    except ImportError:
        print("ERROR: Could not import swirl_string_core or sstbindings")
        sys.exit(1)


def log_test(func_name, latex_formula, inputs_dict, results, description=""):
    """Log test information in structured format."""
    print("\n" + "="*80)
    print(f"Testing: {func_name}")
    if description:
        print(f"Description: {description}")
    print("-"*80)
    print("LaTeX Formula:")
    print(f"  {latex_formula}")
    print("-"*80)
    print("Inputs:")
    for key, value in inputs_dict.items():
        if isinstance(value, (list, np.ndarray)):
            if hasattr(value, 'shape'):
                print(f"  {key} = array of shape {value.shape}")
            elif len(value) > 5:
                print(f"  {key} = {type(value).__name__} of length {len(value)}")
            else:
                print(f"  {key} = {value}")
        else:
            print(f"  {key} = {value}")
    print("-"*80)
    print("Results:")
    if isinstance(results, (list, tuple, np.ndarray)):
        if hasattr(results, 'shape'):
            print(f"  Shape: {results.shape}")
            print(f"  Range: [{results.min():.4e}, {results.max():.4e}]")
        elif len(results) > 5:
            print(f"  Type: {type(results).__name__} of length {len(results)}")
        else:
            print(f"  {results}")
    else:
        print(f"  {results}")
    print("="*80)


def test_curl3d_central():
    """Test central difference curl with periodic boundary conditions."""
    # Create a simple velocity field: solid body rotation
    nx, ny, nz = 5, 5, 3
    vel = np.zeros((nx, ny, nz, 3))
    
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                x = i - nx/2
                y = j - ny/2
                r = np.sqrt(x*x + y*y) + 0.1
                # Azimuthal velocity (vortex)
                vel[i, j, k, 0] = -y / r
                vel[i, j, k, 1] = x / r
                vel[i, j, k, 2] = 0.0
    
    spacing = 0.1
    
    formula = r"$\boldsymbol{\omega} = \nabla \times \mathbf{v} = \left(\frac{\partial v_z}{\partial y} - \frac{\partial v_y}{\partial z}, \frac{\partial v_x}{\partial z} - \frac{\partial v_z}{\partial x}, \frac{\partial v_y}{\partial x} - \frac{\partial v_x}{\partial y}\right)$"
    
    result = swirl_string_core.curl3d_central(vel, spacing)
    
    log_test(
        "curl3d_central",
        formula,
        {
            "vel": f"Velocity field of shape {vel.shape}",
            "spacing": spacing
        },
        result,
        "Central-difference curl with periodic BCs"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("FIELD OPERATIONS COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_curl3d_central()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)