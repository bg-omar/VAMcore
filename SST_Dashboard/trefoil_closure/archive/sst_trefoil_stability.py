"""
SST Trefoil Vortex Stability Analysis
======================================
Computes the stationary core radius a* from the energy functional:

    E_K(a) = rho_f * Gamma_0^2 * L_K * [A_K * ln(L_K/a) + a_K]   (Biot-Savart)
           + (pi/2) * rho_f * v_swirl^2 * a^2 * L_K               (core kinetic)
           + E_contact(a)                                           (topological barrier)

All terms use rho_f only (NOT rho_core) for internal consistency.

Goal: find a* such that dE_K/da = 0 and d²E_K/da² > 0
      then compare a* to r_c_canon = 1.40897017e-15 m

Reference values (SST canon):
    r_c    = 1.40897017e-15 m
    v_swirl = 1.09384563e6 m/s
    rho_f  = 7.0e-7 kg/m³
    Gamma_0 = 2*pi*r_c*v_swirl  (derived, NOT used as independent input)
"""

import numpy as np
from scipy.integrate import dblquad
from scipy.optimize import brentq, minimize_scalar
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# 1. SST canonical constants (primitives)
# ─────────────────────────────────────────────────────────────
r_c_canon  = 1.40897017e-15   # m  — target value
v_swirl    = 1.09384563e6     # m/s — primitive
rho_f      = 7.0e-7           # kg/m³ — primitive
rho_core   = 3.8934358266918687e18  # kg/m³ — mass-equivalent (NOT used in E_K)

# Derived circulation quantum (for reference / sanity check only)
Gamma_0_canon = 2 * np.pi * r_c_canon * v_swirl
print(f"Canonical values:")
print(f"  r_c        = {r_c_canon:.6e} m")
print(f"  v_swirl    = {v_swirl:.6e} m/s")
print(f"  rho_f      = {rho_f:.3e} kg/m³")
print(f"  rho_core   = {rho_core:.6e} kg/m³  (reference only, not in E_K)")
print(f"  Gamma_0    = {Gamma_0_canon:.6e} m²/s  (derived, sanity check)")
print()

# We treat Gamma_0 as an independent primitive in the script.
# The key test: does a* come out equal to r_c_canon?
Gamma_0 = Gamma_0_canon  # for first run; can be varied

# ─────────────────────────────────────────────────────────────
# 2. Torus-trefoil centerline parametrisation
#    X(theta) = ((R_t + r_t*cos(3*theta))*cos(2*theta),
#                (R_t + r_t*cos(3*theta))*sin(2*theta),
#                r_t * sin(3*theta))
#    p=2, q=3 torus knot (standard trefoil)
# ─────────────────────────────────────────────────────────────
R_t = 2.0   # dimensionless torus major radius
r_t = 1.0   # dimensionless torus minor radius  (ratio R_t/r_t = 2 is typical)
N   = 2000  # number of discretisation points

def trefoil_points(N, R_t=2.0, r_t=1.0):
    theta = np.linspace(0, 2*np.pi, N, endpoint=False)
    x = (R_t + r_t * np.cos(3*theta)) * np.cos(2*theta)
    y = (R_t + r_t * np.cos(3*theta)) * np.sin(2*theta)
    z = r_t * np.sin(3*theta)
    return np.stack([x, y, z], axis=1)   # shape (N, 3)

pts = trefoil_points(N, R_t, r_t)

# Centerline arc-length L_K (in dimensionless units)
diffs = np.roll(pts, -1, axis=0) - pts
seg_lengths = np.linalg.norm(diffs, axis=1)
L_K_dimless = np.sum(seg_lengths)

# Tangent vectors (unit)
tangents = diffs / seg_lengths[:, None]

print(f"Trefoil geometry (dimensionless, R_t={R_t}, r_t={r_t}):")
print(f"  N points  = {N}")
print(f"  L_K       = {L_K_dimless:.6f}  (dimensionless arc length)")

# Minimum self-distance d_min (excluding adjacent segments)
# Use a coarser grid for speed
step = max(1, N // 200)
pts_coarse = pts[::step]
n_c = len(pts_coarse)
exclude = max(3, n_c // 20)   # exclude neighbours to avoid trivial minimum

d_min = np.inf
for i in range(n_c):
    for j in range(i + exclude, n_c - exclude):
        d = np.linalg.norm(pts_coarse[i] - pts_coarse[j])
        if d < d_min:
            d_min = d

print(f"  d_min     = {d_min:.6f}  (dimensionless minimum self-distance)")
print()

# ─────────────────────────────────────────────────────────────
# 3. Compute A_K from Biot-Savart self-energy vs ln(a)
#    E_BS(a) / (rho_f * Gamma_0^2 * L_K) = A_K * ln(L_K/a) + a_K
#
#    Discrete regularised form:
#    E_BS(a) = (rho_f * Gamma_0^2) / (8*pi) * sum_{i≠j, |r_ij|>delta(a)}
#              [ t_i . t_j / |X_i - X_j| ] * ds_i * ds_j
#    with delta(a) = xi * a  (xi ~ 1)
#
#    In dimensionless units: replace a → a_dimless = a / L_scale
#    where L_scale is the physical length per dimensionless unit.
#    Since we need A_K dimensionless, we compute:
#    E_BS_norm(a_dimless) = E_BS / (rho_f * Gamma_0^2)
#    = (1/8pi) * sum t_i.t_j / |X_i-X_j| * ds_i * ds_j  [for |X_i-X_j| > delta]
# ─────────────────────────────────────────────────────────────

xi = 1.0   # cutoff proportionality constant

def compute_E_BS_norm(a_dimless, pts, tangents, seg_lengths, xi=1.0):
    """
    Normalised Biot-Savart energy: E_BS / (rho_f * Gamma_0^2)
    a_dimless: core radius in dimensionless units (same scale as pts)
    """
    delta = xi * a_dimless
    N = len(pts)
    total = 0.0
    for i in range(N):
        diff = pts - pts[i]          # (N,3)
        dist = np.linalg.norm(diff, axis=1)  # (N,)
        # exclude self and near-neighbours and pairs closer than delta
        mask = (dist > delta) & (np.arange(N) != i)
        if not np.any(mask):
            continue
        dot_tt = tangents[mask] @ tangents[i]   # t_j . t_i
        integrand = dot_tt / dist[mask]
        total += np.sum(integrand * seg_lengths[mask]) * seg_lengths[i]
    return total / (8 * np.pi)

# Scan over a range of a_dimless values to extract A_K
# a_dimless runs from very small up to d_min/2
a_scan = np.logspace(np.log10(d_min * 1e-4), np.log10(d_min * 0.4), 20)
print("Computing Biot-Savart energies for A_K extraction...")
print("(This may take ~30-60 seconds)")

E_BS_vals = []
for a_d in a_scan:
    e = compute_E_BS_norm(a_d, pts, tangents, seg_lengths, xi)
    E_BS_vals.append(e)
    print(f"  a_dimless = {a_d:.4e}  E_BS_norm = {e:.6f}")

E_BS_vals = np.array(E_BS_vals)

# Fit: E_BS_norm / L_K = A_K * ln(L_K / a) + a_K
#   => E_BS_norm / L_K = A_K * ln(L_K) - A_K * ln(a) + a_K
# Linear fit: y = E_BS_norm/L_K  vs  x = -ln(a_dimless)
# Slope = A_K,  intercept = A_K*ln(L_K) + a_K

x_fit = -np.log(a_scan)
y_fit = E_BS_vals / L_K_dimless

# Linear regression
coeffs = np.polyfit(x_fit, y_fit, 1)
A_K_fit = coeffs[0]
intercept = coeffs[1]
a_K_fit = intercept - A_K_fit * np.log(L_K_dimless)

print(f"\nBiot-Savart fit results:")
print(f"  A_K       = {A_K_fit:.6f}  (dimensionless)")
print(f"  a_K       = {a_K_fit:.6f}  (dimensionless constant)")
print(f"  Expected A_K for a*=r_c: A_K_req = 1/(4*pi) = {1/(4*np.pi):.6f}")
print()

# ─────────────────────────────────────────────────────────────
# 4. Full energy functional E_K(a) in physical units
#    using L_scale = r_c_canon (physical length per dimensionless unit)
#
#    Physical: a_phys = a_dimless * L_scale
#              L_K_phys = L_K_dimless * L_scale
#
#    E_K(a_phys) = rho_f * Gamma_0^2 * L_K_phys
#                  * [A_K * ln(L_K_phys / a_phys) + a_K]
#               + (pi/2) * rho_f * v_swirl^2 * a_phys^2 * L_K_phys
#               + E_contact(a_phys)
#
#    E_contact uses dimensionless d_min scaled to physical units.
# ─────────────────────────────────────────────────────────────

# We need a physical length scale to connect dimensionless to metres.
# The only natural scale from primitives (rho_f, Gamma_0, v_swirl) is:
#   L_natural = Gamma_0 / v_swirl  (= 2*pi*r_c_canon by construction)
L_natural = Gamma_0 / v_swirl   # = 2*pi*r_c_canon
print(f"Natural length scale:")
print(f"  L_natural = Gamma_0 / v_swirl = {L_natural:.6e} m")
print(f"  2*pi*r_c  = {2*np.pi*r_c_canon:.6e} m  (should match)")
print()

# Physical lengths
L_K_phys    = L_K_dimless * L_natural   # physical centerline length
d_min_phys  = d_min * L_natural         # physical minimum self-distance

print(f"Physical trefoil geometry:")
print(f"  L_K_phys  = {L_K_phys:.6e} m")
print(f"  d_min_phys= {d_min_phys:.6e} m")
print()

# Contact barrier parameters
lam_K = 0.01   # dimensionless strength (weak first test)
p_exp = 2      # power law exponent

def E_contact_phys(a, d_min_phys, lam_K, p_exp, rho_f, Gamma_0, L_K_phys):
    """Topological contact barrier energy."""
    if 2*a >= d_min_phys:
        return np.inf
    x = 2*a / (d_min_phys - 2*a)
    return lam_K * rho_f * Gamma_0**2 * L_K_phys * x**p_exp

def E_K_phys(a, A_K, a_K, L_K_phys, Gamma_0, rho_f, v_swirl,
             d_min_phys, lam_K=0.01, p_exp=2):
    """Total energy functional in physical units."""
    if a <= 0 or 2*a >= d_min_phys:
        return np.inf
    E_BS   = rho_f * Gamma_0**2 * L_K_phys * (A_K * np.log(L_K_phys/a) + a_K)
    E_core = (np.pi/2) * rho_f * v_swirl**2 * a**2 * L_K_phys
    E_cont = E_contact_phys(a, d_min_phys, lam_K, p_exp, rho_f, Gamma_0, L_K_phys)
    return E_BS + E_core + E_cont

def dE_K_da(a, A_K, L_K_phys, Gamma_0, rho_f, v_swirl,
            d_min_phys, lam_K=0.01, p_exp=2):
    """Analytical derivative dE_K/da."""
    if a <= 0 or 2*a >= d_min_phys:
        return np.nan
    dE_BS   = -rho_f * Gamma_0**2 * L_K_phys * A_K / a
    dE_core = np.pi * rho_f * v_swirl**2 * a * L_K_phys
    # contact derivative
    x = 2*a / (d_min_phys - 2*a)
    dx_da = 2*d_min_phys / (d_min_phys - 2*a)**2
    dE_cont = lam_K * rho_f * Gamma_0**2 * L_K_phys * p_exp * x**(p_exp-1) * dx_da
    return dE_BS + dE_core + dE_cont

# ─────────────────────────────────────────────────────────────
# 5. Find stationary point a* using fitted A_K
# ─────────────────────────────────────────────────────────────

# Scan dE/da to find sign change
a_lo = d_min_phys * 1e-6
a_hi = d_min_phys * 0.49

a_vals = np.logspace(np.log10(a_lo), np.log10(a_hi), 500)
dE_vals = np.array([dE_K_da(a, A_K_fit, L_K_phys, Gamma_0, rho_f, v_swirl,
                             d_min_phys, lam_K, p_exp) for a in a_vals])

# Find zero crossings
sign_changes = np.where(np.diff(np.sign(dE_vals)))[0]
print(f"Stationary point search:")
print(f"  Search range: [{a_lo:.3e}, {a_hi:.3e}] m")
print(f"  Sign changes found: {len(sign_changes)}")

a_star = None
if len(sign_changes) > 0:
    idx = sign_changes[0]
    try:
        a_star = brentq(dE_K_da, a_vals[idx], a_vals[idx+1],
                        args=(A_K_fit, L_K_phys, Gamma_0, rho_f, v_swirl,
                              d_min_phys, lam_K, p_exp))
        # Check it's a minimum
        h = a_star * 1e-6
        d2E = (dE_K_da(a_star+h, A_K_fit, L_K_phys, Gamma_0, rho_f, v_swirl,
                        d_min_phys, lam_K, p_exp) -
               dE_K_da(a_star-h, A_K_fit, L_K_phys, Gamma_0, rho_f, v_swirl,
                        d_min_phys, lam_K, p_exp)) / (2*h)
        is_minimum = d2E > 0
        print(f"\n  a* (stationary point) = {a_star:.6e} m")
        print(f"  d²E/da² > 0: {is_minimum}  (True = minimum)")
    except Exception as e:
        print(f"  Root finding failed: {e}")
else:
    # No zero crossing — find minimum numerically
    valid = np.isfinite(dE_vals)
    if np.any(valid):
        # Look for minimum of |dE/da|
        idx_min = np.argmin(np.abs(dE_vals[valid]))
        a_star_approx = a_vals[valid][idx_min]
        print(f"\n  No zero crossing found.")
        print(f"  Closest to stationary: a ~ {a_star_approx:.3e} m, dE/da = {dE_vals[valid][idx_min]:.3e}")
        a_star = a_star_approx

# ─────────────────────────────────────────────────────────────
# 6. Results and diagnostic
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("RESULTS SUMMARY")
print("="*60)
print(f"\nPrimitive inputs (no e, m_e, hbar, alpha, G):")
print(f"  rho_f     = {rho_f:.3e} kg/m³")
print(f"  Gamma_0   = {Gamma_0:.6e} m²/s")
print(f"  v_swirl   = {v_swirl:.6e} m/s")
print(f"\nDerived geometry (torus-trefoil, R_t={R_t}, r_t={r_t}):")
print(f"  L_K_phys  = {L_K_phys:.6e} m")
print(f"  d_min     = {d_min_phys:.6e} m")
print(f"  A_K (fit) = {A_K_fit:.6f}")
print(f"  a_K (fit) = {a_K_fit:.6f}")

print(f"\nA_K diagnostic:")
A_K_req_route2 = 1/(4*np.pi)
print(f"  A_K_fit           = {A_K_fit:.6f}")
print(f"  A_K_req (1/4pi)   = {A_K_req_route2:.6f}  (needed for a*=r_c with rho_f only)")
print(f"  Ratio A_K_fit / A_K_req = {A_K_fit / A_K_req_route2:.4f}")

if a_star is not None:
    ratio = a_star / r_c_canon
    print(f"\nStationary core radius:")
    print(f"  a*        = {a_star:.6e} m")
    print(f"  r_c_canon = {r_c_canon:.6e} m")
    print(f"  a*/r_c    = {ratio:.6f}")
    print(f"  log10(a*/r_c) = {np.log10(ratio):.3f}")

    if abs(np.log10(ratio)) < 0.1:
        print(f"\n  ✓ AGREEMENT: a* matches r_c within factor {10**abs(np.log10(ratio)):.2f}")
    elif abs(np.log10(ratio)) < 1:
        print(f"\n  ~ PARTIAL: a* within one order of magnitude of r_c")
    else:
        print(f"\n  ✗ MISMATCH: factor {ratio:.3e} — model needs adjustment")
        missing_factor = r_c_canon / a_star
        print(f"  Missing factor to close gap: {missing_factor:.4e}")
        print(f"  log10(missing) = {np.log10(abs(missing_factor)):.2f}")
        print(f"  alpha^-1 = 137.036  → log10 = {np.log10(137.036):.2f}")
        print(f"  alpha^-2 = 18790    → log10 = {np.log10(18790):.2f}")

# Check if alpha appears in the gap
if a_star is not None:
    alpha_SST = 2 * v_swirl / 3e8
    print(f"\nalpha_SST = 2*v_swirl/c = {alpha_SST:.9f}")
    print(f"alpha_SST^-1           = {1/alpha_SST:.6f}  (NIST: 137.035999177)")

# ─────────────────────────────────────────────────────────────
# 7. Analytical zero-contact result for reference
# ─────────────────────────────────────────────────────────────
print("\n" + "-"*60)
print("ANALYTICAL (no contact barrier):")
a_analytic = np.sqrt(A_K_fit / np.pi) * Gamma_0 / v_swirl
print(f"  a0 = sqrt(A_K/pi) * Gamma_0/v_swirl = {a_analytic:.6e} m")
print(f"  a0 / r_c = {a_analytic/r_c_canon:.6f}")
A_K_needed = np.pi * (r_c_canon * v_swirl / Gamma_0)**2
print(f"\n  A_K needed for a0=r_c: {A_K_needed:.6f} = 1/(4pi) = {1/(4*np.pi):.6f}")
print(f"  They agree: {abs(A_K_needed - 1/(4*np.pi)) < 1e-10}")

# ─────────────────────────────────────────────────────────────
# 8. Plot energy landscape
# ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Panel 1: E_K(a) landscape
a_plot = np.logspace(np.log10(a_lo*10), np.log10(d_min_phys*0.4), 300)
E_plot = [E_K_phys(a, A_K_fit, a_K_fit, L_K_phys, Gamma_0, rho_f, v_swirl,
                   d_min_phys, lam_K, p_exp) for a in a_plot]
E_plot = np.array(E_plot)

finite = np.isfinite(E_plot)
ax1 = axes[0]
ax1.loglog(a_plot[finite]/r_c_canon, E_plot[finite], 'b-', lw=2, label='$E_K(a)$')
ax1.axvline(1.0, color='red', ls='--', lw=1.5, label=f'$r_c$ (canon)')
if a_star is not None:
    ax1.axvline(a_star/r_c_canon, color='green', ls=':', lw=2, label=f'$a^*$')
ax1.set_xlabel('$a / r_c$', fontsize=13)
ax1.set_ylabel('$E_K(a)$ [J]', fontsize=13)
ax1.set_title('Energy functional $E_K(a)$', fontsize=13)
ax1.legend()
ax1.grid(True, alpha=0.3)

# Panel 2: dE/da (sign change = stationary point)
dE_plot = np.array([dE_K_da(a, A_K_fit, L_K_phys, Gamma_0, rho_f, v_swirl,
                             d_min_phys, lam_K, p_exp) for a in a_plot])
ax2 = axes[1]
valid = np.isfinite(dE_plot)
ax2.semilogx(a_plot[valid]/r_c_canon, dE_plot[valid], 'b-', lw=2)
ax2.axhline(0, color='k', lw=1)
ax2.axvline(1.0, color='red', ls='--', lw=1.5, label=f'$r_c$ (canon)')
if a_star is not None:
    ax2.axvline(a_star/r_c_canon, color='green', ls=':', lw=2, label=f'$a^*$')
ax2.set_xlabel('$a / r_c$', fontsize=13)
ax2.set_ylabel('$dE_K/da$ [J/m]', fontsize=13)
ax2.set_title('Derivative $dE_K/da$ — zero = stationary point', fontsize=13)
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/sst_trefoil_stability.png', dpi=150, bbox_inches='tight')
plt.close()

# ─────────────────────────────────────────────────────────────
# 9. Parameter sensitivity: A_K required vs ratio
# ─────────────────────────────────────────────────────────────
fig2, ax = plt.subplots(figsize=(8, 5))
A_K_range = np.logspace(-3, 1, 200)
a_star_range = np.sqrt(A_K_range / np.pi) * Gamma_0 / v_swirl
ratio_range = a_star_range / r_c_canon

ax.loglog(A_K_range, ratio_range, 'b-', lw=2)
ax.axhline(1.0, color='red', ls='--', lw=1.5, label='$a^* = r_c$')
ax.axvline(A_K_fit, color='orange', ls=':', lw=2, label=f'$A_K$ (fitted) = {A_K_fit:.4f}')
ax.axvline(1/(4*np.pi), color='green', ls='--', lw=1.5,
           label=f'$A_K = 1/4\\pi$ = {1/(4*np.pi):.4f}')
ax.set_xlabel('$A_K$ (Biot-Savart coefficient)', fontsize=12)
ax.set_ylabel('$a^* / r_c$', fontsize=12)
ax.set_title('Required $A_K$ for closure (no contact barrier)', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/sst_AK_sensitivity.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nPlots saved.")
print("\n" + "="*60)
print("DIAGNOSTIC CONCLUSION")
print("="*60)
print("""
The script tests whether a* = r_c_canon emerges from:
  E_K(a) = E_BS(a) + E_core(a) + E_contact(a)
with all terms using rho_f only (Route 2).

Key question: does A_K_fit ≈ 1/(4*pi) = 0.0796?

If yes  → the torus-trefoil geometry is consistent with r_c
          and Optie B is numerically plausible.

If no   → the gap is quantified: log10(A_K_fit / (1/4pi))
          tells you how much extra physics is needed.
          If the gap is ~log10(alpha^-1) ≈ 2.14,
          alpha is still hidden in the geometry.
""")
