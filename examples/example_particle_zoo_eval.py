"""
SSTcore: Particle Zoo Evaluator (Topology-First Scaffold)

Pre-registers knot assignments and topology, then tests mass predictions.
Model 1: Geometry-only (no masses) – structural content.
Model 2: Mass model (one calibration constant) – tests if phi is special after topology fixed.

Usage:
    python example_particle_zoo_eval.py

See docs: topology → prediction → comparison. Quark sector: use hadron tests, not raw masses.
"""

from dataclasses import dataclass
from typing import Optional
import math

try:
    import swirl_string_core as sst
except ImportError:
    import sstbindings as sst


@dataclass
class SSTState:
    name: str
    sector: str          # "lepton", "quark"
    knot_family: str     # "vortex-knot", "twist-knot", ...
    knot_id: str         # e.g. "3_1", "5_2", "6_1"
    C: int               # crossing number (or chosen topological count)
    L: Optional[float]   # normalized ropelength if available
    H: Optional[float]   # helicity-like invariant if available
    layer_index: Optional[int]  # e.g. 2k
    obs_mass: Optional[float]   # MeV/c^2 (None if not using direct mass)
    notes: str = ""


def energy_proxy(state: SSTState, alpha=1.0, beta=0.0, gamma=0.0) -> float:
    L = 0.0 if state.L is None else state.L
    H = 0.0 if state.H is None else state.H
    return alpha * state.C + beta * L + gamma * H


def model_mass(state: SSTState, M0: float, base: float, alpha=1.0, beta=0.0, gamma=0.0) -> Optional[float]:
    if state.layer_index is None:
        return None
    F = energy_proxy(state, alpha, beta, gamma)
    return M0 * F * (base ** (-state.layer_index))


def rel_err(pred: float, obs: float) -> float:
    return abs(pred - obs) / obs


# Example seed zoo (replace with actual values/invariants as they become available)
zoo = [
    SSTState("tau", "lepton", "vortex-knot", "3_1", C=3, L=None, H=None, layer_index=0,  obs_mass=1776.86),
    SSTState("mu",  "lepton", "vortex-knot", "3_1", C=3, L=None, H=None, layer_index=6,  obs_mass=105.66),
    SSTState("e",   "lepton", "vortex-knot", "3_1", C=3, L=None, H=None, layer_index=17, obs_mass=0.511),
    SSTState("u?",  "quark",  "twist-knot",  "5_2", C=5, L=None, H=None, layer_index=None, obs_mass=None,
             notes="Use hadron tests, not direct fit"),
    SSTState("d?",  "quark",  "twist-knot",  "6_1", C=6, L=None, H=None, layer_index=None, obs_mass=None,
             notes="Use hadron tests, not direct fit"),
]


def main():
    print("--- SSTcore: Particle Zoo Evaluator (Topology-First Scaffold) ---\n")

    leptons = [s for s in zoo if s.sector == "lepton" and s.obs_mass is not None]
    phi = (1 + math.sqrt(5)) / 2

    # Calibrate M0 on tau only (if F same for leptons, M0*F collapses into one scale)
    tau = next(s for s in leptons if s.name == "tau")
    F_tau = energy_proxy(tau)
    M0 = tau.obs_mass / F_tau

    print("Lepton-only test (M0 calibrated on tau, base=phi):")
    print(f"  M0 = {M0:.6f} MeV (with F_tau = {F_tau})")
    print(f"  {'name':>4} | {'pred':>10} | {'obs':>10} | {'rel_err':>8}")
    for s in leptons:
        pred = model_mass(s, M0=M0, base=phi, alpha=1.0, beta=0.0, gamma=0.0)
        if pred is not None and s.obs_mass is not None:
            err = rel_err(pred, s.obs_mass)
            print(f"  {s.name:>4} | {pred:10.4f} | {s.obs_mass:10.4f} | {err:8.3%}")
        else:
            print(f"  {s.name:>4} | (no prediction)")

    print("\nNote: quark entries are placeholders; evaluate at hadron-combination level, not direct quark masses.")
    print("Next: add permutation test, base scan, and pre-registered topology → prediction benchmarks.")


if __name__ == "__main__":
    main()
