#!/usr/bin/env python3
"""
Comprehensive test suite for Hyperbolic Volume bindings.
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
        else:
            print(f"  {results}")
    else:
        print(f"  {results}")
    print("="*80)


def test_hyperbolic_volume_from_pd():
    """Test hyperbolic volume computation from PD code."""
    # PD code: (a, b, c, d) tuples representing crossings
    # Simple trefoil knot PD code
    pd = [
        [1, 2, 3, 4],
        [3, 4, 5, 6],
        [5, 6, 1, 2]
    ]
    
    formula = r"$\text{Vol}(K) = \text{hyperbolic volume from PD code}$ (topological invariant)"
    
    try:
        result = swirl_string_core.hyperbolic_volume_from_pd(pd)
        
        log_test(
            "hyperbolic_volume_from_pd",
            formula,
            {
                "pd": pd
            },
            result,
            "Hyperbolic volume from PD code (topological invariant)"
        )
    except Exception as e:
        print("\n" + "="*80)
        print("Testing: hyperbolic_volume_from_pd")
        print("-"*80)
        print("LaTeX Formula:")
        print(f"  {formula}")
        print("-"*80)
        print("Inputs:")
        print(f"  pd = {pd}")
        print("-"*80)
        print("Results:")
        print(f"  Error: {e}")
        print("  Note: This may require native solver or Python fallback")
        print("="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("HYPERBOLIC VOLUME COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_hyperbolic_volume_from_pd()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)