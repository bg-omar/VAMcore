#!/usr/bin/env python3
"""
Comprehensive test suite for SST Gravity bindings.
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
                print(f"    First 3: {value[:3]}")
            else:
                print(f"  {key} = {value}")
        else:
            print(f"  {key} = {value}")
    print("-"*80)
    print("Results:")
    if isinstance(results, (list, tuple, np.ndarray)):
        if hasattr(results, 'shape'):
            print(f"  Shape: {results.shape}")
            if results.size > 0:
                print(f"  Range: [{results.min():.4e}, {results.max():.4e}]")
        elif len(results) > 5:
            print(f"  Type: {type(results).__name__} of length {len(results)}")
            print(f"  First 3: {results[:3]}")
        else:
            print(f"  {results}")
    else:
        print(f"  {results}")
    print("="*80)


def test_compute_beltrami_shear():
    """Test Beltrami shear computation."""
    # Create B field and curl B
    n_points = 10
    B_field = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0],
        [1.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
        [0.5, 0.5, 0.5],
        [2.0, 0.0, 0.0],
        [0.0, 2.0, 0.0]
    ])
    
    Curl_B = np.array([
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]
    ])
    
    formula = r"$S = |\mathbf{B} \times (\nabla \times \mathbf{B})|$"
    
    result = swirl_string_core.SSTGravity.compute_beltrami_shear(B_field, Curl_B)
    
    log_test(
        "SSTGravity.compute_beltrami_shear",
        formula,
        {
            "B_field": f"B field with {len(B_field)} points",
            "Curl_B": f"Curl B with {len(Curl_B)} points"
        },
        result,
        "Compute the Beltrami Shear metric: S = || B x (Curl B) ||"
    )


def test_compute_gravity_dilation():
    """Test gravity dilation computation."""
    B_field = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [2.0, 0.0, 0.0],
        [0.0, 2.0, 0.0]
    ])
    omega_drive = 10.9e6  # Hz
    v_swirl = 1.09384563e6  # m/s
    B_saturation = 100.0  # Tesla
    
    formula = r"$G_{local} = G_0\left[1 - \left(\frac{v_{induced}}{v_{swirl}}\right)^2\right]$"
    
    result = swirl_string_core.SSTGravity.compute_gravity_dilation(
        B_field, omega_drive, v_swirl, B_saturation
    )
    
    log_test(
        "SSTGravity.compute_gravity_dilation",
        formula,
        {
            "B_field": f"B field with {len(B_field)} points",
            "omega_drive": omega_drive,
            "v_swirl": v_swirl,
            "B_saturation": B_saturation
        },
        result,
        "Compute the scalar Gravity Map (G_local)"
    )


def test_compute_helicity_density():
    """Test helicity density computation."""
    A_field = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0]
    ])
    B_field = np.array([
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]
    ])
    
    formula = r"$h = \mathbf{A} \cdot \mathbf{B}$"
    
    result = swirl_string_core.SSTGravity.compute_helicity_density(A_field, B_field)
    
    log_test(
        "SSTGravity.compute_helicity_density",
        formula,
        {
            "A_field": f"A field with {len(A_field)} points",
            "B_field": f"B field with {len(B_field)} points"
        },
        result,
        "Compute Helicity Density h = A · B"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SST GRAVITY COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_compute_beltrami_shear()
    test_compute_gravity_dilation()
    test_compute_helicity_density()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)