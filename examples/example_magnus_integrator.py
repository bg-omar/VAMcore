import math
import sys
from pathlib import Path

# Prefer locally built module (examples/ or project root) over site-packages
_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))
_parent = _script_dir.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

import numpy as np

try:
    import sstcore
except ImportError:
    import sstbindings as sstcore

def vector_magnitude(v):
    return math.sqrt(sum(x**2 for x in v))

if __name__ == "__main__":
    print("\n=== SST CONTINUUM MECHANICS: MAGNUS-BERNOULLI INTEGRATOR ===")

    # 1. Establish Canonical SST Constants (Zero-Parameter Boot)
    c = 299792458.0
    alpha = 0.0072973525693

    rho_f = 7.0e-7                      # Effective fluid density [kg/m^3]
    v_swirl = 1.09384563e6              # Characteristic swirl speed [m/s]
    r_c = 1.40897017e-15                # Core radius [m]

    # Quantum of circulation: Integral of velocity around the core
    Gamma = 2.0 * math.pi * r_c * v_swirl

    print(f"[*] Booting C++ Integrator...")
    print(f"    rho_f   = {rho_f:.2e} kg/m^3")
    print(f"    v_swirl = {v_swirl:.2e} m/s")
    print(f"    Gamma   = {Gamma:.2e} m^2/s")

    # Instantiate the C++ object
    integrator = sstcore.MagnusBernoulliIntegrator(rho_f, v_swirl, r_c, Gamma)

    # 2. Simulate an Orbiting Electron Vortex Segment
    # We evaluate a segment of an electron's fluid string moving near a proton.
    tangent = [0.0, 1.0, 0.0]           # String points along Y-axis
    normal = [-1.0, 0.0, 0.0]           # Curvature points inward along -X
    curvature_radius = 5.0e-11          # Bohr-scale curvature [m]

    v_knot = [0.0, 2.18e6, 0.0]         # Knot traversing at ~alpha*c [m/s]
    v_bg = [0.0, 1.0e5, 0.0]            # Background fluid being dragged by proton [m/s]

    # Execute C++ Magnus-Curvature Force Calculation
    F_perp = integrator.compute_magnus_force(tangent, normal, curvature_radius, v_knot, v_bg)
    F_mag = vector_magnitude(F_perp)

    print("\n[>] Test 1: Transverse Magnus Lift (Orbit Deflection)")
    print(f"    Input v_rel = {v_knot[1] - v_bg[1]:.2e} m/s (Tangent: Y-axis)")
    print(f"    [+] C++ Result F_perp = {F_perp}")
    print(f"    [+] Force Magnitude   = {F_mag:.4e} N per unit length")

    # 3. Simulate Swirl-Coulomb Radial Acceleration (Gravity/Electrostatic Replacement)
    eval_pos = [5.29e-11, 0.0, 0.0]     # Bohr radius distance [m]
    source_pos = [0.0, 0.0, 0.0]        # Proton at origin

    # Execute C++ Radial Bernoulli Gradient
    a_r = integrator.compute_swirl_coulomb_accel(eval_pos, source_pos)
    a_mag = vector_magnitude(a_r)

    print("\n[>] Test 2: Radial Swirl-Coulomb Acceleration (Bernoulli Gradient)")
    print(f"    Distance r  = {eval_pos[0]:.2e} m")
    print(f"    [+] C++ Result a_r = {a_r}")
    print(f"    [+] Accel Magnitude= {a_mag:.4e} m/s^2")
    print("==================================================================\n")