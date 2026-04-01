#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SST_INVARIANT_MASS.py (with Muon Ropelength Calculation)
Author: Omar Iskandarani
Date: 2025-08-25

Purpose
-------
A canonical, topology-driven implementation of the Swirl-String Theory (SST)
Invariant Master Mass Formula. This version is extended to calculate the
required ropelength (L_tot) for the muon, based on its proposed topological
assignment as the cinquefoil knot (5_1).

Invariant Master Formula (Canon)
--------------------------------
M(T) = (4/α) * b(T)⁻³/² * φ⁻ᵍ⁽ᵀ⁾ * n(T)⁻¹/φ * ( (1/2)ρ_core * v_swirl² ) * (π * r_c³ * L_tot(T)) / c²
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
import re

# ──────────────────────────────────────────────────────────────────────────────
# Constants (Canon-aligned)
# ──────────────────────────────────────────────────────────────────────────────
phi: float = math.exp(math.asinh(0.5)) # Golden (hyperbolic) = = (1 + math.sqrt(5)) / 2
alpha_fs: float = 7.2973525643e-3
c: float = 299_792_458.0
v_swirl: float = 1.093_845_63e6
r_c: float = 1.408_970_17e-15
rho_core: float = 3.8934358266918687e18
avogadro: float = 6.022_140_76e23

# Physical reference masses (for calibration and error tables)
M_e_actual: float = 9.109_383_7015e-31
M_p_actual: float = 1.672_621_923_69e-27
M_n_actual: float = 1.674_927_498_04e-27
M_mu_actual: float = 1.883_531_627e-28 # Muon mass in kg

# ──────────────────────────────────────────────────────────────────────────────
# Data Structures for Topology
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class KnotTopology:
    """Stores the topological and geometric invariants for a particle."""
    name: str
    b: int  # Braid Index
    g: int  # Seifert Genus
    n: int  # Number of Components
    L_tot: float  # Total Ropelength


# ──────────────────────────────────────────────────────────────────────────────
# Invariant Master Formula Implementation
# ──────────────────────────────────────────────────────────────────────────────
def master_mass_invariant(
        topo: KnotTopology,
        rho: float = rho_core,
        v: float = v_swirl,
        alpha: float = alpha_fs,
        golden_phi: float = phi
) -> float:
    """
    M(T) = (4/α) * b⁻³/² * φ⁻ᵍ * n⁻¹/φ * ( (1/2)ρ v² ) * (π r_c³ L_tot) / c²
    Returns mass in kg.
    """
    u = 0.5 * rho * v * v
    amplification = 4.0 / alpha
    braid_suppression = topo.b ** -1.5
    genus_suppression = golden_phi ** -topo.g
    component_suppression = topo.n ** (-1.0 / golden_phi)
    volume = math.pi * (r_c ** 3) * topo.L_tot
    total_mass = (
            amplification *
            braid_suppression *
            genus_suppression *
            component_suppression *
            (u * volume) / (c * c)
    )
    return total_mass


# ──────────────────────────────────────────────────────────────────────────────
# Calibration Functions
# ──────────────────────────────────────────────────────────────────────────────
def solve_for_L_tot(mass_actual: float, topo_base: KnotTopology) -> float:
    """
    Generic function to solve for L_tot given a known mass and base topology.
    """
    u = 0.5 * rho_core * v_swirl ** 2
    prefactor = (
            (4.0 / alpha_fs) *
            (topo_base.b ** -1.5) *
            (phi ** -topo_base.g) *
            (topo_base.n ** (-1.0 / phi))
    )
    volume_prefactor = math.pi * (r_c ** 3)
    numerator = mass_actual * (c ** 2)
    denominator = prefactor * u * volume_prefactor
    return numerator / denominator


def fit_quark_geom_factors_for_baryons(b: int, g: int, n: int, scaling_factor: float) -> tuple[float, float]:
    """
    Fit (s_u, s_d) so that proton and neutron match CODATA masses exactly.
    """
    u = 0.5 * rho_core * v_swirl**2
    A_baryon = (
        (4.0/alpha_fs) * (b ** -1.5) * (phi ** -g) * (n ** (-1.0/phi)) *
        (u * math.pi * (r_c**3)) / (c*c)
    )
    K = A_baryon * scaling_factor
    s_u = (2.0 * M_p_actual - M_n_actual) / (3.0 * K)
    s_d = (M_p_actual / K) - 2.0 * s_u
    return float(s_u), float(s_d)


# ──────────────────────────────────────────────────────────────────────────────
# Assembly helpers for composite objects
# ──────────────────────────────────────────────────────────────────────────────
def get_particle_topologies() -> Dict:
    """
    Defines the canonical topologies for fundamental particles.
    """
    # Electron: Calibrated using (b=2, g=1, n=1) from the Solomon Link T(4,2)
    electron_base = KnotTopology(name="Electron_base", b=2, g=1, n=1, L_tot=0.0)
    l_tot_e = solve_for_L_tot(M_e_actual, electron_base)

    # Muon: Assigned the 5_1 knot topology. We will calculate its L_tot.
    muon_base = KnotTopology(name="Muon_base", b=5, g=2, n=1, L_tot=0.0)
    l_tot_mu = solve_for_L_tot(M_mu_actual, muon_base)

    # Baryons: Calibrated on p,n
    kappa_R = 2.0
    scaling_factor = 2.0 * (math.pi ** 2) * kappa_R
    s_u, s_d = fit_quark_geom_factors_for_baryons(b=3, g=2, n=3, scaling_factor=scaling_factor)
    l_tot_p = (2 * s_u + s_d) * scaling_factor
    l_tot_n = (s_u + 2 * s_d) * scaling_factor

    topologies = {
        "electron": KnotTopology(name="Electron", b=2, g=1, n=1, L_tot=l_tot_e),
        "muon": KnotTopology(name="Muon (5_1)", b=5, g=2, n=1, L_tot=l_tot_mu),
        "proton": KnotTopology(name="Proton", b=3, g=2, n=3, L_tot=l_tot_p),
        "neutron": KnotTopology(name="Neutron", b=3, g=2, n=3, L_tot=l_tot_n),
    }
    return topologies

# (The rest of the script for tabulation and main execution remains the same)
# ... (omitted for brevity, but it's the same as your refactored script)

# ──────────────────────────────────────────────────────────────────────────────
# Tabulation (abbreviated)
# ──────────────────────────────────────────────────────────────────────────────
def emoji_marker(diff_pct: float) -> str:
    # ... (same function as before)
    d = abs(diff_pct)
    if d < 0.01: return f"{diff_pct:.3f}% ●" # Higher precision for near-zero
    if d < 1: icon = "🩷🡅"
    elif d < 2.5: icon = "🟢🡅"
    elif d < 10: icon = "🟡🡅"
    elif d < 25: icon = "🟠🡅"
    else: icon = "🔴🡅"
    if diff_pct < 0: icon = icon.replace("🡅", "🡇")
    return f"{diff_pct:.2f}% {icon}"

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=== SST Invariant Master Mass (with Muon L_tot Calculation) ===")

    topologies = get_particle_topologies()

    print("\n--- Model Parameters ---")
    print(f"Using rho_core = {rho_core:.6e} kg/m^3")
    print("\n--- Particle Topological & Geometric Invariants ---")
    for p in topologies.values():
        print(f"{p.name:<12}: b={p.b}, g={p.g}, n={p.n}, L_tot={p.L_tot:.4f}")

    # Calculate and display masses
    M_e_pred = master_mass_invariant(topologies["electron"])
    M_mu_pred = master_mass_invariant(topologies["muon"])
    M_p_pred = master_mass_invariant(topologies["proton"])
    M_n_pred = master_mass_invariant(topologies["neutron"])

    rows: List = []
    rows.append(("Electron", M_e_pred, M_e_actual, emoji_marker(100.0*(M_e_pred-M_e_actual)/M_e_actual)))
    rows.append(("Muon", M_mu_pred, M_mu_actual, emoji_marker(100.0*(M_mu_pred-M_mu_actual)/M_mu_actual)))
    rows.append(("Proton", M_p_pred, M_p_actual, emoji_marker(100.0*(M_p_pred-M_p_actual)/M_p_actual)))
    rows.append(("Neutron", M_n_pred, M_n_actual, emoji_marker(100.0*(M_n_pred-M_n_actual)/M_n_actual)))

    df = pd.DataFrame(rows, columns=["Object", "Predicted Mass (kg)", "Actual Mass (kg)", "% Error"])

    print("\n--- Fundamental Particle Mass Results ---")
    pd.set_option("display.float_format", lambda x: f"{x:.6e}" if isinstance(x, float) else str(x))
    print(df.to_string(index=False))

    electron_ltot = topologies["electron"].L_tot
    muon_ltot = topologies["muon"].L_tot
    ratio = muon_ltot / electron_ltot

    print("\n--- Ropelength Analysis ---")
    print(f"Calibrated L_tot for Electron: {electron_ltot:.6f}")
    print(f"Required L_tot for Muon (5_1): {muon_ltot:.6f}")
    print(f"Ratio (L_tot_muon / L_tot_electron): {ratio:.4f}")


if __name__ == "__main__":
    main()