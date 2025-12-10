#!/usr/bin/env python3
"""
Comprehensive test suite for Vortex Ring bindings.
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
        print(f"  {key} = {value}")
    print("-"*80)
    print("Results:")
    print(f"  {results}")
    print("="*80)


def test_lamb_oseen_velocity():
    """Test Lamb-Oseen velocity."""
    gamma = 1.0  # Circulation
    R = 1.0  # Radius
    nu = 0.01  # Kinematic viscosity
    t = 1.0  # Time
    
    formula = r"$v_\theta(r,t) = \frac{\Gamma}{2\pi r}\left(1 - e^{-\frac{r^2}{4\nu t}}\right)$"
    
    result = swirl_string_core.lamb_oseen_velocity(gamma, R, nu, t)
    
    log_test(
        "lamb_oseen_velocity",
        formula,
        {
            "gamma": gamma,
            "R": R,
            "nu": nu,
            "t": t
        },
        result,
        "Lamb-Oseen azimuthal velocity at radius R and time t"
    )


def test_lamb_oseen_vorticity():
    """Test Lamb-Oseen vorticity."""
    gamma = 1.0  # Circulation
    r = 1.0  # Radial distance
    nu = 0.01  # Kinematic viscosity
    t = 1.0  # Time
    
    formula = r"$\omega(r,t) = \frac{\Gamma}{4\pi\nu t}\exp\left(-\frac{r^2}{4\nu t}\right)$"
    
    result = swirl_string_core.lamb_oseen_vorticity(gamma, r, nu, t)
    
    log_test(
        "lamb_oseen_vorticity",
        formula,
        {
            "gamma": gamma,
            "r": r,
            "nu": nu,
            "t": t
        },
        result,
        "Lamb-Oseen vorticity"
    )


def test_hill_streamfunction():
    """Test Hill's vortex streamfunction."""
    A = 1.0  # Amplitude
    r = 0.5  # Radial coordinate
    z = 0.5  # Axial coordinate
    R = 1.0  # Vortex radius
    
    formula = r"$\psi(r,z) = A r^2 (R^2 - r^2 - z^2)$ (inside sphere)"
    
    result = swirl_string_core.hill_streamfunction(A, r, z, R)
    
    log_test(
        "hill_streamfunction",
        formula,
        {
            "A": A,
            "r": r,
            "z": z,
            "R": R
        },
        result,
        "Hill's vortex streamfunction (ψ) inside sphere of radius R"
    )


def test_hill_vorticity():
    """Test Hill's vortex vorticity."""
    A = 1.0
    r = 0.5
    z = 0.5
    R = 1.0
    
    formula = r"$\omega(r,z) = 2A (R^2 - 2r^2 - z^2)$ (inside sphere)"
    
    result = swirl_string_core.hill_vorticity(A, r, z, R)
    
    log_test(
        "hill_vorticity",
        formula,
        {
            "A": A,
            "r": r,
            "z": z,
            "R": R
        },
        result,
        "Hill's vortex vorticity inside sphere of radius R"
    )


def test_hill_circulation():
    """Test Hill's vortex circulation."""
    A = 1.0
    R = 1.0
    
    formula = r"$\Gamma = \int \omega \, dA = \frac{8\pi A R^4}{15}$"
    
    result = swirl_string_core.hill_circulation(A, R)
    
    log_test(
        "hill_circulation",
        formula,
        {
            "A": A,
            "R": R
        },
        result,
        "Circulation of Hill's vortex"
    )


def test_hill_velocity():
    """Test Hill's vortex propagation speed."""
    gamma = 1.0  # Circulation
    R = 1.0  # Radius
    
    formula = r"$U = \frac{\Gamma}{4\pi R}$"
    
    result = swirl_string_core.hill_velocity(gamma, R)
    
    log_test(
        "hill_velocity",
        formula,
        {
            "gamma": gamma,
            "R": R
        },
        result,
        "Propagation speed of Hill's vortex"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("VORTEX RING COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_lamb_oseen_velocity()
    test_lamb_oseen_vorticity()
    test_hill_streamfunction()
    test_hill_vorticity()
    test_hill_circulation()
    test_hill_velocity()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)