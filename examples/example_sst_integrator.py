"""
SST Integrator showcase: compute_sst_mass for closed polylines.

The SST integrator computes core mass (static) and fluid mass (hydrodynamic dressing)
from the Neumann mutual inductance integral with Rosenhead–Moore regularization.
Single API: compute_sst_mass(points, chi_spin) -> (m_core_kg, m_fluid_kg).
"""
import math
import sys
import time
from pathlib import Path

_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))
_parent = _script_dir.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

try:
    import sstcore
except ImportError:
    try:
        import swirl_string_core as sstcore  # backward compatibility
    except ImportError:
        import sstbindings as sstcore

if not getattr(sstcore, "compute_sst_mass", None):
    print(
        "ERROR: This build of sstcore has no 'compute_sst_mass'.\n"
        "Reinstall from source so the SST integrator bindings are included:\n"
        "  cd C:\\workspace\\projects\\SSTcore\n"
        "  pip install -e .\n"
        "Or build with CMake and use the resulting module."
    )
    sys.exit(1)

# kg -> MeV/c² (1 MeV/c² ≈ 1.78266192e-30 kg)
KG_TO_MEV = 1.0 / 1.78266192e-30


def ring_points(n: int, radius: float = 1e-14, z: float = 0.0) -> list:
    """Closed ring in the xy-plane (unknot proxy)."""
    return [
        [radius * math.cos(2 * math.pi * i / n), radius * math.sin(2 * math.pi * i / n), z]
        for i in range(n)
    ]


def small_figure_eight(n: int = 128, scale: float = 1e-14) -> list:
    """Closed figure-8 (two lobes) in the xy-plane."""
    # Parametric (sin t, sin 2t) then scale
    points = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = scale * math.sin(t)
        y = scale * math.sin(2 * t)
        points.append([x, y, 0.0])
    return points


def run_showcase():
    print("\n" + "=" * 70)
    print("  SST INTEGRATOR SHOWCASE — compute_sst_mass(points, chi_spin)")
    print("=" * 70)
    print("  Single function: (m_core_kg, m_fluid_kg) from closed polyline + spin.")
    print("  Uses Rosenhead–Moore regularized Neumann integral (O(N²)).")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # 1. Ring (unknot) — low and high resolution, fermion (chi=2)
    # -------------------------------------------------------------------------
    print("\n[1] RING (unknot proxy) — chi_spin = 2 (fermion)")
    print("-" * 50)
    for n in [100, 1000]:
        pts = ring_points(n)
        m_core, m_fluid = sstcore.compute_sst_mass(pts, 2.0)
        m_tot = m_core + m_fluid
        print(f"    N = {n:5d}  →  M_core = {m_core * KG_TO_MEV:.6e} MeV/c²   "
              f"M_fluid = {m_fluid * KG_TO_MEV:.6e} MeV/c²   M_total = {m_tot * KG_TO_MEV:.6e} MeV/c²")

    # -------------------------------------------------------------------------
    # 2. Spin comparison on same geometry (ring, N=500)
    # -------------------------------------------------------------------------
    print("\n[2] SPIN COMPARISON — ring N=500")
    print("-" * 50)
    pts = ring_points(500)
    for chi, label in [(1.0, "boson (chi=1)"), (2.0, "fermion (chi=2)")]:
        m_core, m_fluid = sstcore.compute_sst_mass(pts, chi)
        print(f"    {label:20s}  →  M_core = {m_core * KG_TO_MEV:.6e}   M_fluid = {m_fluid * KG_TO_MEV:.6e} MeV/c²")

    # -------------------------------------------------------------------------
    # 3. Figure-8 (different topology)
    # -------------------------------------------------------------------------
    print("\n[3] FIGURE-8 (two lobes) — N=256, chi_spin=2")
    print("-" * 50)
    pts = small_figure_eight(256)
    m_core, m_fluid = sstcore.compute_sst_mass(pts, 2.0)
    print(f"    M_core = {m_core * KG_TO_MEV:.6e} MeV/c²   M_fluid = {m_fluid * KG_TO_MEV:.6e} MeV/c²   "
          f"M_total = {(m_core + m_fluid) * KG_TO_MEV:.6e} MeV/c²")

    # -------------------------------------------------------------------------
    # 4. Timing (high-res ring)
    # -------------------------------------------------------------------------
    print("\n[4] TIMING — ring N=4000, chi_spin=2")
    print("-" * 50)
    pts = ring_points(4000)
    t0 = time.perf_counter()
    m_core, m_fluid = sstcore.compute_sst_mass(pts, 2.0)
    t1 = time.perf_counter()
    print(f"    Elapsed: {t1 - t0:.4f} s   M_total = {(m_core + m_fluid) * KG_TO_MEV:.6e} MeV/c²")

    # -------------------------------------------------------------------------
    # 5. Raw kg output (for completeness)
    # -------------------------------------------------------------------------
    print("\n[5] RAW OUTPUT (kg) — ring N=200, chi_spin=2")
    print("-" * 50)
    pts = ring_points(200)
    m_core, m_fluid = sstcore.compute_sst_mass(pts, 2.0)
    print(f"    m_core_kg  = {m_core:.6e}")
    print(f"    m_fluid_kg = {m_fluid:.6e}")

    print("\n" + "=" * 70)
    print("  Showcase done. API: compute_sst_mass(points, chi_spin) -> (m_core_kg, m_fluid_kg)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_showcase()
