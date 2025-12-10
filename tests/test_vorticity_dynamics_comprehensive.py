#!/usr/bin/env python3
"""
Comprehensive test suite for Vorticity Dynamics bindings.
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


def test_vorticity_z_2D():
    """Test 2D vorticity computation."""
    dv_dx = 1.0
    du_dy = -1.0
    
    formula = r"$\omega_z = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}$"
    
    result = swirl_string_core.vorticity_z_2D(dv_dx, du_dy)
    
    log_test(
        "vorticity_z_2D",
        formula,
        {
            "dv_dx": dv_dx,
            "du_dy": du_dy
        },
        result,
        "Compute 2D vorticity: dv/dx - du/dy"
    )


def test_local_circulation_density():
    """Test local circulation density."""
    dv_dx = 1.0
    du_dy = -1.0
    
    formula = r"$\text{Circulation density} = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}$ (via Stokes' theorem)"
    
    result = swirl_string_core.local_circulation_density(dv_dx, du_dy)
    
    log_test(
        "local_circulation_density",
        formula,
        {
            "dv_dx": dv_dx,
            "du_dy": du_dy
        },
        result,
        "Local circulation density (vorticity) via Stokes' theorem"
    )


def test_solid_body_rotation_vorticity():
    """Test solid body rotation vorticity."""
    omega = 2.0
    
    formula = r"$\omega = 2\Omega$"
    
    result = swirl_string_core.solid_body_rotation_vorticity(omega)
    
    log_test(
        "solid_body_rotation_vorticity",
        formula,
        {
            "omega": omega
        },
        result,
        "Vorticity of solid body rotation: 2 * omega"
    )


def test_couette_vorticity():
    """Test Couette flow vorticity."""
    alpha = 1.0
    
    formula = r"$\omega = -\alpha$"
    
    result = swirl_string_core.couette_vorticity(alpha)
    
    log_test(
        "couette_vorticity",
        formula,
        {
            "alpha": alpha
        },
        result,
        "Vorticity of Couette flow: -alpha"
    )


def test_crocco_relation():
    """Test Crocco's relation."""
    vorticity = [0.0, 0.0, 1.0]
    rho = 1.0
    pressure_gradient = [1.0, 0.0, 0.0]
    
    formula = r"$\mathbf{v} \times \boldsymbol{\omega} = \frac{\nabla p}{\rho} - \nabla H$"
    
    result = swirl_string_core.crocco_relation(vorticity, rho, pressure_gradient)
    
    log_test(
        "crocco_relation",
        formula,
        {
            "vorticity": vorticity,
            "rho": rho,
            "pressure_gradient": pressure_gradient
        },
        result,
        "Velocity-curl product equals pressure gradient divided by density (Crocco's theorem)"
    )


def test_compute_vorticity():
    """Test 2D vorticity field computation."""
    nx, ny = 5, 5
    u = [i*0.1 for i in range(nx*ny)]
    v = [j*0.1 for j in range(nx*ny)]
    dx = 0.1
    dy = 0.1
    
    formula = r"$\omega_z = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}$ (2D field)"
    
    result = swirl_string_core.compute_vorticity(u, v, nx, ny, dx, dy)
    
    log_test(
        "compute_vorticity",
        formula,
        {
            "u": f"u-velocity field ({nx}x{ny})",
            "v": f"v-velocity field ({nx}x{ny})",
            "nx": nx,
            "ny": ny,
            "dx": dx,
            "dy": dy
        },
        f"Vorticity field of length {len(result)}",
        "Compute 2D vorticity field"
    )


def test_rotating_frame_rhs():
    """Test rotating frame RHS."""
    velocity = [1.0, 0.0, 0.0]
    vorticity = [0.0, 0.0, 1.0]
    grad_phi = [0.0, 0.0, 0.0]
    grad_p = [1.0, 0.0, 0.0]
    omega = [0.0, 0.0, 1.0]
    rho = 1.0
    
    formula = r"$\frac{D\mathbf{v}}{Dt} = \mathbf{v} \times \boldsymbol{\omega} + \nabla\phi + \frac{\nabla p}{\rho} + 2\mathbf{v} \times \boldsymbol{\Omega}$"
    
    result = swirl_string_core.rotating_frame_rhs(velocity, vorticity, grad_phi, grad_p, omega, rho)
    
    log_test(
        "rotating_frame_rhs",
        formula,
        {
            "velocity": velocity,
            "vorticity": vorticity,
            "grad_phi": grad_phi,
            "grad_p": grad_p,
            "omega": omega,
            "rho": rho
        },
        result,
        "Compute rotating frame momentum RHS"
    )


def test_crocco_gradient():
    """Test Crocco gradient."""
    velocity = [1.0, 0.0, 0.0]
    vorticity = [0.0, 0.0, 1.0]
    grad_phi = [0.0, 0.0, 0.0]
    grad_p = [1.0, 0.0, 0.0]
    rho = 1.0
    
    formula = r"$\nabla H = \mathbf{v} \times \boldsymbol{\omega} + \nabla\phi + \frac{\nabla p}{\rho}$"
    
    result = swirl_string_core.crocco_gradient(velocity, vorticity, grad_phi, grad_p, rho)
    
    log_test(
        "crocco_gradient",
        formula,
        {
            "velocity": velocity,
            "vorticity": vorticity,
            "grad_phi": grad_phi,
            "grad_p": grad_p,
            "rho": rho
        },
        result,
        "Compute ∇H from Crocco's theorem"
    )


def test_baroclinic_term():
    """Test baroclinic term."""
    grad_rho = [0.1, 0.0, 0.0]
    grad_p = [1.0, 0.0, 0.0]
    rho = 1.0
    
    formula = r"$\frac{\nabla\rho \times \nabla p}{\rho^2}$"
    
    result = swirl_string_core.baroclinic_term(grad_rho, grad_p, rho)
    
    log_test(
        "baroclinic_term",
        formula,
        {
            "grad_rho": grad_rho,
            "grad_p": grad_p,
            "rho": rho
        },
        result,
        "Baroclinic torque term"
    )


def test_compute_vorticity_rhs():
    """Test vorticity transport RHS."""
    omega = [0.0, 0.0, 1.0]
    grad_u = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]
    div_u = 0.0
    grad_rho = [0.0, 0.0, 0.0]
    grad_p = [0.0, 0.0, 0.0]
    rho = 1.0
    
    formula = r"$\frac{D\boldsymbol{\omega}}{Dt} = (\boldsymbol{\omega} \cdot \nabla)\mathbf{v} - \boldsymbol{\omega}(\nabla \cdot \mathbf{v}) + \frac{\nabla\rho \times \nabla p}{\rho^2}$"
    
    result = swirl_string_core.compute_vorticity_rhs(omega, grad_u, div_u, grad_rho, grad_p, rho)
    
    log_test(
        "compute_vorticity_rhs",
        formula,
        {
            "omega": omega,
            "grad_u": "3x3 gradient tensor",
            "div_u": div_u,
            "grad_rho": grad_rho,
            "grad_p": grad_p,
            "rho": rho
        },
        result,
        "Vorticity transport RHS"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("VORTICITY DYNAMICS COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_vorticity_z_2D()
    test_local_circulation_density()
    test_solid_body_rotation_vorticity()
    test_couette_vorticity()
    test_crocco_relation()
    test_compute_vorticity()
    test_rotating_frame_rhs()
    test_crocco_gradient()
    test_baroclinic_term()
    test_compute_vorticity_rhs()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)