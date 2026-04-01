#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SST_INVARIANT_MASS.py
Author: Omar Iskandarani
Date: 2025-08-25

Purpose
-------
A canonical, topology-driven implementation of the Swirl-String Theory (SST)
Invariant Master Mass Formula, structured similarly to VAM-MASS_FORMULA.py but
grounded strictly in the Canon “master equation”. The script provides three
calculation modes (see below) that change only topological-to-geometry inputs;
the invariant kernel is identical in all modes.

Modes (Computation Paths)
-------------------------
- exact_closure (default): fits the dimensionless quark geometry factors (s_u, s_d)
  analytically so that the **proton and neutron** masses are matched exactly, while
  preserving the electron-only geometric calibration. No extra scaling beyond
  the Canon kernel is introduced.
- canonical: strict Canon evaluation with a **single** electron calibration (fixes L_tot(e)).
  Uses fixed (s_u, s_d) from hyperbolic-volume assignments; **no** baryon-sector
  rescaling. Nucleon residuals reflect the direct Canon mapping.
- sector_norm: keeps fixed (s_u, s_d) as in canonical, but introduces a **single**
  baryon-sector normalization λ_b to make the **proton** exact; the neutron is predicted.

What changes across modes?
--------------------------
Only the **geometric inputs** to L_tot(T) for baryons:
1) The invariant kernel
       M(T) = (4/α)·k(T)^{-3/2}·φ^{-g(T)}·n(T)^{-1/φ} · [ (1/2)ρ_core v_swirl^2 ] · [ π r_c^3 L_tot(T) ] / c^2      (Eq. K)
   is fixed and identical in all modes.
2) The baryon ropelength mapping uses
       L_tot = scaling_factor · Σ s_i,   with   scaling_factor = 2 π^2 κ_R,   κ_R ≈ 2.                          (Eq. L)
   - **exact_closure**: (s_u, s_d) are solved from M_p, M_n using (Eq. K–L).
   - **canonical**: (s_u, s_d) are fixed constants (from hyperbolic volumes).
   - **sector_norm**: (s_u, s_d) fixed as canonical, and a single λ_b multiplies L_tot
     in the baryon sector so that M_p is exact.

Master Equation (Canon)
-----------------------
Define the swirl energy density
    u = (1/2) ρ v_swirl^2.                                                                               (Eq. 0)

The SST mass mapping can be written compactly as
    M = (4/α) · φ^{-1} · (u · V) / c^2,                                                                  (Eq. 1)
i.e.
    M = (4/α) · (1/φ) · [ (1/2) ρ v_swirl^2 · V ] / c^2.                                                 (Eq. 1′)

Here V is the effective geometric/topological volume associated with the object.
In the invariant kernel actually used in code (Eq. K), V = π r_c^3 L_tot(T) with
L_tot a **dimensionless ropelength** set by topology and the mode-specific mapping (Eq. L).

Symbols:
- α          : fine-structure constant
- φ          : golden ratio
- ρ, ρ_core  : effective density scale (default: ρ = ρ_core)
- v_swirl    : characteristic swirl speed (Canon: v_swirl ≈ 1.09384563×10^6 m/s)
- r_c        : core radius of the swirl string
- c          : speed of light
- k(T)       : kernel suppression index (dimensionless)
               For the torus-lepton ladder T(2,q), the code uses k=q, which equals
               the crossing number c_cross(T(2,q)) and the 2-strand twist exponent.
               This is NOT the mathematical braid index.
               For twist knots K_n (includes 4_1, 5_2, 6_1, ...), k(T) may be taken
               as a REAL number derived from the dominant Alexander root:
                   t_+(n) = ((2n+1) + sqrt(4n+1)) / (2n),
                   k(K_n) = (2 ln φ) / ln t_+(n).
- b_braid(T) : (optional) true braid index, for reference/reporting only.
- g(T)       : Seifert genus
- n(T)       : number of components
- L_tot(T)   : total ropelength (dimensionless)

Geometry
--------
A convenient reference geometry is the torus volume
    V_torus(R, r) = 2 π^2 R r^2,                                                                         (Eq. 2)
with r set to r_c and R = κ_R r_c (κ_R ≈ 2). The ropelength proxy used by the
Canon kernel (Eq. K) is V = π r_c^3 L_tot, consistent with dimensionless L_tot.

Calibration Strategy
--------------------
- Electron-only geometric calibration: determine L_tot(e) so that the model exactly
  reproduces M_e(actual). This fixes the absolute geometry scale for all modes.
- Baryons: assemble L_tot via (Eq. L). Depending on mode, (s_u, s_d) are either
  solved (exact_closure) or taken as fixed (canonical/sector_norm). In sector_norm
  a single λ_b multiplies baryon L_tot to make the proton exact.

Outputs
-------
- Console table with columns:
      Object, Actual Mass (kg), Predicted Mass (kg), % Error
- CSV: SST_Invariant_Mass_Results.csv
- Optional cross-mode comparison (interactive prompt) appends:
      Predicted Mass (kg) [CANON], % Error [CANON],
      Predicted Mass (kg) [Sector Norm], % Error [Sector Norm]
  to SST_Invariant_Mass_Results_all_modes.csv.

Units & Dimensional Check
-------------------------
- u = (1/2) ρ v_swirl^2 has units [J/m^3]; u·V has [J]; division by c^2 gives [kg].
- The factors (4/α), φ^{-g(T)}, n(T)^{-1/φ}, k(T)^{-3/2} are dimensionless.

Purpose
-------
Implements the SST Invariant Master Mass Formula using the rigorous
topological definition of the Electron as a Trefoil (3_1).
Outputs results in the specific "Canonical Mass Summary" style requested.

Topological Basis
-----------------
- Electron (Ξ): Torus knot T(2,3) (Trefoil 3_1) -> k=3, g=1, n=1, b_braid=2
- Muon (Ξ):     Torus knot T(2,5) (5_1)         -> k=5, g=2, n=1, b_braid=2
- Tau (Ξ):      Torus knot T(2,7) (7_1)         -> k=7, g=3, n=1, b_braid=2

Baryon Sector (SST):
Proton/Neutron derived via 'exact_closure' of quark geometric factors (s_u, s_d)
scaling the core Master Equation.


References (BibTeX)
-------------------

@article{CODATA2018,
  author    = {P. J. Mohr and D. B. Newell and B. N. Taylor},
  title     = {CODATA Recommended Values of the Fundamental Physical Constants: 2018},
  journal   = {Reviews of Modern Physics},
  volume    = {88},
  pages     = {035009},
  year      = {2016},
  doi       = {10.1103/RevModPhys.88.035009}
}
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import re
import os

# ──────────────────────────────────────────────────────────────────────────────
# One-shot warnings (avoid spam during sweeps)
# ──────────────────────────────────────────────────────────────────────────────
_WARNED: set[str] = set()

def _warn_once(key: str, msg: str) -> None:
    if key in _WARNED:
        return
    _WARNED.add(key)
    print(msg)

# ──────────────────────────────────────────────────────────────────────────────
# Constants (Canon-aligned)
# ──────────────────────────────────────────────────────────────────────────────
phi0: float = (1 + math.sqrt(5)) / 2
alpha_fs: float = 7.2973525643e-3
c: float = 299_792_458.0
v_swirl: float = 1.093_845_63e6
r_c: float = 1.408_970_17e-15
rho_core: float = 3.8934358266918687e18
avogadro: float = 6.022_140_76e23
m_u: float = 1.660_539_066_60e-27  # atomic mass constant (kg/u)
ln_phi0: float = math.log(phi0)

# Physical reference masses (CODATA 2018)
M_e_actual: float = 9.109_383_7015e-31   # Electron
M_mu_actual: float = 1.883_531_627e-28   # Muon
M_tau_actual: float = 3.167_54e-27       # Tau
M_p_actual: float = 1.672_621_923_69e-27   # Proton
M_n_actual: float = 1.674_927_498_04e-27   # Neutron

#
# Twist-knot real-k support (Alexander-dominant-root proxy)
#   Δ_n(t) = n t^2 - (2n+1) t + n  (normalized; n>=1)
#   t_+(n) = ((2n+1)+sqrt(4n+1)) / (2n)
#   k(K_n) = (2 ln φ) / ln t_+(n)
#
_TWIST_LABEL_TO_N: Dict[str, int] = {
    "4_1": 1,  # figure-eight = K_1
    "5_2": 2,  # twist knot K_2  (your up-quark representative)
    "6_1": 3,  # twist knot K_3  (your down-quark representative)
    "7_2": 4,
    "8_1": 5,
}


def twist_t_plus(n: int) -> float:
    """Dominant Alexander root for twist knot K_n (n>=1)."""
    if n < 1:
        raise ValueError("twist parameter n must be >= 1")
    return ((2.0 * n + 1.0) + math.sqrt(4.0 * n + 1.0)) / (2.0 * n)


def k_from_twist_alexander(n: int, phi_val: float = phi0) -> float:
    """
    Real-valued kernel index for twist knot K_n derived from the dominant Alexander root.
    Normalized so that k(K_1)=1 (since t_+(1)=φ^2).
    """
    t_plus = twist_t_plus(n)
    ln_t = math.log(t_plus)
    if not (ln_t > 0.0):
        raise ValueError(f"ln(t_+) must be positive; got t_+={t_plus}")
    return (2.0 * math.log(phi_val)) / ln_t


def k_from_knot_label(label: str, *, phi_val: float = phi0) -> float | None:
    """
    Convenience: if label corresponds to a supported twist knot (e.g. '5_2'), return k(K_n).
    Otherwise return None.
    """
    n = _TWIST_LABEL_TO_N.get(label.strip())
    if n is None:
        return None
    return k_from_twist_alexander(n, phi_val=phi_val)


# ----------------------------
# Double twist rational-sliceness classifier (Lee 2025, arXiv:2504.07636)
# ----------------------------
def is_rationally_slice_double_twist(m: int, n: int) -> bool:
    """
    Double-twist knots K_{m,n} rationally slice iff:
      mn = 0  OR  n = -m  OR  n = -m ± 1
    (J. Lee, 'Rational Concordance of Double Twist Knots', arXiv:2504.07636v1, 2025)
    """
    return (m * n == 0) or (n == -m) or (n == -m + 1) or (n == -m - 1)


def xi_A(A: int, gamma: float, A0: float, p: float) -> float:
    """
    SST-SEMF modulation factor Xi(A), dimensionless.
    - Xi(0)=1
    - Xi(A) decreases monotonically for gamma>0
    - If gamma==0 -> Xi(A)=1 (standard SEMF).
    """
    if gamma <= 0.0:
        return 1.0
    x = (A / A0) ** p if A0 > 0 else 0.0
    return (1.0 + x) ** (-gamma)


# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class Config:
    # s_u = Vol_H(5_2), s_d = Vol_H(6_1) (canonical up/down)
    mode: str = "exact_closure"
    # Lepton calibration policy:
    #   - "electron_only": calibrate ONLY L_tot(e) on M_e; predict mu/tau from the same geometry scale.
    #   - "each_lepton":   calibrate L_tot separately on (e, mu, tau). Useful for diagnostics, not prediction.
    lepton_calibration: str = "electron_only"
    kappa_R: float = 2.0
    fixed_su: float = 2.8281
    fixed_sd: float = 3.1639
    # Optional diagnostics / future wiring: compute real-k values for twist-knot labels (5_2, 6_1, ...)
    use_twist_alexander_k: bool = True
    # Data / evaluation controls
    use_semf: bool = True
    # SST-SEMF modulation Xi(A): if gamma=0, Xi(A)=1 (standard SEMF).
    xi_gamma: float = 0.0
    xi_A0: float = 200.0
    xi_p: float = 2.0

    # Shielding exponent control
    use_shielding_exponent: bool = False
    sigma_leptons: int = 0
    sigma_baryons: int = 1

    data_source: str = "standard_weight"  # "standard_weight" | "isotope_mass"
    isotope_mass_csv: str = "isotope_masses.csv"  # optional; used only if data_source="isotope_mass"


def _load_isotope_masses_kg(csv_path: str) -> Dict[str, float]:
    """
    Optional: load isotope-resolved atomic masses (neutral atom masses) in atomic mass units.
    CSV format (header required):
        symbol,atomic_mass_u
    Example:
        Fe,55.9349375
        O,15.99491461957

    Returns: { "Fe": mass_kg, ... }
    """
    if not csv_path or not os.path.exists(csv_path):
        return {}
    df = pd.read_csv(csv_path)

    # Accept a few schema variants:
    # - symbol column: symbol | element_symbol | element
    # - mass column:   atomic_mass_u | mass_u | atomicMass_u
    col_sym = None
    for c in ("symbol", "element_symbol", "element"):
        if c in df.columns:
            col_sym = c
            break
    col_u = None
    for c in ("atomic_mass_u", "mass_u", "atomicMass_u"):
        if c in df.columns:
            col_u = c
            break
    if col_sym is None or col_u is None:
        raise ValueError(
            f"Bad isotope CSV schema: need (symbol, atomic_mass_u). "
            f"Accepted symbol columns: symbol|element_symbol|element; "
            f"accepted mass columns: atomic_mass_u|mass_u|atomicMass_u. Got {list(df.columns)}"
        )

    out: Dict[str, float] = {}
    for _, r in df.iterrows():
        sym = str(r[col_sym]).strip()
        mu = float(r[col_u])
        out[sym] = mu * m_u
    return out


class NuclearBinding:
    """
    Models the 'Mass Defect' arising from the constructive interference
    of swirl fields in a composite nucleus.

    Uses the Semi-Empirical Mass Formula (SEMF) coefficients as
    phenomenological proxies for SST interaction terms:
    - Volume Term (a_v): Bulk swirl coherence
    - Surface Term (a_s): Surface tension deficit
    - Coulomb Term (a_c): Swirl-pressure repulsion
    - Symmetry Term (a_a): Isospin/Chirality balance
    - Pairing Term (a_p): Topological locking efficiency
    """
    # Coefficients in MeV (Wapstra/Weizsäcker)
    a_v = 15.75   # Volume
    a_s = 17.8    # Surface
    a_c = 0.711   # Coulomb
    a_a = 23.7    # Asymmetry
    a_p = 11.18   # Pairing

    MeV_to_kg = 1.78266192e-30  # Conversion factor (E/c^2)

    @classmethod
    def get_mass_defect_kg(cls, Z: int, N: int, xi: float = 1.0) -> float:
        """
        Returns mass defect (positive means binding reduces mass) in kg.
        SEMF binding energy is returned in MeV, then converted to kg via E=mc^2.
        """
        if Z <= 1 and N <= 0: return 0.0 # Single proton has no binding defect

        A = Z + N

        # 1. Volume Term (Bulk Coherence)
        # SST-SEMF modulation: Volume term scales ~ Xi(A)
        E_v = cls.a_v * xi * A

        # 2. Surface Term (Surface Tension Penalty)
        # SST-SEMF modulation: Surface term scales ~ Xi(A)^(-1/2)
        E_s = cls.a_s * (xi ** (-0.5)) * (A **(2/3))

        # 3. Coulomb Term (Repulsion)
        E_c = cls.a_c * (Z * (Z - 1)) / (A**(1/3))

        # 4. Asymmetry Term (Chirality Imbalance)
        E_a = cls.a_a * ((N - Z)**2) / A

        # 5. Pairing Term (Topological Locking)
        # delta is +1 for even-even, -1 for odd-odd, 0 for odd-A
        if A % 2 != 0:
            delta = 0
        elif Z % 2 == 0:
            delta = 1  # Even-Even (Most stable)
        else:
            delta = -1 # Odd-Odd (Least stable)

        E_p = cls.a_p * delta / (A**(0.5))

        # Total Binding Energy (MeV)
        E_binding_MeV = E_v - E_s - E_c - E_a + E_p

        # Convert to Mass Defect (kg)
        # Note: We subtract this from the sum of parts.
        return E_binding_MeV * cls.MeV_to_kg

# ──────────────────────────────────────────────────────────────────────────────
# Data Structures for Topology
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class KnotTopology:
    """
    Topological+geometric data needed by the SST mass kernel.

    We use a compact invariant form (per your model):

      M(T) = (4/α) * k^{-3/2} * φ^{-g} * n^{-1/φ} * M0 * L_tot

    with optional shielding gate G(T) so that amplification is (4/α)^{G(T)}.
    """
    name: str
    k: float  # Kernel suppression index used in Eq. K (may be non-integer; e.g. twist Alexander-derived)
    g: int  # Seifert Genus
    n: int  # Number of Components
    L_tot: float  # Total Ropelength
    # Optional: true braid index (e.g., for torus knots T(p,q), b_braid=min(p,q)). Not used in mass kernel.
    b_braid: int | None = None
    # Optional shielding exponent for (4/alpha) amplification (legacy; prefer shielding_gate).
    sigma: int = 1
    # Optional: identify specific families with hard constraints (e.g. double-twist K_{m,n})
    family: str | None = None
    params: tuple[int, int] | None = None  # e.g. (m, n) for double_twist K_{m,n}
    dt_m: int | None = None  # legacy alias
    dt_n: int | None = None  # legacy alias


def shielding_gate(topo: KnotTopology) -> int:
    """
    Binary shielding gate G(T) ∈ {0,1} deciding whether (4/α) is active.

      G(T)=0  => (4/α)^0 = 1  (perfect shielding; amplification OFF)
      G(T)=1  => (4/α)^1      (shielding broken; amplification ON)

    Hard constraint:
      - If topo.family == 'double_twist' and topo.params=(m,n), then
        G(K_{m,n}) = 0 iff K_{m,n} is rationally slice (Lee 2025 criterion).

    Default fallback (model convention used in SST-59):
      - Lepton-like sectors: (n=1, g=1)  -> G=0
      - Otherwise                           G=1
    """
    if topo.family == "double_twist" and topo.params is not None:
        m, n = topo.params
        return 0 if is_rationally_slice_double_twist(m, n) else 1
    return 0 if (topo.n == 1 and topo.g == 1) else 1


# ──────────────────────────────────────────────────────────────────────────────
# Invariant Master Formula
# ──────────────────────────────────────────────────────────────────────────────
def master_mass_invariant(topo: KnotTopology, phi_val: float = phi0) -> float:
    """
    Core SST mass invariant:

      M = (4/α)^{G(T)} * k^{-3/2} * φ^{-g} * n^{-1/φ} * M0 * L_tot
    """
    u = 0.5 * rho_core * v_swirl * v_swirl
    G = shielding_gate(topo)
    amplification = (4.0 / alpha_fs) ** G
    braid_suppression = topo.k ** -1.5
    genus_suppression = phi_val ** -topo.g
    component_suppression = topo.n ** (-1.0 / phi_val)
    volume = math.pi * (r_c ** 3) * topo.L_tot
    return (
            amplification *
            braid_suppression *
            genus_suppression *
            component_suppression *
            (u * volume) / (c * c)
    )

# ──────────────────────────────────────────────────────────────────────────────
# Calibration helpers
# ──────────────────────────────────────────────────────────────────────────────
def solve_for_L_tot(mass_actual: float, topo_base: KnotTopology, phi_val: float = phi0) -> float:
    """Generic function to solve for L_tot given a known mass and base topology."""
    u = 0.5 * rho_core * v_swirl ** 2
    G = shielding_gate(topo_base)
    amplification = (4.0 / alpha_fs) ** G
    prefactor = (
            amplification *
            (topo_base.k ** -1.5) *
            (phi_val ** -topo_base.g) *
            (topo_base.n ** (-1.0 / phi_val))
    )
    volume_prefactor = math.pi * (r_c ** 3)
    return (mass_actual * (c ** 2)) / (prefactor * u * volume_prefactor)


def baryon_prefactor(k: float, g: int, n: int, phi_val: float = phi0) -> float:
    u = 0.5 * rho_core * v_swirl * v_swirl
    return (4.0/alpha_fs) * (k ** -1.5) * (phi_val ** -g) * (n ** (-1.0/phi_val)) * (u * math.pi * (r_c**3)) / (c*c)


def fit_quark_geom_factors_for_baryons(k: float, g: int, n: int, scaling_factor: float, phi_val: float = phi0) -> tuple[float, float]:
    A = baryon_prefactor(k, g, n, phi_val=phi_val)
    K = A * scaling_factor
    s_u = (2.0 * M_p_actual - M_n_actual) / (3.0 * K)
    s_d = (M_p_actual / K) - 2.0 * s_u
    return float(s_u), float(s_d)


# ──────────────────────────────────────────────────────────────────────────────
# Assembly helpers
# ──────────────────────────────────────────────────────────────────────────────
def get_particle_topologies(cfg: Config, phi_val: float = phi0) -> Dict:
    # Lepton Generation Calibration
    electron_sigma = 1
    if cfg.use_shielding_exponent:
        electron_sigma = cfg.sigma_leptons
    electron_base = KnotTopology(name="Electron_base T(2,3)", k=3.0, b_braid=2, g=1, n=1, sigma=electron_sigma, L_tot=0.0)
    muon_base     = KnotTopology(name="Muon_base T(2,5)",     k=5.0, b_braid=2, g=2, n=1, sigma=electron_sigma, L_tot=0.0)
    tau_base      = KnotTopology(name="Tau_base T(2,7)",      k=7.0, b_braid=2, g=3, n=1, sigma=electron_sigma, L_tot=0.0)

    l_tot_e  = solve_for_L_tot(M_e_actual,  electron_base, phi_val=phi_val)
    if cfg.lepton_calibration == "each_lepton":
        # Diagnostic / non-predictive: fit each lepton separately.
        l_tot_mu  = solve_for_L_tot(M_mu_actual,  muon_base, phi_val=phi_val)
        l_tot_tau = solve_for_L_tot(M_tau_actual, tau_base,  phi_val=phi_val)
    else:
        # Predictive test: reuse the electron geometry scale for higher generations.
        l_tot_mu  = l_tot_e
        l_tot_tau = l_tot_e

    # Baryon Sector Calibration
    k_bary, g_bary, n_bary = 3.0, 2, 3
    scaling_factor = 2.0 * (math.pi ** 2) * cfg.kappa_R
    A_bary = baryon_prefactor(k_bary, g_bary, n_bary, phi_val=phi_val)
    K = A_bary * scaling_factor
    lam_b = 1.0

    # Diagnostics: twist-knot real-k values for your quark representatives
    # up  -> 5_2 -> K_2 ; down -> 6_1 -> K_3
    k_up_tw  = None
    k_down_tw = None
    if cfg.use_twist_alexander_k:
        k_up_tw = k_from_knot_label("5_2", phi_val=phi_val)
        k_down_tw = k_from_knot_label("6_1", phi_val=phi_val)

    if cfg.mode == "canonical":
        s_u, s_d = cfg.fixed_su, cfg.fixed_sd
    elif cfg.mode == "sector_norm":
        s_u, s_d = cfg.fixed_su, cfg.fixed_sd
        lam_b = M_p_actual / (K * (2.0 * s_u + s_d))
    else: # exact_closure
        s_u, s_d = fit_quark_geom_factors_for_baryons(k_bary, g_bary, n_bary, scaling_factor, phi_val=phi_val)

    l_tot_p = lam_b * (2.0 * s_u + 1.0 * s_d) * scaling_factor
    l_tot_n = lam_b * (1.0 * s_u + 2.0 * s_d) * scaling_factor

    bary_sigma = 1
    if cfg.use_shielding_exponent:
        bary_sigma = cfg.sigma_baryons
    topologies = {
        "electron": KnotTopology(name="Electron", k=3.0, b_braid=2, g=1, n=1, sigma=electron_sigma, L_tot=l_tot_e),
        "muon":     KnotTopology(name="Muon (T(2,5))", k=5.0, b_braid=2, g=2, n=1, sigma=electron_sigma, L_tot=l_tot_mu),
        "tau":      KnotTopology(name="Tau (T(2,7))",  k=7.0, b_braid=2, g=3, n=1, sigma=electron_sigma, L_tot=l_tot_tau),
        "proton":   KnotTopology(name="Proton",  k=float(k_bary), g=g_bary, n=n_bary, sigma=bary_sigma, L_tot=l_tot_p),
        "neutron":  KnotTopology(name="Neutron", k=float(k_bary), g=g_bary, n=n_bary, sigma=bary_sigma, L_tot=l_tot_n),
        "_diag": {
            "mode": cfg.mode, "kappa_R": cfg.kappa_R, "scaling_factor": scaling_factor,
            "A_bary": A_bary, "K": K, "lambda_b": lam_b, "s_u": s_u, "s_d": s_d
            , "k_up_twist_alex": k_up_tw, "k_down_twist_alex": k_down_tw
        }
    }
    return topologies



# ──────────────────────────────────────────────────────────────────────────────
# Tabulation
# ──────────────────────────────────────────────────────────────────────────────
def emoji_marker(diff_pct: float) -> str:
    d = abs(diff_pct)
    if d < 0.01: return f"{diff_pct:.3f}% 🩷️"
    if d < 1: icon = "❤️🡅"
    elif d < 2.5: icon = "🟢🡅"
    elif d < 10: icon = "🟡🡅"
    elif d < 25: icon = "🟠🡅"
    else: icon = "🔴🡅"
    if diff_pct < 0: icon = icon.replace("🡅", "🡇")
    if diff_pct == 0: icon = "🩷"
    return f"{diff_pct:.2f}% {icon}"


ATOMS_MOLS: List[Tuple[str, int, int, int, float]] = [
    ("H", 1, 0, 1, 1.00784), ("He", 2, 2, 2, 4.002602), ("Li", 3, 4, 3, 6.94), ("Be", 4, 5, 4, 9.0122),
    ("B", 5, 6, 5, 10.81), ("C", 6, 6, 6, 12.011), ("N", 7, 7, 7, 14.0067), ("O", 8, 8, 8, 15.999),
    ("F", 9, 10, 9, 18.998), ("Ne", 10, 10, 10, 20.18), ("Na", 11, 12, 11, 22.989769), ("Mg", 12, 12, 12, 24.305),
    ("Al", 13, 14, 13, 26.9815385), ("Si", 14, 14, 14, 28.085), ("P", 15, 16, 15, 30.973762), ("S", 16, 16, 16, 32.06),
    ("Cl", 17, 18, 17, 35.45), ("Ar", 18, 22, 18, 39.948), ("K", 19, 20, 19, 39.0983), ("Ca", 20, 20, 20, 40.078),
    ("Sc", 21, 24, 21, 44.955), ("Ti", 22, 26, 22, 47.867), ("V", 23, 28, 23, 50.942), ("Cr", 24, 28, 24, 51.996),
    ("Mn", 25, 30, 25, 54.938), ("Fe", 26, 30, 26, 55.845), ("Co", 27, 32, 27, 58.933), ("Ni", 28, 31, 28, 58.693),
    ("Cu", 29, 35, 29, 63.546), ("Zn", 30, 35, 30, 65.38), ("Ga", 31, 39, 31, 69.723), ("Ge", 32, 41, 32, 72.63),
    ("As", 33, 42, 33, 74.922), ("Se", 34, 45, 34, 78.971), ("Br", 35, 45, 35, 79.904), ("Kr", 36, 48, 36, 83.798),
    ("Rb", 37, 48, 37, 85.468), ("Sr", 38, 50, 38, 87.62), ("Y", 39, 50, 39, 88.906), ("Zr", 40, 51, 40, 91.224),
    ("Nb", 41, 52, 41, 92.906), ("Mo", 42, 54, 42, 95.95), ("Tc", 43, 55, 43, 98.0), ("Ru", 44, 57, 44, 101.07),
    ("Rh", 45, 58, 45, 102.91), ("Pd", 46, 60, 46, 106.42), ("Ag", 47, 61, 47, 107.87), ("Cd", 48, 64, 48, 112.41),
    ("In", 49, 66, 49, 114.82), ("Sn", 50, 69, 50, 118.71), ("Sb", 51, 71, 51, 121.76), ("Te", 52, 76, 52, 127.6),
    ("I", 53, 74, 53, 126.90447), ("Xe", 54, 77, 54, 131.29), ("Cs", 55, 78, 55, 132.91), ("Ba", 56, 81, 56, 137.33),
    ("La", 57, 82, 57, 138.91), ("Ce", 58, 82, 58, 140.12), ("Pr", 59, 82, 59, 140.91), ("Nd", 60, 84, 60, 144.24),
    ("Pm", 61, 84, 61, 145.0), ("Sm", 62, 88, 62, 150.36), ("Eu", 63, 89, 63, 151.96), ("Gd", 64, 93, 64, 157.25),
    ("Tb", 65, 94, 65, 158.93), ("Dy", 66, 97, 66, 162.5), ("Ho", 67, 98, 67, 164.93), ("Er", 68, 99, 68, 167.26),
    ("Tm", 69, 100, 69, 168.93), ("Yb", 70, 103, 70, 173.05), ("Lu", 71, 104, 71, 174.97), ("Hf", 72, 106, 72, 178.49),
    ("Ta", 73, 108, 73, 180.95), ("W", 74, 110, 74, 183.84), ("Re", 75, 111, 75, 186.21), ("Os", 76, 114, 76, 190.23),
    ("Ir", 77, 115, 77, 192.22), ("Pt", 78, 117, 78, 195.08), ("Au", 79, 118, 79, 196.97), ("Hg", 80, 121, 80, 200.59),
    ("Tl", 81, 123, 81, 204.38), ("Pb", 82, 125, 82, 207.2), ("Bi", 83, 126, 83, 208.98), ("Po", 84, 125, 84, 209.0),
    ("At", 85, 125, 85, 210.0), ("Rn", 86, 136, 86, 222.0), ("Fr", 87, 136, 87, 223.0), ("Ra", 88, 138, 88, 226.0),
    ("Ac", 89, 138, 89, 227.0), ("Th", 90, 142, 90, 232.04), ("Pa", 91, 140, 91, 231.04), ("U", 92, 146, 92, 238.03),
]

MOLECULES: Dict[str, float] = {
    "H2O": 18.015, "CO2": 44.01, "O2": 31.9988, "N2": 28.0134,
    "CH4": 16.04, "C6H12O6": 180.16, "NH3": 17.0305, "HCl": 36.46,
    "C2H2": 26.04, "NaCl": 58.44, "CaCO3": 100.0869, "C2H6": 30.07,
    "C2H4": 28.05, "C8H18": 114.23, "C6H6": 78.11, "CH3COOH": 60.052,
    "H2SO4": 98.079, "C12H22O11": 342.30, "C8H10N4O2" : 194.19
}


def _elements_from_table() -> Dict[str, tuple[int,int,int,float]]:
    elements = {}
    for name, p, n, e, gmol in ATOMS_MOLS:
        if name.isalpha() and len(name) <= 2:
            elements[name] = (p, n, e, gmol)
    return elements

def _parse_formula(formula: str) -> Dict[str, int]:
    tokens = re.findall(r'([A-Z][a-z]?)(\d*)', formula)
    counts: Dict[str, int] = {}
    for sym, num in tokens:
        k = int(num) if num else 1
        counts[sym] = counts.get(sym, 0) + k
    return counts

def compute_tables(
    topologies: Dict,
    cfg: Config,
    phi_val: float = phi0,
    use_semf: bool = True,
    data_source: str = "standard_weight",
    isotope_masses_kg: Dict[str, float] | None = None,
) -> pd.DataFrame:
    # 1. Base Masses (Sum of Parts)
    M_e_pred = master_mass_invariant(topologies["electron"], phi_val=phi_val)
    M_p_pred = master_mass_invariant(topologies["proton"],   phi_val=phi_val)
    M_n_pred = master_mass_invariant(topologies["neutron"],  phi_val=phi_val)

    rows: List[Tuple[str, float, float, str]] = []

    # Elementary particles (No binding energy)
    rows.append(("Electron", M_e_actual, M_e_pred, emoji_marker(100.0*(M_e_pred-M_e_actual)/M_e_actual)))
    # Higher-generation leptons: either predicted (electron_only) or calibrated (each_lepton).
    if "muon" in topologies:
        M_mu_pred = master_mass_invariant(topologies["muon"], phi_val=phi_val)
        rows.append(("Muon", M_mu_actual, M_mu_pred, emoji_marker(100.0*(M_mu_pred-M_mu_actual)/M_mu_actual)))
    if "tau" in topologies:
        M_tau_pred = master_mass_invariant(topologies["tau"], phi_val=phi_val)
        rows.append(("Tau", M_tau_actual, M_tau_pred, emoji_marker(100.0*(M_tau_pred-M_tau_actual)/M_tau_actual)))
    rows.append(("Proton",   M_p_actual, M_p_pred, emoji_marker(100.0*(M_p_pred-M_p_actual)/M_p_actual)))
    rows.append(("Neutron",  M_n_actual, M_n_pred, emoji_marker(100.0*(M_n_pred-M_n_actual)/M_n_actual)))

    # Elements (With optional Nuclear Binding Correction)
    elements = _elements_from_table()
    iso = isotope_masses_kg or {}

    # IMPORTANT:
    # SEMF is a nucleus model; it is meaningful against isotope-resolved atomic masses,
    # NOT against standard atomic weights (natural abundance averages).
    if use_semf and data_source == "standard_weight":
        _warn_once(
            "semf_vs_standard_weight",
            (
                "\n[WARN] use_semf=True but data_source='standard_weight'.\n"
                "       You are comparing isotope-based (Z,N) predictions to abundance-averaged targets.\n"
                "       This can bias the best-fit phi. Prefer data_source='isotope_mass' when use_semf=True.\n"
            ),
        )

    for name, (pZ, nN, eE, gmol) in elements.items():
        if data_source == "isotope_mass":
            if name not in iso:
                raise KeyError(
                    f"Missing isotope mass for element '{name}' in isotope_masses_kg. "
                    f"Provide it via cfg.isotope_mass_csv or switch to data_source='standard_weight'."
                )
            actual_kg = iso[name]
        else:
            # Standard atomic weight (natural abundance average)
            actual_kg = gmol * 1e-3 / avogadro

        # Sum of parts
        mass_sum = pZ * M_p_pred + nN * M_n_pred + eE * M_e_pred

        # SUBTRACT Binding Energy (The "SST Efficiency" Gain)
        # Toggleable to test whether the SEMF proxy shifts the best-fit phi.
        if use_semf:
            A = pZ + nN
            xi = xi_A(A, cfg.xi_gamma, cfg.xi_A0, cfg.xi_p)
            mass_defect = NuclearBinding.get_mass_defect_kg(pZ, nN, xi=xi)
        else:
            mass_defect = 0.0
        predicted = mass_sum - mass_defect

        rel_error = 100.0 * (predicted - actual_kg) / actual_kg
        rows.append((name, actual_kg, predicted, emoji_marker(rel_error)))

    # Molecules (Sum of corrected atoms)
    # Note: Chemical binding energy (~eV) is negligible compared to Nuclear (~MeV)
    # so we just sum the corrected atomic masses.
    for mol, gmol in MOLECULES.items():
        counts = _parse_formula(mol)
        pred_mol = 0.0

        for sym, k in counts.items():
            pZ, nN, eE, _ = elements[sym]

            # Re-calculate atomic mass with binding for each constituent
            atom_sum = pZ * M_p_pred + nN * M_n_pred + eE * M_e_pred
            if use_semf:
                A_atom = pZ + nN
                xi_atom = xi_A(A_atom, cfg.xi_gamma, cfg.xi_A0, cfg.xi_p)
                atom_defect = NuclearBinding.get_mass_defect_kg(pZ, nN, xi=xi_atom)
            else:
                atom_defect = 0.0
            atom_mass_corrected = atom_sum - atom_defect

            pred_mol += k * atom_mass_corrected

        # Molecules only available in standard-weight mode in this script:
        # isotope-resolved molecular masses require specifying isotopologues.
        if data_source == "isotope_mass":
            # Keep molecules out of isotope-mode objective to avoid mixing semantics.
            # Still compute them if you want, but you must provide explicit isotopologues.
            continue
        actual_kg = gmol * 1e-3 / avogadro
        rel_error = 100.0 * (pred_mol - actual_kg) / actual_kg
        rows.append((mol, actual_kg, pred_mol, emoji_marker(rel_error)))

    return pd.DataFrame(rows, columns=["Object","Actual Mass (kg)","Predicted Mass (kg)","% Error"])

def rms_excluding(df: pd.DataFrame, exclude: list[str]) -> float:
    df2 = df.loc[~df["Object"].isin(exclude), ["Predicted Mass (kg)", "Actual Mass (kg)"]].copy()

    # Drop invalid targets
    df2 = df2.dropna()
    df2 = df2[df2["Actual Mass (kg)"] != 0]

    if df2.empty:
        return float("nan")

    rel = (df2["Predicted Mass (kg)"] - df2["Actual Mass (kg)"]) / df2["Actual Mass (kg)"]
    return float((rel.pow(2).mean() ** 0.5) * 100.0)

def eval_phi(
    phi_val: float,
    mode: str = "canonical",
    use_semf: bool = True,
    data_source: str | None = None,
    isotope_mass_csv: str = "isotope_masses.csv",
) -> dict:
    """Align with phi_sweep: pass data_source/isotope_mass_csv explicitly to match sweep semantics."""
    cfg = Config(mode=mode)
    ds = data_source if data_source is not None else cfg.data_source
    iso = None
    if ds == "isotope_mass":
        iso = _load_isotope_masses_kg(isotope_mass_csv)
    tops = get_particle_topologies(cfg, phi_val=phi_val)
    tops.pop("_diag", None)
    df = compute_tables(
        tops, cfg, phi_val=phi_val,
        use_semf=use_semf,
        data_source=ds,
        isotope_masses_kg=iso,
    )
    return {
        "phi": float(phi_val),
        "ln_phi": float(math.log(phi_val)),
        "RMS_excl_e": float(rms_excluding(df, ["Electron"])),
        "RMS_excl_epn": float(rms_excluding(df, ["Electron", "Proton", "Neutron"])),
    }

def phi_sweep(
    mode: str = "canonical",
    npts: int = 81,
    span: float = 0.08,
    use_semf: bool = True,
    data_source: str = "standard_weight",
    isotope_mass_csv: str = "isotope_masses.csv",
) -> pd.DataFrame:
    """
    span=0.08 sweeps phi in [phi0*(1-span), phi0*(1+span)].
    """
    if npts < 2:
        raise ValueError("npts must be >= 2")
    if span < 0:
        raise ValueError("span must be >= 0")

    cfg = Config(mode=mode)

    iso = None
    if data_source == "isotope_mass":
        iso = _load_isotope_masses_kg(isotope_mass_csv)

    phi_min = phi0 * (1 - span)
    phi_max = phi0 * (1 + span)
    phi_grid = np.linspace(phi_min, phi_max, npts)

    rows = []
    for phi_val in phi_grid:
        tops = get_particle_topologies(cfg, phi_val=float(phi_val))
        tops.pop("_diag", None)

        df = compute_tables(
            tops, cfg, phi_val=float(phi_val),
            use_semf=use_semf,
            data_source=data_source,
            isotope_masses_kg=iso,
        )

        rms_excl_epn = rms_excluding(df, ["Electron", "Proton", "Neutron"])
        rms_excl_e   = rms_excluding(df, ["Electron"])

        rows.append((float(phi_val), float(math.log(phi_val)), float(rms_excl_epn), float(rms_excl_e)))

    return pd.DataFrame(rows, columns=["phi", "ln_phi", "RMS_excl_epn", "RMS_excl_e"])

# ──────────────────────────────────────────────────────────────────────────────
# Main Function
# ──────────────────────────────────────────────────────────────────────────────
def main(mode: str = "exact_closure") -> None:
    print("=== SST Invariant Master Mass (Canon) ===")
    cfg = Config(mode=mode)
    topologies = get_particle_topologies(cfg)
    diag = topologies.pop("_diag")

    print("\n--- Mode & Model Parameters ---")
    print(f"mode = {diag['mode']}  |  kappa_R = {diag['kappa_R']:.6g}")
    print(f"s_u = {diag['s_u']:.6f}, s_d = {diag['s_d']:.6f}, lambda_b = {diag['lambda_b']:.6f}")
    print(f"A_bary = {diag['A_bary']:.6e},  K = {diag['K']:.6e}")
    print(f"scaling_factor = {diag['scaling_factor']:.6f}")
    if diag.get("k_up_twist_alex") is not None and diag.get("k_down_twist_alex") is not None:
        print("\n--- Twist-knot real-k diagnostics (Alexander root proxy) ---")
        print(f"k(5_2) = {diag['k_up_twist_alex']:.9f}  |  k(6_1) = {diag['k_down_twist_alex']:.9f}")

    print("\n--- Particle Topological & Geometric Invariants ---")
    # Pop leptons for separate display
    lepton_topos = {k: topologies.pop(k) for k in ["electron", "muon", "tau"]}
    for p in lepton_topos.values():
        if p.b_braid is not None:
            print(f"{p.name:<18}: k={p.k} (kernel), b_braid={p.b_braid}, g={p.g}, n={p.n}, L_tot={p.L_tot:.6f}")
        else:
            print(f"{p.name:<18}: k={p.k}, g={p.g}, n={p.n}, L_tot={p.L_tot:.6f}")
    for p in topologies.values(): # Baryons
        print(f"{p.name:<18}: k={p.k}, g={p.g}, n={p.n}, L_tot={p.L_tot:.6f}")

    # Re-add leptons for table generation
    topologies.update(lepton_topos)
    df = compute_tables(topologies, cfg)

    print("\n--- Mass Prediction Results ---")
    pd.set_option("display.float_format", lambda x: f"{x:.6e}" if isinstance(x, float) else str(x))
    #print(df.to_string(index=False))

    # Ropelength Analysis
    ltot_e = topologies["electron"].L_tot
    ltot_mu = topologies["muon"].L_tot
    ltot_tau = topologies["tau"].L_tot
    print("\n--- Ropelength Analysis ---")
    print(f"Calibrated L_tot for Electron: {ltot_e:.6f}")
    print(f"Required L_tot for Muon (5_1):  {ltot_mu:.6f}")
    print(f"Required L_tot for Tau (7_1):   {ltot_tau:.6f}")
    print(f"Ratio (L_mu / L_e):   {ltot_mu / ltot_e:.4f}")
    print(f"Ratio (L_tau / L_mu): {ltot_tau / ltot_mu:.4f}")

    out_csv = f"SST_Invariant_Mass_Results_{mode}.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved results to {out_csv}")

# ──────────────────────────────────────────────────────────────────────────────
# Main Execution
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    # --- Phi sweeps: with and without SEMF proxy ---
    # Default: standard weights (averages). SEMF will warn about mixed semantics.
    df_sweep_semf = phi_sweep(mode="canonical", npts=101, span=0.05, use_semf=True, data_source="standard_weight")
    df_sweep_nosemf = phi_sweep(mode="canonical", npts=101, span=0.05, use_semf=False, data_source="standard_weight")

    print("\nTop 10 (canonical, with SEMF):")
    print(df_sweep_semf.sort_values("RMS_excl_epn").head(10))
    df_semf_sorted = df_sweep_semf.sort_values("RMS_excl_epn").reset_index(drop=True)
    best_semf_phi = df_semf_sorted.loc[0, "phi"]
    at_edge_semf = (best_semf_phi == df_sweep_semf["phi"].min()) or (best_semf_phi == df_sweep_semf["phi"].max())
    print("Best at edge? (with SEMF)", at_edge_semf)

    print("\nTop 10 (canonical, no SEMF):")
    print(df_sweep_nosemf.sort_values("RMS_excl_epn").head(10))
    df_nosemf_sorted = df_sweep_nosemf.sort_values("RMS_excl_epn").reset_index(drop=True)
    best_nosemf_phi = df_nosemf_sorted.loc[0, "phi"]
    at_edge_nosemf = (best_nosemf_phi == df_sweep_nosemf["phi"].min()) or (best_nosemf_phi == df_sweep_nosemf["phi"].max())
    print("Best at edge? (no SEMF)", at_edge_nosemf)

    # Optional: isotope-resolved sweep (requires isotope_masses.csv)
    # If you provide isotope masses consistent with your (Z,N) table, this is the correct way
    # to interpret SEMF-on fits.
    try:
        df_sweep_iso_semf = phi_sweep(
            mode="canonical", npts=101, span=0.05, use_semf=True,
            data_source="isotope_mass", isotope_mass_csv="isotope_masses.csv"
        )
        print("\nTop 10 (canonical, with SEMF, isotope_mass targets):")
        print(df_sweep_iso_semf.sort_values("RMS_excl_epn").head(10))
    except Exception as e:
        print("\n[INFO] Isotope-resolved sweep skipped:", str(e))

    # --- Golden-ratio vs best-fit diagnostics ---
    best_semf = df_semf_sorted.iloc[0]
    phi_best_semf = float(best_semf["phi"])
    gold_semf = eval_phi(phi0, mode="canonical", use_semf=True, data_source="standard_weight")
    best_eval_semf = eval_phi(phi_best_semf, mode="canonical", use_semf=True, data_source="standard_weight")

    print("\n--- Phi diagnostics (canonical, with SEMF) ---")
    print("Golden:", gold_semf)
    print("Best  :", best_eval_semf)
    print(f"RMS ratio excl_epn: {gold_semf['RMS_excl_epn']/best_eval_semf['RMS_excl_epn']:.6f}")
    print(f"RMS ratio excl_e  : {gold_semf['RMS_excl_e']/best_eval_semf['RMS_excl_e']:.6f}")

    best_nosemf = df_nosemf_sorted.iloc[0]
    phi_best_nosemf = float(best_nosemf["phi"])
    gold_nosemf = eval_phi(phi0, mode="canonical", use_semf=False, data_source="standard_weight")
    best_eval_nosemf = eval_phi(phi_best_nosemf, mode="canonical", use_semf=False, data_source="standard_weight")

    print("\n--- Phi diagnostics (canonical, no SEMF) ---")
    print("Golden:", gold_nosemf)
    print("Best  :", best_eval_nosemf)
    print(f"RMS ratio excl_epn: {gold_nosemf['RMS_excl_epn']/best_eval_nosemf['RMS_excl_epn']:.6f}")
    print(f"RMS ratio excl_e  : {gold_nosemf['RMS_excl_e']/best_eval_nosemf['RMS_excl_e']:.6f}")

    arg_mode = sys.argv[1] if len(sys.argv) > 1 else "exact_closure"
    main(arg_mode)

    try:
        #ans = input("\nCompare with other modes and add predicted columns? [y/N]: ").strip().lower()
        ans = "y"
    except EOFError:
        ans = "n"

    if ans in ("y", "yes"):
        all_modes = ["exact_closure", "canonical", "sector_norm"]
        label_map = {"canonical":"CANON", "sector_norm":"Sector Norm", "exact_closure":"Exact Closure"}

        # Get the base dataframe from the mode just run
        cfg_base = Config(mode=arg_mode)
        tops_base = get_particle_topologies(cfg_base)
        # We need to remove the diagnostic dict before passing to compute_tables
        tops_base.pop("_diag", None)
        df_cmp = compute_tables(tops_base, cfg_base)

        # Compute results for other modes and merge
        other_modes = [m for m in all_modes if m != arg_mode]
        for m in other_modes:
            cfg_m = Config(mode=m)
            tops_m = get_particle_topologies(cfg_m)
            tops_m.pop("_diag", None)
            df_m = compute_tables(tops_m, cfg_m)[["Object","Actual Mass (kg)","Predicted Mass (kg)"]].rename(
                columns={"Predicted Mass (kg)": f"Predicted Mass (kg) [{label_map[m]}]"}
            )
            # Error column for that mode
            df_m[f"% Error [{label_map[m]}]"] = 100.0 * (df_m[f"Predicted Mass (kg) [{label_map[m]}]"] - df_m["Actual Mass (kg)"]) / df_m["Actual Mass (kg)"]
            df_m[f"% Error [{label_map[m]}]"] = df_m[f"% Error [{label_map[m]}]"].apply(emoji_marker)
            df_m = df_m.drop(columns=["Actual Mass (kg)"])
            df_cmp = df_cmp.merge(df_m, on="Object", how="left")

        # Reorder columns for clarity
        desired_cols = ["Object","Actual Mass (kg)","Predicted Mass (kg)","% Error",
                        "Predicted Mass (kg) [CANON]","% Error [CANON]",
                        "Predicted Mass (kg) [Sector Norm]","% Error [Sector Norm]"]
        cols = [c for c in desired_cols if c in df_cmp.columns] + [c for c in df_cmp.columns if c not in desired_cols]
        df_cmp = df_cmp[cols]

        out_csv_all = "SST_Invariant_Mass_Results_all_modes.csv"
        df_cmp.to_csv(out_csv_all, index=False)
        print(df_cmp.to_string(index=False))
        print(f"\nSaved comparison to {out_csv_all}")