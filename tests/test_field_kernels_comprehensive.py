#!/usr/bin/env python3
"""
Comprehensive test suite for Field Kernels bindings.
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
                print(f"    First 3 elements: {value[:3]}")
            else:
                print(f"  {key} = {value}")
        else:
            print(f"  {key} = {value}")
    print("-"*80)
    print("Results:")
    if isinstance(results, (list, tuple, np.ndarray)):
        if len(results) > 5:
            print(f"  Type: {type(results).__name__} of length {len(results)}")
            print(f"  First 3 elements: {results[:3]}")
            if hasattr(results, 'shape'):
                print(f"  Shape: {results.shape}")
        else:
            print(f"  {results}")
    elif isinstance(results, dict):
        for key, value in results.items():
            print(f"  {key} = {value}")
    else:
        print(f"  {results}")
    print("="*80)


def test_dipole_field_at_point():
    """Test point dipole field calculation."""
    r = [1.0, 0.0, 0.0]  # Observation point
    m = [0.0, 0.0, 1.0]  # Dipole moment (z-direction)
    
    formula = r"$\mathbf{B}(\mathbf{r}) = \frac{\mu_0}{4\pi}\frac{3(\mathbf{m}\cdot\hat{\mathbf{r}})\hat{\mathbf{r}}-\mathbf{m}}{r^3}$"
    
    result = swirl_string_core.dipole_field_at_point(r, m)
    
    log_test(
        "dipole_field_at_point",
        formula,
        {
            "r": r,
            "m": m
        },
        result,
        "Analytical point dipole field (mu0=1)"
    )


def test_biot_savart_wire_grid():
    """Test Biot-Savart on 3D grid."""
    # Create a circular wire
    n_wire = 20
    theta = np.linspace(0, 2*np.pi, n_wire)
    wire_points = np.array([
        [np.cos(t), np.sin(t), 0.0] for t in theta
    ])
    
    # Create grid
    nx, ny, nz = 5, 5, 3
    x = np.linspace(-2, 2, nx)
    y = np.linspace(-2, 2, ny)
    z = np.linspace(-1, 1, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    current = 1.0
    
    formula = r"$\mathbf{B}(\mathbf{r}) = \frac{\mu_0 I}{4\pi}\sum_{segments}\frac{d\mathbf{l}\times(\mathbf{r}-\mathbf{r}_{mid})}{|\mathbf{r}-\mathbf{r}_{mid}|^3}$"
    
    bx, by, bz = swirl_string_core.biot_savart_wire_grid(
        X.flatten(), Y.flatten(), Z.flatten(),
        wire_points, current
    )
    
    log_test(
        "biot_savart_wire_grid",
        formula,
        {
            "wire_points": f"Circular wire with {n_wire} points",
            "grid": f"Grid of shape {X.shape}",
            "current": current
        },
        {
            "Bx": f"Shape {bx.shape}, range [{bx.min():.4e}, {bx.max():.4e}]",
            "By": f"Shape {by.shape}, range [{by.min():.4e}, {by.max():.4e}]",
            "Bz": f"Shape {bz.shape}, range [{bz.min():.4e}, {bz.max():.4e}]"
        },
        "Biot-Savart of polyline on a 3D grid (midpoint per segment)"
    )


def test_dipole_ring_field_grid():
    """Test superposition of point dipoles on grid."""
    # Create a ring of dipoles
    n_dipoles = 8
    theta = np.linspace(0, 2*np.pi, n_dipoles, endpoint=False)
    positions = np.array([
        [np.cos(t), np.sin(t), 0.0] for t in theta
    ])
    moments = np.array([
        [0.0, 0.0, 1.0] for _ in theta  # All pointing in z-direction
    ])
    
    # Create grid
    nx, ny, nz = 5, 5, 3
    x = np.linspace(-2, 2, nx)
    y = np.linspace(-2, 2, ny)
    z = np.linspace(-1, 1, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    formula = r"$\mathbf{B}(\mathbf{r}) = \sum_{i=1}^{M}\frac{\mu_0}{4\pi}\frac{3(\mathbf{m}_i\cdot\hat{\mathbf{r}}_i)\hat{\mathbf{r}}_i-\mathbf{m}_i}{|\mathbf{r}-\mathbf{r}_i|^3}$"
    
    bx, by, bz = swirl_string_core.dipole_ring_field_grid(
        X.flatten(), Y.flatten(), Z.flatten(),
        positions, moments
    )
    
    log_test(
        "dipole_ring_field_grid",
        formula,
        {
            "positions": f"Ring of {n_dipoles} dipoles",
            "moments": f"{n_dipoles} dipole moments",
            "grid": f"Grid of shape {X.shape}"
        },
        {
            "Bx": f"Shape {bx.shape}, range [{bx.min():.4e}, {bx.max():.4e}]",
            "By": f"Shape {by.shape}, range [{by.min():.4e}, {by.max():.4e}]",
            "Bz": f"Shape {bz.shape}, range [{bz.min():.4e}, {bz.max():.4e}]"
        },
        "Superposition of point dipoles on a 3D grid"
    )


def test_biot_savart_vector_potential_grid():
    """Test magnetic vector potential computation."""
    # Create a simple wire loop
    n_wire = 16
    theta = np.linspace(0, 2*np.pi, n_wire)
    polyline = np.array([
        [np.cos(t), np.sin(t), 0.0] for t in theta
    ])
    
    # Create observation grid
    n_grid = 10
    grid = np.array([
        [np.cos(t)*2, np.sin(t)*2, z]
        for t in np.linspace(0, 2*np.pi, int(np.sqrt(n_grid)))
        for z in np.linspace(-0.5, 0.5, int(np.sqrt(n_grid)))
    ])
    
    current = 1.0
    
    formula = r"$\mathbf{A}(\mathbf{r}) = \frac{\mu_0 I}{4\pi}\int\frac{d\mathbf{l}}{|\mathbf{r}-\mathbf{r}'|}$"
    
    Ax, Ay, Az = swirl_string_core.biot_savart_vector_potential_grid(polyline, grid, current)
    
    log_test(
        "biot_savart_vector_potential_grid",
        formula,
        {
            "polyline": f"Circular wire with {n_wire} points",
            "grid": f"Grid with {len(grid)} points",
            "current": current
        },
        {
            "Ax": f"Shape {Ax.shape}, range [{Ax.min():.4e}, {Ax.max():.4e}]",
            "Ay": f"Shape {Ay.shape}, range [{Ay.min():.4e}, {Ay.max():.4e}]",
            "Az": f"Shape {Az.shape}, range [{Az.min():.4e}, {Az.max():.4e}]"
        },
        "Computes Magnetic Vector Potential A on a grid"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("FIELD KERNELS COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_dipole_field_at_point()
    test_biot_savart_wire_grid()
    test_dipole_ring_field_grid()
    test_biot_savart_vector_potential_grid()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)