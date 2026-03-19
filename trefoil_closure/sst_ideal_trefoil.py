"""
SST Optie B — Ideale Trefoil (Gilbert database, Id=3:1:1)
==========================================================
Gebruikt de Fourier-coëfficiënten van de ideale trefoil uit:
  Gilbert, B. (2016). Database of Ideal Knots 3-10 crossings.
  L = 16.371637, D = 1.000000  =>  ropelength = L/D = 16.37

Representatie:
  X(t) = sum_k [ A_k * cos(2*pi*k*t) + B_k * sin(2*pi*k*t) ],  t in [0,1)

Vergelijking met torus-trefoil:
  - Torus: L_K_dimless ~ 31.9  (overkritisch, te lang)
  - Ideaal: L_K_dimless = 16.37  (minieme ropelength)

Verwachting: hogere zelfinductie per eenheid lengte => hogere A_K
=> a* dichter bij r_c of exacte sluiting.
"""

import numpy as np
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ─────────────────────────────────────────────────────────────
# 1. SST primitieven
# ─────────────────────────────────────────────────────────────
r_c_canon     = 1.40897017e-15    # m  (vergelijkingsdoel)
v_swirl       = 1.09384563e6      # m/s
rho_f         = 7.0e-7            # kg/m³
c_exact       = 299792458.0       # m/s
Gamma_0_input = 9.68361918e-9     # m²/s  (onafhankelijke invoer)

# ─────────────────────────────────────────────────────────────
# 2. Fourier-coëfficiënten ideale trefoil (Gilbert Id=3:1:1)
# ─────────────────────────────────────────────────────────────
# Formaat: (k, Ax, Ay, Az, Bx, By, Bz)
ideal_trefoil_coeffs = [
    (  1,  0.374139,  0.000000,  0.000000,  0.000000,  0.373928,  0.000000),
    (  2,  0.824246,  0.750260,  0.000352,  0.750450, -0.823952, -0.001991),
    (  3,  0.000257, -0.000932,  0.352397, -0.000770,  0.000726, -0.386764),
    (  4,  0.011652, -0.010656,  0.000743,  0.010739,  0.011613, -0.000230),
    (  5,  0.010504,  0.110306,  0.000199,  0.110745, -0.010366, -0.000235),
    (  6,  0.000015, -0.000006, -0.047465, -0.000050, -0.000001,  0.004595),
    (  7, -0.000292,  0.002417, -0.000008, -0.002529, -0.000255, -0.000009),
    (  8,  0.016487, -0.021784,  0.000041, -0.021922, -0.016421, -0.000044),
    (  9, -0.000029, -0.000018,  0.011178,  0.000049,  0.000041,  0.008414),
    ( 10, -0.000216, -0.000290, -0.000018,  0.000311, -0.000197, -0.000044),
    ( 11, -0.011727,  0.002184,  0.000007,  0.002202,  0.011682,  0.000020),
    ( 12,  0.000026,  0.000019, -0.001308, -0.000004, -0.000019, -0.007039),
    ( 13,  0.000325,  0.000055, -0.000009, -0.000059,  0.000289,  0.000024),
    ( 14,  0.005213,  0.003201,  0.000001,  0.003210, -0.005188,  0.000010),
    ( 15, -0.000015, -0.000016, -0.001917, -0.000017,  0.000001,  0.003121),
    ( 16, -0.000136,  0.000062,  0.000019, -0.000075, -0.000112, -0.000007),
    ( 17, -0.000995, -0.003463, -0.000001, -0.003474,  0.000988, -0.000015),
    ( 18,  0.000003,  0.000008,  0.002178,  0.000019,  0.000008, -0.000615),
    ( 19,  0.000033, -0.000094, -0.000016,  0.000113,  0.000028, -0.000004),
    ( 20, -0.000999,  0.002013, -0.000000,  0.002019,  0.000998,  0.000000),
    ( 21,  0.000004,  0.000001, -0.001270, -0.000013, -0.000012, -0.000626),
    ( 22,  0.000034,  0.000060,  0.000009, -0.000072,  0.000026,  0.000010),
    ( 23,  0.001383, -0.000539,  0.000002, -0.000540, -0.001382,  0.000004),
    ( 24, -0.000005, -0.000011,  0.000344,  0.000009,  0.000007,  0.000890),
    ( 25, -0.000057, -0.000025,  0.000001,  0.000019, -0.000048, -0.000008),
    ( 26, -0.000931, -0.000356, -0.000000, -0.000357,  0.000931, -0.000005),
    ( 27,  0.000006,  0.000009,  0.000228, -0.000002, -0.000000, -0.000597),
    ( 28,  0.000040, -0.000007, -0.000004,  0.000019,  0.000036,  0.000004),
    ( 29,  0.000308,  0.000611,  0.000001,  0.000611, -0.000307,  0.000007),
    ( 30,  0.000002,  0.000001, -0.000391, -0.000006,  0.000001,  0.000195),
]

def eval_ideal_trefoil(t_arr, coeffs):
    """
    Evalueer de Fourier-reeks op t_arr (shape N).
    Returns X shape (N,3).
    """
    X = np.zeros((len(t_arr), 3))
    for (k, Ax, Ay, Az, Bx, By, Bz) in coeffs:
        phase = 2 * np.pi * k * t_arr
        X[:, 0] += Ax * np.cos(phase) + Bx * np.sin(phase)
        X[:, 1] += Ay * np.cos(phase) + By * np.sin(phase)
        X[:, 2] += Az * np.cos(phase) + Bz * np.sin(phase)
    return X

def eval_ideal_trefoil_deriv(t_arr, coeffs):
    """dX/dt — analytische afgeleide."""
    dX = np.zeros((len(t_arr), 3))
    for (k, Ax, Ay, Az, Bx, By, Bz) in coeffs:
        phase = 2 * np.pi * k * t_arr
        w = 2 * np.pi * k
        dX[:, 0] += w * (-Ax * np.sin(phase) + Bx * np.cos(phase))
        dX[:, 1] += w * (-Ay * np.sin(phase) + By * np.cos(phase))
        dX[:, 2] += w * (-Az * np.sin(phase) + Bz * np.cos(phase))
    return dX

# ─────────────────────────────────────────────────────────────
# 3. Geometrie berekenen
# ─────────────────────────────────────────────────────────────
N_pts = 4000
t_arr = np.linspace(0, 1, N_pts, endpoint=False)

pts      = eval_ideal_trefoil(t_arr, ideal_trefoil_coeffs)
dpts_dt  = eval_ideal_trefoil_deriv(t_arr, ideal_trefoil_coeffs)

# Arc-length element: ds = |dX/dt| * dt
dt = 1.0 / N_pts
ds_arr = np.linalg.norm(dpts_dt, axis=1) * dt

# Tangent unit vectors
tangents = dpts_dt / np.linalg.norm(dpts_dt, axis=1, keepdims=True)

# Total arc-length L_K
L_K_dimless = np.sum(ds_arr)

# Segment chord lengths (for d_min estimate)
diffs = np.roll(pts, -1, axis=0) - pts
chord_lengths = np.linalg.norm(diffs, axis=1)

# Minimum self-distance (coarse grid)
step = max(1, N_pts // 300)
pts_c = pts[::step]
n_c   = len(pts_c)
excl  = max(5, n_c // 15)
d_min = np.inf
for i in range(n_c):
    for j in range(i + excl, n_c - excl):
        d = np.linalg.norm(pts_c[i] - pts_c[j])
        if d < d_min:
            d_min = d

# Ropelength check: L/D, D=1 by construction
print("=" * 65)
print("IDEALE TREFOIL GEOMETRIE (Gilbert Id=3:1:1)")
print("=" * 65)
print(f"  N_pts           = {N_pts}")
print(f"  L_K (dimless)   = {L_K_dimless:.6f}   (Gilbert: 16.371637)")
print(f"  d_min (dimless) = {d_min:.6f}   (tube diameter D=1 => d_min~1)")
print(f"  Ropelength L/D  = {L_K_dimless / 1.0:.4f}   (literatuur: ~16.37)")
print()

# Vergelijking met torus-trefoil
print(f"  Torus-trefoil L_K  ~ 31.9   (factor {31.9/L_K_dimless:.2f}x langer)")
print(f"  => Ideale trefoil heeft hogere zelfinductie per lengte-eenheid")
print()

# ─────────────────────────────────────────────────────────────
# 4. Biot-Savart zelfinductie vs cutoff a
# ─────────────────────────────────────────────────────────────
xi = 1.0

def compute_E_BS_norm_ideal(a_dimless, pts, tangents, ds_arr, xi=1.0):
    """E_BS / (rho_f * Gamma_0^2) voor ideale trefoil."""
    delta = xi * a_dimless
    N = len(pts)
    total = 0.0
    for i in range(N):
        diff = pts - pts[i]
        dist = np.linalg.norm(diff, axis=1)
        mask = (dist > delta) & (np.arange(N) != i)
        if not np.any(mask):
            continue
        dot_tt  = tangents[mask] @ tangents[i]
        integrand = dot_tt / dist[mask]
        total += np.sum(integrand * ds_arr[mask]) * ds_arr[i]
    return total / (8 * np.pi)

# Scan bereik: van 3x mediane ds tot 0.35 * d_min
ds_med  = np.median(ds_arr)
a_lo_d  = max(3 * ds_med, d_min * 5e-4)
a_hi_d  = d_min * 0.35
a_scan  = np.logspace(np.log10(a_lo_d), np.log10(a_hi_d), 22)

print("Berekenen E_BS_norm(a)  [~1 minuut]...")
E_BS_vals = []
for a_d in a_scan:
    e = compute_E_BS_norm_ideal(a_d, pts, tangents, ds_arr, xi)
    E_BS_vals.append(e)
    print(f"  a={a_d:.5e}  E_BS={e:.6f}")
E_BS_vals = np.array(E_BS_vals)
print()

# ─────────────────────────────────────────────────────────────
# 5. A_K extractie — lokale helling
# ─────────────────────────────────────────────────────────────
x_scan = -np.log(a_scan)
y_scan = E_BS_vals / L_K_dimless

x_mid = 0.5 * (x_scan[:-1] + x_scan[1:])
a_mid = np.sqrt(a_scan[:-1] * a_scan[1:])
A_local = np.diff(y_scan) / np.diff(x_scan)

rel_dE = np.abs(np.diff(E_BS_vals)) / np.maximum(np.abs(E_BS_vals[:-1]), 1e-300)
plateau_mask = (A_local > 0) & (rel_dE > 1e-4) & (a_mid < 0.12 * d_min)

if np.any(plateau_mask):
    A_K_plateau = np.median(A_local[plateau_mask])
    A_K_spread  = np.std(A_local[plateau_mask])
    method = "lokale helling (plateau)"
else:
    coeffs_fit = np.polyfit(x_scan, y_scan, 1)
    A_K_plateau = coeffs_fit[0]
    A_K_spread  = np.nan
    method = "globale fit (fallback)"

# Globale fit ook voor referentie
coeffs_global = np.polyfit(x_scan, y_scan, 1)
A_K_global    = coeffs_global[0]
a_K_global    = coeffs_global[1] - A_K_global * np.log(L_K_dimless)

# a_K bepalen via ankerpunt
if np.any(plateau_mask):
    idx_ref = np.where(plateau_mask)[0][len(np.where(plateau_mask)[0]) // 2]
    y_ref   = 0.5 * (y_scan[idx_ref] + y_scan[idx_ref+1])
    a_K_use = y_ref - A_K_plateau * np.log(L_K_dimless / a_mid[idx_ref])
else:
    a_K_use = a_K_global

A_K_use = A_K_plateau

print("A_K extractie:")
print(f"  methode          = {method}")
print(f"  A_K (plateau)    = {A_K_use:.8f}  ± {A_K_spread:.8f}")
print(f"  A_K (globaal)    = {A_K_global:.8f}")
print(f"  A_K vereist 1/4π = {1/(4*np.pi):.8f}")
print(f"  A_K / A_req      = {A_K_use / (1/(4*np.pi)):.6f}")
print()

# ─────────────────────────────────────────────────────────────
# 6. Fysische schaling & energiefunctionaal
# ─────────────────────────────────────────────────────────────
L_natural  = Gamma_0_input / v_swirl
L_K_phys   = L_K_dimless * L_natural
d_min_phys = d_min * L_natural

print("Fysische schaling:")
print(f"  L_natural  = {L_natural:.6e} m  (= Gamma_0/v_swirl)")
print(f"  L_K_phys   = {L_K_phys:.6e} m")
print(f"  d_min_phys = {d_min_phys:.6e} m")
print()

lam_K = 0.01
p_exp = 2

def dE_K_da(a, A_K, L_K_phys, Gamma_0, rho_f, v_swirl, d_min_phys, lam_K, p_exp):
    if a <= 0 or 2*a >= d_min_phys:
        return np.nan
    dE_BS   = -rho_f * Gamma_0**2 * L_K_phys * A_K / a
    dE_core =  np.pi * rho_f * v_swirl**2 * a * L_K_phys
    xc      = 2*a / (d_min_phys - 2*a)
    dx_da   = 2*d_min_phys / (d_min_phys - 2*a)**2
    dE_cont = lam_K * rho_f * Gamma_0**2 * L_K_phys * p_exp * xc**(p_exp-1) * dx_da
    return dE_BS + dE_core + dE_cont

def E_K_phys(a, A_K, a_K, L_K_phys, Gamma_0, rho_f, v_swirl, d_min_phys, lam_K, p_exp):
    if a <= 0 or 2*a >= d_min_phys:
        return np.inf
    E_BS   = rho_f * Gamma_0**2 * L_K_phys * (A_K * np.log(L_K_phys/a) + a_K)
    E_core = (np.pi/2) * rho_f * v_swirl**2 * a**2 * L_K_phys
    xc = 2*a / (d_min_phys - 2*a)
    E_cont = lam_K * rho_f * Gamma_0**2 * L_K_phys * xc**p_exp
    return E_BS + E_core + E_cont

# Analytisch minimum (geen contact)
a0 = np.sqrt(A_K_use / np.pi) * Gamma_0_input / v_swirl

# Stationair punt zoeken
a_lo_p = max(d_min_phys * 1e-7, L_natural * 1e-8)
a_hi_p = d_min_phys * 0.49
a_vals = np.logspace(np.log10(a_lo_p), np.log10(a_hi_p), 800)
dE_vals = np.array([dE_K_da(a, A_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
                             d_min_phys, lam_K, p_exp) for a in a_vals])

sign_ch = np.where(np.diff(np.sign(dE_vals)))[0]
a_star  = np.nan
is_min  = False

if len(sign_ch) > 0:
    idx = sign_ch[0]
    a_star = brentq(dE_K_da, a_vals[idx], a_vals[idx+1],
                    args=(A_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
                          d_min_phys, lam_K, p_exp))
    h = max(a_star * 1e-6, 1e-30)
    d2E = (dE_K_da(a_star+h, A_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
                   d_min_phys, lam_K, p_exp) -
           dE_K_da(a_star-h, A_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
                   d_min_phys, lam_K, p_exp)) / (2*h)
    is_min = d2E > 0
else:
    valid = np.isfinite(dE_vals)
    if np.any(valid):
        a_star = a_vals[valid][np.argmin(np.abs(dE_vals[valid]))]

chi_eff    = a_star * v_swirl / Gamma_0_input if np.isfinite(a_star) else np.nan
chi_req    = 1 / (2 * np.pi)
alpha_SST  = 2 * v_swirl / c_exact
Gamma_req  = r_c_canon * v_swirl / chi_eff if np.isfinite(chi_eff) else np.nan

# ─────────────────────────────────────────────────────────────
# 7. Resultaten
# ─────────────────────────────────────────────────────────────
print("=" * 65)
print("RESULTATEN — IDEALE TREFOIL")
print("=" * 65)
print(f"\n  A_K_use          = {A_K_use:.8f}")
print(f"  A_K_req (1/4π)   = {1/(4*np.pi):.8f}")
print(f"  A_K / A_req      = {A_K_use/(1/(4*np.pi)):.6f}")
print(f"\n  a0 (geen contact)= {a0:.8e} m")
print(f"  a* (vol model)   = {a_star:.8e} m")
print(f"  r_c_canon        = {r_c_canon:.8e} m")
print(f"  a*/r_c           = {a_star/r_c_canon:.8f}")
print(f"  is minimum       = {is_min}")
print(f"\n  chi_eff          = {chi_eff:.10f}")
print(f"  chi_req = 1/(2π) = {chi_req:.10f}")
print(f"  chi_eff/chi_req  = {chi_eff/chi_req:.8f}")
print(f"\n  Gamma_req (voor a*=r_c) = {Gamma_req:.8e} m²/s")
print(f"  Gamma_0_input           = {Gamma_0_input:.8e} m²/s")
print(f"  Gamma_req/Gamma_0       = {Gamma_req/Gamma_0_input:.8f}")
print(f"\n  alpha_SST^-1     = {1/alpha_SST:.9f}")
print(f"  NIST doelwaarde  = 137.035999177")

if np.isfinite(a_star):
    ratio = a_star / r_c_canon
    log_gap = np.log10(ratio)
    print(f"\n  log10(a*/r_c)    = {log_gap:.5f}")
    if abs(log_gap) < 0.02:
        print("  VERDICT: ✓✓ SLUITING  a* = r_c binnen 5%")
    elif abs(log_gap) < 0.05:
        print("  VERDICT: ✓  a* ≈ r_c binnen ~12%")
    elif abs(log_gap) < 0.1:
        print("  VERDICT: ~  a* binnen factor 1.25 van r_c")
    else:
        print(f"  VERDICT: ✗  gat = factor {10**abs(log_gap):.3f}")

# Vergelijking ideaal vs torus
print("\n" + "-"*65)
print("VERGELIJKING: Ideale trefoil vs Torus-trefoil")
print("-"*65)
print(f"  L_K ideaal    = {L_K_dimless:.4f}")
print(f"  L_K torus     ~ 31.90  (factor {31.90/L_K_dimless:.3f}x)")
print(f"  A_K ideaal    = {A_K_use:.6f}")
print(f"  A_K req       = {1/(4*np.pi):.6f}")
print(f"  a*/r_c ideaal = {a_star/r_c_canon:.6f}")
print(f"  a*/r_c torus  ~ 0.993  (uit vorige run)")

# ─────────────────────────────────────────────────────────────
# 8. Visualisatie
# ─────────────────────────────────────────────────────────────

# Plot 1: 3D knoop
fig = plt.figure(figsize=(7, 6))
ax3d = fig.add_subplot(111, projection='3d')
ax3d.plot(pts[:, 0], pts[:, 1], pts[:, 2], 'b-', lw=1.5)
ax3d.set_title('Ideale trefoil (Gilbert Id=3:1:1)\nL=16.37, D=1', fontsize=11)
ax3d.set_xlabel('x'); ax3d.set_ylabel('y'); ax3d.set_zlabel('z')
plt.tight_layout()
plt.savefig('./ideal_trefoil_3d.png', dpi=150, bbox_inches='tight')
plt.close()

# Plot 2: E_BS en lokale helling
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].semilogx(a_scan, E_BS_vals / L_K_dimless, 'bo-', ms=4, lw=1.5,
                 label='$E_{BS}/L_K$')
axes[0].set_xlabel('$a$ (dimless)', fontsize=12)
axes[0].set_ylabel('$E_{BS}/L_K$', fontsize=12)
axes[0].set_title('Biot-Savart zelfinductie', fontsize=12)
axes[0].grid(True, alpha=0.3); axes[0].legend()

axes[1].semilogx(a_mid, A_local, 'go-', ms=4, lw=1.5, label='Lokale helling')
if np.any(plateau_mask):
    axes[1].semilogx(a_mid[plateau_mask], A_local[plateau_mask],
                     'ro', ms=6, label='Plateau')
axes[1].axhline(1/(4*np.pi), color='green', ls='--', lw=2,
                label=f'1/(4π)={1/(4*np.pi):.4f}')
axes[1].axhline(A_K_use, color='orange', ls='-.', lw=1.5,
                label=f'A_K={A_K_use:.4f}')
axes[1].set_xlabel('$a$ (dimless)', fontsize=12)
axes[1].set_ylabel('$A_K$ lokale helling', fontsize=12)
axes[1].set_title('A_K extractie — ideale trefoil', fontsize=12)
axes[1].grid(True, alpha=0.3); axes[1].legend(fontsize=9)
plt.tight_layout()
plt.savefig('./ideal_trefoil_AK.png', dpi=150, bbox_inches='tight')
plt.close()

# Plot 3: energie en afgeleide
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
a_plot = np.logspace(np.log10(a_lo_p), np.log10(d_min_phys*0.4), 400)
E_plot  = [E_K_phys(a, A_K_use, a_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
                    d_min_phys, lam_K, p_exp) for a in a_plot]
dE_plot = [dE_K_da(a, A_K_use, L_K_phys, Gamma_0_input, rho_f, v_swirl,
                   d_min_phys, lam_K, p_exp) for a in a_plot]
E_plot  = np.array(E_plot)
dE_plot = np.array(dE_plot)
fin_E   = np.isfinite(E_plot)
fin_dE  = np.isfinite(dE_plot)

axes[0].loglog(a_plot[fin_E]/r_c_canon, E_plot[fin_E], 'b-', lw=2)
axes[0].axvline(1.0, color='red',   ls='--', lw=1.5, label='$r_c$ canon')
if np.isfinite(a_star):
    axes[0].axvline(a_star/r_c_canon, color='green', ls=':', lw=2,
                    label=f'$a^*$ = {a_star/r_c_canon:.4f}$r_c$')
axes[0].set_xlabel('$a/r_c$', fontsize=12); axes[0].set_ylabel('$E_K$ [J]', fontsize=12)
axes[0].set_title('Energielandschap — ideale trefoil', fontsize=12)
axes[0].legend(fontsize=9); axes[0].grid(True, alpha=0.3)

axes[1].semilogx(a_plot[fin_dE]/r_c_canon, dE_plot[fin_dE], 'b-', lw=2)
axes[1].axhline(0, color='k', lw=1)
axes[1].axvline(1.0, color='red',   ls='--', lw=1.5, label='$r_c$ canon')
if np.isfinite(a_star):
    axes[1].axvline(a_star/r_c_canon, color='green', ls=':', lw=2,
                    label=f'$a^*$ = {a_star/r_c_canon:.4f}$r_c$')
axes[1].set_xlabel('$a/r_c$', fontsize=12); axes[1].set_ylabel('$dE/da$', fontsize=12)
axes[1].set_title('Stationariteitsconditie', fontsize=12)
axes[1].legend(fontsize=9); axes[1].grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('./ideal_trefoil_energy.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nPlots opgeslagen in ./")
print("\nScript klaar.")