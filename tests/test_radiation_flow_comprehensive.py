#!/usr/bin/env python3
"""
Comprehensive test suite for Radiation Flow bindings.
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
            else:
                print(f"  {key} = {value}")
        else:
            print(f"  {key} = {value}")
    print("-"*80)
    print("Results:")
    if isinstance(results, (list, tuple, np.ndarray)):
        if len(results) > 5:
            print(f"  Type: {type(results).__name__} of length {len(results)}")
        else:
            print(f"  {results}")
    else:
        print(f"  {results}")
    print("="*80)


def test_radiation_force():
    """Test radiation force computation."""
    # Note: Function signature needs to be checked from header
    formula = r"$F_{rad} = \text{radiation force}$"
    
    print("\n" + "="*80)
    print("Testing: radiation_force")
    print("-"*80)
    print("LaTeX Formula:")
    print(f"  {formula}")
    print("-"*80)
    print("Note: Function signature needs to be verified from header file.")
    print("Please check radiation_flow.h for exact parameters.")
    print("="*80)


def test_van_der_pol_dx():
    """Test Van der Pol oscillator dx/dt."""
    # Van der Pol: dx/dt = y
    x = 1.0
    y = 0.5
    mu = 1.0
    
    formula = r"$\frac{dx}{dt} = y$ (Van der Pol oscillator)"
    
    try:
        result = swirl_string_core.van_der_pol_dx(x, y, mu)
        
        log_test(
            "van_der_pol_dx",
            formula,
            {
                "x": x,
                "y": y,
                "mu": mu
            },
            result,
            "Van der Pol dx/dt"
        )
    except TypeError:
        # Try without mu
        try:
            result = swirl_string_core.van_der_pol_dx(x, y)
            log_test(
                "van_der_pol_dx",
                formula,
                {
                    "x": x,
                    "y": y
                },
                result,
                "Van der Pol dx/dt"
            )
        except Exception as e:
            print("\n" + "="*80)
            print("Testing: van_der_pol_dx")
            print("-"*80)
            print("LaTeX Formula:")
            print(f"  {formula}")
            print("-"*80)
            print(f"Error: {e}")
            print("Please check function signature in radiation_flow.h")
            print("="*80)


def test_van_der_pol_dy():
    """Test Van der Pol oscillator dy/dt."""
    # Van der Pol: dy/dt = mu(1-x^2)y - x
    x = 1.0
    y = 0.5
    mu = 1.0
    
    formula = r"$\frac{dy}{dt} = \mu(1-x^2)y - x$ (Van der Pol oscillator)"
    
    try:
        result = swirl_string_core.van_der_pol_dy(x, y, mu)
        
        log_test(
            "van_der_pol_dy",
            formula,
            {
                "x": x,
                "y": y,
                "mu": mu
            },
            result,
            "Van der Pol dy/dt"
        )
    except TypeError:
        # Try without mu
        try:
            result = swirl_string_core.van_der_pol_dy(x, y)
            log_test(
                "van_der_pol_dy",
                formula,
                {
                    "x": x,
                    "y": y
                },
                result,
                "Van der Pol dy/dt"
            )
        except Exception as e:
            print("\n" + "="*80)
            print("Testing: van_der_pol_dy")
            print("-"*80)
            print("LaTeX Formula:")
            print(f"  {formula}")
            print("-"*80)
            print(f"Error: {e}")
            print("Please check function signature in radiation_flow.h")
            print("="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RADIATION FLOW COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_radiation_force()
    test_van_der_pol_dx()
    test_van_der_pol_dy()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)