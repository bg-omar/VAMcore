#!/usr/bin/env python3
"""
SST ideal-trefoil robustness sweep v2
===================================

Upgrades over v1:
- separate geometry resolution N_geom from Biot-Savart integration resolution N_int,
- explicit root-branch selection,
- final best-estimate postprocessing,
- LaTeX-ready and CSV best-estimate outputs,
- extra diagnostics for lambda sensitivity.

This script still does NOT prove parameter-free closure. It is a numerical
robustness tool for the present regularized ideal-trefoil Route-2 analysis.
"""

from __future__ import annotations

import csv
import math
import os
os.environ["ONEAPI_DEVICE_SELECTOR"] = "level_zero:0"
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq

try:
    import torch  # type: ignore[import]

    _TORCH_AVAILABLE = True
except Exception:  # ImportError or any other issue -> disable torch path
    torch = None  # type: ignore[assignment]
    _TORCH_AVAILABLE = False

# -----------------------------------------------------------------------------
# 1. Canonical SST constants
# -----------------------------------------------------------------------------
r_c_canon = 1.40897017e-15      # m
v_swirl = 1.09384563e6          # m/s
rho_f = 7.0e-7                  # kg/m^3
c_exact = 299792458.0           # m/s
Gamma_0_input = 9.68361918e-9   # m^2/s
A_req = 1.0 / (4.0 * np.pi)
L_natural = Gamma_0_input / v_swirl

# -----------------------------------------------------------------------------
# 2. Ideal trefoil Fourier coefficients (Gilbert database, Id=3:1:1)
# -----------------------------------------------------------------------------
ideal_trefoil_coeffs = [
    (1, 0.374139, 0.000000, 0.000000, 0.000000, 0.373928, 0.000000),
    (2, 0.824246, 0.750260, 0.000352, 0.750450, -0.823952, -0.001991),
    (3, 0.000257, -0.000932, 0.352397, -0.000770, 0.000726, -0.386764),
    (4, 0.011652, -0.010656, 0.000743, 0.010739, 0.011613, -0.000230),
    (5, 0.010504, 0.110306, 0.000199, 0.110745, -0.010366, -0.000235),
    (6, 0.000015, -0.000006, -0.047465, -0.000050, -0.000001, 0.004595),
    (7, -0.000292, 0.002417, -0.000008, -0.002529, -0.000255, -0.000009),
    (8, 0.016487, -0.021784, 0.000041, -0.021922, -0.016421, -0.000044),
    (9, -0.000029, -0.000018, 0.011178, 0.000049, 0.000041, 0.008414),
    (10, -0.000216, -0.000290, -0.000018, 0.000311, -0.000197, -0.000044),
    (11, -0.011727, 0.002184, 0.000007, 0.002202, 0.011682, 0.000020),
    (12, 0.000026, 0.000019, -0.001308, -0.000004, -0.000019, -0.007039),
    (13, 0.000325, 0.000055, -0.000009, -0.000059, 0.000289, 0.000024),
    (14, 0.005213, 0.003201, 0.000001, 0.003210, -0.005188, 0.000010),
    (15, -0.000015, -0.000016, -0.001917, -0.000017, 0.000001, 0.003121),
    (16, -0.000136, 0.000062, 0.000019, -0.000075, -0.000112, -0.000007),
    (17, -0.000995, -0.003463, -0.000001, -0.003474, 0.000988, -0.000015),
    (18, 0.000003, 0.000008, 0.002178, 0.000019, 0.000008, -0.000615),
    (19, 0.000033, -0.000094, -0.000016, 0.000113, 0.000028, -0.000004),
    (20, -0.000999, 0.002013, -0.000000, 0.002019, 0.000998, 0.000000),
    (21, 0.000004, 0.000001, -0.001270, -0.000013, -0.000012, -0.000626),
    (22, 0.000034, 0.000060, 0.000009, -0.000072, 0.000026, 0.000010),
    (23, 0.001383, -0.000539, 0.000002, -0.000540, -0.001382, 0.000004),
    (24, -0.000005, -0.000011, 0.000344, 0.000009, 0.000007, 0.000890),
    (25, -0.000057, -0.000025, 0.000001, 0.000019, -0.000048, -0.000008),
    (26, -0.000931, -0.000356, -0.000000, -0.000357, 0.000931, -0.000005),
    (27, 0.000006, 0.000009, 0.000228, -0.000002, -0.000000, -0.000597),
    (28, 0.000040, -0.000007, -0.000004, 0.000019, 0.000036, 0.000004),
    (29, 0.000308, 0.000611, 0.000001, 0.000611, -0.000307, 0.000007),
    (30, 0.000002, 0.000001, -0.000391, -0.000006, 0.000001, 0.000195),
]

# -----------------------------------------------------------------------------
# 3. Sweep controls
# -----------------------------------------------------------------------------
OUTPUT_DIR = os.path.abspath("./sst_ideal_trefoil_robustness_outputs_v2")
os.makedirs(OUTPUT_DIR, exist_ok=True)

N_GEOM_LIST = [4000, 8000, 16000, 32000]
N_INT_LIST = [2000, 4000, 8000, 16000, 32000]
A_SCAN_COUNT = 24
PLATEAU_FRACS = [0.08, 0.12, 0.16]
REL_DE_THRESH = 1e-4
LAMBDA_LIST = [0.0, 1e-3, 3e-3, 1e-2]
P_LIST = [2]
BS_BLOCK = 512

# Enable or disable the optional PyTorch-accelerated Biot–Savart energy kernel.
ENABLE_TORCH_ACCEL = True
SAVE_PER_RUN_DIAGNOSTICS = False
SAVE_SUMMARY_PLOTS = True

# Root selection among multiple minima / stationary branches:
#   "closest_to_a0" or "lowest_energy"
BRANCH_MODE = "closest_to_a0"

# Preferred fit method for final best estimate.
PREFERRED_FIT_METHOD = "plateau_0.12"

# Stability thresholds for labeling.
STABLE_TOL = 0.02
DRIFT_TOL = 0.08
A_STABLE_TOL = 0.02
A_DRIFT_TOL = 0.08


@dataclass
class GeometryData:
    N_geom: int
    N_int_target: int
    N_int_actual: int
    pts_full: np.ndarray
    ds_full: np.ndarray
    tangents_full: np.ndarray
    L_dimless_full: float
    d_min_full: float
    pts_int: np.ndarray
    tangents_int: np.ndarray
    ds_int: np.ndarray
    d_min_int: float


@dataclass
class FitResult:
    fit_method: str
    plateau_frac: Optional[float]
    A_K: float
    A_spread: float
    a_K: float
    a_ref: float
    n_plateau: int


@dataclass
class RootCandidate:
    a_star: float
    is_min: bool
    E_star: float


def eval_ideal_trefoil(t_arr: np.ndarray) -> np.ndarray:
    X = np.zeros((len(t_arr), 3), dtype=float)
    for (k, Ax, Ay, Az, Bx, By, Bz) in ideal_trefoil_coeffs:
        phase = 2.0 * np.pi * k * t_arr
        X[:, 0] += Ax * np.cos(phase) + Bx * np.sin(phase)
        X[:, 1] += Ay * np.cos(phase) + By * np.sin(phase)
        X[:, 2] += Az * np.cos(phase) + Bz * np.sin(phase)
    return X


def eval_ideal_trefoil_deriv(t_arr: np.ndarray) -> np.ndarray:
    dX = np.zeros((len(t_arr), 3), dtype=float)
    for (k, Ax, Ay, Az, Bx, By, Bz) in ideal_trefoil_coeffs:
        phase = 2.0 * np.pi * k * t_arr
        w = 2.0 * np.pi * k
        dX[:, 0] += w * (-Ax * np.sin(phase) + Bx * np.cos(phase))
        dX[:, 1] += w * (-Ay * np.sin(phase) + By * np.cos(phase))
        dX[:, 2] += w * (-Az * np.sin(phase) + Bz * np.cos(phase))
    return dX


def circular_index_distance(ii: np.ndarray, jj: np.ndarray, n: int) -> np.ndarray:
    d = np.abs(ii[:, None] - jj[None, :])
    return np.minimum(d, n - d)


def coarse_min_self_distance(pts: np.ndarray, excl: int) -> float:
    n = len(pts)
    d_min = np.inf
    for i0 in range(0, n, BS_BLOCK):
        i1 = min(i0 + BS_BLOCK, n)
        Pi = pts[i0:i1]
        ii = np.arange(i0, i1)
        for j0 in range(i0, n, BS_BLOCK):
            j1 = min(j0 + BS_BLOCK, n)
            Pj = pts[j0:j1]
            jj = np.arange(j0, j1)
            diff = Pi[:, None, :] - Pj[None, :, :]
            dist = np.linalg.norm(diff, axis=2)
            mask = circular_index_distance(ii, jj, n) > excl
            if j0 == i0:
                mask &= np.triu(np.ones_like(mask, dtype=bool), k=1)
            if np.any(mask):
                local = np.min(dist[mask])
                if local < d_min:
                    d_min = local
    return float(d_min)


def build_geometry(N_geom: int, N_int_target: int) -> GeometryData:
    t_full = np.linspace(0.0, 1.0, N_geom, endpoint=False)
    pts_full = eval_ideal_trefoil(t_full)
    dpts_dt = eval_ideal_trefoil_deriv(t_full)
    speed = np.linalg.norm(dpts_dt, axis=1)
    ds_full = speed * (1.0 / N_geom)
    tangents_full = dpts_dt / speed[:, None]
    L_dimless_full = float(np.sum(ds_full))

    if N_int_target >= N_geom:
        stride = 1
    else:
        stride = max(1, int(math.ceil(N_geom / N_int_target)))
    pts_int = pts_full[::stride]
    tangents_int = tangents_full[::stride]
    ds_int = ds_full[::stride] * stride
    ds_int[-1] += L_dimless_full - np.sum(ds_int)

    excl_int = max(5, len(pts_int) // 15)
    d_min_int = coarse_min_self_distance(pts_int, excl_int)

    # For full d_min use the full geometry if manageable, else a capped dense proxy.
    n_dmin_cap = min(max(3000, N_int_target), N_geom)
    if n_dmin_cap >= N_geom:
        pts_dmin = pts_full
    else:
        stride_dmin = max(1, int(math.ceil(N_geom / n_dmin_cap)))
        pts_dmin = pts_full[::stride_dmin]
    excl_dmin = max(5, len(pts_dmin) // 15)
    d_min_full = coarse_min_self_distance(pts_dmin, excl_dmin)

    return GeometryData(
        N_geom=N_geom,
        N_int_target=N_int_target,
        N_int_actual=len(pts_int),
        pts_full=pts_full,
        ds_full=ds_full,
        tangents_full=tangents_full,
        L_dimless_full=L_dimless_full,
        d_min_full=d_min_full,
        pts_int=pts_int,
        tangents_int=tangents_int,
        ds_int=ds_int,
        d_min_int=d_min_int,
    )


def _pick_torch_device() -> "torch.device":  # type: ignore[name-defined]
    """Select the best available torch device.

    Preference order: XPU (Intel), CUDA, MPS (Apple), then CPU.
    """

    assert _TORCH_AVAILABLE and torch is not None

    # Environment override takes precedence if valid.
    dev_str = os.environ.get("SST_TORCH_DEVICE")
    if dev_str:
        try:
            return torch.device(dev_str)
        except Exception:
            # Fall through to automatic selection on invalid string.
            pass

    # Intel XPU
    if hasattr(torch, "xpu") and getattr(torch, "xpu").is_available():
        return torch.device("xpu")

    # NVIDIA CUDA
    if torch.cuda.is_available():
        return torch.device("cuda")

    # Apple MPS
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")

    # Fallback: CPU
    return torch.device("cpu")


def _compute_E_BS_norm_numpy_impl(a_dimless: float, pts: np.ndarray, tangents: np.ndarray, ds_arr: np.ndarray) -> float:
    """Reference NumPy implementation of the Biot–Savart kernel.

    This is the original implementation, kept verbatim so the torch
    path can be validated against it.
    """

    delta = float(a_dimless)
    n = len(pts)
    total = 0.0
    all_idx = np.arange(n)
    for i0 in range(0, n, BS_BLOCK):
        i1 = min(i0 + BS_BLOCK, n)
        Pi = pts[i0:i1]
        Ti = tangents[i0:i1]
        dsi = ds_arr[i0:i1]
        ii = np.arange(i0, i1)
        row_sum = np.zeros(i1 - i0, dtype=float)
        for j0 in range(0, n, BS_BLOCK):
            j1 = min(j0 + BS_BLOCK, n)
            Pj = pts[j0:j1]
            Tj = tangents[j0:j1]
            dsj = ds_arr[j0:j1]
            jj = all_idx[j0:j1]
            diff = Pj[None, :, :] - Pi[:, None, :]
            dist = np.linalg.norm(diff, axis=2)
            dot_tt = Ti @ Tj.T
            mask = (dist > delta) & (ii[:, None] != jj[None, :])
            contrib = np.where(mask, dot_tt / np.maximum(dist, 1e-300), 0.0)
            row_sum += contrib @ dsj
        total += np.sum(row_sum * dsi)
    return float(total / (8.0 * np.pi))


def _compute_E_BS_norm_torch_impl(a_dimless: float, pts: np.ndarray, tangents: np.ndarray, ds_arr: np.ndarray, device: torch.device) -> float:
    import math
    delta = float(a_dimless)
    n = len(pts)

    # Bepaal het werk-datatype op basis van de hardwarecapaciteit
    # XPU en MPS (Mac) gebruiken float32; CUDA of CPU kunnen float64 gebruiken
    compute_dtype = torch.float32 if device.type in ["xpu", "mps"] else torch.float64

    # Stuur data naar de GPU in het ondersteunde datatype
    pts_t = torch.tensor(pts, dtype=compute_dtype, device=device)
    tangents_t = torch.tensor(tangents, dtype=compute_dtype, device=device)
    ds_t = torch.tensor(ds_arr, dtype=compute_dtype, device=device)

    # We accumuleren het eindtotaal lokaal in Python (wat standaard 64-bit float is).
    # Dit voorkomt 'catastrophic cancellation' bij het optellen van miljoenen FP32 waarden.
    total_cpu = 0.0
    all_idx = torch.arange(n, device=device)

    # Haal de constante BS_BLOCK op (normaal 512 in het script)
    # Als deze in uw scope niet direct toegankelijk is, zet hem dan hard op 512
    BS_BLOCK = 512

    for i0 in range(0, n, BS_BLOCK):
        i1 = min(i0 + BS_BLOCK, n)
        Pi = pts_t[i0:i1]
        Ti = tangents_t[i0:i1]
        dsi = ds_t[i0:i1]
        ii = all_idx[i0:i1].unsqueeze(1)

        for j0 in range(0, n, BS_BLOCK):
            j1 = min(j0 + BS_BLOCK, n)
            Pj = pts_t[j0:j1]
            Tj = tangents_t[j0:j1]
            dsj = ds_t[j0:j1]
            jj = all_idx[j0:j1].unsqueeze(0)

            diff = Pj.unsqueeze(0) - Pi.unsqueeze(1)
            dist = torch.norm(diff, dim=2)
            dot_tt = torch.sum(Ti.unsqueeze(1) * Tj.unsqueeze(0), dim=2)

            mask = (dist > delta) & (ii != jj)

            # Voorkom delen door nul (1e-30 is een veilige limiet voor float32)
            dist_safe = torch.clamp(dist, min=1e-30)
            contrib = torch.where(mask, dot_tt / dist_safe, torch.tensor(0.0, dtype=compute_dtype, device=device))

            # Vermenigvuldig met de segmentlengtes en tel het blok op (bypasses oneDNN matmul bug)
            block_sum = torch.sum(contrib * dsj.unsqueeze(0) * dsi.unsqueeze(1))

            # Verplaats de waarde van dít specifieke blok naar de CPU en tel het 64-bit op
            total_cpu += float(block_sum.item())

    # if device.type in ["cuda", "xpu"]:
    #     getattr(torch, device.type).empty_cache()

    return total_cpu / (8.0 * math.pi)

def compute_E_BS_norm(a_dimless: float, pts: np.ndarray, tangents: np.ndarray, ds_arr: np.ndarray) -> float:
    """Compute dimensionless Biot–Savart energy density.

    Uses an optional torch-accelerated backend if available and enabled,
    otherwise falls back to the original NumPy implementation.
    """

    # Always use the pure NumPy path if torch is not available or explicitly disabled.
    if not _TORCH_AVAILABLE or not ENABLE_TORCH_ACCEL:
        return _compute_E_BS_norm_numpy_impl(a_dimless, pts, tangents, ds_arr)

    try:
        device = _pick_torch_device()
    except Exception:
        # If anything goes wrong with device selection, fall back safely.
        return _compute_E_BS_norm_numpy_impl(a_dimless, pts, tangents, ds_arr)

    return _compute_E_BS_norm_torch_impl(a_dimless, pts, tangents, ds_arr, device=device)


def scan_BS_energy(geom: GeometryData) -> Tuple[np.ndarray, np.ndarray]:
    ds_med = float(np.median(geom.ds_int))
    a_lo = max(3.0 * ds_med, geom.d_min_int * 5e-4)
    a_hi = geom.d_min_int * 0.35
    a_scan = np.logspace(np.log10(a_lo), np.log10(a_hi), A_SCAN_COUNT)
    E_vals = np.array([
        compute_E_BS_norm(a, geom.pts_int, geom.tangents_int, geom.ds_int)
        for a in a_scan
    ])
    return a_scan, E_vals


def extract_fits(a_scan: np.ndarray, E_vals: np.ndarray, L_dimless: float, d_min_dimless: float) -> Tuple[List[FitResult], Dict[str, np.ndarray]]:
    x_scan = -np.log(a_scan)
    y_scan = E_vals / L_dimless
    a_mid = np.sqrt(a_scan[:-1] * a_scan[1:])
    A_local = np.diff(y_scan) / np.diff(x_scan)
    rel_dE = np.abs(np.diff(E_vals)) / np.maximum(np.abs(E_vals[:-1]), 1e-300)

    out: List[FitResult] = []

    coeffs_global = np.polyfit(x_scan, y_scan, 1)
    A_global = float(coeffs_global[0])
    b_global = float(coeffs_global[1])
    a_K_global = b_global - A_global * np.log(L_dimless)
    out.append(FitResult("global", None, A_global, np.nan, a_K_global, float(a_scan[len(a_scan)//2]), 0))

    for frac in PLATEAU_FRACS:
        mask = (A_local > 0.0) & (rel_dE > REL_DE_THRESH) & (a_mid < frac * d_min_dimless)
        if np.any(mask):
            A_plateau = float(np.median(A_local[mask]))
            A_spread = float(np.std(A_local[mask]))
            idxs = np.where(mask)[0]
            idx_ref = idxs[len(idxs)//2]
            y_ref = float(0.5 * (y_scan[idx_ref] + y_scan[idx_ref + 1]))
            a_ref = float(a_mid[idx_ref])
            a_K = y_ref - A_plateau * np.log(L_dimless / a_ref)
            out.append(FitResult(f"plateau_{frac:.2f}", frac, A_plateau, A_spread, float(a_K), a_ref, int(np.sum(mask))))
        else:
            out.append(FitResult(f"plateau_{frac:.2f}", frac, np.nan, np.nan, np.nan, np.nan, 0))

    diagnostics = {
        "a_mid": a_mid,
        "A_local": A_local,
        "x_scan": x_scan,
        "y_scan": y_scan,
    }
    return out, diagnostics


def dE_da(a: float, A_K: float, L_K_phys: float, d_min_phys: float, lam_K: float, p_exp: int) -> float:
    if a <= 0.0 or 2.0 * a >= d_min_phys:
        return np.nan
    dE_BS = -rho_f * Gamma_0_input**2 * L_K_phys * A_K / a
    dE_core = np.pi * rho_f * v_swirl**2 * a * L_K_phys
    if lam_K == 0.0:
        dE_cont = 0.0
    else:
        xc = 2.0 * a / (d_min_phys - 2.0 * a)
        dx_da = 2.0 * d_min_phys / (d_min_phys - 2.0 * a)**2
        dE_cont = lam_K * rho_f * Gamma_0_input**2 * L_K_phys * p_exp * xc**(p_exp - 1) * dx_da
    return float(dE_BS + dE_core + dE_cont)


def E_K_phys(a: float, A_K: float, a_K: float, L_K_phys: float, d_min_phys: float, lam_K: float, p_exp: int) -> float:
    if a <= 0.0 or 2.0 * a >= d_min_phys:
        return np.inf
    E_BS = rho_f * Gamma_0_input**2 * L_K_phys * (A_K * np.log(L_K_phys / a) + a_K)
    E_core = 0.5 * np.pi * rho_f * v_swirl**2 * a**2 * L_K_phys
    if lam_K == 0.0:
        E_cont = 0.0
    else:
        xc = 2.0 * a / (d_min_phys - 2.0 * a)
        E_cont = lam_K * rho_f * Gamma_0_input**2 * L_K_phys * xc**p_exp
    return float(E_BS + E_core + E_cont)


def find_root_candidates(A_K: float, a_K: float, L_dimless: float, d_min_dimless: float, lam_K: float, p_exp: int) -> List[RootCandidate]:
    L_K_phys = L_dimless * L_natural
    d_min_phys = d_min_dimless * L_natural
    a_lo = max(d_min_phys * 1e-7, L_natural * 1e-8)
    a_hi = d_min_phys * 0.49
    a_vals = np.logspace(np.log10(a_lo), np.log10(a_hi), 1200)
    dE_vals = np.array([dE_da(a, A_K, L_K_phys, d_min_phys, lam_K, p_exp) for a in a_vals])
    valid = np.isfinite(dE_vals)
    if np.count_nonzero(valid) < 3:
        return []
    av = a_vals[valid]
    dv = dE_vals[valid]
    signs = np.sign(dv)
    changes = np.where((signs[:-1] * signs[1:] < 0) | ((signs[:-1] == 0) & (signs[1:] != 0)) | ((signs[:-1] != 0) & (signs[1:] == 0)))[0]

    roots: List[RootCandidate] = []
    seen: List[float] = []
    for i in changes:
        left = float(av[i])
        right = float(av[i + 1])
        try:
            root = float(brentq(dE_da, left, right, args=(A_K, L_K_phys, d_min_phys, lam_K, p_exp), maxiter=200))
        except ValueError:
            continue
        if any(abs(root - r) / max(abs(root), 1e-300) < 1e-8 for r in seen):
            continue
        seen.append(root)
        h = max(root * 1e-6, 1e-30)
        d2 = (dE_da(root + h, A_K, L_K_phys, d_min_phys, lam_K, p_exp) -
              dE_da(root - h, A_K, L_K_phys, d_min_phys, lam_K, p_exp)) / (2.0 * h)
        is_min = bool(np.isfinite(d2) and d2 > 0.0)
        E_star = E_K_phys(root, A_K, a_K, L_K_phys, d_min_phys, lam_K, p_exp)
        roots.append(RootCandidate(root, is_min, E_star))

    # Fallback when no sign change was captured.
    if not roots:
        idx = int(np.argmin(np.abs(dv)))
        root = float(av[idx])
        h = max(root * 1e-6, 1e-30)
        d2 = (dE_da(root + h, A_K, L_K_phys, d_min_phys, lam_K, p_exp) -
              dE_da(root - h, A_K, L_K_phys, d_min_phys, lam_K, p_exp)) / (2.0 * h)
        is_min = bool(np.isfinite(d2) and d2 > 0.0)
        E_star = E_K_phys(root, A_K, a_K, L_K_phys, d_min_phys, lam_K, p_exp)
        roots.append(RootCandidate(root, is_min, E_star))

    roots.sort(key=lambda rc: rc.a_star)
    return roots


def choose_root(candidates: List[RootCandidate], a0: float, branch_mode: str) -> Tuple[float, bool, float, int, int, str]:
    if not candidates:
        return np.nan, False, np.inf, 0, 0, "none"
    mins = [c for c in candidates if c.is_min]
    pool = mins if mins else candidates
    if branch_mode == "lowest_energy":
        chosen = min(pool, key=lambda c: c.E_star)
        choice = "lowest_energy"
    else:
        chosen = min(pool, key=lambda c: abs(c.a_star - a0))
        choice = "closest_to_a0"
    return chosen.a_star, chosen.is_min, chosen.E_star, len(candidates), len(mins), choice


def classify_run(A_ratio: float, a_star_over_rc: float, is_min: bool) -> str:
    if (not np.isfinite(A_ratio)) or (not np.isfinite(a_star_over_rc)) or (not is_min):
        return "inconclusive"
    A_err = abs(A_ratio - 1.0)
    r_err = abs(a_star_over_rc - 1.0)
    if A_err <= A_STABLE_TOL and r_err <= STABLE_TOL:
        return "stable"
    if A_err <= A_DRIFT_TOL and r_err <= DRIFT_TOL:
        return "drift"
    return "inconclusive"


def save_geometry_plot(geom: GeometryData, outpath: str) -> None:
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(geom.pts_full[:, 0], geom.pts_full[:, 1], geom.pts_full[:, 2], lw=1.2)
    ax.set_title(f"Ideal trefoil (Gilbert 3_1) - N_geom={geom.N_geom}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    plt.tight_layout()
    plt.savefig(outpath, dpi=160, bbox_inches="tight")
    plt.close(fig)


def save_bs_diagnostics(a_scan: np.ndarray, E_vals: np.ndarray, fit_results: List[FitResult], diagnostics: Dict[str, np.ndarray], outpath: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].semilogx(a_scan, E_vals, "o-", ms=4, lw=1.5)
    axes[0].set_xlabel("a (dimless)")
    axes[0].set_ylabel("E_BS_norm")
    axes[0].set_title("Biot-Savart scan")
    axes[0].grid(True, alpha=0.3)

    a_mid = diagnostics["a_mid"]
    A_local = diagnostics["A_local"]
    axes[1].semilogx(a_mid, A_local, "o-", ms=4, lw=1.2, label="local slope")
    axes[1].axhline(A_req, color="green", ls="--", lw=2, label=f"1/(4*pi)={A_req:.6f}")
    for fr in fit_results:
        if np.isfinite(fr.A_K):
            style = "-." if fr.fit_method == "global" else ":"
            axes[1].axhline(fr.A_K, ls=style, lw=1.2, label=f"{fr.fit_method}={fr.A_K:.6f}")
    axes[1].set_xlabel("a (dimless)")
    axes[1].set_ylabel("local A_K slope")
    axes[1].set_title("A_K extraction")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outpath, dpi=170, bbox_inches="tight")
    plt.close(fig)


def save_summary_plots(rows: List[dict], outdir: str) -> None:
    if not rows:
        return

    preferred = [r for r in rows if r["fit_method"] == PREFERRED_FIT_METHOD and r["lambda_K"] == 0.0]
    if preferred:
        fig = plt.figure(figsize=(8, 5.5))
        for N_geom in sorted(set(r["N_geom"] for r in preferred)):
            subset = sorted([r for r in preferred if r["N_geom"] == N_geom], key=lambda rr: rr["N_int_actual"])
            xs = np.array([r["N_int_actual"] for r in subset], dtype=float)
            ys = np.array([r["A_K"] for r in subset], dtype=float)
            plt.plot(xs, ys, "o-", lw=1.6, label=f"N_geom={N_geom}")
        plt.axhline(A_req, ls="--", lw=2, label=f"1/(4*pi)={A_req:.8f}")
        plt.xscale("log")
        plt.xlabel("N_int_actual")
        plt.ylabel("A_K")
        plt.title(f"A_K vs Biot-Savart resolution ({PREFERRED_FIT_METHOD}, lambda=0)")
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "summary_AK_vs_Nint.png"), dpi=170, bbox_inches="tight")
        plt.close(fig)

        fig = plt.figure(figsize=(8, 5.5))
        for N_geom in sorted(set(r["N_geom"] for r in preferred)):
            subset = sorted([r for r in preferred if r["N_geom"] == N_geom], key=lambda rr: rr["N_int_actual"])
            xs = np.array([r["N_int_actual"] for r in subset], dtype=float)
            ys = np.array([r["a0_over_rc"] for r in subset], dtype=float)
            plt.plot(xs, ys, "o-", lw=1.6, label=f"N_geom={N_geom}")
        plt.axhline(1.0, ls="--", lw=2, label="a0/r_c = 1")
        plt.xscale("log")
        plt.xlabel("N_int_actual")
        plt.ylabel("a0/r_c")
        plt.title(f"a0/r_c vs Biot-Savart resolution ({PREFERRED_FIT_METHOD}, lambda=0)")
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "summary_a0_over_rc_vs_Nint.png"), dpi=170, bbox_inches="tight")
        plt.close(fig)

    preferred_non_nan = [r for r in rows if r["fit_method"] == PREFERRED_FIT_METHOD and np.isfinite(r["a_star_over_rc"])]
    if preferred_non_nan:
        fig = plt.figure(figsize=(8, 5.5))
        for key in sorted(set((r["N_geom"], r["N_int_actual"]) for r in preferred_non_nan)):
            N_geom, N_int = key
            subset = sorted([r for r in preferred_non_nan if r["N_geom"] == N_geom and r["N_int_actual"] == N_int], key=lambda rr: rr["lambda_K"])
            xs = np.array([r["lambda_K"] for r in subset], dtype=float)
            ys = np.array([r["a_star_over_rc"] for r in subset], dtype=float)
            xplot = np.where(xs > 0.0, xs, 1e-5)
            plt.semilogx(xplot, ys, "o-", lw=1.3, label=f"Ng={N_geom}, Ni={N_int}")
        plt.axhline(1.0, ls="--", lw=2, label="a*/r_c = 1")
        plt.xlabel("lambda_K  (lambda=0 shown at 1e-5)")
        plt.ylabel("a*/r_c")
        plt.title(f"Closure vs contact strength ({PREFERRED_FIT_METHOD})")
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=7, ncol=2)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "summary_astar_over_rc_vs_lambda.png"), dpi=170, bbox_inches="tight")
        plt.close(fig)


def write_csv(rows: List[dict], outpath: str) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(outpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def robust_half_range(vals: List[float]) -> float:
    arr = np.array([v for v in vals if np.isfinite(v)], dtype=float)
    if arr.size == 0:
        return np.nan
    return float(0.5 * (np.max(arr) - np.min(arr)))


def select_best_row(rows: List[dict]) -> Optional[dict]:
    preferred = [r for r in rows if r["fit_method"] == PREFERRED_FIT_METHOD and r["lambda_K"] == 0.0 and r["p_exp"] == P_LIST[0]]
    finite = [r for r in preferred if np.isfinite(r["A_K"]) and np.isfinite(r["a0_over_rc"])]
    if finite:
        finite.sort(key=lambda r: (abs(r["A_ratio"] - 1.0), abs(r["a0_over_rc"] - 1.0), -r["N_int_actual"], -r["N_geom"]))
        return finite[0]
    fallback = [r for r in rows if r["lambda_K"] == 0.0 and np.isfinite(r["A_K"]) and np.isfinite(r["a0_over_rc"])]
    if not fallback:
        return None
    fallback.sort(key=lambda r: (abs(r["A_ratio"] - 1.0), abs(r["a0_over_rc"] - 1.0), -r["N_int_actual"], -r["N_geom"]))
    return fallback[0]


def write_best_estimate(rows: List[dict], outdir: str) -> None:
    best = select_best_row(rows)
    if best is None:
        return

    # Systematic spreads from no-contact runs over all fit methods and N choices.
    no_contact = [r for r in rows if r["lambda_K"] == 0.0 and np.isfinite(r["A_K"]) and np.isfinite(r["a0_over_rc"])]
    A_sys = robust_half_range([r["A_K"] for r in no_contact])
    A_ratio_sys = robust_half_range([r["A_ratio"] for r in no_contact])
    a0_sys = robust_half_range([r["a0_over_rc"] for r in no_contact])

    # Provisional full-model spread at preferred fit method.
    pref_rows = [r for r in rows if r["fit_method"] == best["fit_method"] and np.isfinite(r["a_star_over_rc"])]
    if pref_rows:
        a_star_center = float(np.median([r["a_star_over_rc"] for r in pref_rows]))
        a_star_sys = robust_half_range([r["a_star_over_rc"] for r in pref_rows])
    else:
        a_star_center = np.nan
        a_star_sys = np.nan

    result = {
        "preferred_fit_method": best["fit_method"],
        "N_geom_best": best["N_geom"],
        "N_int_best": best["N_int_actual"],
        "A_K_best": best["A_K"],
        "A_K_systematic_half_range": A_sys,
        "A_ratio_best": best["A_ratio"],
        "A_ratio_systematic_half_range": A_ratio_sys,
        "a0_over_rc_best": best["a0_over_rc"],
        "a0_over_rc_systematic_half_range": a0_sys,
        "a_star_over_rc_provisional_center": a_star_center,
        "a_star_over_rc_provisional_half_range": a_star_sys,
        "branch_mode": BRANCH_MODE,
        "comment": "Quote A_K_best and a0_over_rc_best as the cleanest current estimates. Treat a_star_over_rc as provisional until branch sensitivity is reduced.",
    }

    csv_path = os.path.join(outdir, "final_best_estimate.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.keys()))
        writer.writeheader()
        writer.writerow(result)

    txt_path = os.path.join(outdir, "final_best_estimate.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("SST ideal-trefoil final best-estimate (v2)\n")
        f.write("=" * 48 + "\n")
        f.write(f"Preferred fit method       : {best['fit_method']}\n")
        f.write(f"Best grid                  : N_geom={best['N_geom']}, N_int={best['N_int_actual']}\n")
        f.write(f"A_K_best                   : {best['A_K']:.8f} +- {A_sys:.8f} (systematic half-range)\n")
        f.write(f"A_ratio_best               : {best['A_ratio']:.8f} +- {A_ratio_sys:.8f}\n")
        f.write(f"a0/r_c_best                : {best['a0_over_rc']:.8f} +- {a0_sys:.8f}\n")
        if np.isfinite(a_star_center):
            f.write(f"a*/r_c provisional center  : {a_star_center:.8f} +- {a_star_sys:.8f}\n")
        else:
            f.write("a*/r_c provisional center  : nan\n")
        f.write(f"Branch mode                : {BRANCH_MODE}\n")
        f.write("\n")
        f.write("Interpretation: A_K_best and a0/r_c_best are the cleanest current closure estimates. ")
        f.write("The full-model a*/r_c remains provisional until branch sensitivity and Biot-Savart resolution are better constrained.\n")

    tex_path = os.path.join(outdir, "final_best_estimate.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\\paragraph{Final best-estimate from the present v2 sweep.}\n")
        f.write("Using the ideal trefoil (Gilbert $3_1$), the preferred current estimate is taken from the selected best no-contact run at the preferred fit window. ")
        f.write(f"This gives\\n\\[\nA_K^{{\\mathrm{{best}}}} = {best['A_K']:.8f} \\pm {A_sys:.8f}_{{\\mathrm{{syst}}}},\n\\]\n")
        f.write(f"relative to $1/(4\\pi)={A_req:.8f}$, i.e.\\n\\[\n\\frac{{A_K^{{\\mathrm{{best}}}}}}{{1/(4\\pi)}} = {best['A_ratio']:.8f} \\pm {A_ratio_sys:.8f}_{{\\mathrm{{syst}}}}.\n\\]\n")
        f.write(f"The corresponding no-contact radius estimate is\\n\\[\n\\left(\\frac{{a_0}}{{r_c}}\\right)^{{\\mathrm{{best}}}} = {best['a0_over_rc']:.8f} \\pm {a0_sys:.8f}_{{\\mathrm{{syst}}}}.\n\\]\n")
        if np.isfinite(a_star_center):
            f.write(f"For the present regularized model, a provisional summary of the selected branch gives\\n\\[\n\\left(\\frac{{a^*}}{{r_c}}\\right)_{{\\mathrm{{prov}}}} = {a_star_center:.8f} \\pm {a_star_sys:.8f}.\n\\]\n")
        f.write("These numbers should be interpreted as numerical support for percent-level closure, not yet as a parameter-free derivation.\n")


def main() -> None:
    print("=" * 78)
    print("SST IDEAL-TREFOIL ROBUSTNESS SWEEP V2")
    print("=" * 78)
    print(f"Output directory : {OUTPUT_DIR}")
    print(f"Gamma_0_input    : {Gamma_0_input:.8e} m^2/s")
    print(f"v_swirl          : {v_swirl:.8e} m/s")
    print(f"r_c_canon        : {r_c_canon:.8e} m")
    print(f"A_req            : 1/(4*pi) = {A_req:.8f}")
    print(f"Branch mode      : {BRANCH_MODE}")
    print(f"Preferred fit    : {PREFERRED_FIT_METHOD}")
    print()

    rows: List[dict] = []

    for N_geom in N_GEOM_LIST:
        for N_int_target in N_INT_LIST:
            print("-" * 78)
            print(f"Building geometry for N_geom={N_geom}, N_int_target={N_int_target}")
            geom = build_geometry(N_geom, N_int_target)
            print(f"  L_dimless_full = {geom.L_dimless_full:.6f}")
            print(f"  d_min_full     = {geom.d_min_full:.6f}")
            print(f"  N_int_actual   = {geom.N_int_actual}")
            print(f"  d_min_int      = {geom.d_min_int:.6f}")

            if SAVE_PER_RUN_DIAGNOSTICS:
                save_geometry_plot(geom, os.path.join(OUTPUT_DIR, f"geom_Ng{N_geom}_Ni{geom.N_int_actual}.png"))

            print("  Scanning Biot-Savart energy...")
            a_scan, E_vals = scan_BS_energy(geom)
            fit_results, diagnostics = extract_fits(a_scan, E_vals, geom.L_dimless_full, geom.d_min_full)

            if SAVE_PER_RUN_DIAGNOSTICS:
                save_bs_diagnostics(a_scan, E_vals, fit_results, diagnostics, os.path.join(OUTPUT_DIR, f"bs_diagnostics_Ng{N_geom}_Ni{geom.N_int_actual}.png"))

            baseline_by_fit: Dict[str, float] = {}

            for fr in fit_results:
                if not np.isfinite(fr.A_K):
                    rows.append({
                        "N_geom": N_geom,
                        "N_int_target": N_int_target,
                        "N_int_actual": geom.N_int_actual,
                        "L_dimless": geom.L_dimless_full,
                        "d_min_dimless": geom.d_min_full,
                        "fit_method": fr.fit_method,
                        "plateau_frac": fr.plateau_frac,
                        "n_plateau": fr.n_plateau,
                        "A_K": np.nan,
                        "A_spread": np.nan,
                        "A_ratio": np.nan,
                        "a_ref_dimless": np.nan,
                        "a0_m": np.nan,
                        "a0_over_rc": np.nan,
                        "lambda_K": np.nan,
                        "p_exp": np.nan,
                        "root_count": 0,
                        "min_root_count": 0,
                        "root_choice": "none",
                        "a_star_m": np.nan,
                        "a_star_over_rc": np.nan,
                        "E_star_J": np.nan,
                        "delta_lambda_over_rc": np.nan,
                        "is_min": False,
                        "status": "inconclusive",
                        "notes": "A_K extraction failed for this window",
                    })
                    continue

                a0 = math.sqrt(fr.A_K / np.pi) * Gamma_0_input / v_swirl
                a0_over_rc = a0 / r_c_canon
                A_ratio = fr.A_K / A_req
                print(f"  Fit {fr.fit_method:>12s}: A_K={fr.A_K:.8f}, A/A_req={A_ratio:.6f}, a0/r_c={a0_over_rc:.6f}")

                for lam_K in LAMBDA_LIST:
                    for p_exp in P_LIST:
                        candidates = find_root_candidates(fr.A_K, fr.a_K, geom.L_dimless_full, geom.d_min_full, lam_K, p_exp)
                        a_star, is_min, E_star, root_count, min_root_count, root_choice = choose_root(candidates, a0, BRANCH_MODE)
                        a_star_over_rc = a_star / r_c_canon if np.isfinite(a_star) else np.nan
                        if lam_K == 0.0:
                            baseline_by_fit[fr.fit_method] = a_star_over_rc
                        baseline = baseline_by_fit.get(fr.fit_method, np.nan)
                        delta_lambda_over_rc = a_star_over_rc - baseline if np.isfinite(a_star_over_rc) and np.isfinite(baseline) else np.nan
                        status = classify_run(A_ratio, a_star_over_rc, is_min)
                        notes = []
                        if fr.fit_method.startswith("plateau"):
                            notes.append(f"n_plateau={fr.n_plateau}")
                        if geom.N_int_actual < geom.N_geom:
                            notes.append("Biot-Savart downsampled")
                        if lam_K == 0.0:
                            notes.append("no-contact case")
                        rows.append({
                            "N_geom": N_geom,
                            "N_int_target": N_int_target,
                            "N_int_actual": geom.N_int_actual,
                            "L_dimless": geom.L_dimless_full,
                            "d_min_dimless": geom.d_min_full,
                            "fit_method": fr.fit_method,
                            "plateau_frac": fr.plateau_frac,
                            "n_plateau": fr.n_plateau,
                            "A_K": fr.A_K,
                            "A_spread": fr.A_spread,
                            "A_ratio": A_ratio,
                            "a_ref_dimless": fr.a_ref,
                            "a0_m": a0,
                            "a0_over_rc": a0_over_rc,
                            "lambda_K": lam_K,
                            "p_exp": p_exp,
                            "root_count": root_count,
                            "min_root_count": min_root_count,
                            "root_choice": root_choice,
                            "a_star_m": a_star,
                            "a_star_over_rc": a_star_over_rc,
                            "E_star_J": E_star,
                            "delta_lambda_over_rc": delta_lambda_over_rc,
                            "is_min": is_min,
                            "status": status,
                            "notes": "; ".join(notes),
                        })

    csv_path = os.path.join(OUTPUT_DIR, "robustness_summary_v2.csv")
    write_csv(rows, csv_path)
    if SAVE_SUMMARY_PLOTS:
        save_summary_plots(rows, OUTPUT_DIR)
    write_best_estimate(rows, OUTPUT_DIR)

    print("\n" + "=" * 78)
    print("Sweep complete")
    print(f"CSV summary        : {csv_path}")
    print(f"Best-estimate CSV  : {os.path.join(OUTPUT_DIR, 'final_best_estimate.csv')}")
    print(f"Best-estimate TXT  : {os.path.join(OUTPUT_DIR, 'final_best_estimate.txt')}")
    print(f"Best-estimate TeX  : {os.path.join(OUTPUT_DIR, 'final_best_estimate.tex')}")
    print(f"Plots              : {OUTPUT_DIR}")
    print("=" * 78)

    stable_rows = [r for r in rows if r["status"] == "stable"]
    if stable_rows:
        print("\nStable runs (first 10):")
        for r in stable_rows[:10]:
            print(
                f"  Ng={r['N_geom']:>5d}, Ni={r['N_int_actual']:>5d}, fit={r['fit_method']:<12s}, "
                f"lambda={r['lambda_K']:<7g}, A/Areq={r['A_ratio']:.5f}, a*/r_c={r['a_star_over_rc']:.5f}"
            )
    else:
        print("\nNo runs met the current stable criterion")


if __name__ == "__main__":
    main()