"""
SST Trefoil Vortex Stability Analysis — patched baseline
=======================================================

Key repairs relative to the earlier baseline:

1) Gamma_0 is treated as an independent input or scan variable.
   Nothing in the computation derives Gamma_0 from r_c_canon.

2) A_K is extracted from a local slope plateau in
      y(a) = E_BS_norm(a) / L_K
   versus
      x(a) = -ln(a)
   rather than from one global linear fit across mixed regimes.

3) Uses exact c = 299792458 m/s for the alpha consistency check.

The script computes:
- dimensionless trefoil geometry
- regularised Biot–Savart self-energy E_BS_norm(a_dimless)
- local slope A_K_local(a)
- plateau estimate A_K_plateau
- stationary radius a* from the Route-2 functional
- diagnostic chi_eff = a* v_swirl / Gamma_0

Important epistemic note:
This script may compare against r_c_canon, but does NOT use r_c_canon
to define Gamma_0 or the natural length scale. Physical scaling is set by
L_natural = Gamma_0 / v_swirl only.
"""

import numpy as np
from scipy.optimize import brentq
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# 1. Canonical reference values (for comparison only)
# ─────────────────────────────────────────────────────────────
r_c_canon = 1.40897017e-15         # m, comparison target only
v_swirl   = 1.09384563e6           # m/s, primitive
rho_f     = 7.0e-7                 # kg/m^3, primitive
rho_core  = 3.8934358266918687e18  # kg/m^3, reference only, not used in Route 2
c_exact   = 299792458.0            # m/s, exact

# Independent Gamma_0 input.
# For a first comparison run, we choose the canonical-scale value numerically,
# but NOT by computing it from r_c inside the algorithm.
Gamma_0_input = 9.68361918e-09     # m^2/s  <-- independent input / scan variable

print("Reference / input values:")
print(f"  r_c_canon   = {r_c_canon:.8e} m   (comparison only)")
print(f"  v_swirl     = {v_swirl:.8e} m/s")
print(f"  rho_f       = {rho_f:.8e} kg/m^3")
print(f"  rho_core    = {rho_core:.8e} kg/m^3  (not used in Route 2)")
print(f"  Gamma_0     = {Gamma_0_input:.8e} m^2/s  (independent input)")
print(f"  c           = {c_exact:.1f} m/s")
print()

# ─────────────────────────────────────────────────────────────
# 2. Trefoil centerline geometry (dimensionless)
# ─────────────────────────────────────────────────────────────
R_t = 2.0
r_t = 1.0
N   = 2000


def trefoil_points(N, R_t=2.0, r_t=1.0):
    theta = np.linspace(0, 2*np.pi, N, endpoint=False)
    x = (R_t + r_t * np.cos(3*theta)) * np.cos(2*theta)
    y = (R_t + r_t * np.cos(3*theta)) * np.sin(2*theta)
    z = r_t * np.sin(3*theta)
    return np.stack([x, y, z], axis=1)


pts = trefoil_points(N, R_t, r_t)
diffs = np.roll(pts, -1, axis=0) - pts
seg_lengths = np.linalg.norm(diffs, axis=1)
L_K_dimless = np.sum(seg_lengths)
tangents = diffs / seg_lengths[:, None]

# coarse self-distance estimate
step = max(1, N // 200)
pts_coarse = pts[::step]
n_c = len(pts_coarse)
exclude = max(3, n_c // 20)
d_min = np.inf
for i in range(n_c):
    for j in range(i + exclude, n_c - exclude):
        d = np.linalg.norm(pts_coarse[i] - pts_coarse[j])
        if d < d_min:
            d_min = d

# segment spacing estimate for UV-discretisation diagnostics
ell_seg_med = np.median(seg_lengths)

print("Trefoil geometry (dimensionless):")
print(f"  N               = {N}")
print(f"  L_K             = {L_K_dimless:.8f}")
print(f"  d_min           = {d_min:.8f}")
print(f"  median ds       = {ell_seg_med:.8e}")
print()

# ─────────────────────────────────────────────────────────────
# 3. Regularised Biot–Savart self-energy E_BS_norm(a_dimless)
# ─────────────────────────────────────────────────────────────
xi = 1.0


def compute_E_BS_norm(a_dimless, pts, tangents, seg_lengths, xi=1.0):
    """
    E_BS_norm = E_BS / (rho_f * Gamma_0^2)
    Dimensionless geometry only.
    """
    delta = xi * a_dimless
    N = len(pts)
    total = 0.0
    index = np.arange(N)
    for i in range(N):
        diff = pts - pts[i]
        dist = np.linalg.norm(diff, axis=1)
        mask = (dist > delta) & (index != i)
        if not np.any(mask):
            continue
        dot_tt = tangents[mask] @ tangents[i]
        integrand = dot_tt / dist[mask]
        total += np.sum(integrand * seg_lengths[mask]) * seg_lengths[i]
    return total / (8 * np.pi)


# Scan range:
# start somewhat above the segment scale, otherwise the curve is mesh-flat.
a_scan = np.logspace(np.log10(max(3*ell_seg_med, d_min*1e-4)), np.log10(d_min * 0.35), 24)

print("Computing E_BS_norm(a_dimless)...")
E_BS_vals = []
for a_d in a_scan:
    e = compute_E_BS_norm(a_d, pts, tangents, seg_lengths, xi=xi)
    E_BS_vals.append(e)
    print(f"  a_dimless = {a_d:.6e}   E_BS_norm = {e:.8f}")
E_BS_vals = np.array(E_BS_vals)
print()

# ─────────────────────────────────────────────────────────────
# 4. Local-slope extraction of A_K
# ─────────────────────────────────────────────────────────────
# Model: y = E_BS_norm/L_K = A_K ln(L_K/a) + a_K
# Hence A_K = d y / d(-ln a)

x = -np.log(a_scan)
y = E_BS_vals / L_K_dimless

# local finite-difference slopes and centers
x_mid = 0.5 * (x[:-1] + x[1:])
a_mid = np.sqrt(a_scan[:-1] * a_scan[1:])
A_local = np.diff(y) / np.diff(x)

# Plateau selector:
# keep only region where
# - slope is positive
# - relative change in E_BS is non-negligible (avoid mesh-flat region)
# - a is still well below d_min (stay in slender-ish regime)
rel_dE = np.abs(np.diff(E_BS_vals)) / np.maximum(np.abs(E_BS_vals[:-1]), 1e-300)
plateau_mask = (A_local > 0) & (rel_dE > 1e-4) & (a_mid < 0.12 * d_min)

if np.any(plateau_mask):
    A_plateau_vals = A_local[plateau_mask]
    A_K_plateau = np.median(A_plateau_vals)
    A_K_spread = np.std(A_plateau_vals)
    plateau_method = "local-slope plateau"
else:
    # fallback: use the median of the first third of positive local slopes
    pos = A_local[A_local > 0]
    if len(pos) == 0:
        A_K_plateau = np.nan
        A_K_spread = np.nan
        plateau_method = "failed"
    else:
        take = max(3, len(pos)//3)
        A_K_plateau = np.median(pos[:take])
        A_K_spread = np.std(pos[:take])
        plateau_method = "fallback-positive-slope"

# Also compute the old-style global fit as a reference only
coeffs = np.polyfit(x, y, 1)
A_K_global = coeffs[0]
intercept = coeffs[1]
a_K_global = intercept - A_K_global * np.log(L_K_dimless)

print("A_K extraction:")
print(f"  method                 = {plateau_method}")
print(f"  A_K_local_plateau      = {A_K_plateau:.8f}")
print(f"  spread                 = {A_K_spread:.8f}")
print(f"  A_K_global_fit         = {A_K_global:.8f}")
print(f"  A_K_req = 1/(4*pi)     = {1/(4*np.pi):.8f}")
print()

# choose plateau estimate if finite, else fall back
A_K_use = A_K_plateau if np.isfinite(A_K_plateau) else A_K_global

# Estimate a_K from local choice by anchoring at median y over plateau region
if np.any(plateau_mask):
    idx_ref = np.where(plateau_mask)[0][len(np.where(plateau_mask)[0]) // 2]
    a_ref = a_mid[idx_ref]
    y_ref = 0.5 * (y[idx_ref] + y[idx_ref + 1])
    a_K_use = y_ref - A_K_use * np.log(L_K_dimless / a_ref)
else:
    a_K_use = a_K_global

print("Chosen Biot–Savart parameters for energy model:")
print(f"  A_K_use                = {A_K_use:.8f}")
print(f"  a_K_use                = {a_K_use:.8f}")
print()

# ─────────────────────────────────────────────────────────────
# 5. Physical scaling from independent Gamma_0 and v_swirl
# ─────────────────────────────────────────────────────────────
# Natural internal scale from primitives only:
L_natural = Gamma_0_input / v_swirl
L_K_phys = L_K_dimless * L_natural
d_min_phys = d_min * L_natural

print("Physical scaling from primitives:")
print(f"  L_natural = Gamma_0 / v_swirl = {L_natural:.8e} m")
print(f"  L_K_phys  = {L_K_phys:.8e} m")
print(f"  d_min_phys= {d_min_phys:.8e} m")
print()

# ─────────────────────────────────────────────────────────────
# 6. Route-2 total energy functional
# ─────────────────────────────────────────────────────────────
lam_K = 0.01
p_exp = 2


def E_contact_phys(a, d_min_phys, lam_K, p_exp, rho_f, Gamma_0, L_K_phys):
    if 2*a >= d_min_phys:
        return np.inf
    x = 2*a / (d_min_phys - 2*a)
    return lam_K * rho_f * Gamma_0**2 * L_K_phys * x**p_exp



def E_K_phys(a, A_K, a_K, L_K_phys, Gamma_0, rho_f, v_swirl,
             d_min_phys, lam_K=0.01, p_exp=2):
    if a <= 0 or 2*a >= d_min_phys:
        return np.inf
    E_BS = rho_f * Gamma_0**2 * L_K_phys * (A_K * np.log(L_K_phys / a) + a_K)
    E_core = (np.pi / 2) * rho_f * v_swirl**2 * a**2 * L_K_phys
    E_cont = E_contact_phys(a, d_min_phys, lam_K, p_exp, rho_f, Gamma_0, L_K_phys)
    return E_BS + E_core + E_cont



def dE_K_da(a, A_K, L_K_phys, Gamma_0, rho_f, v_swirl,
            d_min_phys, lam_K=0.01, p_exp=2):
    if a <= 0 or 2*a >= d_min_phys:
        return np.nan
    dE_BS = -rho_f * Gamma_0**2 * L_K_phys * A_K / a
    dE_core = np.pi * rho_f * v_swirl**2 * a * L_K_phys
    x = 2*a / (d_min_phys - 2*a)
    dx_da = 2*d_min_phys / (d_min_phys - 2*a)**2
    dE_cont = lam_K * rho_f * Gamma_0**2 * L_K_phys * p_exp * x**(p_exp - 1) * dx_da
    return dE_BS + dE_core + dE_cont


# analytical no-contact baseline
if np.isfinite(A_K_use):
    a0 = np.sqrt(A_K_use / np.pi) * Gamma_0_input / v_swirl
else:
    a0 = np.nan

# search stationary point
# do not search below machine-noise scale; use a fraction of L_natural
# and stay below self-contact threshold
a_lo = max(d_min_phys * 1e-7, L_natural * 1e-8)
a_hi = d_min_phys * 0.49
a_vals = np.logspace(np.log10(a_lo), np.log10(a_hi), 600)
dE_vals = np.array([
    dE_K_da(a, A_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
            d_min_phys, lam_K, p_exp)
    for a in a_vals
])

sign_changes = np.where(np.diff(np.sign(dE_vals)))[0]
a_star = np.nan
is_minimum = False

if len(sign_changes) > 0:
    idx = sign_changes[0]
    a_star = brentq(
        dE_K_da, a_vals[idx], a_vals[idx + 1],
        args=(A_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
              d_min_phys, lam_K, p_exp)
    )
    h = max(a_star * 1e-6, 1e-30)
    d2E_num = (
        dE_K_da(a_star + h, A_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
                d_min_phys, lam_K, p_exp)
        - dE_K_da(a_star - h, A_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
                  d_min_phys, lam_K, p_exp)
    ) / (2*h)
    is_minimum = d2E_num > 0
else:
    valid = np.isfinite(dE_vals)
    if np.any(valid):
        a_star = a_vals[valid][np.argmin(np.abs(dE_vals[valid]))]

# dimensionless effective closure factor
chi_eff = a_star * v_swirl / Gamma_0_input if np.isfinite(a_star) else np.nan
chi_req = 1 / (2 * np.pi)

alpha_SST = 2 * v_swirl / c_exact

# ─────────────────────────────────────────────────────────────
# 7. Optional Gamma_0 scan (still independent)
# ─────────────────────────────────────────────────────────────
Gamma_scan = Gamma_0_input * np.logspace(-1.0, 1.0, 21)
a_star_scan = []
chi_scan = []

for G in Gamma_scan:
    L_nat = G / v_swirl
    L_phys = L_K_dimless * L_nat
    d_phys = d_min * L_nat
    a0_scan = np.sqrt(A_K_use / np.pi) * G / v_swirl if np.isfinite(A_K_use) else np.nan
    # use analytical no-contact as baseline because contact term is weak in the first model
    a_star_scan.append(a0_scan)
    chi_scan.append(a0_scan * v_swirl / G if np.isfinite(a0_scan) else np.nan)

a_star_scan = np.array(a_star_scan)
chi_scan = np.array(chi_scan)

# ─────────────────────────────────────────────────────────────
# 8. Results
# ─────────────────────────────────────────────────────────────
print("=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)
print("\nPrimitive inputs:")
print(f"  rho_f         = {rho_f:.8e} kg/m^3")
print(f"  Gamma_0       = {Gamma_0_input:.8e} m^2/s")
print(f"  v_swirl       = {v_swirl:.8e} m/s")

print("\nBiot–Savart extraction:")
print(f"  A_K_use       = {A_K_use:.8f}")
print(f"  A_K_req       = {1/(4*np.pi):.8f}")
print(f"  A_K_use/A_req = {A_K_use / (1/(4*np.pi)):.8f}")
print(f"  a_K_use       = {a_K_use:.8f}")

print("\nStationary radius:")
print(f"  a0 (no contact)   = {a0:.8e} m")
print(f"  a* (full model)   = {a_star:.8e} m")
print(f"  is minimum        = {is_minimum}")
print(f"  a*/r_c_canon      = {a_star / r_c_canon:.8f}")
print(f"  chi_eff           = {chi_eff:.8f}")
print(f"  chi_req = 1/(2pi) = {chi_req:.8f}")
print(f"  chi_eff/chi_req   = {chi_eff / chi_req:.8f}")

print("\nAlpha consistency check:")
print(f"  alpha_SST        = {alpha_SST:.12f}")
print(f"  alpha_SST^-1     = {1/alpha_SST:.9f}")
print("  NIST target      = 137.035999177")
print()

if np.isfinite(a_star):
    gap = r_c_canon / a_star
    print("Interpretation:")
    if abs(np.log10(a_star / r_c_canon)) < 0.1:
        print("  ✓ a* agrees with r_c_canon within about 25%.")
    elif abs(np.log10(a_star / r_c_canon)) < 0.3:
        print("  ~ a* is within a factor about 2 of r_c_canon.")
    else:
        print("  ✗ a* differs from r_c_canon by more than a factor about 2.")
    print(f"  multiplicative closure factor r_c_canon/a* = {gap:.8f}")
print()

# ─────────────────────────────────────────────────────────────
# 9. Plots
# ─────────────────────────────────────────────────────────────
out1 = "/mnt/data/sst_trefoil_AK_local_plateau.png"
out2 = "/mnt/data/sst_trefoil_energy_patched.png"
out3 = "/mnt/data/sst_trefoil_gamma_scan.png"

# Plot 1: A_local vs a_mid
plt.figure(figsize=(8, 5))
plt.semilogx(a_mid, A_local, 'o-', lw=1.5, ms=4, label='Local slope $A_K(a)$')
if np.any(plateau_mask):
    plt.semilogx(a_mid[plateau_mask], A_local[plateau_mask], 'ro', ms=5, label='Plateau region')
plt.axhline(1/(4*np.pi), color='green', ls='--', lw=1.5, label=r'$1/(4\pi)$')
if np.isfinite(A_K_use):
    plt.axhline(A_K_use, color='orange', ls=':', lw=2, label=f'Chosen $A_K$ = {A_K_use:.4f}')
plt.xlabel(r'$a_{\rm dimless}$')
plt.ylabel('$A_K$ from local slope')
plt.title('Local-slope extraction of $A_K$')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out1, dpi=160, bbox_inches='tight')
plt.close()

# Plot 2: energy and derivative
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
a_plot = np.logspace(np.log10(a_lo), np.log10(d_min_phys * 0.4), 350)
E_plot = np.array([
    E_K_phys(a, A_K_use, a_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
             d_min_phys, lam_K, p_exp)
    for a in a_plot
])
dE_plot = np.array([
    dE_K_da(a, A_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
            d_min_phys, lam_K, p_exp)
    for a in a_plot
])

finite_E = np.isfinite(E_plot)
finite_dE = np.isfinite(dE_plot)

axes[0].loglog(a_plot[finite_E] / r_c_canon, E_plot[finite_E], 'b-', lw=2)
axes[0].axvline(1.0, color='red', ls='--', lw=1.5, label='$r_c$ canon')
if np.isfinite(a_star):
    axes[0].axvline(a_star / r_c_canon, color='green', ls=':', lw=2, label='$a^*$')
axes[0].set_xlabel('a / r_c_canon')
axes[0].set_ylabel('$E_K(a)$ [J]')
axes[0].set_title('Energy landscape')
axes[0].grid(True, alpha=0.3)
axes[0].legend()

axes[1].semilogx(a_plot[finite_dE] / r_c_canon, dE_plot[finite_dE], 'b-', lw=2)
axes[1].axhline(0.0, color='k', lw=1)
axes[1].axvline(1.0, color='red', ls='--', lw=1.5, label='$r_c$ canon')
if np.isfinite(a_star):
    axes[1].axvline(a_star / r_c_canon, color='green', ls=':', lw=2, label='$a^*$')
axes[1].set_xlabel('a / r_c_canon')
axes[1].set_ylabel('$dE/da$ [J/m]')
axes[1].set_title('Stationarity condition')
axes[1].grid(True, alpha=0.3)
axes[1].legend()

plt.tight_layout()
plt.savefig(out2, dpi=160, bbox_inches='tight')
plt.close()

# Plot 3: Gamma_0 scan
plt.figure(figsize=(8, 5))
plt.loglog(Gamma_scan, a_star_scan / r_c_canon, 'o-', lw=1.7, ms=4, label='a0 / r_c_canon')
plt.axhline(1.0, color='red', ls='--', lw=1.5, label='a = r_c_canon')
plt.xlabel(r'$\Gamma_0$ [m$^2$/s]')
plt.ylabel('$a_0/r_c^{canon}$')
plt.title(r'Independent $\Gamma_0$ scan (no-contact baseline)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out3, dpi=160, bbox_inches='tight')
plt.close()

print("Saved files:")
print(f"  {out1}")
print(f"  {out2}")
print(f"  {out3}")
print(f"  /mnt/data/sst_trefoil_stability_patched.py")
