#!/usr/bin/env python3
"""
Comprehensive test suite for Biot-Savart bindings.
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


def test_biot_savart_velocity():
    """Test single point velocity calculation."""
    r = [0.0, 0.0, 1.0]  # Observation point
    filament_points = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [-1.0, 0.0, 0.0],
        [0.0, -1.0, 0.0],
        [1.0, 0.0, 0.0]  # Closed loop
    ]
    tangent_vectors = [
        [-1.0, 1.0, 0.0],
        [-1.0, -1.0, 0.0],
        [1.0, -1.0, 0.0],
        [1.0, 1.0, 0.0],
        [-1.0, 1.0, 0.0]
    ]
    circulation = 1.0
    
    formula = r"$\mathbf{v}(\mathbf{r}) = \frac{\Gamma}{4\pi}\int\frac{d\mathbf{l}\times(\mathbf{r}-\mathbf{r}')}{|\mathbf{r}-\mathbf{r}'|^3}$"
    
    result = swirl_string_core.biot_savart_velocity(r, filament_points, tangent_vectors, circulation)
    
    log_test(
        "biot_savart_velocity",
        formula,
        {
            "r": r,
            "filament_points": filament_points,
            "tangent_vectors": tangent_vectors,
            "circulation": circulation
        },
        result,
        "Velocity at a single point due to a filament"
    )


def test_biot_savart_velocity_grid():
    """Test grid-based velocity calculation."""
    # Create a simple circular filament
    n_points = 20
    theta = np.linspace(0, 2*np.pi, n_points)
    polyline = np.array([
        [np.cos(t), np.sin(t), 0.0] for t in theta
    ])
    
    # Create a grid of observation points
    x = np.linspace(-2, 2, 5)
    y = np.linspace(-2, 2, 5)
    z = np.linspace(0, 1, 3)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    grid = np.stack([X.flatten(), Y.flatten(), Z.flatten()], axis=-1)
    
    formula = r"$\mathbf{v}(\mathbf{r}_i) = \frac{\Gamma}{4\pi}\sum_{segments}\frac{d\mathbf{l}\times(\mathbf{r}_i-\mathbf{r}_{mid})}{|\mathbf{r}_i-\mathbf{r}_{mid}|^3}$"
    
    result = swirl_string_core.biot_savart_velocity_grid(polyline, grid)
    
    log_test(
        "biot_savart_velocity_grid",
        formula,
        {
            "polyline": f"Circular loop with {n_points} points",
            "grid": f"Grid of shape {grid.shape}"
        },
        f"Velocity field of shape {result.shape}",
        "Biot-Savart velocity at arbitrary grid points"
    )


def test_biot_savart_compute_velocity():
    """Test BiotSavart.compute_velocity static method."""
    # Simple square loop
    curve = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0]
    ]
    
    grid_points = [
        [0.5, 0.5, 0.5],
        [2.0, 2.0, 2.0]
    ]
    
    formula = r"$\mathbf{v}(\mathbf{r}) = \frac{1}{4\pi}\int\frac{d\mathbf{l}\times(\mathbf{r}-\mathbf{r}')}{|\mathbf{r}-\mathbf{r}'|^3}$"
    
    result = swirl_string_core.BiotSavart.compute_velocity(curve, grid_points)
    
    log_test(
        "BiotSavart.compute_velocity",
        formula,
        {
            "curve": f"Square loop with {len(curve)} points",
            "grid_points": f"{len(grid_points)} observation points"
        },
        f"Velocity vectors: {result}",
        "Compute velocity field from closed curve"
    )


def test_biot_savart_compute_vorticity():
    """Test vorticity computation from velocity field."""
    # Create a simple velocity field (vortex in z-direction)
    nx, ny, nz = 5, 5, 3
    n_total = nx * ny * nz
    velocity = []
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                x, y = i - nx/2, j - ny/2
                r = np.sqrt(x*x + y*y) + 0.1
                # Azimuthal velocity
                vx = -y / r
                vy = x / r
                velocity.append([vx, vy, 0.0])
    
    shape = [nx, ny, nz]
    spacing = 0.1
    
    formula = r"$\boldsymbol{\omega} = \nabla \times \mathbf{v}$"
    
    result = swirl_string_core.BiotSavart.compute_vorticity(velocity, shape, spacing)
    
    log_test(
        "BiotSavart.compute_vorticity",
        formula,
        {
            "velocity": f"Velocity field of shape {shape}",
            "spacing": spacing
        },
        f"Vorticity field with {len(result)} vectors",
        "Compute vorticity from velocity field on regular grid"
    )


def test_biot_savart_extract_interior():
    """Test interior field extraction."""
    # Create a dummy field
    nx, ny, nz = 10, 10, 10
    n_total = nx * ny * nz
    field = [[i*0.1, j*0.1, k*0.1] for k in range(nz) for j in range(ny) for i in range(nx)]
    shape = [nx, ny, nz]
    margin = 2
    
    formula = r"$\mathbf{f}_{int} = \mathbf{f}[margin:N-margin, margin:M-margin, margin:L-margin]$"
    
    result = swirl_string_core.BiotSavart.extract_interior(field, shape, margin)
    
    log_test(
        "BiotSavart.extract_interior",
        formula,
        {
            "field": f"Field of shape {shape}",
            "margin": margin
        },
        f"Interior field with {len(result)} vectors",
        "Extract cubic interior field subset"
    )


def test_biot_savart_compute_invariants():
    """Test invariant computation."""
    # Create sample velocity and vorticity fields
    n = 10
    v_sub = [[1.0, 0.0, 0.0] for _ in range(n)]
    w_sub = [[0.0, 0.0, 1.0] for _ in range(n)]
    r_sq = [i*0.1 for i in range(n)]
    
    formula = r"$H_{charge}, H_{mass}, a_\mu = \text{invariants}(\mathbf{v}, \boldsymbol{\omega}, r^2)$"
    
    result = swirl_string_core.BiotSavart.compute_invariants(v_sub, w_sub, r_sq)
    
    log_test(
        "BiotSavart.compute_invariants",
        formula,
        {
            "v_sub": f"Velocity subset with {len(v_sub)} vectors",
            "w_sub": f"Vorticity subset with {len(w_sub)} vectors",
            "r_sq": f"Radial distances squared: {r_sq[:3]}..."
        },
        f"H_charge={result[0]:.6e}, H_mass={result[1]:.6e}, a_mu={result[2]:.6e}",
        "Compute H_charge, H_mass, and a_mu from velocity/vorticity"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("BIOT-SAVART COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_biot_savart_velocity()
    test_biot_savart_velocity_grid()
    test_biot_savart_compute_velocity()
    test_biot_savart_compute_vorticity()
    test_biot_savart_extract_interior()
    test_biot_savart_compute_invariants()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)