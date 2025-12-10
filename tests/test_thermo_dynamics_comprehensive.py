#!/usr/bin/env python3
"""
Comprehensive test suite for Thermodynamics bindings.
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


def test_potential_temperature():
    """Test potential temperature computation."""
    T = 300.0  # Temperature (K)
    p0 = 101325.0  # Reference pressure (Pa)
    p = 80000.0  # Current pressure (Pa)
    R = 287.0  # Gas constant (J/(kg·K))
    cp = 1005.0  # Specific heat at constant pressure (J/(kg·K))
    
    formula = r"$\theta = T\left(\frac{p_0}{p}\right)^\kappa$ where $\kappa = \frac{R}{c_p}$"
    
    result = swirl_string_core.potential_temperature(T, p0, p, R, cp)
    
    log_test(
        "potential_temperature",
        formula,
        {
            "T": T,
            "p0": p0,
            "p": p,
            "R": R,
            "cp": cp
        },
        result,
        "Compute potential temperature θ = T (p0/p)^k"
    )


def test_entropy_from_theta():
    """Test entropy from potential temperature."""
    cp = 1005.0  # Specific heat (J/(kg·K))
    theta = 310.0  # Potential temperature (K)
    dtheta = 10.0  # Change in potential temperature (K)
    
    formula = r"$ds = c_p \frac{d\theta}{\theta}$"
    
    result = swirl_string_core.entropy_from_theta(cp, theta, dtheta)
    
    log_test(
        "entropy_from_theta",
        formula,
        {
            "cp": cp,
            "theta": theta,
            "dtheta": dtheta
        },
        result,
        "Entropy differential ds = cp * dθ / θ"
    )


def test_entropy_from_pv():
    """Test entropy from pressure and volume."""
    N = 1.0  # Number of moles
    R = 8.314  # Gas constant (J/(mol·K))
    p = 101325.0  # Pressure (Pa)
    V = 0.024  # Volume (m³)
    gamma = 1.4  # Adiabatic index
    
    formula = r"$ds = \frac{NR}{\gamma-1}(\ln(p) + \ln(V))$"
    
    result = swirl_string_core.entropy_from_pv(N, R, p, V, gamma)
    
    log_test(
        "entropy_from_pv",
        formula,
        {
            "N": N,
            "R": R,
            "p": p,
            "V": V,
            "gamma": gamma
        },
        result,
        "Entropy from pressure and volume ds = NR/(γ-1) * (ln(p)+ln(V))"
    )


def test_enthalpy():
    """Test enthalpy computation."""
    internal_energy = 1000.0  # J
    p = 101325.0  # Pressure (Pa)
    V = 0.001  # Volume (m³)
    
    formula = r"$H = E + pV$"
    
    result = swirl_string_core.enthalpy(internal_energy, p, V)
    
    log_test(
        "enthalpy",
        formula,
        {
            "internal_energy": internal_energy,
            "p": p,
            "V": V
        },
        result,
        "Enthalpy H = E + pV"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("THERMODYNAMICS COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_potential_temperature()
    test_entropy_from_theta()
    test_entropy_from_pv()
    test_enthalpy()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)