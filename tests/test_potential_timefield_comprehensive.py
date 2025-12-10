#!/usr/bin/env python3
"""
Comprehensive test suite for Potential Time Field bindings.
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
            if len(value) > 5:
                print(f"  {key} = {type(value).__name__} of length {len(value)}")
                print(f"    First 3: {value[:3]}")
            else:
                print(f"  {key} = {value}")
        else:
            print(f"  {key} = {value}")
    print("-"*80)
    print("Results:")
    if isinstance(results, (list, tuple, np.ndarray)):
        if len(results) > 5:
            print(f"  Type: {type(results).__name__} of length {len(results)}")
            print(f"  First 3: {results[:3]}")
            if hasattr(results, 'min') and hasattr(results, 'max'):
                print(f"  Range: [{results.min():.6e}, {results.max():.6e}]")
        else:
            print(f"  {results}")
    else:
        print(f"  {results}")
    print("="*80)


def test_compute_gravitational_potential_gradient():
    """Test gravitational potential (gradient method)."""
    positions = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [1.0, 1.0, 0.0]
    ]
    vorticity = [
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]
    ]
    epsilon = 7e-7
    
    formula = r"$\Phi(\mathbf{r}) = \int \frac{\boldsymbol{\omega} \cdot d\mathbf{A}}{|\mathbf{r}-\mathbf{r}'| + \epsilon}$ (gradient-based)"
    
    result = swirl_string_core.compute_gravitational_potential_gradient(positions, vorticity, epsilon)
    
    log_test(
        "compute_gravitational_potential_gradient",
        formula,
        {
            "positions": positions,
            "vorticity": vorticity,
            "epsilon": epsilon
        },
        result,
        "Compute Ætheric gravitational potential field from vorticity gradients"
    )


def test_compute_time_dilation_map_sqrt():
    """Test time dilation (sqrt method)."""
    tangents = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 0.0]
    ]
    C_e = 1093845.63
    
    formula = r"$\gamma = \sqrt{1 - \frac{|\mathbf{v}|^2}{C_e^2}}$"
    
    result = swirl_string_core.compute_time_dilation_map_sqrt(tangents, C_e)
    
    log_test(
        "compute_time_dilation_map_sqrt",
        formula,
        {
            "tangents": tangents,
            "C_e": C_e
        },
        result,
        "Compute time dilation factors from knot tangential velocities (sqrt method)"
    )


def test_compute_gravitational_potential_direct():
    """Test gravitational potential (direct method)."""
    positions = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ]
    vorticity = [
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]
    ]
    epsilon = 0.1
    
    formula = r"$\Phi(\mathbf{r}) = \int \frac{\boldsymbol{\omega} \cdot d\mathbf{A}}{|\mathbf{r}-\mathbf{r}'| + \epsilon}$ (direct computation)"
    
    result = swirl_string_core.compute_gravitational_potential_direct(positions, vorticity, epsilon)
    
    log_test(
        "compute_gravitational_potential_direct",
        formula,
        {
            "positions": positions,
            "vorticity": vorticity,
            "epsilon": epsilon
        },
        result,
        "Compute Æther gravitational potential field from vorticity (direct computation method)"
    )


def test_compute_time_dilation_map_linear():
    """Test time dilation (linear method)."""
    tangents = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]
    C_e = 1093845.63
    
    formula = r"$\gamma = 1 - \frac{|\mathbf{v}|}{C_e}$ (linear approximation)"
    
    result = swirl_string_core.compute_time_dilation_map_linear(tangents, C_e)
    
    log_test(
        "compute_time_dilation_map_linear",
        formula,
        {
            "tangents": tangents,
            "C_e": C_e
        },
        result,
        "Compute local time dilation factor map from tangential velocities (linear method)"
    )


def test_compute_gravitational_potential():
    """Test backward compatibility wrapper."""
    positions = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0]
    ]
    vorticity = [
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]
    ]
    epsilon = 7e-7
    
    formula = r"$\Phi(\mathbf{r}) = \int \frac{\boldsymbol{\omega} \cdot d\mathbf{A}}{|\mathbf{r}-\mathbf{r}'| + \epsilon}$ (backward compat)"
    
    result = swirl_string_core.compute_gravitational_potential(positions, vorticity, epsilon)
    
    log_test(
        "compute_gravitational_potential",
        formula,
        {
            "positions": positions,
            "vorticity": vorticity,
            "epsilon": epsilon
        },
        result,
        "Compute Ætheric gravitational potential field (backward compatibility - uses gradient method)"
    )


def test_compute_time_dilation_map():
    """Test backward compatibility wrapper."""
    tangents = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ]
    C_e = 1093845.63
    
    formula = r"$\gamma = \sqrt{1 - \frac{|\mathbf{v}|^2}{C_e^2}}$ (backward compat)"
    
    result = swirl_string_core.compute_time_dilation_map(tangents, C_e)
    
    log_test(
        "compute_time_dilation_map",
        formula,
        {
            "tangents": tangents,
            "C_e": C_e
        },
        result,
        "Compute time dilation factors (backward compatibility - uses sqrt method)"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("POTENTIAL TIME FIELD COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_compute_gravitational_potential_gradient()
    test_compute_time_dilation_map_sqrt()
    test_compute_gravitational_potential_direct()
    test_compute_time_dilation_map_linear()
    test_compute_gravitational_potential()
    test_compute_time_dilation_map()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)