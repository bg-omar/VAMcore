# sst_canon_pipeline.py
import math
import pandas as pd
import numpy as np, re, math

# ── Golden ratio ─────────────────────────────────────────────────────────────
phi = (1 + math.sqrt(5)) / 2

# ── Physical constants (SI unless noted) ─────────────────────────────────────
alpha_fs = 7.2973525643e-3      # fine-structure constant
rho_0    = 3.8934358266918687e18  # kg/m^3  (SST/VAM canonical)
v_swirl  = 1.09384563e6         # m/s
r_c      = 1.40897017e-15       # m
c        = 299_792_458          # m/s
M_e_SI   = 9.1093837015e-31     # kg
m_e_eV   = 0.510_998_950e6      # eV (electron mass), natural units
NA       = 6.02214076e23

# ── Knot “volumes” for hadrons (tube model) ──────────────────────────────────
# V_torus = 4π^2 r_c^3  (your algebraic form 2π^2 (2r_c) r_c^2 is identical)
V_torus  = 4 * math.pi**2 * r_c**3
# V_u_topo = 2.8281   # for 5_2
# V_d_topo = 3.1639   # for 6_1
# --- Hyperbolic volume of knot complements -----------------------------------
# Priority: use SnapPy if present; otherwise use a small built-in table.
# Note: torus/satellite knots have volume 0 by definition.

try:
    import snappy  # pip install snappy
    HAVE_SNAPPY = True
except Exception:
    HAVE_SNAPPY = False

# Minimal fallback table (5 significant digits typical in the literature)
HYP_VOL_TABLE = {
    # hyperbolic:
    "4_1": 2.02988,   # 2 twist
    "5_2": 2.82812,   # 3 twist
    "6_1": 3.16396,   # 4 twist
    "7_2": 3.33174,   # 5 twist
    "8_1": 3.42721,   # 6 twist
    "9_2": 3.48666,   # 7 twist
    "10_1": 3.5262,   # 8 twist
    # non-hyperbolic (torus): volumes are 0.0
    "3_1": 0.0,
    "5_1": 0.0,
    "7_1": 0.0,
}

def base_from_filename(path):
    import os, re
    s = os.path.basename(path).replace("knot.","").replace(".fseries","")
    m = re.match(r"(\d+(?:a|n)?_\d+|15331)", s)
    return m.group(1) if m else s

def hyperbolic_volume_for(name):
    """
    Returns the hyperbolic volume Vol_hyp(K) (dimensionless).
    If SnapPy is available, computes it canonically.
    Otherwise falls back to a small table (extend as needed).
    """
    # Non-hyperbolic quick outs (torus knots, satellites) → 0
    # Known torus: T(2,2n+1) = 3_1, 5_1, 7_1, ...
    if name in {"3_1", "5_1", "7_1"}:
        return 0.0

    if HAVE_SNAPPY:
        # SnapPy naming: small knots usually accessible via spherogram link names
        # e.g. '5_2', '6_1'. If that fails, try 'K5_2' etc.
        try:
            L = snappy.Link(name)
        except Exception:
            try:
                L = snappy.Link("K"+name)
            except Exception:
                L = None
        if L is not None:
            M = L.exterior()
            try:
                vol = float(M.volume())
                # Some knots are not hyperbolic; SnapPy may return 0 or raise
                return max(vol, 0.0)
            except Exception:
                pass  # fall through to table

    # Fallback numeric
    if name in HYP_VOL_TABLE:
        return HYP_VOL_TABLE[name]

    # Last resort: 0.0 (unknown); better to log and fill later
    return 0.0
V_u_topo = hyperbolic_volume_for("5_2")  # ≈ 2.82812
V_d_topo = hyperbolic_volume_for("6_1")  # ≈ 3.16396

V_u = V_u_topo * V_torus
V_d = V_d_topo * V_torus

# ---- L_K from .fseries, normalized to unknot ----
from fseries_compat import parse_fseries_multi, eval_fourier_block
from sst_exports import get_exports_dir

def polyline_length(x,y,z):
    pts = np.stack([x,y,z], axis=1)
    d = np.diff(pts, axis=0, append=pts[:1])
    return np.sum(np.linalg.norm(d, axis=1))

def L_from_fseries(path_K, path_unknot, L0=7.64, N=4000):
    s = np.linspace(0, 2*np.pi, N, endpoint=False)
    coeffs_K = max(parse_fseries_multi(path_K), key=lambda b: b[1]['a_x'].size)[1]
    coeffs_U = max(parse_fseries_multi(path_unknot), key=lambda b: b[1]['a_x'].size)[1]
    xK,yK,zK = eval_fourier_block(coeffs_K, s)
    xU,yU,zU = eval_fourier_block(coeffs_U, s)
    LK = polyline_length(xK,yK,zK)
    LU = polyline_length(xU,yU,zU)
    return L0 * (LK/LU)

# ---- genus map (extend as needed); fallback ≈ floor((C-1)/2) ----
GENUS_HINT = {
    "3_1": 1, "5_1": 2, "5_2": 1,
    "6_1": 1, "5_2": 1, "6_3": 1,
    "7_1": 3, "7_2": 2, "7_3": 2, "7_4": 2, "7_5": 1, "7_6": 2, "7_7": 2,
    # add more as needed
}
def crossing_from_name(name):
    m = re.match(r"(\d+)_", name)
    return int(m.group(1)) if m else None

def genus_of(name):
    if name in GENUS_HINT: return GENUS_HINT[name]
    c = crossing_from_name(name)
    return max(1, (c-1)//2) if c else 1  # crude lower bound fallback

# ---- canonical k-selection ----
def pick_k_canonical(name, a_mu_list, delta_star=0.03, sigma_star=0.02):
    a_mu_arr = np.asarray(a_mu_list, float)
    delta_bar = float(a_mu_arr.mean() + 0.5)
    sigma = float(a_mu_arr.std(ddof=0))
    if abs(delta_bar) <= delta_star and sigma <= sigma_star:
        return 0  # helicity-band override
    return -genus_of(name)  # topological base

# ── SST/VAM master mass for composites (proton/neutron) ──────────────────────
def vam_master_mass(n_knots, m_threads, s, V_list):
    """
    Mass = (4/alpha_fs) * eta * xi * tension * sum(V_i) * (0.5*rho_0*v_swirl^2) / c^2
    """
    volume_sum = sum(V_list)
    eta     = (1 / m_threads) ** 3
    xi      = n_knots ** (-1 / phi)
    tension = 1 / phi ** s
    energy_density = 0.5 * rho_0 * v_swirl ** 2
    M = (4 / alpha_fs) * eta * xi * tension * volume_sum * energy_density / c**2
    return M

# ── Topological factor Ξ_K = [(α_topo*C + β*L)/(β*L0)] * φ^{-2k} ─────────────
def xi_normalized(C, L, k, alpha_topo, beta, L0):
    return ((alpha_topo * C + beta * L) / (beta * L0)) * (phi ** (-2 * k))

def solve_alpha_from_mu(L0, L3, beta, k3, mu_over_e=206.7682830):
    # α_topo = (β/3) * [ (m_mu/m_e)*L0*φ^(2k3) - L3 ]
    return (beta / 3.0) * ((mu_over_e * L0 * (phi ** (2 * k3))) - L3)

# ── OPTIONAL: helicity-based electron (kept for continuity; not used by Ξ_K) ─
def vam_electron_mass_helicity(p=2, q=3):
    sqrt_term = math.sqrt(p**2 + q**2)
    m = 1; n = 1; s = 1
    eta = (1 / m) ** 1.5
    xi  = n ** (-1 / phi)
    tension = 1 / phi ** s
    V_helical = 4 * math.pi ** 2 * r_c ** 3
    A = eta * xi * tension * V_helical
    factor = 8 * math.pi * rho_0 * r_c**3 / v_swirl  # NOTE: legacy form; not needed for Ξ calibration
    return factor * (sqrt_term + A)

# ── Pretty marker for % diffs ────────────────────────────────────────────────
def emoji_marker(diff_pct):
    d = abs(diff_pct)
    if d < 1: icon = "🩷"
    elif d < 2.5: icon = "🟢"
    elif d < 10: icon = "🟡"
    elif d < 25: icon = "🟠"
    else: icon = "🔴"
    arrow = "🡇" if diff_pct < 0 else "🡅"
    if diff_pct == 0: return "0.00% ●"
    return f"{diff_pct:.2f}% {icon}{arrow}"

# ── Demo atom/molecule list (as before) ──────────────────────────────────────
atoms_molecules = [
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
    ("H2O", 10, 8, 10, 18.015), ("CO2", 22, 22, 22, 44.01), ("O2", 16, 16, 16, 31.9988), ("N2", 14, 14, 14, 28.0134),
    ("CH4", 10, 10, 10, 16.04), ("C6H12O6", 72, 72, 72, 180.16), ("NH3", 10, 10, 10, 17.0305), ("HCl", 18, 18, 18, 36.46),
    ("C2H6", 18, 18, 18, 30.07), ("C2H4", 16, 16, 16, 28.05), ("C2H2", 14, 14, 14, 26.04), ("NaCl", 28, 28, 28, 58.44),
    ("C8H18", 98, 98, 98, 114.23), ("C6H6", 48, 48, 48, 78.11), ("CH3COOH", 32, 32, 32, 60.052), ("H2SO4", 50, 50, 50, 98.079),
    ("CaCO3", 50, 50, 50, 100.0869), ("C12H22O11", 176, 176, 176, 342.30),
    ("Caffeine", 194, 194, 194, 194.19), ("DNA (avg)", 10000, 10000, 10000, 6500.0)
]

# ── Main canonical flow ──────────────────────────────────────────────────────
if __name__ == "__main__":
    # === 1) Calibrate topological mass factor on (e, μ) ======================
    # Keep your provisional values here; change freely:
    L0 = 7.64          # ropelength-like for 0_1
    L3 = 16.4          # ropelength-like for 3_1
    beta_t = 0.1       # dimensionless
    k3    = 0          # Golden-layer index for μ; adjust if desired

    alpha_topo = solve_alpha_from_mu(L0, L3, beta_t, k3)   # ~52.11 with these inputs
    Xi_e  = 1.0                                          # enforced by normalization
    Xi_mu = xi_normalized(3, L3, k3, alpha_topo, beta_t, L0)

    # Lepton masses in eV (by construction: exact e, exact μ)
    m_e_pred_eV  = m_e_eV * Xi_e
    m_mu_pred_eV = m_e_eV * Xi_mu

    # === 2) Optional τ prediction once L5, k5 are set ========================
    # Supply L5 when you’re ready; leave as None to skip
    L5 = None          # e.g. set to your cinquefoil measure
    k5 = 0
    m_tau_pred_eV = None
    if L5 is not None:
        Xi_tau = xi_normalized(5, L5, k5, alpha_topo, beta_t, L0)
        m_tau_pred_eV = m_e_eV * Xi_tau

    # === 3) Proton / neutron from SST/VAM energy scale =======================
    V_u = V_u_topo * V_torus
    V_d = V_d_topo * V_torus
    s_layer = 3        # your “Golden tension” index for nucleons
    M_p_pred = vam_master_mass(n_knots=3, m_threads=1, s=s_layer, V_list=[V_u, V_u, V_d])
    M_n_pred = vam_master_mass(n_knots=3, m_threads=1, s=s_layer, V_list=[V_u, V_d, V_d])

    # Experimental SI masses for comparison
    M_p_exp = 1.67262192369e-27
    M_n_exp = 1.67492749804e-27

    # === 4) Display a concise report ========================================
    rows = []
    rows.append(("electron (Ξ)",  m_e_pred_eV, 0.510998950e6, emoji_marker(100*(m_e_pred_eV/0.510998950e6 - 1.0))))
    rows.append(("muon (Ξ)",      m_mu_pred_eV, 105.6583755e6, emoji_marker(100*(m_mu_pred_eV/105.6583755e6 - 1.0))))
    if m_tau_pred_eV is not None:
        rows.append(("tau (Ξ)",   m_tau_pred_eV, 1776.86e6,    emoji_marker(100*(m_tau_pred_eV/1776.86e6 - 1.0))))

    rows.append(("proton (SST)",  M_p_pred, M_p_exp, emoji_marker(100*(M_p_pred/M_p_exp - 1.0))))
    rows.append(("neutron (SST)", M_n_pred, M_n_exp, emoji_marker(100*(M_n_pred/M_n_exp - 1.0))))

    df_summary = pd.DataFrame(rows, columns=["Object", "Predicted", "Reference", "% Error"])
    print("\n=== SST Canonical Mass Summary ===")
    print(df_summary.to_string(index=False))

    # === 5) Atomic/molecular “toy” masses from predicted p/n + e =============
    elem_rows = [("Proton (kg)", M_p_pred, M_p_exp, emoji_marker(100*(M_p_pred/M_p_exp - 1.0))),
                 ("Neutron (kg)", M_n_pred, M_n_exp, emoji_marker(100*(M_n_pred/M_n_exp - 1.0))),
                 ("Electron (kg)", M_e_SI, M_e_SI, "—")]

    df_elem = pd.DataFrame(elem_rows, columns=["Particle", "Predicted", "Reference", "% Error"])

    atom_rows = []
    for name, p, n, e, gmol in atoms_molecules:
        actual_kg = gmol * 1e-3 / NA
        predicted = p * M_p_pred + n * M_n_pred + e * M_e_SI
        rel_error = 100 * (predicted / actual_kg - 1.0)
        atom_rows.append((name, predicted, actual_kg, emoji_marker(rel_error)))
    df_atoms = pd.DataFrame(atom_rows, columns=["Species", "Predicted mass (kg)", "Ref mass (kg)", "% Error"])

    print("\n=== Nuclei/Atoms (toy aggregation from p/n/e) ===")
    print(df_atoms.head(12).to_string(index=False))  # don’t spam; show a few

    # Save optional CSVs to exports
    out_dir = get_exports_dir()
    df_summary.to_csv(out_dir / "SST_Mass_Summary.csv", index=False)
    df_atoms.to_csv(out_dir / "SST_Atom_Toy_Masses.csv", index=False)