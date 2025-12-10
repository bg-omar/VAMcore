#!/usr/bin/env python3
"""
Comprehensive test suite for Fluid Dynamics bindings.
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
        if hasattr(results, 'shape'):
            print(f"  Shape: {results.shape}")
            if results.size > 0:
                print(f"  Range: [{results.min():.4e}, {results.max():.4e}]")
        elif len(results) > 5:
            print(f"  Type: {type(results).__name__} of length {len(results)}")
            print(f"  First 3: {results[:3]}")
        else:
            print(f"  {results}")
    else:
        print(f"  {results}")
    print("="*80)


def test_compute_pressure_field():
    """Test Bernoulli pressure field computation."""
    velocity_magnitude = [1.0, 2.0, 3.0, 4.0, 5.0]
    rho_ae = 7.0e-7
    P_infinity = 101325.0  # Standard atmospheric pressure
    
    formula = r"$P = P_\infty - \frac{1}{2}\rho|\mathbf{v}|^2$"
    
    result = swirl_string_core.compute_pressure_field(velocity_magnitude, rho_ae, P_infinity)
    
    log_test(
        "compute_pressure_field",
        formula,
        {
            "velocity_magnitude": velocity_magnitude,
            "rho_ae": rho_ae,
            "P_infinity": P_infinity
        },
        result,
        "Compute Bernoulli pressure field from velocity magnitude"
    )


def test_compute_velocity_magnitude():
    """Test velocity magnitude computation."""
    velocity = [
        [1.0, 0.0, 0.0],
        [0.0, 2.0, 0.0],
        [1.0, 1.0, 1.0],
        [3.0, 4.0, 0.0]
    ]
    
    formula = r"$|\mathbf{v}| = \sqrt{v_x^2 + v_y^2 + v_z^2}$"
    
    result = swirl_string_core.compute_velocity_magnitude(velocity)
    
    log_test(
        "compute_velocity_magnitude",
        formula,
        {
            "velocity": velocity
        },
        result,
        "Compute magnitude |v| from vector velocity field"
    )


def test_evolve_positions_euler():
    """Test Euler step position update."""
    positions = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]
    velocity = [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    dt = 0.1
    
    formula = r"$\mathbf{r}(t+\Delta t) = \mathbf{r}(t) + \mathbf{v}(t)\Delta t$"
    
    # Make a copy since function may modify in place
    pos_copy = [list(p) for p in positions]
    swirl_string_core.evolve_positions_euler(pos_copy, velocity, dt)
    
    log_test(
        "evolve_positions_euler",
        formula,
        {
            "positions": positions,
            "velocity": velocity,
            "dt": dt
        },
        pos_copy,
        "Euler-step update of particle positions from velocity vectors"
    )


def test_compute_vorticity():
    """Test vorticity from gradient tensor."""
    grad = [
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],  # du/dx, du/dy, du/dz
        [[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]],  # dv/dx, dv/dy, dv/dz
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]   # dw/dx, dw/dy, dw/dz
    ]
    
    formula = r"$\boldsymbol{\omega} = \nabla \times \mathbf{v} = \left(\frac{\partial w}{\partial y} - \frac{\partial v}{\partial z}, \frac{\partial u}{\partial z} - \frac{\partial w}{\partial x}, \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}\right)$"
    
    result = swirl_string_core.compute_vorticity(grad)
    
    log_test(
        "compute_vorticity",
        formula,
        {
            "grad": "3x3 gradient tensor"
        },
        result,
        "Compute vorticity vector ω = ∇ × v from the velocity gradient tensor"
    )


def test_swirl_clock_rate():
    """Test swirl clock rate computation."""
    dv_dx = 1.0
    du_dy = -1.0
    
    formula = r"$\text{Swirl rate} = \frac{1}{2}\left(\frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}\right)$"
    
    result = swirl_string_core.swirl_clock_rate(dv_dx, du_dy)
    
    log_test(
        "swirl_clock_rate",
        formula,
        {
            "dv_dx": dv_dx,
            "du_dy": du_dy
        },
        result,
        "Swirl clock rate 0.5 * (dv/dx - du/dy)"
    )


def test_vorticity_from_curvature():
    """Test vorticity from curvature."""
    V = 10.0  # Velocity
    R = 1.0   # Radius of curvature
    
    formula = r"$\omega = \frac{V}{R}$"
    
    result = swirl_string_core.vorticity_from_curvature(V, R)
    
    log_test(
        "vorticity_from_curvature",
        formula,
        {
            "V": V,
            "R": R
        },
        result,
        "Vorticity magnitude for curved flow V/R"
    )


def test_vortex_pressure_drop():
    """Test vortex pressure drop."""
    rho = 1.0
    c = 10.0  # Circulation or characteristic speed
    
    formula = r"$\Delta P = \frac{1}{2}\rho c^2$"
    
    result = swirl_string_core.vortex_pressure_drop(rho, c)
    
    log_test(
        "vortex_pressure_drop",
        formula,
        {
            "rho": rho,
            "c": c
        },
        result,
        "Pressure drop 0.5 * ρ * c^2 in a vortex core"
    )


def test_vortex_transverse_pressure_diff():
    """Test transverse pressure difference."""
    rho = 1.0
    c = 10.0
    
    formula = r"$\Delta P_{transverse} = \frac{1}{4}\rho c^2$"
    
    result = swirl_string_core.vortex_transverse_pressure_diff(rho, c)
    
    log_test(
        "vortex_transverse_pressure_diff",
        formula,
        {
            "rho": rho,
            "c": c
        },
        result,
        "Transverse pressure difference 0.25 * ρ * c^2"
    )


def test_swirl_energy():
    """Test swirl energy computation."""
    rho = 1.0
    omega = 2.0
    
    formula = r"$E_{swirl} = \frac{1}{2}\rho\omega^2$"
    
    result = swirl_string_core.swirl_energy(rho, omega)
    
    log_test(
        "swirl_energy",
        formula,
        {
            "rho": rho,
            "omega": omega
        },
        result,
        "Rotational kinetic energy density (1/2) * ρ * ω^2"
    )


def test_kairos_energy_trigger():
    """Test kairos energy trigger."""
    rho = 1.0
    omega = 5.0
    Ce = 10.0
    
    formula = r"$\text{Trigger if } \frac{1}{2}\rho\omega^2 > \frac{1}{2}\rho C_e^2$"
    
    result = swirl_string_core.kairos_energy_trigger(rho, omega, Ce)
    
    log_test(
        "kairos_energy_trigger",
        formula,
        {
            "rho": rho,
            "omega": omega,
            "Ce": Ce
        },
        result,
        "Trigger when swirl energy exceeds 0.5 * ρ * Ce^2"
    )


def test_compute_helicity():
    """Test helicity computation."""
    velocity = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]
    vorticity = [
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]
    ]
    dV = 0.1
    
    formula = r"$H = \int \mathbf{v} \cdot \boldsymbol{\omega} \, dV = \sum_i (\mathbf{v}_i \cdot \boldsymbol{\omega}_i) \Delta V$"
    
    result = swirl_string_core.compute_helicity(velocity, vorticity, dV)
    
    log_test(
        "compute_helicity",
        formula,
        {
            "velocity": velocity,
            "vorticity": vorticity,
            "dV": dV
        },
        result,
        "Compute helicity ∑ (v · ω) dV over a discretized field"
    )


def test_potential_vorticity():
    """Test potential vorticity."""
    fa = 1.0      # Absolute vorticity
    zeta_r = 0.5  # Relative vorticity
    h = 2.0       # Layer thickness
    
    formula = r"$PV = \frac{f_a + \zeta_r}{h}$"
    
    result = swirl_string_core.potential_vorticity(fa, zeta_r, h)
    
    log_test(
        "potential_vorticity",
        formula,
        {
            "fa": fa,
            "zeta_r": zeta_r,
            "h": h
        },
        result,
        "Potential vorticity (fa + ζ_r) / h"
    )


def test_is_incompressible():
    """Test incompressibility check."""
    dudx = [1.0, 0.0, 0.0]
    dvdy = [0.0, 1.0, 0.0]
    dwdz = [0.0, 0.0, -2.0]  # Sum = 0, so incompressible
    
    formula = r"$\nabla \cdot \mathbf{v} = \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} + \frac{\partial w}{\partial z} \approx 0$"
    
    result = swirl_string_core.is_incompressible(dudx, dvdy, dwdz)
    
    log_test(
        "is_incompressible",
        formula,
        {
            "dudx": dudx,
            "dvdy": dvdy,
            "dwdz": dwdz
        },
        result,
        "Determine if flow is incompressible by checking divergence ≈ 0"
    )


def test_circulation_surface_integral():
    """Test circulation as surface integral."""
    omega_field = [
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]
    ]
    dA_field = [
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]
    ]
    
    formula = r"$\Gamma = \oint \boldsymbol{\omega} \cdot d\mathbf{A} = \sum_i \boldsymbol{\omega}_i \cdot \Delta\mathbf{A}_i$"
    
    result = swirl_string_core.circulation_surface_integral(omega_field, dA_field)
    
    log_test(
        "circulation_surface_integral",
        formula,
        {
            "omega_field": omega_field,
            "dA_field": dA_field
        },
        result,
        "Circulation as surface integral of vorticity dot area vector"
    )


def test_enstrophy():
    """Test enstrophy computation."""
    omega_squared = [1.0, 4.0, 9.0, 16.0]
    ds_area = [0.1, 0.1, 0.1, 0.1]
    
    formula = r"$\text{Enstrophy} = \int \omega^2 \, dA = \sum_i \omega_i^2 \Delta A_i$"
    
    result = swirl_string_core.enstrophy(omega_squared, ds_area)
    
    log_test(
        "enstrophy",
        formula,
        {
            "omega_squared": omega_squared,
            "ds_area": ds_area
        },
        result,
        "Enstrophy as sum of squared vorticity weighted by area"
    )


def test_compute_bernoulli_pressure():
    """Test Bernoulli pressure computation."""
    velocity_magnitude = [1.0, 2.0, 3.0, 4.0]
    rho = 7.0e-7
    p_inf = 0.0
    
    formula = r"$P = P_\infty - \frac{1}{2}\rho|\mathbf{v}|^2$"
    
    result = swirl_string_core.compute_bernoulli_pressure(velocity_magnitude, rho, p_inf)
    
    log_test(
        "compute_bernoulli_pressure",
        formula,
        {
            "velocity_magnitude": velocity_magnitude,
            "rho": rho,
            "p_inf": p_inf
        },
        result,
        "Compute Bernoulli pressure field from velocity magnitude"
    )


def test_pressure_gradient():
    """Test pressure gradient computation."""
    pressure_field = [
        [100.0, 101.0, 102.0],
        [103.0, 104.0, 105.0],
        [106.0, 107.0, 108.0]
    ]
    dx = 1.0
    dy = 1.0
    
    formula = r"$\nabla P = \left(\frac{\partial P}{\partial x}, \frac{\partial P}{\partial y}\right)$"
    
    result = swirl_string_core.pressure_gradient(pressure_field, dx, dy)
    
    log_test(
        "pressure_gradient",
        formula,
        {
            "pressure_field": pressure_field,
            "dx": dx,
            "dy": dy
        },
        f"Gradient field with {len(result)} vectors",
        "Compute spatial pressure gradient vector field"
    )


def test_laplacian_phi():
    """Test Laplacian of potential function."""
    d2phidx2 = 2.0
    d2phidy2 = 2.0
    d2phidz2 = 2.0
    
    formula = r"$\nabla^2\phi = \frac{\partial^2\phi}{\partial x^2} + \frac{\partial^2\phi}{\partial y^2} + \frac{\partial^2\phi}{\partial z^2}$"
    
    result = swirl_string_core.laplacian_phi(d2phidx2, d2phidy2, d2phidz2)
    
    log_test(
        "laplacian_phi",
        formula,
        {
            "d2phidx2": d2phidx2,
            "d2phidy2": d2phidy2,
            "d2phidz2": d2phidz2
        },
        result,
        "Compute Laplacian of potential function"
    )


def test_grad_phi():
    """Test gradient of potential function."""
    phi_grad = [1.0, 2.0, 3.0]
    
    formula = r"$\nabla\phi = \left(\frac{\partial\phi}{\partial x}, \frac{\partial\phi}{\partial y}, \frac{\partial\phi}{\partial z}\right)$"
    
    result = swirl_string_core.grad_phi(phi_grad)
    
    log_test(
        "grad_phi",
        formula,
        {
            "phi_grad": phi_grad
        },
        result,
        "Compute gradient of potential function"
    )


def test_bernoulli_pressure_potential():
    """Test Bernoulli pressure from potential flow."""
    velocity_squared = 100.0
    V = 10.0
    
    formula = r"$P = P_0 - \frac{1}{2}\rho V^2$"
    
    result = swirl_string_core.bernoulli_pressure_potential(velocity_squared, V)
    
    log_test(
        "bernoulli_pressure_potential",
        formula,
        {
            "velocity_squared": velocity_squared,
            "V": V
        },
        result,
        "Compute Bernoulli pressure from potential flow"
    )


def test_compute_kinetic_energy():
    """Test kinetic energy computation."""
    velocity = [
        [1.0, 0.0, 0.0],
        [0.0, 2.0, 0.0],
        [1.0, 1.0, 1.0]
    ]
    rho_ae = 1.0
    
    formula = r"$E_k = \frac{1}{2}\rho\sum_i |\mathbf{v}_i|^2$"
    
    result = swirl_string_core.compute_kinetic_energy(velocity, rho_ae)
    
    log_test(
        "compute_kinetic_energy",
        formula,
        {
            "velocity": velocity,
            "rho_ae": rho_ae
        },
        result,
        "Compute kinetic energy E = (1/2) * ρ * ∑ |v|^2"
    )


def test_rossby_number():
    """Test Rossby number."""
    U = 10.0
    omega = 1.0
    d = 1000.0
    
    formula = r"$Ro = \frac{U}{2\Omega d}$"
    
    result = swirl_string_core.rossby_number(U, omega, d)
    
    log_test(
        "rossby_number",
        formula,
        {
            "U": U,
            "omega": omega,
            "d": d
        },
        result,
        "Rossby number: Ro = U / (2Ωd)"
    )


def test_ekman_number():
    """Test Ekman number."""
    nu = 1.0e-6
    omega = 1.0
    H = 1000.0
    
    formula = r"$Ek = \frac{\nu}{\Omega H^2}$"
    
    result = swirl_string_core.ekman_number(nu, omega, H)
    
    log_test(
        "ekman_number",
        formula,
        {
            "nu": nu,
            "omega": omega,
            "H": H
        },
        result,
        "Ekman number: Ek = ν / (Ω H²)"
    )


def test_cylinder_mass():
    """Test cylinder mass."""
    rho = 1000.0
    R = 1.0
    H = 2.0
    
    formula = r"$m = \rho \pi R^2 H$"
    
    result = swirl_string_core.cylinder_mass(rho, R, H)
    
    log_test(
        "cylinder_mass",
        formula,
        {
            "rho": rho,
            "R": R,
            "H": H
        },
        result,
        "Cylinder mass: m = ρ π R² H"
    )


def test_cylinder_inertia():
    """Test cylinder moment of inertia."""
    mass = 1000.0
    R = 1.0
    
    formula = r"$I = \frac{1}{2}mR^2$"
    
    result = swirl_string_core.cylinder_inertia(mass, R)
    
    log_test(
        "cylinder_inertia",
        formula,
        {
            "mass": mass,
            "R": R
        },
        result,
        "Moment of inertia: I = (1/2) m R²"
    )


def test_torque():
    """Test torque computation."""
    inertia = 500.0
    alpha = 2.0
    
    formula = r"$\tau = I\alpha$"
    
    result = swirl_string_core.torque(inertia, alpha)
    
    log_test(
        "torque",
        formula,
        {
            "inertia": inertia,
            "alpha": alpha
        },
        result,
        "Torque: τ = I α"
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("FLUID DYNAMICS COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    test_compute_pressure_field()
    test_compute_velocity_magnitude()
    test_evolve_positions_euler()
    test_compute_vorticity()
    test_swirl_clock_rate()
    test_vorticity_from_curvature()
    test_vortex_pressure_drop()
    test_vortex_transverse_pressure_diff()
    test_swirl_energy()
    test_kairos_energy_trigger()
    test_compute_helicity()
    test_potential_vorticity()
    test_is_incompressible()
    test_circulation_surface_integral()
    test_enstrophy()
    test_compute_bernoulli_pressure()
    test_pressure_gradient()
    test_laplacian_phi()
    test_grad_phi()
    test_bernoulli_pressure_potential()
    test_compute_kinetic_energy()
    test_rossby_number()
    test_ekman_number()
    test_cylinder_mass()
    test_cylinder_inertia()
    test_torque()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)