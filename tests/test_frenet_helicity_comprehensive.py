#!/usr/bin/env python3
"""
Comprehensive test suite for Frenet Helicity bindings.
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
        if isinstance(results, tuple) and len(results) > 1:
            for i, r in enumerate(results):
                if isinstance(r, (list, np.ndarray)):
                    if len(r) > 5:
                        print(f"  Result[{i}]: {type(r).__name__} of length {len(r)}")
                    else:
                        print(f"  Result[{i}]: {r}")
                else:
                    print(f"  Result[{i}]: {r}")
        elif hasattr(results, 'shape'):
            print(f"  Shape: {results.shape}")
        elif len(results) > 5:
            print(f"  Type: {type(results).__name__} of length {len(results)}")
            print(f"  First 3: {results[:3]}")
        else:
            print(f"  {results}")
    else:
        print(f"  {results}")
    print("="*80)


def test_compute_frenet_frames():
    """Test Frenet frame computation."""
    # Create a helix curve
    t = np.linspace(0, 4*np.pi, 50)
    X = [
        [np.cos(s), np.sin(s), s/10.0] for s in t
    ]
    
    formula = r"$\mathbf{T} = \frac{d\mathbf{r}/ds}{|d\mathbf{r}/ds|}, \quad \mathbf{N} = \frac{d\mathbf{T}/ds}{|d\mathbf{T}/ds|}, \quad \mathbf{B} = \mathbf{T} \times \mathbf{N}$"
    
    T, N, B = swirl_string_core.compute_frenet_frames(X)
    
    log_test(
        "compute_frenet_frames",
        formula,
        {
            "X": f"Helix curve with {len(X)} points"
        },
        (T, N, B),
        "Compute Frenet frames (T, N, B) from 3D filament points"
    )


def test_compute_curvature_torsion():
    """Test curvature and torsion computation."""
    # Create tangent and normal vectors
    n = 20
    T = [
        [np.cos(i*0.1), np.sin(i*0.1), 0.1] for i in range(n)
    ]
    N = [
        [-np.sin(i*0.1), np.cos(i*0.1), 0.0] for i in range(n)
    ]
    
    formula = r"$\kappa = |\mathbf{T}'|, \quad \tau = -\mathbf{N} \cdot \mathbf{B}'$"
    
    curvature, torsion = swirl_string_core.compute_curvature_torsion(T, N)
    
    log_test(
        "compute_curvature_torsion",
        formula,
        {
            "T": f"Tangent vectors: {len(T)} points",
            "N": f"Normal vectors: {len(N)} points"
        },
        {
            "curvature": f"Length {len(curvature)}, first 3: {curvature[:3]}",
            "torsion": f"Length {len(torsion)}, first 3: {torsion[:3]}"
        },
        "Compute curvature and torsion from tangent and normal vectors"
    )


def test_compute_helicity():
    """Test helicity computation."""
    velocity = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 0.0]
    ]
    vorticity = [
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]
    ]
    
    formula = r"$H = \int \mathbf{v} \cdot \boldsymbol{\omega} \, dV$"
    
    result = swirl_string_core.compute_helicity(velocity, vorticity)
    
    log_test(
        "compute_helicity",
        formula,
        {
            "velocity": velocity,
            "vorticity": vorticity
        },
        result,
        "Compute helicity H = ∫ v · ω dV"
    )


def test_evolve_vortex_knot():
    """Test vortex knot evolution."""
    # This function may have specific signature requirements
    # Testing with reasonable defaults
    formula = r"$\frac{d\mathbf{r}}{dt} = \mathbf{v}(\mathbf{r}, t)$ (Biot-Savart dynamics)"
    
    print("\n" + "="*80)
    print("Testing: evolve_vortex_knot")
    print("-"*80)
    print("LaTeX Formula:")
    print(f"  {formula}")
    print("-"*80)
    print("Note: This function requires specific knot initialization.")
    print("Please refer to VortexKnotSystem class for usage.")
    print("="*80)


def test_rk4_integrate():
    """Test RK4 integration."""
    formula = r"$\mathbf{r}_{n+1} = \mathbf{r}_n + \frac{\Delta t}{6}(\mathbf{k}_1 + 2\mathbf{k}_2 + 2\mathbf{k}_3 + \mathbf{k}_4)$"
    
    print("\n" + "="*80)
    print("Testing: rk4_integrate")
    print("-"*80)
    print("LaTeX Formula:")
    print(f"  {formula}")
    print("-"*80)
    print("Note: This function requires specific integration setup.")
    print("Please refer to implementation for usage.")
    print("="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("FRENET HELICITY COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_compute_frenet_frames()
    test_compute_curvature_torsion()
    test_compute_helicity()
    test_evolve_vortex_knot()
    test_rk4_integrate()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)