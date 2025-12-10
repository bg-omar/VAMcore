#!/usr/bin/env python3
"""
Comprehensive test suite for Time Evolution bindings.
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
        else:
            print(f"  {results}")
    else:
        print(f"  {results}")
    print("="*80)


def test_time_evolution():
    """Test TimeEvolution class."""
    initial_positions = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ]
    initial_tangents = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]
    gamma = 1.0
    
    formula = r"$\frac{d\mathbf{r}}{dt} = \mathbf{v}(\mathbf{r}, t)$"
    
    # Create TimeEvolution instance
    te = swirl_string_core.TimeEvolution(initial_positions, initial_tangents, gamma)
    
    # Get initial state
    pos_init = te.get_positions()
    tan_init = te.get_tangents()
    
    log_test(
        "TimeEvolution.__init__",
        formula,
        {
            "initial_positions": initial_positions,
            "initial_tangents": initial_tangents,
            "gamma": gamma
        },
        {
            "initial_positions": pos_init,
            "initial_tangents": tan_init
        },
        "Initialize TimeEvolution system"
    )
    
    # Evolve
    dt = 0.01
    steps = 10
    
    formula_evolve = r"$\mathbf{r}(t+\Delta t) = \mathbf{r}(t) + \int_t^{t+\Delta t} \mathbf{v}(\mathbf{r}, \tau) d\tau$"
    
    te.evolve(dt, steps)
    
    pos_final = te.get_positions()
    tan_final = te.get_tangents()
    
    log_test(
        "TimeEvolution.evolve",
        formula_evolve,
        {
            "dt": dt,
            "steps": steps
        },
        {
            "final_positions": pos_final,
            "final_tangents": tan_final
        },
        "Evolve system forward in time"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TIME EVOLUTION COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_time_evolution()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)