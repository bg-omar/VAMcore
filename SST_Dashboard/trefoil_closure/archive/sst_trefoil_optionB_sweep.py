"""
SST Trefoil Option-B Sweep
==========================

Purpose
-------
1) Harder Option-B test:
   Treat Gamma_0 as an independent input and compute the dimensionless closure
   factor chi_eff = a* v_swirl / Gamma_0.
   Then infer the Gamma_0 required to reproduce the canonical r_c:
       Gamma_req = r_c_canon * v_swirl / chi_eff.
   This avoids feeding r_c into the algorithmic definition of Gamma_0.

2) Small parameter study:
   Sweep over
     - Gamma_0
     - trefoil geometry ratio R_t / r_t
     - Biot-Savart cutoff xi
     - contact barrier strength lam_K and exponent p_exp

Energy model (Route 2, rho_f only)
----------------------------------
E_K(a) = rho_f * Gamma_0^2 * L_K * [A_K * ln(L_K/a) + a_K]
       + (pi/2) * rho_f * v_swirl^2 * a^2 * L_K
       + E_contact(a)

Output
------
- CSV tables for the physics sweep and the contact-barrier study
- summary text file
- plots for closure and sensitivity
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Dict, Tuple, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import brentq

# -----------------------------------------------------------------------------
# Canonical comparison values (comparison only unless explicitly stated)
# -----------------------------------------------------------------------------
r_c_canon = 1.40897017e-15               # m
v_swirl   = 1.09384563e6                 # m/s
rho_f     = 7.0e-7                       # kg/m^3
rho_core  = 3.8934358266918687e18        # kg/m^3 (not used in Route 2)
c_exact   = 299_792_458.0                # m/s
chi_req   = 1.0 / (2.0 * np.pi)
A_req     = 1.0 / (4.0 * np.pi)
Gamma0_canon_numeric = 2.0 * np.pi * r_c_canon * v_swirl
alpha_sst = 2.0 * v_swirl / c_exact

OUTDIR = "/mnt/data/sst_optionB_outputs"
os.makedirs(OUTDIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Geometry and Biot-Savart helpers
# -----------------------------------------------------------------------------

def trefoil_points(N: int, R_t: float, r_t: float) -> np.ndarray:
    theta = np.linspace(0.0, 2.0 * np.pi, N, endpoint=False)
    x = (R_t + r_t * np.cos(3.0 * theta)) * np.cos(2.0 * theta)
    y = (R_t + r_t * np.cos(3.0 * theta)) * np.sin(2.0 * theta)
    z = r_t * np.sin(3.0 * theta)
    return np.stack([x, y, z], axis=1)


def coarse_min_self_distance(pts: np.ndarray, coarse_target: int = 160) -> float:
    N = len(pts)
    step = max(1, N // coarse_target)
    pts_c = pts[::step]
    n_c = len(pts_c)
    exclude = max(3, n_c // 20)
    d_min = np.inf
    for i in range(n_c):
        for j in range(i + exclude, n_c - exclude):
            d = np.linalg.norm(pts_c[i] - pts_c[j])
            if d < d_min:
                d_min = d
    return float(d_min)


@dataclass
class GeometryData:
    R_t: float
    r_t: float
    ratio: float
    N: int
    pts: np.ndarray
    seg_lengths: np.ndarray
    tangents: np.ndarray
    L_K_dimless: float
    d_min_dimless: float
    ds_median: float
    dist_matrix: np.ndarray
    dot_matrix: np.ndarray
    weight_matrix: np.ndarray
    valid_offdiag: np.ndarray


def build_geometry(N: int, ratio: float, r_t: float = 1.0) -> GeometryData:
    R_t = ratio * r_t
    pts = trefoil_points(N, R_t, r_t)
    diffs = np.roll(pts, -1, axis=0) - pts
    seg_lengths = np.linalg.norm(diffs, axis=1)
    tangents = diffs / seg_lengths[:, None]
    L_K_dimless = float(np.sum(seg_lengths))
    d_min_dimless = coarse_min_self_distance(pts)
    ds_median = float(np.median(seg_lengths))

    # pairwise matrices for fast repeated E_BS evaluation
    diff = pts[:, None, :] - pts[None, :, :]
    dist = np.linalg.norm(diff, axis=2)
    dot = tangents @ tangents.T
    weight = np.outer(seg_lengths, seg_lengths)
    offdiag = ~np.eye(N, dtype=bool)
    return GeometryData(
        R_t=R_t,
        r_t=r_t,
        ratio=ratio,
        N=N,
        pts=pts,
        seg_lengths=seg_lengths,
        tangents=tangents,
        L_K_dimless=L_K_dimless,
        d_min_dimless=d_min_dimless,
        ds_median=ds_median,
        dist_matrix=dist,
        dot_matrix=dot,
        weight_matrix=weight,
        valid_offdiag=offdiag,
    )


def compute_E_BS_norm_from_mats(a_dimless: float, xi: float, geom: GeometryData) -> float:
    delta = xi * a_dimless
    mask = (geom.dist_matrix > delta) & geom.valid_offdiag
    total = np.sum((geom.dot_matrix / np.where(mask, geom.dist_matrix, 1.0)) * geom.weight_matrix * mask)
    return float(total / (8.0 * np.pi))


def extract_AK_local(a_scan: np.ndarray, E_vals: np.ndarray, L_K_dimless: float, d_min: float):
    x = -np.log(a_scan)
    y = E_vals / L_K_dimless
    A_local = np.diff(y) / np.diff(x)
    a_mid = np.sqrt(a_scan[:-1] * a_scan[1:])
    rel_dE = np.abs(np.diff(E_vals)) / np.maximum(np.abs(E_vals[:-1]), 1e-300)

    # plateau selector: avoid mesh-flat UV region and avoid too-large a where asymptotics deteriorate
    plateau_mask = (A_local > 0.0) & (rel_dE > 1e-4) & (a_mid < 0.12 * d_min)
    if np.any(plateau_mask):
        A_vals = A_local[plateau_mask]
        A_K = float(np.median(A_vals))
        A_spread = float(np.std(A_vals))
        idxs = np.where(plateau_mask)[0]
        idx_ref = idxs[len(idxs) // 2]
        a_ref = a_mid[idx_ref]
        y_ref = 0.5 * (y[idx_ref] + y[idx_ref + 1])
        a_K = float(y_ref - A_K * np.log(L_K_dimless / a_ref))
        method = "local-plateau"
    else:
        coeffs = np.polyfit(x, y, 1)
        A_K = float(coeffs[0])
        intercept = float(coeffs[1])
        a_K = float(intercept - A_K * np.log(L_K_dimless))
        A_spread = float('nan')
        method = "global-fit-fallback"

    coeffs_global = np.polyfit(x, y, 1)
    A_global = float(coeffs_global[0])
    return {
        "A_K_use": A_K,
        "a_K_use": a_K,
        "A_K_spread": A_spread,
        "method": method,
        "A_K_global": A_global,
        "a_mid": a_mid,
        "A_local": A_local,
        "plateau_mask": plateau_mask,
        "x": x,
        "y": y,
    }


# -----------------------------------------------------------------------------
# Route-2 energy model in physical units
# -----------------------------------------------------------------------------

def E_contact_phys(a: float, d_min_phys: float, lam_K: float, p_exp: int,
                   rho_f: float, Gamma_0: float, L_K_phys: float) -> float:
    if a <= 0.0 or 2.0 * a >= d_min_phys:
        return np.inf
    x = 2.0 * a / (d_min_phys - 2.0 * a)
    return lam_K * rho_f * Gamma_0**2 * L_K_phys * x**p_exp


def dE_da(a: float, A_K: float, L_K_phys: float, Gamma_0: float, rho_f: float,
          v_swirl: float, d_min_phys: float, lam_K: float, p_exp: int) -> float:
    if a <= 0.0 or 2.0 * a >= d_min_phys:
        return np.nan
    dE_bs = -rho_f * Gamma_0**2 * L_K_phys * A_K / a
    dE_core = np.pi * rho_f * v_swirl**2 * a * L_K_phys
    x = 2.0 * a / (d_min_phys - 2.0 * a)
    dx_da = 2.0 * d_min_phys / (d_min_phys - 2.0 * a)**2
    dE_cont = lam_K * rho_f * Gamma_0**2 * L_K_phys * p_exp * x**(p_exp - 1) * dx_da
    return dE_bs + dE_core + dE_cont


def stationary_radius(A_K: float, L_K_phys: float, d_min_phys: float,
                      Gamma_0: float, rho_f: float, v_swirl: float,
                      lam_K: float, p_exp: int):
    a_lo = d_min_phys * 1e-6
    a_hi = d_min_phys * 0.49
    a_vals = np.logspace(np.log10(a_lo), np.log10(a_hi), 400)
    dE_vals = np.array([
        dE_da(a, A_K, L_K_phys, Gamma_0, rho_f, v_swirl, d_min_phys, lam_K, p_exp)
        for a in a_vals
    ])
    sign_changes = np.where(np.diff(np.sign(dE_vals)))[0]
    if len(sign_changes) > 0:
        idx = sign_changes[0]
        a_star = brentq(
            dE_da,
            a_vals[idx],
            a_vals[idx + 1],
            args=(A_K, L_K_phys, Gamma_0, rho_f, v_swirl, d_min_phys, lam_K, p_exp),
        )
        h = max(a_star * 1e-6, 1e-24)
        d2 = (
            dE_da(a_star + h, A_K, L_K_phys, Gamma_0, rho_f, v_swirl, d_min_phys, lam_K, p_exp)
            - dE_da(a_star - h, A_K, L_K_phys, Gamma_0, rho_f, v_swirl, d_min_phys, lam_K, p_exp)
        ) / (2.0 * h)
        return float(a_star), bool(d2 > 0.0), float(d2)
    idx = int(np.nanargmin(np.abs(dE_vals)))
    return float(a_vals[idx]), False, float('nan')


# -----------------------------------------------------------------------------
# Single-case runner
# -----------------------------------------------------------------------------

def run_case(geom: GeometryData, xi: float, Gamma_0: float, lam_K: float, p_exp: int,
             n_ascan: int = 18) -> Dict[str, float]:
    a_min = max(3.0 * geom.ds_median, geom.d_min_dimless * 1e-4)
    a_max = geom.d_min_dimless * 0.35
    a_scan = np.logspace(np.log10(a_min), np.log10(a_max), n_ascan)
    E_vals = np.array([compute_E_BS_norm_from_mats(a, xi, geom) for a in a_scan])
    fit = extract_AK_local(a_scan, E_vals, geom.L_K_dimless, geom.d_min_dimless)

    A_K = fit["A_K_use"]
    a_K = fit["a_K_use"]

    L_natural = Gamma_0 / v_swirl
    L_K_phys = geom.L_K_dimless * L_natural
    d_min_phys = geom.d_min_dimless * L_natural

    a0 = math.sqrt(A_K / np.pi) * Gamma_0 / v_swirl
    a_star, is_min, d2 = stationary_radius(A_K, L_K_phys, d_min_phys, Gamma_0, rho_f, v_swirl, lam_K, p_exp)

    chi_eff = a_star * v_swirl / Gamma_0
    gamma_required_for_rc = r_c_canon * v_swirl / chi_eff
    gamma_required_ratio = gamma_required_for_rc / Gamma0_canon_numeric

    # small barrier influence metric
    barrier_shift = (a_star / a0) - 1.0 if a0 > 0 else np.nan

    return {
        "ratio_R_over_r": geom.ratio,
        "R_t": geom.R_t,
        "r_t": geom.r_t,
        "N": geom.N,
        "L_K_dimless": geom.L_K_dimless,
        "d_min_dimless": geom.d_min_dimless,
        "xi": xi,
        "Gamma_0": Gamma_0,
        "lam_K": lam_K,
        "p_exp": p_exp,
        "A_K": A_K,
        "A_K_spread": fit["A_K_spread"],
        "A_K_global": fit["A_K_global"],
        "a_K": a_K,
        "A_over_Areq": A_K / A_req,
        "L_natural_m": L_natural,
        "L_K_phys_m": L_K_phys,
        "d_min_phys_m": d_min_phys,
        "a0_m": a0,
        "a_star_m": a_star,
        "is_minimum": is_min,
        "d2E": d2,
        "a_star_over_rc": a_star / r_c_canon,
        "chi_eff": chi_eff,
        "chi_eff_over_chireq": chi_eff / chi_req,
        "gamma_required_for_rc": gamma_required_for_rc,
        "gamma_required_ratio_vs_canonical": gamma_required_ratio,
        "barrier_shift_frac": barrier_shift,
        "A_method": fit["method"],
        "a_scan_min": a_scan.min(),
        "a_scan_max": a_scan.max(),
    }


# -----------------------------------------------------------------------------
# Sweeps
# -----------------------------------------------------------------------------
print("Building geometry cache...", flush=True)
geometry_ratios = [1.8, 2.0, 2.2, 2.5]
N_geom = 600
geom_cache = {ratio: build_geometry(N_geom, ratio) for ratio in geometry_ratios}
print("Geometry cache ready.\n", flush=True)

# Main physics sweep: Gamma_0, geometry ratio, xi with weak contact barrier
Gamma_multipliers = [0.8, 1.0, 1.2]
Gamma_values = [Gamma0_canon_numeric * m for m in Gamma_multipliers]
xis = [0.8, 1.0, 1.2]
lam_baseline = 0.01
p_baseline = 2

physics_rows: List[Dict[str, float]] = []
for ratio in geometry_ratios:
    geom = geom_cache[ratio]
    for xi in xis:
        for G in Gamma_values:
            physics_rows.append(run_case(geom, xi, G, lam_baseline, p_baseline))

physics_df = pd.DataFrame(physics_rows)
physics_csv = os.path.join(OUTDIR, "sst_optionB_physics_sweep.csv")
physics_df.to_csv(physics_csv, index=False)

# Contact-barrier study around the nominal geometry/cutoff/gamma
contact_rows: List[Dict[str, float]] = []
geom_nom = geom_cache[2.0]
for lam in [0.0, 0.005, 0.01, 0.05]:
    for pexp in [2, 4]:
        contact_rows.append(run_case(geom_nom, 1.0, Gamma0_canon_numeric, lam, pexp))

contact_df = pd.DataFrame(contact_rows)
contact_csv = os.path.join(OUTDIR, "sst_optionB_contact_study.csv")
contact_df.to_csv(contact_csv, index=False)

# -----------------------------------------------------------------------------
# Summary diagnostics
# -----------------------------------------------------------------------------
summary_lines = []
summary_lines.append("SST Option-B sweep summary")
summary_lines.append("=" * 70)
summary_lines.append(f"r_c_canon = {r_c_canon:.12e} m")
summary_lines.append(f"v_swirl   = {v_swirl:.12e} m/s")
summary_lines.append(f"rho_f     = {rho_f:.12e} kg/m^3")
summary_lines.append(f"Gamma0_canonical_numeric = {Gamma0_canon_numeric:.12e} m^2/s")
summary_lines.append(f"alpha_SST = {alpha_sst:.12e}")
summary_lines.append(f"alpha_SST^-1 = {1.0/alpha_sst:.12f}")
summary_lines.append("")

# Best closure cases by chi_eff and by a_star/rc
physics_df["closure_error_chi"] = np.abs(physics_df["chi_eff_over_chireq"] - 1.0)
physics_df["closure_error_a"] = np.abs(physics_df["a_star_over_rc"] - 1.0)

best_chi = physics_df.sort_values("closure_error_chi").iloc[0]
best_a = physics_df.sort_values("closure_error_a").iloc[0]
summary_lines.append("Best case by chi closure:")
summary_lines.append(best_chi.to_string())
summary_lines.append("")
summary_lines.append("Best case by a*/r_c closure:")
summary_lines.append(best_a.to_string())
summary_lines.append("")

# Nominal case summary
nom_mask = (
    np.abs(physics_df["ratio_R_over_r"] - 2.0) < 1e-12
    ) & (
    np.abs(physics_df["xi"] - 1.0) < 1e-12
    ) & (
    np.abs(physics_df["Gamma_0"] - Gamma0_canon_numeric) < 1e-18
)
nom = physics_df[nom_mask].iloc[0]
summary_lines.append("Nominal case (R/r=2.0, xi=1.0, Gamma0=canonical numeric value):")
summary_lines.append(nom.to_string())
summary_lines.append("")

summary_lines.append("Contact study:")
summary_lines.append(contact_df.to_string(index=False))
summary_lines.append("")

summary_path = os.path.join(OUTDIR, "sst_optionB_summary.txt")
with open(summary_path, "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))

# -----------------------------------------------------------------------------
# Plots
# -----------------------------------------------------------------------------
# 1) Heatmap of chi_eff/chi_req for nominal Gamma0 across geometry ratio and xi
nomG = Gamma0_canon_numeric
sub = physics_df[np.abs(physics_df["Gamma_0"] - nomG) < 1e-18].copy()
if len(sub) == 0:
    sub = physics_df.iloc[(physics_df["Gamma_0"] - nomG).abs().argsort()[:len(geometry_ratios)*len(xis)]].copy()
sub = sub.groupby(["ratio_R_over_r", "xi"], as_index=False)[["chi_eff_over_chireq", "A_over_Areq"]].mean()
pivot_chi = sub.pivot(index="ratio_R_over_r", columns="xi", values="chi_eff_over_chireq")
pivot_A = sub.pivot(index="ratio_R_over_r", columns="xi", values="A_over_Areq")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, piv, title in [
    (axes[0], pivot_chi, r"$\chi_{\rm eff}/\chi_{\rm req}$"),
    (axes[1], pivot_A, r"$A_K/A_{\rm req}$"),
]:
    im = ax.imshow(piv.values, origin="lower", aspect="auto")
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels([f"{c:.1f}" for c in piv.columns])
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels([f"{i:.1f}" for i in piv.index])
    ax.set_xlabel(r"cutoff $\xi$")
    ax.set_ylabel(r"geometry ratio $R_t/r_t$")
    ax.set_title(title)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            ax.text(j, i, f"{piv.values[i, j]:.3f}", ha="center", va="center", color="white", fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
plt.tight_layout()
plot1 = os.path.join(OUTDIR, "sst_optionB_heatmaps.png")
plt.savefig(plot1, dpi=160, bbox_inches="tight")
plt.close(fig)

# 2) Gamma sweep: a*/Gamma0 and chi_eff for nominal geometry/cutoff
sub_nom = physics_df[(np.abs(physics_df["ratio_R_over_r"] - 2.0) < 1e-12) & (np.abs(physics_df["xi"] - 1.0) < 1e-12)].copy()
sub_nom = sub_nom.sort_values("Gamma_0")
fig, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot(sub_nom["Gamma_0"], sub_nom["a_star_m"] / sub_nom["Gamma_0"], marker="o", label=r"$a^*/\Gamma_0$")
ax1.set_xlabel(r"$\Gamma_0$ [m$^2$/s]")
ax1.set_ylabel(r"$a^*/\Gamma_0$ [s/m]")
ax1.grid(True, alpha=0.3)
ax2 = ax1.twinx()
ax2.plot(sub_nom["Gamma_0"], sub_nom["chi_eff_over_chireq"], marker="s", color="tab:red", label=r"$\chi_{\rm eff}/\chi_{\rm req}$")
ax2.set_ylabel(r"$\chi_{\rm eff}/\chi_{\rm req}$")
ax2.axhline(1.0, color="tab:red", ls="--", lw=1)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")
plt.title("Gamma sweep at nominal geometry/cutoff")
plt.tight_layout()
plot2 = os.path.join(OUTDIR, "sst_optionB_gamma_sweep.png")
plt.savefig(plot2, dpi=160, bbox_inches="tight")
plt.close(fig)

# 3) Contact study plot
fig, ax = plt.subplots(figsize=(8, 5))
for pexp in sorted(contact_df["p_exp"].unique()):
    subc = contact_df[contact_df["p_exp"] == pexp].sort_values("lam_K")
    ax.plot(subc["lam_K"], subc["a_star_over_rc"], marker="o", label=fr"$p={pexp}$")
ax.axhline(1.0, color="k", ls="--", lw=1)
ax.set_xlabel(r"contact strength $\lambda_K$")
ax.set_ylabel(r"$a^*/r_c$")
ax.set_title("Contact-barrier sensitivity (nominal geometry/cutoff)")
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plot3 = os.path.join(OUTDIR, "sst_optionB_contact_sensitivity.png")
plt.savefig(plot3, dpi=160, bbox_inches="tight")
plt.close(fig)

# 4) Local-slope diagnostic plot for nominal geometry/cutoff/Gamma0
# recompute nominal fit arrays for plotting
geom = geom_nom
a_min = max(3.0 * geom.ds_median, geom.d_min_dimless * 1e-4)
a_max = geom.d_min_dimless * 0.35
a_scan_nom = np.logspace(np.log10(a_min), np.log10(a_max), 18)
E_vals_nom = np.array([compute_E_BS_norm_from_mats(a, 1.0, geom) for a in a_scan_nom])
fit_nom = extract_AK_local(a_scan_nom, E_vals_nom, geom.L_K_dimless, geom.d_min_dimless)
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogx(fit_nom["a_mid"], fit_nom["A_local"], marker="o", label=r"local $A_K(a)$")
mask = fit_nom["plateau_mask"]
if np.any(mask):
    ax.semilogx(fit_nom["a_mid"][mask], fit_nom["A_local"][mask], 'ro', label='plateau points')
ax.axhline(A_req, color="green", ls="--", lw=1.5, label=r"$1/(4\pi)$")
ax.axhline(fit_nom["A_K_use"], color="tab:red", ls=":", lw=1.5, label=fr"chosen $A_K={fit_nom['A_K_use']:.4f}$")
ax.set_xlabel(r"$a$ (dimensionless)")
ax.set_ylabel(r"local $A_K$")
ax.set_title("Nominal local-slope plateau diagnostic")
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plot4 = os.path.join(OUTDIR, "sst_optionB_AK_local_nominal.png")
plt.savefig(plot4, dpi=160, bbox_inches="tight")
plt.close(fig)

# console summary
print("Saved files:")
for p in [physics_csv, contact_csv, summary_path, plot1, plot2, plot3, plot4]:
    print(f"  {p}")

print("\nNominal case summary:")
print(nom.to_string())
print("\nBest closure case (by chi):")
print(best_chi.to_string())
