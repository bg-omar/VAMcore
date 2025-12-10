#!/usr/bin/env python3
"""
Comprehensive test suite for Knot Dynamics bindings.
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
                    if hasattr(r, 'shape'):
                        print(f"  Result[{i}]: shape {r.shape}")
                    elif len(r) > 5:
                        print(f"  Result[{i}]: length {len(r)}")
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


def test_fourier_knot_eval():
    """Test Fourier knot evaluation."""
    # Simple Fourier coefficients
    n_harmonics = 3
    a_x = [0.0, 1.0, 0.0]
    b_x = [0.0, 0.0, 0.0]
    a_y = [0.0, 0.0, 1.0]
    b_y = [0.0, 0.0, 0.0]
    a_z = [0.0, 0.0, 0.0]
    b_z = [0.0, 0.0, 0.0]
    s = np.linspace(0, 2*np.pi, 20)
    
    formula = r"$\mathbf{r}(s) = \sum_{n=0}^{N} \left(a_n \cos(ns) + b_n \sin(ns)\right)$"
    
    x, y, z = swirl_string_core.fourier_knot_eval(a_x, b_x, a_y, b_y, a_z, b_z, s)
    
    log_test(
        "fourier_knot_eval",
        formula,
        {
            "a_x": a_x,
            "b_x": b_x,
            "a_y": a_y,
            "b_y": b_y,
            "a_z": a_z,
            "b_z": b_z,
            "s": f"Parameter array of length {len(s)}"
        },
        (x, y, z),
        "NumPy-friendly Fourier evaluation returning (x,y,z)"
    )


def test_compute_writhe():
    """Test writhe computation."""
    # Create a simple closed curve (trefoil-like)
    n_points = 50
    t = np.linspace(0, 2*np.pi, n_points)
    r = [
        [np.cos(3*s), np.sin(3*s), np.sin(2*s)] for s in t
    ]
    
    formula = r"$Wr = \frac{1}{4\pi}\oint\oint\frac{(\mathbf{r}_1-\mathbf{r}_2)\cdot(d\mathbf{r}_1\times d\mathbf{r}_2)}{|\mathbf{r}_1-\mathbf{r}_2|^3}$"
    
    try:
        result = swirl_string_core.compute_writhe(r)
        
        log_test(
            "compute_writhe",
            formula,
            {
                "r": f"Closed curve with {len(r)} points"
            },
            result,
            "Compute the writhe of a closed filament (topological self-linking)"
        )
    except Exception as e:
        print("\n" + "="*80)
        print("Testing: compute_writhe")
        print("-"*80)
        print("LaTeX Formula:")
        print(f"  {formula}")
        print("-"*80)
        print(f"Error: {e}")
        print("="*80)


def test_compute_linking_number():
    """Test linking number computation."""
    # Two linked circles
    n1, n2 = 20, 20
    t1 = np.linspace(0, 2*np.pi, n1)
    t2 = np.linspace(0, 2*np.pi, n2)
    
    curve1 = [
        [np.cos(s), np.sin(s), 0.0] for s in t1
    ]
    curve2 = [
        [1.0 + 0.5*np.cos(s), 0.5*np.sin(s), 0.5*np.sin(s)] for s in t2
    ]
    
    formula = r"$Lk = \frac{1}{4\pi}\oint\oint\frac{(\mathbf{r}_1-\mathbf{r}_2)\cdot(d\mathbf{r}_1\times d\mathbf{r}_2)}{|\mathbf{r}_1-\mathbf{r}_2|^3}$"
    
    try:
        result = swirl_string_core.compute_linking_number(curve1, curve2)
        
        log_test(
            "compute_linking_number",
            formula,
            {
                "curve1": f"First curve with {len(curve1)} points",
                "curve2": f"Second curve with {len(curve2)} points"
            },
            result,
            "Compute the Gauss linking number between two closed loops"
        )
    except Exception as e:
        print("\n" + "="*80)
        print("Testing: compute_linking_number")
        print("-"*80)
        print("LaTeX Formula:")
        print(f"  {formula}")
        print("-"*80)
        print(f"Error: {e}")
        print("="*80)


def test_compute_twist():
    """Test twist computation."""
    # Create Frenet frames
    n = 30
    t = np.linspace(0, 2*np.pi, n)
    T = [
        [-np.sin(s), np.cos(s), 0.1] for s in t
    ]
    N = [
        [-np.cos(s), -np.sin(s), 0.0] for s in t
    ]
    
    formula = r"$Tw = \frac{1}{2\pi}\oint \tau(s) ds$ where $\tau = -\mathbf{N} \cdot \mathbf{B}'$"
    
    try:
        result = swirl_string_core.compute_twist(T, N)
        
        log_test(
            "compute_twist",
            formula,
            {
                "T": f"Tangent vectors: {len(T)} points",
                "N": f"Normal vectors: {len(N)} points"
            },
            result,
            "Compute twist from Frenet frames along a filament"
        )
    except Exception as e:
        print("\n" + "="*80)
        print("Testing: compute_twist")
        print("-"*80)
        print("LaTeX Formula:")
        print(f"  {formula}")
        print("-"*80)
        print(f"Error: {e}")
        print("="*80)


def test_compute_centerline_helicity():
    """Test centerline helicity computation."""
    # Create a simple curve
    n = 20
    t = np.linspace(0, 2*np.pi, n)
    r = [
        [np.cos(s), np.sin(s), s/10.0] for s in t
    ]
    
    formula = r"$H_{centerline} = Wr + Tw$"
    
    try:
        result = swirl_string_core.compute_centerline_helicity(r)
        
        log_test(
            "compute_centerline_helicity",
            formula,
            {
                "r": f"Closed curve with {len(r)} points"
            },
            result,
            "Compute the centerline helicity as the sum of writhe and twist"
        )
    except Exception as e:
        print("\n" + "="*80)
        print("Testing: compute_centerline_helicity")
        print("-"*80)
        print("LaTeX Formula:")
        print(f"  {formula}")
        print("-"*80)
        print(f"Error: {e}")
        print("="*80)


def test_pd_from_curve():
    """Test PD code generation from curve."""
    # Create a simple trefoil-like curve
    n = 30
    t = np.linspace(0, 2*np.pi, n)
    P3 = [
        [np.cos(3*s), np.sin(3*s), np.sin(2*s)] for s in t
    ]
    tries = 40
    seed = 12345
    min_angle_deg = 1.0
    depth_tol = 1e-6
    
    formula = r"$\text{PD code} = \{(a_i, b_i, c_i, d_i)\}$ from curve projection"
    
    try:
        result = swirl_string_core.pd_from_curve(P3, tries, seed, min_angle_deg, depth_tol)
        
        log_test(
            "pd_from_curve",
            formula,
            {
                "P3": f"Closed curve with {len(P3)} points",
                "tries": tries,
                "seed": seed,
                "min_angle_deg": min_angle_deg,
                "depth_tol": depth_tol
            },
            f"PD code with {len(result)} crossings",
            "Compute a PD code from a closed 3D polygonal curve"
        )
    except Exception as e:
        print("\n" + "="*80)
        print("Testing: pd_from_curve")
        print("-"*80)
        print("LaTeX Formula:")
        print(f"  {formula}")
        print("-"*80)
        print(f"Error: {e}")
        print("="*80)


def test_estimate_crossing_number():
    """Test crossing number estimation."""
    # Create a curve
    n = 30
    t = np.linspace(0, 2*np.pi, n)
    r = [
        [np.cos(3*s), np.sin(3*s), np.sin(2*s)] for s in t
    ]
    directions = 24
    seed = 12345
    
    formula = r"$\text{Crossing number} = \text{max crossings over random projections}$"
    
    try:
        result = swirl_string_core.estimate_crossing_number(r, directions, seed)
        
        log_test(
            "estimate_crossing_number",
            formula,
            {
                "r": f"Curve with {len(r)} points",
                "directions": directions,
                "seed": seed
            },
            result,
            "Estimate crossing number from projections"
        )
    except Exception as e:
        print("\n" + "="*80)
        print("Testing: estimate_crossing_number")
        print("-"*80)
        print("LaTeX Formula:")
        print(f"  {formula}")
        print("-"*80)
        print(f"Error: {e}")
        print("="*80)


def test_vortex_knot_system():
    """Test VortexKnotSystem class."""
    circulation = 1.0
    
    formula = r"$\frac{d\mathbf{r}}{dt} = \mathbf{v}(\mathbf{r}, t)$ (Biot-Savart dynamics)"
    
    # Initialize system
    knot = swirl_string_core.VortexKnotSystem(circulation)
    
    log_test(
        "VortexKnotSystem.__init__",
        formula,
        {
            "circulation": circulation
        },
        "System initialized",
        "Initialize a VortexKnotSystem with optional circulation parameter"
    )
    
    # Initialize trefoil
    resolution = 100
    knot.initialize_trefoil_knot(resolution)
    
    pos = knot.get_positions()
    tan = knot.get_tangents()
    
    log_test(
        "VortexKnotSystem.initialize_trefoil_knot",
        formula,
        {
            "resolution": resolution
        },
        {
            "positions": f"Trefoil with {len(pos)} points",
            "tangents": f"Tangents with {len(tan)} vectors"
        },
        "Initialize a trefoil knot with given resolution"
    )
    
    # Evolve
    dt = 0.01
    steps = 10
    knot.evolve(dt, steps)
    
    pos_evolved = knot.get_positions()
    
    log_test(
        "VortexKnotSystem.evolve",
        formula,
        {
            "dt": dt,
            "steps": steps
        },
        {
            "final_positions": f"Evolved knot with {len(pos_evolved)} points"
        },
        "Evolve vortex knot using Biot–Savart dynamics"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("KNOT DYNAMICS COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_fourier_knot_eval()
    test_compute_writhe()
    test_compute_linking_number()
    test_compute_twist()
    test_compute_centerline_helicity()
    test_pd_from_curve()
    test_estimate_crossing_number()
    test_vortex_knot_system()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)