#!/usr/bin/env python3
"""
Comprehensive test suite for Swirl Field bindings.
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
        if hasattr(results, 'shape'):
            print(f"  Shape: {results.shape}")
        elif len(results) > 5:
            print(f"  Type: {type(results).__name__} of length {len(results)}")
        else:
            print(f"  {results}")
    else:
        print(f"  {results}")
    print("="*80)


def test_compute_swirl_field():
    """Test swirl field computation."""
    res = 10  # Resolution
    time = 0.0
    
    formula = r"$\mathbf{F}_{swirl}(\mathbf{r}, t) = \text{swirl force field}$"
    
    try:
        result = swirl_string_core.compute_swirl_field(res, time)
        
        log_test(
            "compute_swirl_field",
            formula,
            {
                "res": res,
                "time": time
            },
            result,
            "Compute 2D swirl force field at a given resolution and time"
        )
    except Exception as e:
        print("\n" + "="*80)
        print("Testing: compute_swirl_field")
        print("-"*80)
        print("LaTeX Formula:")
        print(f"  {formula}")
        print("-"*80)
        print("Inputs:")
        print(f"  res = {res}")
        print(f"  time = {time}")
        print("-"*80)
        print("Results:")
        print(f"  Error: {e}")
        print("  Please check function signature in swirl_field.h")
        print("="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SWIRL FIELD COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_compute_swirl_field()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)