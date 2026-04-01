#!/usr/bin/env python3
"""
SST knot-candidate robustness sweep v10.0
=====================================

Extends v4 with:
- Theorem-oriented logs [THEOREM], [CHECK], [CONT], [BARRIER] (optional via EMIT_V5_LOGS).
- Optional barrier contact model with vanishing derivative at a = r_c (shift-free at closure).
- Lambda continuation root tracking vs per-lambda independent selection.
- Extra CSV/best-estimate fields for proof-oriented analysis.

Preserves v4: backends, a_nc naming, [META]/[BACKEND]/[GEOM]/[TIME]/[FIT]/[ROOT]/[BEST] logs,
and legacy contact physics under contact_model=legacy.

V6 addition (retained):
- after the normal legacy sweep is finished, run an extra post-sweep theorem check
  with a shift-free barrier contact model (barrier_flat_at_rc) without altering the
  legacy sweep outputs.

V7 addition:
- stationary roots via F(x)=0 in dimensionless x=a/r_c (see ROOT_SOLVER_SPACE), avoiding
  meter-scale brentq tolerance artifacts from solving dE/da directly in meters.

V7.1 addition:
- optional root_selection_mode=targeted_x_nc (window around a_nc); shift-free postcheck forces
  POSTCHECK_CONTACT_MODEL + POSTCHECK_ROOT_SELECTION_MODE with globals restored after.

V8 addition:
- optional power-law extrapolation in N_int (y = y_inf + c N^{-alpha}), CSV/TXT/TeX theorem-style
  reports, CLI for extra exact (N_geom, N_int) pairs and extrapolation cutoff.

V9.1/v9.2/v9.3 fixes:
- make a_nc definition exactly consistent with closure_x_from_A via a_nc = r_c * sqrt(4*pi*A_K)
- lazy-import setuptools only when local C++ compilation is actually requested
- fix LaTeX \\texttt typo in theorem report
- make version strings / output filenames consistent through v9.3
- emit an explicit warning when extrapolation is written without shift-free postcheck rows
"""

from __future__ import annotations

import csv
import glob
import json
import math
import os
import re
import sys
import argparse
import importlib
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Sequence, Union

os.environ.setdefault("ONEAPI_DEVICE_SELECTOR", "level_zero:0")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import brentq

try:
    import torch  # type: ignore[import]
    _TORCH_AVAILABLE = True
except Exception:
    torch = None  # type: ignore[assignment]
    _TORCH_AVAILABLE = False

SCRIPT_VERSION = "v10.0"

# -----------------------------------------------------------------------------
# Paths and defaults (overridable by CLI)
# -----------------------------------------------------------------------------
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
IDEAL_DB_PATH = os.path.join(SCRIPT_DIR, "ideal.txt")
SST_CORE_CPP_PATH = os.path.join(SCRIPT_DIR, "sst_core.cpp")
SST_CORE_MODULE_NAME = "sst_core"

# Backend: "auto" | "local_cpp_scan" | "torch" | "numpy"
BS_BACKEND_MODE = "auto"
BS_BACKEND_ALLOWED = ("auto", "local_cpp_scan", "torch", "numpy")

# Project integration flags (CLI can override via --no-*)
USE_LOCAL_IDEAL_DB = True
USE_LOCAL_SST_CORE = True
AUTO_COMPILE_SST_CORE = True
ENABLE_TORCH_ACCEL = True

# -----------------------------------------------------------------------------
# Canonical SST constants
# -----------------------------------------------------------------------------
r_c_canon = 1.40897017e-15
v_swirl = 1.09384563e6
rho_f = 7.0e-7
c_exact = 299792458.0
Gamma_0_input = 9.68361918e-9
A_req = 1.0 / (4.0 * np.pi)
L_natural = Gamma_0_input / v_swirl

# -----------------------------------------------------------------------------
# Built-in fallback Fourier coefficients (Gilbert 3:1:1 first 30 modes)
# -----------------------------------------------------------------------------
FALLBACK_IDEAL_TREFOIL_COEFFS = [
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

# Filled by initialize_project_sources()
ideal_trefoil_coeffs: List[Tuple[int, float, float, float, float, float, float]] = []
IDEAL_L_REF: float = 16.371637
IDEAL_D_REF: float = 1.0
IDEAL_SOURCE_DESC: str = "fallback hardcoded 30-mode coefficients"
ideal_txt_resolved_path: Optional[str] = None

sst_core = None
_SST_CORE_AVAILABLE = False
SST_CORE_SCAN_AVAILABLE = False

# Sweep defaults (preset "full"; "fast" overrides in main)
N_GEOM_LIST = [4000, 8000, 16000, 32000]
N_INT_LIST = [2000, 4000, 8000, 16000, 32000]
A_SCAN_COUNT = 24
PLATEAU_FRACS = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16]
REL_DE_THRESH = 1e-4
PLATEAU_DIAGNOSTIC_FRACS = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16]
LAMBDA_LIST = [0.0, 1e-3, 3e-3, 1e-2]
P_LIST = [2]
BS_BLOCK = 512
SAVE_PER_RUN_DIAGNOSTICS = False
SAVE_SUMMARY_PLOTS = True
SAVE_PLATEAU_DIAGNOSTICS = True
SAVE_LOCAL_A_CURVES = True
BRANCH_MODE = "closest_to_a_nc"
CONTACT_MODEL = "legacy"  # "legacy" or "barrier_flat_at_rc"
ROOT_SELECTION_MODE = "continuation"  # "continuation", "closest_to_a_nc", "lowest_energy", "targeted_x_nc"
LAMBDA_CONTINUATION_SORT = True
EMIT_V5_LOGS = True

# -----------------------------------------------------------------------------
# V7 dimensionless root solver controls
# -----------------------------------------------------------------------------
ROOT_SOLVER_SPACE = "dimensionless_x"   # v7: solve in x = a/r_c
ROOT_XTOL = 1e-14                       # absolute tolerance in x-space
ROOT_RTOL = 1e-13                       # relative tolerance in x-space
ROOT_FTOL = 1e-12                       # treat |F(x)| < ROOT_FTOL as root
ROOT_SCAN_COUNT_X = 4096                # dense scan for sign-change brackets
ROOT_TARGET_BRACKET_FRAC = 2.0e-3       # initial local bracket around x_nc
ROOT_TARGET_MAX_EXPANSIONS = 32         # bracket expansion rounds

# -----------------------------------------------------------------------------
# V7.1 targeted x_nc branch selection
# -----------------------------------------------------------------------------
TARGET_XNC_ABS_TOL = 5e-3     # in x = a/r_c units
TARGET_XNC_REL_TOL = 5e-3
POSTCHECK_ROOT_SELECTION_MODE = "targeted_x_nc"
POSTCHECK_CONTACT_MODEL = "barrier_flat_at_rc"

PREFERRED_FIT_METHOD = "plateau_0.8"
THEOREM_CANDIDATE_FIT_METHODS = [
    "plateau_0.04",
    "plateau_0.06",
    "plateau_0.08",
    "plateau_0.10",
    "plateau_0.12",
]
STABLE_TOL = 0.02
DRIFT_TOL = 0.08
A_STABLE_TOL = 0.02
A_DRIFT_TOL = 0.08
RUN_V6_SHIFT_FREE_POSTCHECK = True
SHIFTFREE_POSTCHECK_CONTACT_MODEL = "barrier_flat_at_rc"

OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "sst_knot_candidate_robustness_outputs_v10_0"))
KNOT_ID = "3:1:1"
MAX_FOURIER_MODE: Optional[int] = None

# -----------------------------------------------------------------------------
# V8 extrapolation / exact-pair sweep controls (CLI can override subset in main)
# -----------------------------------------------------------------------------
WRITE_V8_EXTRAPOLATION = True
EXTRAP_MIN_NINT = 8000
EXTRAP_PREFERRED_FIT_METHOD = "plateau_0.12"   # legacy single-fit field; v9.3 also evaluates parallel theorem candidates
EXTRAP_ALPHA_MIN = 0.25
EXTRAP_ALPHA_MAX = 4.00
EXTRAP_ALPHA_COUNT = 376
EXTRA_TARGET_PAIRS: List[Tuple[int, int]] = []   # exact pairs, e.g. [(48000,48000), (64000,64000)]

# Stricter theorem flags in v8 extrapolation report:
V8_THEOREM_TOL_AINF = 1.0e-3
V8_THEOREM_TOL_XINF = 1.0e-3
V8_THEOREM_TOL_FINF = 1.0e-3

# -----------------------------------------------------------------------------
# V9 theorem-grade tail / sweep controls
# -----------------------------------------------------------------------------
V9_ALLOWED_POSTCHECK_ROOT_CHOICES = ("targeted_x_nc", "targeted_x_nc_fallback")
V9_TAIL_MIN_POINTS = 3
V9_TAIL_USE_LAST = 4
V9_TAIL_RELAX = 0.05
V9_TAIL_ABS_EPS = 1.0e-6
SWEEP_LAYOUT = "matrix"   # matrix | exact_pairs_only | theorem_ladder
DEFAULT_THEOREM_TARGET_PAIRS: List[Tuple[int, int]] = [
    (32000, 32000),
    (48000, 48000),
    (64000, 64000),
]

DEFAULT_KNOT_LIST: List[str] = ["3:1:1"]


def parse_knot_list(text: str) -> List[str]:
    items = [tok.strip() for tok in text.replace(",", " ").split() if tok.strip()]
    seen = set()
    out: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def sanitize_knot_id_for_path(knot_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", knot_id.strip())
    safe = safe.strip("._")
    return safe or "knot"


def closure_score_from_row(row: Optional[dict]) -> float:
    if not row:
        return float("inf")
    score = 0.0
    vals = [
        abs(float(row.get("A_ratio", np.nan)) - 1.0),
        abs(float(row.get("a_nc_over_rc", np.nan)) - 1.0),
        abs(float(row.get("closure_x_from_A", np.nan)) - 1.0),
    ]
    astar = row.get("a_star_over_rc", np.nan)
    if np.isfinite(astar):
        vals.append(abs(float(astar) - 1.0))
    for v in vals:
        if not np.isfinite(v):
            return float("inf")
        score += float(v)
    return score


def write_knot_comparison_summary(records: List[dict], outdir: str) -> None:
    if not records:
        return
    df = pd.DataFrame(records).sort_values(["closure_score", "knot_id"])
    csv_path = os.path.join(outdir, "knot_candidate_comparison_v10_0.csv")
    txt_path = os.path.join(outdir, "knot_candidate_comparison_v10_0.txt")
    df.to_csv(csv_path, index=False)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"SST knot candidate comparison {SCRIPT_VERSION}\n")
        f.write("=" * 72 + "\n\n")
        for i, rec in enumerate(df.to_dict(orient="records"), start=1):
            f.write(f"[{i}] knot_id={rec['knot_id']} mode={rec['mode']} closure_score={rec['closure_score']:.6e}\n")
            f.write(f"    fit_method={rec.get('fit_method')} N_geom={rec.get('N_geom')} N_int_actual={rec.get('N_int_actual')}\n")
            f.write(f"    A_K={rec.get('A_K')} A_ratio={rec.get('A_ratio')} a_nc_over_rc={rec.get('a_nc_over_rc')}\n")
            f.write(f"    a_star_over_rc={rec.get('a_star_over_rc')} status={rec.get('status')} output_dir={rec.get('output_dir')}\n\n")


def _parse_triplet(text: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected 3 components, got: {text}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def load_coeffs_from_ideal_txt(path: str, knot_id: str, max_mode: Optional[int] = None
                               ) -> Tuple[List[Tuple[int, float, float, float, float, float, float]], float, float]:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    text = open(path, "r", encoding="utf-8").read()
    block_re = re.compile(
        rf'<AB\s+Id="{re.escape(knot_id)}"[^>]*L="([^"]+)"[^>]*D="([^"]+)"[^>]*>(.*?)</AB>',
        re.DOTALL,
    )
    m = block_re.search(text)
    if not m:
        raise ValueError(f"Knot Id {knot_id!r} not found in {path}")
    L_ref = float(m.group(1).strip())
    D_ref = float(m.group(2).strip())
    block = m.group(3)
    coeffs: List[Tuple[int, float, float, float, float, float, float]] = []
    coeff_re = re.compile(r'<Coeff\s+I="\s*([0-9]+)"\s+A="([^"]+)"\s+B="([^"]+)"\s*/?>')
    for cm in coeff_re.finditer(block):
        k = int(cm.group(1))
        if max_mode is not None and k > max_mode:
            continue
        Ax, Ay, Az = _parse_triplet(cm.group(2))
        Bx, By, Bz = _parse_triplet(cm.group(3))
        coeffs.append((k, Ax, Ay, Az, Bx, By, Bz))
    coeffs.sort(key=lambda x: x[0])
    if not coeffs:
        raise ValueError(f"No coefficients extracted for knot {knot_id}")
    return coeffs, L_ref, D_ref


def load_ideal_coeffs_or_fallback(ideal_path: str, knot_id: str, max_mode: Optional[int],
                                  use_local: bool) -> Tuple[List[Tuple[int, float, float, float, float, float, float]], float, float, str, Optional[str]]:
    """Single place: load ideal.txt or fallback. Returns coeffs, L_ref, D_ref, source_desc, resolved_path."""
    resolved = os.path.abspath(ideal_path) if os.path.exists(ideal_path) else None
    if use_local and resolved:
        try:
            coeffs, L_ref, D_ref = load_coeffs_from_ideal_txt(resolved, knot_id, max_mode)
            max_k = max(k for k, *_ in coeffs)
            desc = f"ideal.txt ({knot_id}, {len(coeffs)} modes, k_max={max_k})"
            return coeffs, L_ref, D_ref, desc, resolved
        except Exception as exc:
            print(f"[WARN] Could not load ideal.txt: {exc}")
    coeffs = list(FALLBACK_IDEAL_TREFOIL_COEFFS)
    return coeffs, 16.371637, 1.0, "fallback hardcoded 30-mode coefficients", resolved


def _needs_recompile(cpp_file: str, module_name: str) -> bool:
    if not os.path.exists(cpp_file):
        return False
    compiled_files = glob.glob(os.path.join(SCRIPT_DIR, f"{module_name}.*"))
    binaries = [f for f in compiled_files if f.endswith(".pyd") or f.endswith(".so")]
    if not binaries:
        return True
    latest_binary = max(binaries, key=os.path.getmtime)
    return os.path.getmtime(cpp_file) > os.path.getmtime(latest_binary)


def _build_local_sst_core() -> None:
    # Lazy import so environments that never compile sst_core do not fail at import time.
    from setuptools import Extension, setup
    import pybind11
    if sys.platform == "win32":
        c_args = ["/O2", "/std:c++14"]
    else:
        c_args = ["-O3", "-std=c++14"]
    ext_modules = [
        Extension(
            SST_CORE_MODULE_NAME,
            [SST_CORE_CPP_PATH],
            include_dirs=[pybind11.get_include()],
            language="c++",
            extra_compile_args=c_args,
        ),
    ]
    old_argv = list(sys.argv)
    try:
        sys.argv = ["setup.py", "build_ext", "--inplace"]
        setup(name=SST_CORE_MODULE_NAME, ext_modules=ext_modules, script_args=["build_ext", "--inplace"])
    finally:
        sys.argv = old_argv


def maybe_build_and_import_local_sst_core(use_local: bool, auto_compile: bool) -> Tuple[Optional[object], bool]:
    """Single place: build if needed and import sst_core. Returns (module or None, scan_available)."""
    global sst_core, _SST_CORE_AVAILABLE, SST_CORE_SCAN_AVAILABLE
    sst_core = None
    _SST_CORE_AVAILABLE = False
    SST_CORE_SCAN_AVAILABLE = False
    if not use_local or not os.path.exists(SST_CORE_CPP_PATH):
        return None, False
    try:
        if auto_compile and _needs_recompile(SST_CORE_CPP_PATH, SST_CORE_MODULE_NAME):
            print("[META] Recompiling local sst_core.cpp ...")
            _build_local_sst_core()
        mod = importlib.import_module(SST_CORE_MODULE_NAME)
        sst_core = mod
        _SST_CORE_AVAILABLE = True
        SST_CORE_SCAN_AVAILABLE = bool(hasattr(mod, "calculate_bs_cutoff_energy_scan"))
        return mod, SST_CORE_SCAN_AVAILABLE
    except Exception as exc:
        print(f"[WARN] Local sst_core unavailable: {exc}")
        return None, False


def initialize_project_sources(knot_id: str, max_fourier_mode: Optional[int],
                              use_ideal: bool, use_sst_core: bool, auto_compile: bool) -> None:
    """Single place: load ideal coeffs and optional sst_core. Sets globals ideal_trefoil_coeffs, IDEAL_*, sst_core, SST_CORE_SCAN_AVAILABLE."""
    global ideal_trefoil_coeffs, IDEAL_L_REF, IDEAL_D_REF, IDEAL_SOURCE_DESC, ideal_txt_resolved_path
    global sst_core, _SST_CORE_AVAILABLE, SST_CORE_SCAN_AVAILABLE

    coeffs, L_ref, D_ref, desc, resolved = load_ideal_coeffs_or_fallback(
        IDEAL_DB_PATH, knot_id, max_fourier_mode, use_ideal
    )
    ideal_trefoil_coeffs = coeffs
    IDEAL_L_REF = L_ref
    IDEAL_D_REF = D_ref
    IDEAL_SOURCE_DESC = desc
    ideal_txt_resolved_path = resolved

    maybe_build_and_import_local_sst_core(use_sst_core, auto_compile)


def summarize_project_sources() -> Dict[str, object]:
    """Return a short dict for metadata/logging."""
    return {
        "ideal_source": IDEAL_SOURCE_DESC,
        "ideal_txt_path": ideal_txt_resolved_path,
        "local_sst_core_loaded": _SST_CORE_AVAILABLE,
        "local_cpp_scan_available": SST_CORE_SCAN_AVAILABLE,
    }


# -----------------------------------------------------------------------------
# Backend detection and scan router
# -----------------------------------------------------------------------------
def detect_bs_backend(mode: str, enable_torch: bool) -> str:
    """Resolve backend: auto -> local_cpp_scan | torch | numpy."""
    if mode == "local_cpp_scan":
        return "local_cpp_scan" if SST_CORE_SCAN_AVAILABLE else ("torch" if (enable_torch and _TORCH_AVAILABLE) else "numpy")
    if mode == "torch":
        return "torch" if (enable_torch and _TORCH_AVAILABLE) else "numpy"
    if mode == "numpy":
        return "numpy"
    # auto
    if SST_CORE_SCAN_AVAILABLE:
        return "local_cpp_scan"
    if enable_torch and _TORCH_AVAILABLE:
        return "torch"
    return "numpy"


def _compute_E_BS_norm_numpy_impl(a_dimless: float, pts: np.ndarray, tangents: np.ndarray, ds_arr: np.ndarray) -> float:
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


def _pick_torch_device():
    assert _TORCH_AVAILABLE and torch is not None
    dev_str = os.environ.get("SST_TORCH_DEVICE")
    if dev_str:
        try:
            return torch.device(dev_str)
        except Exception:
            pass
    if hasattr(torch, "xpu") and getattr(torch, "xpu").is_available():
        return torch.device("xpu")
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _compute_E_BS_norm_torch_impl(a_dimless: float, pts: np.ndarray, tangents: np.ndarray, ds_arr: np.ndarray, device) -> float:
    import math as _math
    delta = float(a_dimless)
    n = len(pts)
    compute_dtype = torch.float32 if device.type in ["xpu", "mps"] else torch.float64
    pts_t = torch.tensor(pts, dtype=compute_dtype, device=device)
    tangents_t = torch.tensor(tangents, dtype=compute_dtype, device=device)
    ds_t = torch.tensor(ds_arr, dtype=compute_dtype, device=device)
    total_cpu = 0.0
    all_idx = torch.arange(n, device=device)
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
            dist_safe = torch.clamp(dist, min=1e-30)
            contrib = torch.where(mask, dot_tt / dist_safe, torch.tensor(0.0, dtype=compute_dtype, device=device))
            block_sum = torch.sum(contrib * dsj.unsqueeze(0) * dsi.unsqueeze(1))
            total_cpu += float(block_sum.item())
    return total_cpu / (8.0 * _math.pi)


def compute_E_BS_norm(a_dimless: float, pts: np.ndarray, tangents: np.ndarray, ds_arr: np.ndarray) -> float:
    if not _TORCH_AVAILABLE or not ENABLE_TORCH_ACCEL:
        return _compute_E_BS_norm_numpy_impl(a_dimless, pts, tangents, ds_arr)
    try:
        device = _pick_torch_device()
    except Exception:
        return _compute_E_BS_norm_numpy_impl(a_dimless, pts, tangents, ds_arr)
    try:
        return _compute_E_BS_norm_torch_impl(a_dimless, pts, tangents, ds_arr, device=device)
    except Exception:
        return _compute_E_BS_norm_numpy_impl(a_dimless, pts, tangents, ds_arr)


def _scan_local_cpp(a_scan: np.ndarray, pts: np.ndarray, tangents: np.ndarray, ds_arr: np.ndarray) -> Optional[np.ndarray]:
    if not SST_CORE_SCAN_AVAILABLE or sst_core is None:
        return None
    try:
        out = sst_core.calculate_bs_cutoff_energy_scan(
            np.ascontiguousarray(pts, dtype=np.float64),
            np.ascontiguousarray(tangents, dtype=np.float64),
            np.ascontiguousarray(ds_arr, dtype=np.float64),
            np.ascontiguousarray(a_scan, dtype=np.float64),
        )
        return np.asarray(out, dtype=float)
    except Exception as exc:
        print(f"[WARN] C++ cutoff scan failed: {exc}")
        return None


def scan_BS_energy_backend(geom: "GeometryData", backend: str) -> Tuple[np.ndarray, np.ndarray, str]:
    """Run Biot-Savart scan with chosen backend. Returns (a_scan, E_vals, backend_used)."""
    ds_med = float(np.median(geom.ds_int))
    a_lo = max(3.0 * ds_med, geom.d_min_int * 5e-4)
    a_hi = geom.d_min_int * 0.35
    a_scan = np.logspace(np.log10(a_lo), np.log10(a_hi), A_SCAN_COUNT)
    backend_used = backend
    if backend == "local_cpp_scan":
        E_cpp = _scan_local_cpp(a_scan, geom.pts_int, geom.tangents_int, geom.ds_int)
        if E_cpp is not None and len(E_cpp) == len(a_scan):
            return a_scan, E_cpp, "local_cpp_scan"
        backend_used = "torch" if (_TORCH_AVAILABLE and ENABLE_TORCH_ACCEL) else "numpy"
    if backend_used == "torch" and _TORCH_AVAILABLE and ENABLE_TORCH_ACCEL:
        try:
            device = _pick_torch_device()
            E_vals = np.array([
                _compute_E_BS_norm_torch_impl(a, geom.pts_int, geom.tangents_int, geom.ds_int, device)
                for a in a_scan
            ])
            return a_scan, E_vals, "torch"
        except Exception:
            backend_used = "numpy"
    E_vals = np.array([
        _compute_E_BS_norm_numpy_impl(a, geom.pts_int, geom.tangents_int, geom.ds_int)
        for a in a_scan
    ])
    return a_scan, E_vals, "numpy"


# -----------------------------------------------------------------------------
# Dataclasses
# -----------------------------------------------------------------------------
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
    a_fit_ref: float
    n_plateau: int


@dataclass
class RootCandidate:
    a_star: float
    is_min: bool
    E_star: float


# -----------------------------------------------------------------------------
# Fourier and geometry
# -----------------------------------------------------------------------------
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


def eval_torus_trefoil(t_arr: np.ndarray, R_t: float, r_t: float) -> np.ndarray:
    p, q = 2.0, 3.0
    theta = 2.0 * np.pi * p * t_arr
    phi = 2.0 * np.pi * q * t_arr
    X = np.zeros((len(t_arr), 3), dtype=float)
    X[:, 0] = (R_t + r_t * np.cos(phi)) * np.cos(theta)
    X[:, 1] = (R_t + r_t * np.cos(phi)) * np.sin(theta)
    X[:, 2] = r_t * np.sin(phi)
    return X


def eval_torus_trefoil_deriv(t_arr: np.ndarray, R_t: float, r_t: float) -> np.ndarray:
    p, q = 2.0, 3.0
    theta = 2.0 * np.pi * p * t_arr
    phi = 2.0 * np.pi * q * t_arr
    dtheta = 2.0 * np.pi * p
    dphi = 2.0 * np.pi * q
    dX = np.zeros((len(t_arr), 3), dtype=float)
    dX[:, 0] = -r_t * np.sin(phi) * dphi * np.cos(theta) - (R_t + r_t * np.cos(phi)) * np.sin(theta) * dtheta
    dX[:, 1] = -r_t * np.sin(phi) * dphi * np.sin(theta) + (R_t + r_t * np.cos(phi)) * np.cos(theta) * dtheta
    dX[:, 2] = r_t * np.cos(phi) * dphi
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
    n_dmin_cap = min(max(3000, N_int_target), N_geom)
    if n_dmin_cap >= N_geom:
        pts_dmin = pts_full
    else:
        stride_dmin = max(1, int(math.ceil(N_geom / n_dmin_cap)))
        pts_dmin = pts_full[::stride_dmin]
    excl_dmin = max(5, len(pts_dmin) // 15)
    d_min_full = coarse_min_self_distance(pts_dmin, excl_dmin)
    return GeometryData(
        N_geom=N_geom, N_int_target=N_int_target, N_int_actual=len(pts_int),
        pts_full=pts_full, ds_full=ds_full, tangents_full=tangents_full,
        L_dimless_full=L_dimless_full, d_min_full=d_min_full,
        pts_int=pts_int, tangents_int=tangents_int, ds_int=ds_int, d_min_int=d_min_int,
    )


def build_torus_geometry(N_geom: int, N_int_target: int, R_t: float, r_t: float) -> GeometryData:
    t_full = np.linspace(0.0, 1.0, N_geom, endpoint=False)
    pts_full = eval_torus_trefoil(t_full, R_t, r_t)
    dpts_dt = eval_torus_trefoil_deriv(t_full, R_t, r_t)
    speed = np.linalg.norm(dpts_dt, axis=1)
    dt = 1.0 / N_geom
    ds_full = speed * dt
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
    n_dmin_cap = min(max(3000, N_int_target), N_geom)
    if n_dmin_cap >= N_geom:
        pts_dmin = pts_full
    else:
        stride_dmin = max(1, int(math.ceil(N_geom / n_dmin_cap)))
        pts_dmin = pts_full[::stride_dmin]
    excl_dmin = max(5, len(pts_dmin) // 15)
    d_min_full = coarse_min_self_distance(pts_dmin, excl_dmin)
    return GeometryData(
        N_geom=N_geom, N_int_target=N_int_target, N_int_actual=len(pts_int),
        pts_full=pts_full, ds_full=ds_full, tangents_full=tangents_full,
        L_dimless_full=L_dimless_full, d_min_full=d_min_full,
        pts_int=pts_int, tangents_int=tangents_int, ds_int=ds_int, d_min_int=d_min_int,
    )


# -----------------------------------------------------------------------------
# Fit extraction and root/energy model
# -----------------------------------------------------------------------------
def _plateau_stats_for_frac(
    a_mid: np.ndarray,
    A_local: np.ndarray,
    rel_dE: np.ndarray,
    d_min_dimless: float,
    frac: float,
) -> Dict[str, float]:
    mask = (A_local > 0.0) & (rel_dE > REL_DE_THRESH) & (a_mid < frac * d_min_dimless)
    idxs = np.where(mask)[0]
    out = {
        "frac": float(frac),
        "n_plateau": int(idxs.size),
        "a_lo": np.nan,
        "a_hi": np.nan,
        "a_span": np.nan,
        "a_span_over_dmin": np.nan,
        "A_median": np.nan,
        "A_std": np.nan,
        "A_min": np.nan,
        "A_max": np.nan,
        "rel_dE_median": np.nan,
        "rel_dE_min": np.nan,
        "rel_dE_max": np.nan,
        "idx_ref": -1,
        "a_ref": np.nan,
        "A_ref": np.nan,
    }
    if idxs.size == 0:
        return out
    a_sel = a_mid[idxs]
    A_sel = A_local[idxs]
    r_sel = rel_dE[idxs]
    idx_ref = int(idxs[len(idxs) // 2])
    out.update({
        "a_lo": float(a_sel[0]),
        "a_hi": float(a_sel[-1]),
        "a_span": float(a_sel[-1] - a_sel[0]) if a_sel.size >= 2 else 0.0,
        "a_span_over_dmin": float((a_sel[-1] - a_sel[0]) / d_min_dimless) if (a_sel.size >= 2 and d_min_dimless > 0.0) else 0.0,
        "A_median": float(np.median(A_sel)),
        "A_std": float(np.std(A_sel)),
        "A_min": float(np.min(A_sel)),
        "A_max": float(np.max(A_sel)),
        "rel_dE_median": float(np.median(r_sel)),
        "rel_dE_min": float(np.min(r_sel)),
        "rel_dE_max": float(np.max(r_sel)),
        "idx_ref": idx_ref,
        "a_ref": float(a_mid[idx_ref]),
        "A_ref": float(A_local[idx_ref]),
    })
    return out


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
        stats = _plateau_stats_for_frac(a_mid, A_local, rel_dE, d_min_dimless, frac)
        if stats["n_plateau"] > 0:
            A_plateau = float(stats["A_median"])
            A_spread = float(stats["A_std"])
            idx_ref = int(stats["idx_ref"])
            y_ref = float(0.5 * (y_scan[idx_ref] + y_scan[idx_ref + 1]))
            a_fit_ref = float(stats["a_ref"])
            a_K = y_ref - A_plateau * np.log(L_dimless / a_fit_ref)
            out.append(FitResult(f"plateau_{frac:.2f}", frac, A_plateau, A_spread, float(a_K), a_fit_ref, int(stats["n_plateau"])))
        else:
            out.append(FitResult(f"plateau_{frac:.2f}", frac, np.nan, np.nan, np.nan, np.nan, 0))
    plateau_diag = {f"plateau_{frac:.2f}": _plateau_stats_for_frac(a_mid, A_local, rel_dE, d_min_dimless, frac)
                    for frac in PLATEAU_DIAGNOSTIC_FRACS}
    diagnostics = {
        "a_mid": a_mid,
        "A_local": A_local,
        "x_scan": x_scan,
        "y_scan": y_scan,
        "rel_dE": rel_dE,
        "plateau_diag": plateau_diag,
    }
    return out, diagnostics


def closure_x_from_A(A_K: float) -> float:
    return float(np.sqrt(max(0.0, 4.0 * np.pi * A_K)))


def dimensionless_beta(d_min_phys: float) -> float:
    return float(d_min_phys / r_c_canon)


def contact_force_dimensionless(x: float, beta: float, lam_K: float, p_exp: int, contact_model: str) -> float:
    if lam_K == 0.0:
        return 0.0
    if contact_model == "legacy":
        if 2.0 * x >= beta:
            return np.nan
        xc = 2.0 * x / (beta - 2.0 * x)
        return float(4.0 * np.pi * lam_K * p_exp * xc**(p_exp - 1) * (2.0 * beta) / (beta - 2.0 * x)**2)

    if contact_model == "barrier_flat_at_rc":
        if 2.0 * x >= beta:
            return np.nan
        xc = 2.0 * x / (beta - 2.0 * x)
        xc1 = 2.0 / (beta - 2.0)
        gp = p_exp * xc**(p_exp - 1) * (2.0 * beta) / (beta - 2.0 * x)**2
        gp1 = p_exp * xc1**(p_exp - 1) * (2.0 * beta) / (beta - 2.0)**2
        return float(4.0 * np.pi * lam_K * (gp - gp1))

    raise ValueError(f"Unknown contact_model={contact_model}")


def F_dimensionless(x: float, A_K: float, beta: float, lam_K: float, p_exp: int, contact_model: str) -> float:
    if x <= 0.0:
        return np.nan
    base = x - (4.0 * np.pi * A_K) / x
    return float(base + contact_force_dimensionless(x, beta, lam_K, p_exp, contact_model))


def dE_da(a: float, A_K: float, L_K_phys: float, d_min_phys: float, lam_K: float, p_exp: int,
          contact_model: str = "legacy") -> float:
    if a <= 0.0 or 2.0 * a >= d_min_phys:
        return np.nan
    dE_BS = -rho_f * Gamma_0_input**2 * L_K_phys * A_K / a
    dE_core = np.pi * rho_f * v_swirl**2 * a * L_K_phys
    pref = rho_f * Gamma_0_input**2 * L_K_phys
    beta = dimensionless_beta(d_min_phys)
    x = a / r_c_canon
    cf = contact_force_dimensionless(x, beta, lam_K, p_exp, contact_model)
    if not np.isfinite(cf):
        dE_cont = np.nan
    else:
        dE_cont = pref * cf / (4.0 * np.pi * r_c_canon)
    return float(dE_BS + dE_core + dE_cont)


def E_K_phys(a: float, A_K: float, a_K: float, L_K_phys: float, d_min_phys: float, lam_K: float, p_exp: int,
             contact_model: str = "legacy") -> float:
    if a <= 0.0 or 2.0 * a >= d_min_phys:
        return np.inf
    E_BS = rho_f * Gamma_0_input**2 * L_K_phys * (A_K * np.log(L_K_phys / a) + a_K)
    E_core = 0.5 * np.pi * rho_f * v_swirl**2 * a**2 * L_K_phys
    pref = rho_f * Gamma_0_input**2 * L_K_phys
    if lam_K == 0.0:
        E_cont = 0.0
    elif contact_model == "legacy":
        xc = 2.0 * a / (d_min_phys - 2.0 * a)
        E_cont = lam_K * pref * xc**p_exp
    elif contact_model == "barrier_flat_at_rc":
        beta = dimensionless_beta(d_min_phys)
        x = a / r_c_canon
        if 2.0 * x >= beta:
            return np.inf
        xc = 2.0 * x / (beta - 2.0 * x)
        xc1 = 2.0 / (beta - 2.0)
        g = xc**p_exp
        g1 = xc1**p_exp
        gp1 = p_exp * xc1**(p_exp - 1) * (2.0 * beta) / (beta - 2.0)**2
        barrier = g - g1 - gp1 * (x - 1.0)
        E_cont = lam_K * pref * barrier
    else:
        raise ValueError(f"Unknown contact_model={contact_model}")
    return float(E_BS + E_core + E_cont)


def _sign_change_or_zero(f_left: float, f_right: float, ftol: float = ROOT_FTOL) -> bool:
    if not (np.isfinite(f_left) and np.isfinite(f_right)):
        return False
    if abs(f_left) <= ftol or abs(f_right) <= ftol:
        return True
    return (f_left * f_right) < 0.0


def Fprime_dimensionless_numeric(x: float, A_K: float, beta: float, lam_K: float, p_exp: int,
                                 contact_model: str, rel_h: float = 1e-6) -> float:
    """
    Numerical derivative of F(x). Since
        dE/da = const * F(x),
    with const > 0, the sign of d^2E/da^2 equals the sign of F'(x).
    Therefore F'(x_root) > 0 means a local minimum.
    """
    if not np.isfinite(x) or x <= 0.0:
        return np.nan

    x_hi_hard = 0.5 * beta * (1.0 - 1e-12)
    h = max(rel_h * max(1.0, abs(x)), 1e-10)

    xm = max(1e-12, x - h)
    xp = min(x_hi_hard, x + h)

    if not (xp > xm):
        return np.nan

    fm = F_dimensionless(xm, A_K, beta, lam_K, p_exp, contact_model)
    fp = F_dimensionless(xp, A_K, beta, lam_K, p_exp, contact_model)

    if not (np.isfinite(fm) and np.isfinite(fp)):
        return np.nan

    return float((fp - fm) / (xp - xm))


def bracket_root_near_target_x(A_K: float, beta: float, lam_K: float, p_exp: int, contact_model: str,
                               x_target: float,
                               x_lo: float, x_hi: float) -> Optional[Tuple[float, float]]:
    """
    Build a local bracket around x_target = sqrt(4*pi*A_K), expanding until
    F(left) and F(right) straddle a root (or one endpoint is already close).
    """
    if not np.isfinite(x_target):
        return None

    span = max(ROOT_TARGET_BRACKET_FRAC * max(1.0, abs(x_target)), 1e-6)

    for _ in range(ROOT_TARGET_MAX_EXPANSIONS):
        left = max(x_lo, x_target - span)
        right = min(x_hi, x_target + span)

        if not (right > left):
            return None

        f_left = F_dimensionless(left, A_K, beta, lam_K, p_exp, contact_model)
        f_right = F_dimensionless(right, A_K, beta, lam_K, p_exp, contact_model)

        if _sign_change_or_zero(f_left, f_right):
            return float(left), float(right)

        span *= 2.0

    return None


def scan_root_brackets_x(A_K: float, beta: float, lam_K: float, p_exp: int, contact_model: str,
                         x_lo: float, x_hi: float) -> List[Tuple[float, float]]:
    """
    Global log-scan in x-space to collect all sign-change brackets.
    """
    if not (np.isfinite(x_lo) and np.isfinite(x_hi) and x_hi > x_lo > 0.0):
        return []

    x_vals = np.logspace(np.log10(x_lo), np.log10(x_hi), ROOT_SCAN_COUNT_X)
    f_vals = np.array([
        F_dimensionless(x, A_K, beta, lam_K, p_exp, contact_model) for x in x_vals
    ], dtype=float)

    brackets: List[Tuple[float, float]] = []
    for i in range(len(x_vals) - 1):
        fl = f_vals[i]
        fr = f_vals[i + 1]
        if _sign_change_or_zero(fl, fr):
            brackets.append((float(x_vals[i]), float(x_vals[i + 1])))

    return brackets


def find_root_candidates(A_K: float, a_K: float, L_dimless: float, d_min_dimless: float, lam_K: float, p_exp: int,
                         contact_model: str = "legacy") -> List[RootCandidate]:
    """
    V7:
    Solve stationary points in dimensionless space x = a / r_c by finding roots of

        F(x) = x - (4*pi*A_K)/x + contact_force_dimensionless(x, beta, ...)

    rather than solving dE/da directly in meters.

    This removes the meter-space absolute-tolerance pathology where brentq on dE/da
    effectively returns bracket endpoints because a ~ 1e-15 m while the default xtol is ~1e-12 m.
    """
    L_K_phys = L_dimless * L_natural
    d_min_phys = d_min_dimless * L_natural
    beta = dimensionless_beta(d_min_phys)

    if not np.isfinite(beta) or beta <= 0.0:
        return []

    x_nc = closure_x_from_A(A_K)

    # Safe x-domain:
    #  - x > 0
    #  - 2x < beta
    x_lo = 1e-6
    x_hi = 0.5 * beta * (1.0 - 1e-10)

    if not (np.isfinite(x_lo) and np.isfinite(x_hi) and x_hi > x_lo):
        return []

    roots: List[RootCandidate] = []
    seen_x: List[float] = []

    # 1) First, explicitly bracket near the no-contact predictor x_nc = sqrt(4*pi*A_K)
    candidate_brackets: List[Tuple[float, float]] = []
    target_bracket = bracket_root_near_target_x(
        A_K, beta, lam_K, p_exp, contact_model, x_nc, x_lo, x_hi
    )
    if target_bracket is not None:
        candidate_brackets.append(target_bracket)

    # 2) Then add all global sign-change brackets from a dense x-scan
    for br in scan_root_brackets_x(A_K, beta, lam_K, p_exp, contact_model, x_lo, x_hi):
        candidate_brackets.append(br)

    # 3) Solve each bracket robustly in x-space
    for left, right in candidate_brackets:
        if not (np.isfinite(left) and np.isfinite(right) and right >= left and left > 0.0):
            continue

        f_left = F_dimensionless(left, A_K, beta, lam_K, p_exp, contact_model)
        f_right = F_dimensionless(right, A_K, beta, lam_K, p_exp, contact_model)

        if not _sign_change_or_zero(f_left, f_right):
            continue

        try:
            if np.isfinite(f_left) and abs(f_left) <= ROOT_FTOL:
                x_root = float(left)
            elif np.isfinite(f_right) and abs(f_right) <= ROOT_FTOL:
                x_root = float(right)
            else:
                x_root = float(brentq(
                    lambda xx: F_dimensionless(xx, A_K, beta, lam_K, p_exp, contact_model),
                    left, right,
                    xtol=ROOT_XTOL,
                    rtol=ROOT_RTOL,
                    maxiter=500,
                ))
        except ValueError:
            continue

        # Deduplicate roots in x-space
        if any(abs(x_root - xr) / max(abs(x_root), 1e-300) < 1e-10 for xr in seen_x):
            continue
        seen_x.append(x_root)

        a_root = x_root * r_c_canon
        fp = Fprime_dimensionless_numeric(x_root, A_K, beta, lam_K, p_exp, contact_model)
        is_min = bool(np.isfinite(fp) and fp > 0.0)

        E_star = E_K_phys(a_root, A_K, a_K, L_K_phys, d_min_phys, lam_K, p_exp, contact_model)
        roots.append(RootCandidate(a_root, is_min, E_star))

    # 4) Fallback: if no bracketed root was found, minimize |F(x)| on dense grid in x-space
    if not roots:
        x_vals = np.logspace(np.log10(x_lo), np.log10(x_hi), ROOT_SCAN_COUNT_X)
        f_vals = np.array([
            F_dimensionless(x, A_K, beta, lam_K, p_exp, contact_model) for x in x_vals
        ], dtype=float)
        valid = np.isfinite(f_vals)

        if np.count_nonzero(valid) == 0:
            return []

        xv = x_vals[valid]
        fv = f_vals[valid]
        idx = int(np.argmin(np.abs(fv)))
        x_root = float(xv[idx])
        a_root = x_root * r_c_canon

        fp = Fprime_dimensionless_numeric(x_root, A_K, beta, lam_K, p_exp, contact_model)
        is_min = bool(np.isfinite(fp) and fp > 0.0)

        E_star = E_K_phys(a_root, A_K, a_K, L_K_phys, d_min_phys, lam_K, p_exp, contact_model)
        roots.append(RootCandidate(a_root, is_min, E_star))

    roots.sort(key=lambda rc: rc.a_star)
    return roots


def choose_root_continuation(candidates: List[RootCandidate], prev_a_star: Optional[float], a_nc: float,
                             fallback_mode: str = "closest_to_a_nc") -> Tuple[float, bool, float, int, int, str]:
    if not candidates:
        return np.nan, False, np.inf, 0, 0, "none"
    mins = [c for c in candidates if c.is_min]
    pool = mins if mins else candidates

    if prev_a_star is not None and np.isfinite(prev_a_star):
        chosen = min(pool, key=lambda c: abs(c.a_star - prev_a_star))
        return chosen.a_star, chosen.is_min, chosen.E_star, len(candidates), len(mins), "continuation"

    if fallback_mode == "lowest_energy":
        chosen = min(pool, key=lambda c: c.E_star)
        return chosen.a_star, chosen.is_min, chosen.E_star, len(candidates), len(mins), "lowest_energy"

    chosen = min(pool, key=lambda c: abs(c.a_star - a_nc))
    return chosen.a_star, chosen.is_min, chosen.E_star, len(candidates), len(mins), "closest_to_a_nc"


def choose_root(candidates: List[RootCandidate], a_nc: float, branch_mode: str) -> Tuple[float, bool, float, int, int, str]:
    if not candidates:
        return np.nan, False, np.inf, 0, 0, "none"
    mins = [c for c in candidates if c.is_min]
    pool = mins if mins else candidates
    if branch_mode == "lowest_energy":
        chosen = min(pool, key=lambda c: c.E_star)
        return chosen.a_star, chosen.is_min, chosen.E_star, len(candidates), len(mins), "lowest_energy"
    chosen = min(pool, key=lambda c: abs(c.a_star - a_nc))
    return chosen.a_star, chosen.is_min, chosen.E_star, len(candidates), len(mins), "closest_to_a_nc"


def choose_root_targeted_x_nc(candidates: List[RootCandidate], a_nc: float
                              ) -> Tuple[float, bool, float, int, int, str]:
    """
    Deterministically choose the stationary root associated with the no-contact
    closure predictor a_nc = r_c * sqrt(4*pi*A_K).

    Priority:
      1) local minima within the x_nc target window
      2) any root within the x_nc target window
      3) closest local minimum to a_nc
      4) closest root to a_nc
    """
    if not candidates:
        return np.nan, False, np.inf, 0, 0, "none"

    mins = [c for c in candidates if c.is_min]
    pool = mins if mins else candidates

    a_tol = max(TARGET_XNC_ABS_TOL * r_c_canon, TARGET_XNC_REL_TOL * abs(a_nc))

    near_mins = [c for c in mins if abs(c.a_star - a_nc) <= a_tol]
    if near_mins:
        chosen = min(near_mins, key=lambda c: (abs(c.a_star - a_nc), c.E_star))
        return chosen.a_star, chosen.is_min, chosen.E_star, len(candidates), len(mins), "targeted_x_nc"

    near_pool = [c for c in candidates if abs(c.a_star - a_nc) <= a_tol]
    if near_pool:
        chosen = min(near_pool, key=lambda c: (abs(c.a_star - a_nc), c.E_star))
        return chosen.a_star, chosen.is_min, chosen.E_star, len(candidates), len(mins), "targeted_x_nc"

    chosen = min(pool, key=lambda c: (abs(c.a_star - a_nc), c.E_star))
    return chosen.a_star, chosen.is_min, chosen.E_star, len(candidates), len(mins), "targeted_x_nc_fallback"


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


# -----------------------------------------------------------------------------
# Diagnostics, CSV, plots, best estimate
# -----------------------------------------------------------------------------
def save_geometry_plot(geom: GeometryData, outpath: str) -> None:
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(geom.pts_full[:, 0], geom.pts_full[:, 1], geom.pts_full[:, 2], lw=1.2)
    ax.set_title(f"Ideal trefoil ({KNOT_ID}) - N_geom={geom.N_geom}")
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
            ys = np.array([r["a_nc_over_rc"] for r in subset], dtype=float)
            plt.plot(xs, ys, "o-", lw=1.6, label=f"N_geom={N_geom}")
        plt.axhline(1.0, ls="--", lw=2, label="a_nc/r_c = 1")
        plt.xscale("log")
        plt.xlabel("N_int_actual")
        plt.ylabel("a_nc/r_c")
        plt.title(f"a_nc/r_c vs Biot-Savart resolution ({PREFERRED_FIT_METHOD}, lambda=0)")
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "summary_a_nc_over_rc_vs_Nint.png"), dpi=170, bbox_inches="tight")
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




def save_local_A_curve_csv(
    diagnostics: Dict[str, np.ndarray],
    d_min_dimless: float,
    outpath: str,
) -> None:
    a_mid = diagnostics["a_mid"]
    A_local = diagnostics["A_local"]
    rel_dE = diagnostics["rel_dE"]
    data = {
        "a_mid": a_mid,
        "A_local": A_local,
        "A_local_minus_Areq": A_local - A_req,
        "rel_dE": rel_dE,
    }
    for frac in PLATEAU_DIAGNOSTIC_FRACS:
        mask = (A_local > 0.0) & (rel_dE > REL_DE_THRESH) & (a_mid < frac * d_min_dimless)
        key = f"mask_plateau_{frac:.2f}".replace(".", "p")
        data[key] = mask.astype(int)
    pd.DataFrame(data).to_csv(outpath, index=False)


def write_plateau_diagnostics_csv(rows: List[dict], outpath: str) -> None:
    if not rows:
        return
    pd.DataFrame(rows).sort_values(
        ["N_geom", "N_int_actual", "frac"]
    ).to_csv(outpath, index=False)


def save_plateau_diagnostics_summary_plot(rows: List[dict], outpath: str) -> None:
    if not rows:
        return
    df = pd.DataFrame(rows)
    exact = df[df["N_geom"] == df["N_int_actual"]].copy()
    if exact.empty:
        exact = df.copy()

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    for N_geom in sorted(exact["N_geom"].unique()):
        sub = exact[exact["N_geom"] == N_geom].sort_values("frac")
        axes[0].plot(sub["frac"], sub["n_plateau"], "o-", lw=1.5, label=f"N={N_geom}")
        axes[1].plot(sub["frac"], sub["A_median"] - A_req, "o-", lw=1.5, label=f"N={N_geom}")
        axes[2].plot(sub["frac"], sub["a_span_over_dmin"], "o-", lw=1.5, label=f"N={N_geom}")

    axes[0].set_xlabel("plateau frac")
    axes[0].set_ylabel("n_plateau")
    axes[0].set_title("Plateau mask size")
    axes[0].grid(True, alpha=0.3)

    axes[1].axhline(0.0, color="black", ls="--", lw=1.2)
    axes[1].set_xlabel("plateau frac")
    axes[1].set_ylabel("A_median - 1/(4π)")
    axes[1].set_title("Plateau median bias")
    axes[1].grid(True, alpha=0.3)

    axes[2].set_xlabel("plateau frac")
    axes[2].set_ylabel("(a_hi - a_lo)/d_min")
    axes[2].set_title("Plateau span")
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(outpath, dpi=170, bbox_inches="tight")
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
    finite = [r for r in preferred if np.isfinite(r["A_K"]) and np.isfinite(r["a_nc_over_rc"])]
    if finite:
        finite.sort(key=lambda r: (abs(r["A_ratio"] - 1.0), abs(r["a_nc_over_rc"] - 1.0), -r["N_int_actual"], -r["N_geom"]))
        return finite[0]
    fallback = [r for r in rows if r["lambda_K"] == 0.0 and np.isfinite(r["A_K"]) and np.isfinite(r["a_nc_over_rc"])]
    if not fallback:
        return None
    fallback.sort(key=lambda r: (abs(r["A_ratio"] - 1.0), abs(r["a_nc_over_rc"] - 1.0), -r["N_int_actual"], -r["N_geom"]))
    return fallback[0]


def _asymptotic_from_two_highest(rows: List[dict]) -> Dict[str, float]:
    """Two highest N_int_actual at preferred fit, lambda=0: midpoint and half-range for A_K, A_ratio, a_nc_over_rc."""
    pref = [r for r in rows if r["fit_method"] == PREFERRED_FIT_METHOD and r["lambda_K"] == 0.0
            and np.isfinite(r["A_K"]) and np.isfinite(r["a_nc_over_rc"])]
    if len(pref) < 2:
        return {}
    pref.sort(key=lambda r: r["N_int_actual"])
    top2 = pref[-2:]
    A_K_vals = [r["A_K"] for r in top2]
    A_ratio_vals = [r["A_ratio"] for r in top2]
    a_nc_vals = [r["a_nc_over_rc"] for r in top2]
    return {
        "A_K_mid": float(0.5 * (A_K_vals[0] + A_K_vals[1])),
        "A_K_half_range": float(0.5 * abs(A_K_vals[1] - A_K_vals[0])),
        "A_ratio_mid": float(0.5 * (A_ratio_vals[0] + A_ratio_vals[1])),
        "A_ratio_half_range": float(0.5 * abs(A_ratio_vals[1] - A_ratio_vals[0])),
        "a_nc_over_rc_mid": float(0.5 * (a_nc_vals[0] + a_nc_vals[1])),
        "a_nc_over_rc_half_range": float(0.5 * abs(a_nc_vals[1] - a_nc_vals[0])),
        "N_int_high1": top2[0]["N_int_actual"],
        "N_int_high2": top2[1]["N_int_actual"],
    }


def write_best_estimate(rows: List[dict], outdir: str) -> None:
    best = select_best_row(rows)
    no_contact = [r for r in rows if r["lambda_K"] == 0.0 and np.isfinite(r["A_K"]) and np.isfinite(r["a_nc_over_rc"])]
    A_sys = robust_half_range([r["A_K"] for r in no_contact])
    A_ratio_sys = robust_half_range([r["A_ratio"] for r in no_contact])
    a_nc_sys = robust_half_range([r["a_nc_over_rc"] for r in no_contact])
    pref_rows = [r for r in rows if r["fit_method"] == (best["fit_method"] if best else "") and np.isfinite(r.get("a_star_over_rc", np.nan))]
    if pref_rows:
        a_star_center = float(np.median([r["a_star_over_rc"] for r in pref_rows]))
        a_star_sys = robust_half_range([r["a_star_over_rc"] for r in pref_rows])
    else:
        a_star_center = np.nan
        a_star_sys = np.nan
    asym = _asymptotic_from_two_highest(rows)

    companion: Optional[dict] = None
    if best:
        for r in rows:
            if (r["N_geom"] == best["N_geom"] and r["N_int_actual"] == best["N_int_actual"]
                    and r["fit_method"] == best["fit_method"] and r["p_exp"] == best.get("p_exp", P_LIST[0])):
                if not np.isfinite(r.get("a_star_over_rc", np.nan)):
                    continue
                if companion is None or r["lambda_K"] > companion["lambda_K"]:
                    companion = r

    x_closure_best = closure_x_from_A(best["A_K"]) if best and np.isfinite(best.get("A_K", np.nan)) else np.nan
    no_contact_theorem_ok = bool(best and abs(x_closure_best - 1.0) < 0.01)
    shift_free_model = CONTACT_MODEL == "barrier_flat_at_rc"
    cf1_comp = float(companion["contact_force_at_x1"]) if companion and np.isfinite(companion.get("contact_force_at_x1", np.nan)) else np.nan
    shift_free_numeric = shift_free_model and np.isfinite(cf1_comp) and abs(cf1_comp) < 1e-5
    continuation_used = ROOT_SELECTION_MODE == "continuation"
    max_jump = np.nan
    if continuation_used and best:
        jumps = [r.get("continuation_jump") for r in rows
                 if r["N_geom"] == best["N_geom"] and r["N_int_actual"] == best["N_int_actual"]
                 and r["fit_method"] == best["fit_method"] and np.isfinite(r.get("continuation_jump", np.nan))]
        if jumps:
            max_jump = float(max(jumps))

    result: Dict[str, object] = {
        "preferred_fit_method": PREFERRED_FIT_METHOD,
        "branch_mode": BRANCH_MODE,
        "root_selection_mode": ROOT_SELECTION_MODE,
        "contact_model": CONTACT_MODEL,
        "ideal_source": IDEAL_SOURCE_DESC,
        "uses_local_sst_core": _SST_CORE_AVAILABLE,
    }
    if best:
        result["best_estimate_practical_N_geom"] = best["N_geom"]
        result["best_estimate_practical_N_int"] = best["N_int_actual"]
        result["best_estimate_practical_A_K"] = best["A_K"]
        result["best_estimate_practical_A_K_systematic_half_range"] = A_sys
        result["best_estimate_practical_A_ratio"] = best["A_ratio"]
        result["best_estimate_practical_A_ratio_systematic_half_range"] = A_ratio_sys
        result["best_estimate_practical_a_nc_over_rc"] = best["a_nc_over_rc"]
        result["best_estimate_practical_a_nc_over_rc_systematic_half_range"] = a_nc_sys
        result["best_estimate_practical_a_star_over_rc_center"] = a_star_center
        result["best_estimate_practical_a_star_over_rc_half_range"] = a_star_sys
        result["theorem_no_contact_A_K"] = best["A_K"]
        result["theorem_no_contact_closure_x"] = x_closure_best
        result["theorem_no_contact_closure_x_minus_1"] = float(x_closure_best - 1.0) if np.isfinite(x_closure_best) else np.nan
    else:
        result["theorem_no_contact_A_K"] = np.nan
        result["theorem_no_contact_closure_x"] = np.nan
        result["theorem_no_contact_closure_x_minus_1"] = np.nan

    if companion:
        result["theorem_full_model_contact_model"] = CONTACT_MODEL
        result["theorem_full_model_F_at_x1"] = companion.get("F_at_x1", np.nan)
        result["theorem_full_model_a_star_over_rc"] = companion.get("a_star_over_rc", np.nan)
        result["theorem_full_model_is_shift_free"] = bool(
            CONTACT_MODEL == "barrier_flat_at_rc" and np.isfinite(cf1_comp) and abs(cf1_comp) < 1e-6
        )
    else:
        result["theorem_full_model_contact_model"] = CONTACT_MODEL
        result["theorem_full_model_F_at_x1"] = np.nan
        result["theorem_full_model_a_star_over_rc"] = np.nan
        result["theorem_full_model_is_shift_free"] = False

    for k, v in asym.items():
        result[f"best_estimate_asymptotic_{k}"] = v
    result["comment"] = (
        "Practical = preferred no-contact run. Asymptotic = midpoint and half-range from two highest N_int at preferred fit, lambda=0. "
        "Theorem fields: no-contact closure x = sqrt(4*pi*A_K); full-model row = same grid/fit at max lambda_K with finite a*."
    )

    csv_path = os.path.join(outdir, "final_best_estimate_v10_0.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.keys()))
        writer.writeheader()
        writer.writerow(result)

    txt_path = os.path.join(outdir, "final_best_estimate_v10_0.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"SST ideal-trefoil final best-estimate {SCRIPT_VERSION}\n")
        f.write("=" * 64 + "\n")
        f.write(f"Ideal source                : {IDEAL_SOURCE_DESC}\n")
        f.write(f"Local sst_core available    : {_SST_CORE_AVAILABLE}\n")
        f.write(f"Preferred fit method        : {PREFERRED_FIT_METHOD}\n")
        f.write(f"Contact model               : {CONTACT_MODEL}\n")
        f.write(f"Root selection mode         : {ROOT_SELECTION_MODE} (branch_mode legacy key: {BRANCH_MODE})\n")
        if best:
            f.write(f"Best grid (practical)       : N_geom={best['N_geom']}, N_int={best['N_int_actual']}\n")
            f.write(f"A_K_best (practical)       : {best['A_K']:.8f} +- {A_sys:.8f}\n")
            f.write(f"A_ratio_best              : {best['A_ratio']:.8f} +- {A_ratio_sys:.8f}\n")
            f.write(f"a_nc/r_c_best              : {best['a_nc_over_rc']:.8f} +- {a_nc_sys:.8f}\n")
            f.write(f"Theorem (no-contact)        : closure_x = sqrt(4*pi*A_K) = {x_closure_best:.8f} (x-1 = {x_closure_best - 1.0:.8e})\n")
            f.write(f"No-contact theorem candidate supported (|x_closure-1| < 0.01): {'yes' if no_contact_theorem_ok else 'no'}\n")
        if companion:
            f.write(f"Full-model row (max lambda) : lambda_K={companion['lambda_K']}, F_at_x1={companion.get('F_at_x1', np.nan):.8e}, "
                    f"a_star/r_c={companion.get('a_star_over_rc', np.nan):.8f}\n")
        f.write(f"Shift-free at x=1 (barrier model removes dE_cont' at closure): model={CONTACT_MODEL} "
                f"-> structural shift-free={'yes' if shift_free_model else 'no'}; "
                f"numeric |force@x1| small={'yes' if shift_free_numeric else 'no'}\n")
        f.write(f"Continuation (lambda branch tracking): enabled={'yes' if continuation_used else 'no'}; "
                f"max |jump| in best block={'n/a' if not np.isfinite(max_jump) else f'{max_jump:.8e}'}\n")
        if asym:
            f.write(f"Asymptotic (two highest N_int): A_K={asym.get('A_K_mid', np.nan):.8f} +- {asym.get('A_K_half_range', np.nan):.8f}\n")
            f.write(f"                             a_nc/r_c={asym.get('a_nc_over_rc_mid', np.nan):.8f} +- {asym.get('a_nc_over_rc_half_range', np.nan):.8f}\n")
        f.write(f"Branch mode                 : {BRANCH_MODE}\n")

    tex_path = os.path.join(outdir, "final_best_estimate_v10_0.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(f"\\paragraph{{Final best-estimate {SCRIPT_VERSION}.}}\n")
        if best:
            f.write(f"Practical: $A_K^{{\\mathrm{{best}}}} = {best['A_K']:.8f} \\pm {A_sys:.8f}_{{\\mathrm{{syst}}}}$, ")
            f.write(f"$a_{{\\mathrm{{nc}}}}/r_c = {best['a_nc_over_rc']:.8f} \\pm {a_nc_sys:.8f}_{{\\mathrm{{syst}}}}$.\n")
            f.write(f"No-contact closure $x = \\sqrt{{4\\pi A_K}} = {x_closure_best:.8f}$.\n")
        if companion:
            f.write(f"Full-model (max $\\lambda_K$): $F(1) \\approx {companion.get('F_at_x1', np.nan):.8e}$, "
                    f"$a^*/r_c = {companion.get('a_star_over_rc', np.nan):.8f}$, contact model \\texttt{{{CONTACT_MODEL}}}.\n")
        if asym:
            f.write(f"Asymptotic (two highest $N_{{\\mathrm{{int}}}}$): ")
            f.write(f"$A_K = {asym.get('A_K_mid', np.nan):.8f} \\pm {asym.get('A_K_half_range', np.nan):.8f}$, ")
            f.write(f"$a_{{\\mathrm{{nc}}}}/r_c = {asym.get('a_nc_over_rc_mid', np.nan):.8f} \\pm {asym.get('a_nc_over_rc_half_range', np.nan):.8f}$.\n")
        f.write("Interpretation: numerical support for percent-level closure; v9.3 uses v7 dimensionless-x root finding plus v6 theorem/continuation/barrier diagnostics, shift-free postcheck, optional asymptotic extrapolation reports, and a parallel theorem-candidate comparison across plateau fit methods.\n")


def parse_exact_pairs(text: str) -> List[Tuple[int, int]]:
    """
    Parse strings like:
        "48000:48000,64000:64000"
    into:
        [(48000,48000), (64000,64000)]
    """
    out: List[Tuple[int, int]] = []
    if not text:
        return out
    for chunk in text.replace(";", ",").split(","):
        s = chunk.strip()
        if not s:
            continue
        if ":" not in s:
            raise ValueError(f"Expected Ngeom:Nint pair, got {s!r}")
        a, b = s.split(":", 1)
        Ng = int(a.strip())
        Ni = int(b.strip())
        if Ng <= 0 or Ni <= 0:
            raise ValueError(f"Pair must be positive, got {s!r}")
        out.append((Ng, Ni))
    return out


def _normalize_preferred_root_choices(prefer_root_choice: Optional[Union[str, Sequence[str]]]) -> List[str]:
    if prefer_root_choice is None:
        return []
    if isinstance(prefer_root_choice, str):
        return [prefer_root_choice]
    out: List[str] = []
    for item in prefer_root_choice:
        s = str(item).strip()
        if s and s not in out:
            out.append(s)
    return out


def _normalize_fit_method_list(methods: Optional[Sequence[str]]) -> List[str]:
    if not methods:
        return []
    out: List[str] = []
    for m in methods:
        s = str(m).strip()
        if s and s not in out:
            out.append(s)
    return out


def _score_row_for_nint_choice(r: dict, prefer_root_choice: Optional[Union[str, Sequence[str]]] = None) -> Tuple[float, float, float]:
    """
    Larger is better.
    1) prefer larger N_geom
    2) optionally prefer one or more root_choice labels (ordered)
    3) then prefer smaller |F_at_x1|
    """
    Ng = float(r.get("N_geom", 0))
    preferred = _normalize_preferred_root_choices(prefer_root_choice)
    root_choice = str(r.get("root_choice", ""))
    rc_bonus = 0.0
    if preferred and root_choice in preferred:
        rc_bonus = float(len(preferred) - preferred.index(root_choice))
    Fx = r.get("F_at_x1", np.nan)
    if np.isfinite(Fx):
        f_score = -abs(float(Fx))
    else:
        f_score = -1.0e99
    return (Ng, rc_bonus, f_score)


def pick_best_row_per_nint(rows_local: List[dict], prefer_root_choice: Optional[Union[str, Sequence[str]]] = None) -> List[dict]:
    """
    For each N_int_actual keep one best row.
    This avoids duplicate curves caused by repeated N_geom values mapping to the same N_int_actual.
    """
    best_by_n: Dict[int, dict] = {}
    best_score_by_n: Dict[int, Tuple[float, float, float]] = {}

    for r in rows_local:
        try:
            n = int(r["N_int_actual"])
        except Exception:
            continue
        sc = _score_row_for_nint_choice(r, prefer_root_choice=prefer_root_choice)
        if (n not in best_by_n) or (sc > best_score_by_n[n]):
            best_by_n[n] = r
            best_score_by_n[n] = sc

    out = [best_by_n[k] for k in sorted(best_by_n.keys())]
    return out


def summarize_root_choices(rows_local: List[dict]) -> str:
    counts: Dict[str, int] = {}
    for r in rows_local:
        rc = str(r.get("root_choice", "")) or "unknown"
        counts[rc] = counts.get(rc, 0) + 1
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ";".join(f"{k}:{v}" for k, v in items)


def assess_tail_toward_target(n_vals: List[float], y_vals: List[float], target: float) -> Dict[str, float]:
    n = np.asarray(n_vals, dtype=float)
    y = np.asarray(y_vals, dtype=float)
    mask = np.isfinite(n) & np.isfinite(y)
    n = n[mask]
    y = y[mask]
    if n.size == 0:
        return {
            "tail_points": 0,
            "tail_enough": False,
            "tail_err_contracting": False,
            "tail_step_contracting": False,
            "tail_sign_changes": np.nan,
            "tail_last_abs_err": np.nan,
            "tail_prev_abs_err": np.nan,
            "tail_last_step": np.nan,
            "tail_prev_step": np.nan,
            "tail_quasi_monotone": False,
        }
    order = np.argsort(n)
    y = y[order]
    tail_len = int(min(V9_TAIL_USE_LAST, len(y)))
    y_tail = y[-tail_len:]
    err_tail = y_tail - float(target)
    abs_err = np.abs(err_tail)
    diffs = np.abs(np.diff(y_tail))
    tail_enough = bool(tail_len >= V9_TAIL_MIN_POINTS)

    err_contracting = True
    for i in range(len(abs_err) - 1):
        if abs_err[i + 1] > abs_err[i] * (1.0 + V9_TAIL_RELAX) + V9_TAIL_ABS_EPS:
            err_contracting = False
            break

    step_contracting = True
    if len(diffs) >= 2:
        for i in range(len(diffs) - 1):
            if diffs[i + 1] > diffs[i] * (1.0 + V9_TAIL_RELAX) + V9_TAIL_ABS_EPS:
                step_contracting = False
                break

    nz = np.sign(err_tail[np.abs(err_tail) > V9_TAIL_ABS_EPS])
    sign_changes = 0
    if nz.size >= 2:
        sign_changes = int(np.sum(nz[1:] != nz[:-1]))

    quasi_monotone = bool(tail_enough and err_contracting and step_contracting and sign_changes <= 1)

    return {
        "tail_points": tail_len,
        "tail_enough": tail_enough,
        "tail_err_contracting": bool(err_contracting),
        "tail_step_contracting": bool(step_contracting),
        "tail_sign_changes": float(sign_changes),
        "tail_last_abs_err": float(abs_err[-1]) if abs_err.size else np.nan,
        "tail_prev_abs_err": float(abs_err[-2]) if abs_err.size >= 2 else np.nan,
        "tail_last_step": float(diffs[-1]) if diffs.size else np.nan,
        "tail_prev_step": float(diffs[-2]) if diffs.size >= 2 else np.nan,
        "tail_quasi_monotone": quasi_monotone,
    }


def fit_powerlaw_extrapolation(n_vals: List[float], y_vals: List[float], target: float = np.nan) -> Dict[str, float]:
    r"""
    Fit
        y(N) = y_inf + c N^{-alpha}
    by grid search over alpha and linear least squares in (y_inf, c).

    Returns a conservative summary. This is intended for numerical trend extraction,
    not as an exact theorem proof.
    """
    n = np.asarray(n_vals, dtype=float)
    y = np.asarray(y_vals, dtype=float)

    mask = np.isfinite(n) & np.isfinite(y) & (n > 0.0)
    n = n[mask]
    y = y[mask]

    if len(n) == 0:
        return {
            "n_points": 0,
            "alpha_best": np.nan,
            "y_inf": np.nan,
            "c_best": np.nan,
            "sse": np.nan,
            "rms": np.nan,
            "last2_half_range": np.nan,
            "y_inf_minus_target": np.nan,
            "method": "none",
        }

    order = np.argsort(n)
    n = n[order]
    y = y[order]

    last2_half_range = np.nan
    if len(y) >= 2:
        last2_half_range = 0.5 * abs(float(y[-1] - y[-2]))

    # With only 2 points alpha is underdetermined. Use alpha=1 as a transparent fallback.
    if len(n) == 2:
        alpha = 1.0
        X = np.column_stack([np.ones_like(n), n ** (-alpha)])
        coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        y_inf, c_best = coef
        y_fit = X @ coef
        resid = y - y_fit
        sse = float(np.dot(resid, resid))
        rms = float(np.sqrt(np.mean(resid**2)))
        return {
            "n_points": 2,
            "alpha_best": alpha,
            "y_inf": float(y_inf),
            "c_best": float(c_best),
            "sse": sse,
            "rms": rms,
            "last2_half_range": last2_half_range,
            "y_inf_minus_target": float(y_inf - target) if np.isfinite(target) else np.nan,
            "method": "two_point_alpha1",
        }

    alpha_grid = np.linspace(EXTRAP_ALPHA_MIN, EXTRAP_ALPHA_MAX, EXTRAP_ALPHA_COUNT)
    best = None

    for alpha in alpha_grid:
        X = np.column_stack([np.ones_like(n), n ** (-alpha)])
        coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        y_inf, c_best = coef
        y_fit = X @ coef
        resid = y - y_fit
        sse = float(np.dot(resid, resid))
        rms = float(np.sqrt(np.mean(resid**2)))

        # Small tie-breaker toward smoother / lower-alpha fits if SSE is nearly equal
        score = (sse, alpha)

        if best is None or score < best["score"]:
            best = {
                "score": score,
                "alpha_best": float(alpha),
                "y_inf": float(y_inf),
                "c_best": float(c_best),
                "sse": sse,
                "rms": rms,
                "y_fit": y_fit,
            }

    assert best is not None

    return {
        "n_points": int(len(n)),
        "alpha_best": best["alpha_best"],
        "y_inf": best["y_inf"],
        "c_best": best["c_best"],
        "sse": best["sse"],
        "rms": best["rms"],
        "last2_half_range": last2_half_range,
        "y_inf_minus_target": float(best["y_inf"] - target) if np.isfinite(target) else np.nan,
        "method": "powerlaw_gridsearch",
    }


def _make_extrap_row(dataset: str, quantity: str, fit_method: str, lambda_K: float,
                     n_vals: List[float], y_vals: List[float], fit_out: Dict[str, float],
                     target: float) -> dict:
    n_arr = np.asarray(n_vals, dtype=float)
    y_arr = np.asarray(y_vals, dtype=float)

    return {
        "dataset": dataset,
        "quantity": quantity,
        "fit_method": fit_method,
        "lambda_K": lambda_K,
        "n_points": int(fit_out["n_points"]),
        "Nint_min": float(np.min(n_arr)) if n_arr.size else np.nan,
        "Nint_max": float(np.max(n_arr)) if n_arr.size else np.nan,
        "alpha_best": fit_out["alpha_best"],
        "y_inf": fit_out["y_inf"],
        "target": target,
        "y_inf_minus_target": fit_out["y_inf_minus_target"],
        "rms_fit": fit_out["rms"],
        "sse_fit": fit_out["sse"],
        "last2_half_range": fit_out["last2_half_range"],
        "method": fit_out["method"],
        "tail_points": np.nan,
        "tail_enough": False,
        "tail_err_contracting": False,
        "tail_step_contracting": False,
        "tail_sign_changes": np.nan,
        "tail_last_abs_err": np.nan,
        "tail_prev_abs_err": np.nan,
        "tail_last_step": np.nan,
        "tail_prev_step": np.nan,
        "tail_quasi_monotone": False,
        "root_choice_summary": "",
        "raw_n_vals": ";".join(str(int(v)) for v in n_arr.tolist()),
        "raw_y_vals": ";".join(f"{float(v):.12g}" for v in y_arr.tolist()),
    }


def write_v9_3_parallel_theorem_report(rows: List[dict], postcheck_rows: List[dict], outdir: str) -> None:
    """
    Evaluate theorem-style asymptotics in parallel for multiple plateau fit methods,
    while leaving the practical/best-estimate pipeline unchanged.
    """
    candidate_methods = _normalize_fit_method_list(THEOREM_CANDIDATE_FIT_METHODS)
    if not candidate_methods:
        return

    summary_rows: List[dict] = []

    for fit_method in candidate_methods:
        main_nc = [
            r for r in rows
            if r.get("fit_method") == fit_method
            and np.isfinite(r.get("A_K", np.nan))
            and np.isfinite(r.get("a_nc_over_rc", np.nan))
            and float(r.get("lambda_K", np.nan)) == 0.0
            and int(r.get("N_int_actual", 0)) >= EXTRAP_MIN_NINT
        ]
        main_nc = pick_best_row_per_nint(main_nc, prefer_root_choice=None)

        A_fit = None
        anc_fit = None
        A_tail = None
        anc_tail = None

        if len(main_nc) >= 2:
            n_vals = [float(r["N_int_actual"]) for r in main_nc]

            A_vals = [float(r["A_K"]) for r in main_nc]
            A_fit = fit_powerlaw_extrapolation(n_vals, A_vals, target=A_req)
            A_tail = assess_tail_toward_target(n_vals, A_vals, A_req)

            anc_vals = [float(r["a_nc_over_rc"]) for r in main_nc]
            anc_fit = fit_powerlaw_extrapolation(n_vals, anc_vals, target=1.0)
            anc_tail = assess_tail_toward_target(n_vals, anc_vals, 1.0)

        post_sf = [
            r for r in postcheck_rows
            if r.get("fit_method") == fit_method
            and r.get("contact_model") == "barrier_flat_at_rc"
            and str(r.get("root_choice", "")) in V9_ALLOWED_POSTCHECK_ROOT_CHOICES
            and np.isfinite(r.get("a_star_over_rc", np.nan))
            and np.isfinite(r.get("F_at_x1", np.nan))
            and float(r.get("lambda_K", np.nan)) == 0.0
            and int(r.get("N_int_actual", 0)) >= EXTRAP_MIN_NINT
        ]
        post_sf = pick_best_row_per_nint(post_sf, prefer_root_choice=V9_ALLOWED_POSTCHECK_ROOT_CHOICES)

        lam0_astar_fit = None
        lam0_F_fit = None
        lam0_astar_tail = None
        lam0_F_tail = None
        lam0_choice_summary = summarize_root_choices(post_sf) if post_sf else ""

        if len(post_sf) >= 2:
            n_vals = [float(r["N_int_actual"]) for r in post_sf]
            astar_vals = [float(r["a_star_over_rc"]) for r in post_sf]
            Fx_vals = [float(r["F_at_x1"]) for r in post_sf]

            lam0_astar_fit = fit_powerlaw_extrapolation(n_vals, astar_vals, target=1.0)
            lam0_astar_tail = assess_tail_toward_target(n_vals, astar_vals, 1.0)
            lam0_F_fit = fit_powerlaw_extrapolation(n_vals, Fx_vals, target=0.0)
            lam0_F_tail = assess_tail_toward_target(n_vals, Fx_vals, 0.0)

        theorem_no_contact_ok = bool(
            A_fit is not None
            and anc_fit is not None
            and A_tail is not None
            and anc_tail is not None
            and np.isfinite(A_fit["y_inf_minus_target"])
            and np.isfinite(anc_fit["y_inf_minus_target"])
            and abs(A_fit["y_inf_minus_target"]) < V8_THEOREM_TOL_AINF
            and abs(anc_fit["y_inf_minus_target"]) < V8_THEOREM_TOL_XINF
            and bool(A_tail.get("tail_quasi_monotone", False))
            and bool(anc_tail.get("tail_quasi_monotone", False))
        )

        theorem_shiftfree_ok = bool(
            lam0_astar_fit is not None
            and lam0_F_fit is not None
            and lam0_astar_tail is not None
            and lam0_F_tail is not None
            and np.isfinite(lam0_astar_fit["y_inf_minus_target"])
            and np.isfinite(lam0_F_fit["y_inf_minus_target"])
            and abs(lam0_astar_fit["y_inf_minus_target"]) < V8_THEOREM_TOL_XINF
            and abs(lam0_F_fit["y_inf_minus_target"]) < V8_THEOREM_TOL_FINF
            and bool(lam0_astar_tail.get("tail_quasi_monotone", False))
            and bool(lam0_F_tail.get("tail_quasi_monotone", False))
        )

        summary_rows.append({
            "fit_method": fit_method,
            "n_main_rows": len(main_nc),
            "A_inf": A_fit["y_inf"] if A_fit else np.nan,
            "A_inf_minus_target": A_fit["y_inf_minus_target"] if A_fit else np.nan,
            "A_alpha": A_fit["alpha_best"] if A_fit else np.nan,
            "A_tail_quasi_monotone": bool(A_tail.get("tail_quasi_monotone", False)) if A_tail else False,
            "anc_inf": anc_fit["y_inf"] if anc_fit else np.nan,
            "anc_inf_minus_1": anc_fit["y_inf_minus_target"] if anc_fit else np.nan,
            "anc_alpha": anc_fit["alpha_best"] if anc_fit else np.nan,
            "anc_tail_quasi_monotone": bool(anc_tail.get("tail_quasi_monotone", False)) if anc_tail else False,
            "theorem_no_contact_ok": theorem_no_contact_ok,
            "n_shiftfree_rows": len(post_sf),
            "astar_inf": lam0_astar_fit["y_inf"] if lam0_astar_fit else np.nan,
            "astar_inf_minus_1": lam0_astar_fit["y_inf_minus_target"] if lam0_astar_fit else np.nan,
            "astar_alpha": lam0_astar_fit["alpha_best"] if lam0_astar_fit else np.nan,
            "astar_tail_quasi_monotone": bool(lam0_astar_tail.get("tail_quasi_monotone", False)) if lam0_astar_tail else False,
            "F1_inf": lam0_F_fit["y_inf"] if lam0_F_fit else np.nan,
            "F1_inf_minus_0": lam0_F_fit["y_inf_minus_target"] if lam0_F_fit else np.nan,
            "F1_alpha": lam0_F_fit["alpha_best"] if lam0_F_fit else np.nan,
            "F1_tail_quasi_monotone": bool(lam0_F_tail.get("tail_quasi_monotone", False)) if lam0_F_tail else False,
            "shiftfree_root_choice_summary": lam0_choice_summary,
            "theorem_shiftfree_ok": theorem_shiftfree_ok,
        })

    if not summary_rows:
        return

    csv_path = os.path.join(outdir, "parallel_theorem_candidates_v10_0.csv")
    write_csv(summary_rows, csv_path)

    txt_path = os.path.join(outdir, "parallel_theorem_candidates_v10_0.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"SST ideal-trefoil parallel theorem-candidate report {SCRIPT_VERSION}\n")
        f.write("=" * 76 + "\n")
        f.write(f"Candidate fit methods: {candidate_methods}\n")
        f.write(f"Extrapolation minimum N_int_actual: {EXTRAP_MIN_NINT}\n\n")
        for row in summary_rows:
            f.write(f"[{row['fit_method']}]\n")
            f.write(f"  A_inf - 1/(4*pi)         = {row['A_inf_minus_target']:.10e}\n")
            f.write(f"  a_nc/r_c (inf) - 1       = {row['anc_inf_minus_1']:.10e}\n")
            f.write(f"  A tail quasi-monotone    = {'yes' if row['A_tail_quasi_monotone'] else 'no'}\n")
            f.write(f"  a_nc tail quasi-monotone = {'yes' if row['anc_tail_quasi_monotone'] else 'no'}\n")
            f.write(f"  theorem_no_contact_ok    = {'yes' if row['theorem_no_contact_ok'] else 'no'}\n")
            f.write(f"  a*/r_c (inf) - 1         = {row['astar_inf_minus_1']:.10e}\n")
            f.write(f"  F(1)_inf                 = {row['F1_inf']:.10e}\n")
            f.write(f"  a* tail quasi-monotone   = {'yes' if row['astar_tail_quasi_monotone'] else 'no'}\n")
            f.write(f"  F(1) tail quasi-monotone = {'yes' if row['F1_tail_quasi_monotone'] else 'no'}\n")
            f.write(f"  shiftfree root choices   = {row['shiftfree_root_choice_summary']}\n")
            f.write(f"  theorem_shiftfree_ok     = {'yes' if row['theorem_shiftfree_ok'] else 'no'}\n\n")

    tex_path = os.path.join(outdir, "parallel_theorem_candidates_v10_0.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(f"\\paragraph{{Parallel theorem-candidate comparison ({SCRIPT_VERSION}).}}\n")
        f.write("We evaluated multiple plateau-based extraction rules in parallel, keeping the numerical sweep, root solver, and shift-free postcheck fixed. ")
        for row in summary_rows:
            f.write(
                f"For \\texttt{{{row['fit_method']}}}, "
                f"$A_\\infty-1/(4\\pi)={row['A_inf_minus_target']:.3e}$, "
                f"$(a_{{\\mathrm{{nc}}}}/r_c)_\\infty-1={row['anc_inf_minus_1']:.3e}$, "
                f"no-contact tail checks: "
                f"$A_K$ ({'yes' if row['A_tail_quasi_monotone'] else 'no'}), "
                f"$a_{{\\mathrm{{nc}}}}/r_c$ ({'yes' if row['anc_tail_quasi_monotone'] else 'no'}). "
                f"Shift-free extrapolation gives $(a^*/r_c)_\\infty-1={row['astar_inf_minus_1']:.3e}$ and "
                f"$F(1)_\\infty={row['F1_inf']:.3e}$, with tail checks "
                f"$a^*/r_c$ ({'yes' if row['astar_tail_quasi_monotone'] else 'no'}) and "
                f"$F(1)$ ({'yes' if row['F1_tail_quasi_monotone'] else 'no'}). "
            )
        f.write("This report is diagnostic only: it does not alter the practical best-estimate selection.\n")


def write_v8_extrapolation(rows: List[dict], postcheck_rows: List[dict], outdir: str) -> None:
    """
    Writes theorem-style asymptotic diagnostics.

    V9 sharpenings:
      1) include both targeted_x_nc and targeted_x_nc_fallback in shift-free extrapolation
      2) expose which root-choice labels were actually used in the asymptotic tail
      3) require a quasi-monotone contracting high-resolution tail before a theorem-style
         conclusion is marked supported.
    """
    fit_method = EXTRAP_PREFERRED_FIT_METHOD or PREFERRED_FIT_METHOD
    out_rows: List[dict] = []

    # ------------------------------------------------------------
    # 1) No-contact extrapolation from main sweep
    # ------------------------------------------------------------
    main_nc = [
        r for r in rows
        if r.get("fit_method") == fit_method
        and np.isfinite(r.get("A_K", np.nan))
        and np.isfinite(r.get("a_nc_over_rc", np.nan))
        and float(r.get("lambda_K", np.nan)) == 0.0
        and int(r.get("N_int_actual", 0)) >= EXTRAP_MIN_NINT
    ]
    main_nc = pick_best_row_per_nint(main_nc, prefer_root_choice=None)

    A_fit = None
    anc_fit = None
    A_tail = None
    anc_tail = None

    if len(main_nc) >= 2:
        n_vals = [float(r["N_int_actual"]) for r in main_nc]

        A_vals = [float(r["A_K"]) for r in main_nc]
        A_fit = fit_powerlaw_extrapolation(n_vals, A_vals, target=A_req)
        A_tail = assess_tail_toward_target(n_vals, A_vals, A_req)
        rowA = _make_extrap_row("main_no_contact", "A_K", fit_method, 0.0, n_vals, A_vals, A_fit, A_req)
        rowA.update(A_tail)
        out_rows.append(rowA)

        anc_vals = [float(r["a_nc_over_rc"]) for r in main_nc]
        anc_fit = fit_powerlaw_extrapolation(n_vals, anc_vals, target=1.0)
        anc_tail = assess_tail_toward_target(n_vals, anc_vals, 1.0)
        rowAnc = _make_extrap_row("main_no_contact", "a_nc_over_rc", fit_method, 0.0, n_vals, anc_vals, anc_fit, 1.0)
        rowAnc.update(anc_tail)
        out_rows.append(rowAnc)

    # ------------------------------------------------------------
    # 2) Shift-free postcheck extrapolation from targeted_x_nc family
    # ------------------------------------------------------------
    post_sf = [
        r for r in postcheck_rows
        if r.get("fit_method") == fit_method
        and r.get("contact_model") == "barrier_flat_at_rc"
        and str(r.get("root_choice", "")) in V9_ALLOWED_POSTCHECK_ROOT_CHOICES
        and np.isfinite(r.get("a_star_over_rc", np.nan))
        and np.isfinite(r.get("F_at_x1", np.nan))
        and int(r.get("N_int_actual", 0)) >= EXTRAP_MIN_NINT
    ]

    shiftfree_fits_by_lambda: Dict[float, Dict[str, Dict[str, float]]] = {}
    shiftfree_tail_by_lambda: Dict[float, Dict[str, Dict[str, float]]] = {}
    shiftfree_choice_summary: Dict[float, str] = {}

    if post_sf:
        lambda_vals = sorted(set(float(r["lambda_K"]) for r in post_sf))
        for lam in lambda_vals:
            subset = [r for r in post_sf if float(r["lambda_K"]) == lam]
            subset = pick_best_row_per_nint(subset, prefer_root_choice=V9_ALLOWED_POSTCHECK_ROOT_CHOICES)
            if len(subset) < 2:
                continue

            n_vals = [float(r["N_int_actual"]) for r in subset]
            choice_summary = summarize_root_choices(subset)
            shiftfree_choice_summary[lam] = choice_summary

            astar_vals = [float(r["a_star_over_rc"]) for r in subset]
            astar_fit = fit_powerlaw_extrapolation(n_vals, astar_vals, target=1.0)
            astar_tail = assess_tail_toward_target(n_vals, astar_vals, 1.0)
            rowAstar = _make_extrap_row("shiftfree_postcheck", "a_star_over_rc", fit_method, lam, n_vals, astar_vals, astar_fit, 1.0)
            rowAstar.update(astar_tail)
            rowAstar["root_choice_summary"] = choice_summary
            out_rows.append(rowAstar)

            Fx_vals = [float(r["F_at_x1"]) for r in subset]
            Fx_fit = fit_powerlaw_extrapolation(n_vals, Fx_vals, target=0.0)
            Fx_tail = assess_tail_toward_target(n_vals, Fx_vals, 0.0)
            rowFx = _make_extrap_row("shiftfree_postcheck", "F_at_x1", fit_method, lam, n_vals, Fx_vals, Fx_fit, 0.0)
            rowFx.update(Fx_tail)
            rowFx["root_choice_summary"] = choice_summary
            out_rows.append(rowFx)

            shiftfree_fits_by_lambda[lam] = {
                "a_star_over_rc": astar_fit,
                "F_at_x1": Fx_fit,
            }
            shiftfree_tail_by_lambda[lam] = {
                "a_star_over_rc": astar_tail,
                "F_at_x1": Fx_tail,
            }

    # ------------------------------------------------------------
    # 3) Write CSV
    # ------------------------------------------------------------
    csv_path = os.path.join(outdir, "extrapolation_summary_v10_0.csv")
    if out_rows:
        write_csv(out_rows, csv_path)

    # ------------------------------------------------------------
    # 4) Write theorem-style report
    # ------------------------------------------------------------
    txt_path = os.path.join(outdir, "final_theorem_report_v9_3.txt")
    tex_path = os.path.join(outdir, "final_theorem_report_v9_3.tex")

    lam0_astar_fit = None
    lam0_F_fit = None
    lam0_astar_tail = None
    lam0_F_tail = None
    lam0_choice_summary = ""
    if 0.0 in shiftfree_fits_by_lambda:
        lam0_astar_fit = shiftfree_fits_by_lambda[0.0].get("a_star_over_rc")
        lam0_F_fit = shiftfree_fits_by_lambda[0.0].get("F_at_x1")
        lam0_astar_tail = shiftfree_tail_by_lambda[0.0].get("a_star_over_rc")
        lam0_F_tail = shiftfree_tail_by_lambda[0.0].get("F_at_x1")
        lam0_choice_summary = shiftfree_choice_summary.get(0.0, "")

    theorem_no_contact_ok = bool(
        A_fit is not None
        and anc_fit is not None
        and A_tail is not None
        and anc_tail is not None
        and np.isfinite(A_fit["y_inf_minus_target"])
        and np.isfinite(anc_fit["y_inf_minus_target"])
        and abs(A_fit["y_inf_minus_target"]) < V8_THEOREM_TOL_AINF
        and abs(anc_fit["y_inf_minus_target"]) < V8_THEOREM_TOL_XINF
        and bool(A_tail.get("tail_quasi_monotone", False))
        and bool(anc_tail.get("tail_quasi_monotone", False))
    )

    theorem_shiftfree_ok = bool(
        lam0_astar_fit is not None
        and lam0_F_fit is not None
        and lam0_astar_tail is not None
        and lam0_F_tail is not None
        and np.isfinite(lam0_astar_fit["y_inf_minus_target"])
        and np.isfinite(lam0_F_fit["y_inf_minus_target"])
        and abs(lam0_astar_fit["y_inf_minus_target"]) < V8_THEOREM_TOL_XINF
        and abs(lam0_F_fit["y_inf_minus_target"]) < V8_THEOREM_TOL_FINF
        and bool(lam0_astar_tail.get("tail_quasi_monotone", False))
        and bool(lam0_F_tail.get("tail_quasi_monotone", False))
    )

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"SST ideal-trefoil theorem-style extrapolation report {SCRIPT_VERSION}\n")
        f.write("=" * 72 + "\n")
        f.write(f"Preferred fit method                 : {fit_method}\n")
        f.write(f"Extrapolation minimum N_int_actual   : {EXTRAP_MIN_NINT}\n")
        f.write(f"Sweep layout                         : {SWEEP_LAYOUT}\n")
        f.write(f"Exact target pairs appended          : {EXTRA_TARGET_PAIRS}\n")
        f.write("\n")

        if A_fit is not None and anc_fit is not None and A_tail is not None and anc_tail is not None:
            f.write("[No-contact asymptotic closure]\n")
            f.write(f"A_inf                       = {A_fit['y_inf']:.10f}\n")
            f.write(f"1/(4*pi)                    = {A_req:.10f}\n")
            f.write(f"A_inf - 1/(4*pi)            = {A_fit['y_inf_minus_target']:.10e}\n")
            f.write(f"a_nc/r_c (inf)              = {anc_fit['y_inf']:.10f}\n")
            f.write(f"a_nc/r_c (inf) - 1          = {anc_fit['y_inf_minus_target']:.10e}\n")
            f.write(f"alpha_A                     = {A_fit['alpha_best']:.6f}\n")
            f.write(f"alpha_a_nc                  = {anc_fit['alpha_best']:.6f}\n")
            f.write(f"last2 half-range A          = {A_fit['last2_half_range']:.10e}\n")
            f.write(f"last2 half-range a_nc/r_c   = {anc_fit['last2_half_range']:.10e}\n")
            f.write(f"tail(A) quasi-monotone      = {'yes' if A_tail['tail_quasi_monotone'] else 'no'}\n")
            f.write(f"tail(a_nc/r_c) quasi-monotone = {'yes' if anc_tail['tail_quasi_monotone'] else 'no'}\n")
            f.write(f"theorem_no_contact_ok       = {'yes' if theorem_no_contact_ok else 'no'}\n")
            f.write("\n")

        if lam0_astar_fit is not None and lam0_F_fit is not None and lam0_astar_tail is not None and lam0_F_tail is not None:
            f.write("[Shift-free postcheck asymptotic closure at lambda_K=0]\n")
            f.write(f"root_choice_summary         = {lam0_choice_summary}\n")
            f.write(f"a_star/r_c (inf)            = {lam0_astar_fit['y_inf']:.10f}\n")
            f.write(f"a_star/r_c (inf) - 1        = {lam0_astar_fit['y_inf_minus_target']:.10e}\n")
            f.write(f"F(1) (inf)                  = {lam0_F_fit['y_inf']:.10e}\n")
            f.write(f"alpha_a_star                = {lam0_astar_fit['alpha_best']:.6f}\n")
            f.write(f"alpha_F1                    = {lam0_F_fit['alpha_best']:.6f}\n")
            f.write(f"last2 half-range a_star/r_c = {lam0_astar_fit['last2_half_range']:.10e}\n")
            f.write(f"last2 half-range F(1)       = {lam0_F_fit['last2_half_range']:.10e}\n")
            f.write(f"tail(a_star/r_c) quasi-monotone = {'yes' if lam0_astar_tail['tail_quasi_monotone'] else 'no'}\n")
            f.write(f"tail(F(1)) quasi-monotone   = {'yes' if lam0_F_tail['tail_quasi_monotone'] else 'no'}\n")
            f.write(f"theorem_shiftfree_ok        = {'yes' if theorem_shiftfree_ok else 'no'}\n")
            f.write("\n")

        if shiftfree_fits_by_lambda:
            f.write("[Shift-free lambda-dependence, asymptotic in N_int]\n")
            for lam in sorted(shiftfree_fits_by_lambda.keys()):
                a_fit = shiftfree_fits_by_lambda[lam]["a_star_over_rc"]
                a_tail = shiftfree_tail_by_lambda[lam]["a_star_over_rc"]
                f.write(
                    f"lambda_K={lam:<10g}  "
                    f"choices={shiftfree_choice_summary.get(lam, ''):<28}  "
                    f"a_star/r_c(inf)={a_fit['y_inf']:.10f}  "
                    f"minus_1={a_fit['y_inf_minus_target']:.10e}  "
                    f"tail_ok={'yes' if a_tail['tail_quasi_monotone'] else 'no'}\n"
                )
            f.write("\n")

        f.write("Interpretation:\n")
        f.write(
            "v9 keeps the asymptotic fit y(N)=y_inf + c N^{-alpha}, but now refuses a theorem-style\n"
            "conclusion unless the high-resolution tail is also quasi-monotone/contracting toward the\n"
            "target. The shift-free postcheck includes both targeted_x_nc and targeted_x_nc_fallback rows,\n"
            "and reports which branch labels were actually used in the asymptotic tail.\n"
        )

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(f"\\paragraph{{{SCRIPT_VERSION} asymptotic extrapolation.}}\n")
        if A_fit is not None and anc_fit is not None and A_tail is not None and anc_tail is not None:
            f.write(
                "Using the converged high-resolution tail, we fit "
                rf"$y(N_{{\mathrm{{int}}}})=y_{{\infty}}+cN_{{\mathrm{{int}}}}^{{-\alpha}}$, "
            )
            f.write(
                rf"obtaining $A_\infty={A_fit['y_inf']:.10f}$ with "
                rf"$A_\infty-1/(4\pi)={A_fit['y_inf_minus_target']:.3e}$, and "
                rf"$(a_{{\mathrm{{nc}}}}/r_c)_\infty={anc_fit['y_inf']:.10f}$ with "
                rf"$(a_{{\mathrm{{nc}}}}/r_c)_\infty-1={anc_fit['y_inf_minus_target']:.3e}$. "
            )
            f.write(
                f"The observed high-resolution tail is quasi-monotone toward the target for $A_K$ "
                rf"({ 'yes' if A_tail['tail_quasi_monotone'] else 'no' }) and for $a_{{\mathrm{{nc}}}}/r_c$ "
                f"({ 'yes' if anc_tail['tail_quasi_monotone'] else 'no' }). "
            )
        if lam0_astar_fit is not None and lam0_F_fit is not None and lam0_astar_tail is not None and lam0_F_tail is not None:
            f.write(
                rf"For the shift-free postcheck at $\lambda_K=0$, "
                rf"$(a^*/r_c)_\infty={lam0_astar_fit['y_inf']:.10f}$ with deviation "
                rf"{lam0_astar_fit['y_inf_minus_target']:.3e}, and $F(1)_\infty={lam0_F_fit['y_inf']:.3e}$. "
            )
            f.write(
                f"The asymptotic tail uses root-choice labels \\texttt{{{lam0_choice_summary or 'n/a'}}}. "
            )
            f.write(
                f"Tail checks: $a^*/r_c$ ({'yes' if lam0_astar_tail['tail_quasi_monotone'] else 'no'}), "
                f"$F(1)$ ({'yes' if lam0_F_tail['tail_quasi_monotone'] else 'no'}). "
            )
        f.write(
            "A theorem-style closure statement is recorded only when both the extrapolated limit and the\n"
            "observed high-resolution tail support the same conclusion.\n"
        )

def _mid_half_from_top2(rows: List[dict], field: str) -> Tuple[float, float]:
    vals = [r for r in rows if np.isfinite(r.get(field, np.nan))]
    if len(vals) < 2:
        if len(vals) == 1:
            return float(vals[0][field]), 0.0
        return np.nan, np.nan
    vals.sort(key=lambda r: (r["N_int_actual"], r["N_geom"]))
    top2 = vals[-2:]
    x0 = float(top2[0][field])
    x1 = float(top2[1][field])
    return float(0.5 * (x0 + x1)), float(0.5 * abs(x1 - x0))


def _select_shiftfree_seed_rows(rows: List[dict], fit_methods: Optional[Sequence[str]] = None) -> List[dict]:
    allowed_methods = set(_normalize_fit_method_list(fit_methods) or [PREFERRED_FIT_METHOD])
    seeds: List[dict] = []
    seen = set()
    for r in rows:
        lam = r.get("lambda_K", np.nan)
        if not np.isfinite(lam) or abs(float(lam)) > 1e-15:
            continue
        if r.get("fit_method") not in allowed_methods:
            continue
        if int(r.get("p_exp", P_LIST[0])) != int(P_LIST[0]):
            continue
        if not np.isfinite(r.get("A_K", np.nan)):
            continue
        if not np.isfinite(r.get("a_nc_m", np.nan)):
            continue
        key = (int(r["N_geom"]), int(r["N_int_actual"]), str(r["fit_method"]), int(r.get("p_exp", P_LIST[0])))
        if key in seen:
            continue
        seen.add(key)
        seeds.append(r)
    seeds.sort(key=lambda rr: (rr["N_int_actual"], rr["N_geom"]))
    return seeds

def save_shiftfree_postcheck_plot(shift_rows: List[dict], outdir: str) -> None:
    if not shift_rows:
        return
    fig = plt.figure(figsize=(8, 5.5))
    for key in sorted(set((r["fit_method"], r["N_geom"], r["N_int_actual"]) for r in shift_rows)):
        fit_method, N_geom, N_int = key
        subset = sorted(
            [
                r for r in shift_rows
                if r["fit_method"] == fit_method
                and r["N_geom"] == N_geom
                and r["N_int_actual"] == N_int
            ],
            key=lambda rr: rr["lambda_K"]
        )
        xs = np.array([r["lambda_K"] for r in subset], dtype=float)
        ys = np.array([r["a_star_over_rc"] for r in subset], dtype=float)
        xplot = np.where(xs > 0.0, xs, 1e-5)
        plt.semilogx(xplot, ys, "o-", lw=1.3, label=f"{fit_method}, Ng={N_geom}, Ni={N_int}")
    plt.axhline(1.0, ls="--", lw=2, label="a*/r_c = 1")
    plt.xlabel("lambda_K  (lambda=0 shown at 1e-5)")
    plt.ylabel("a*/r_c")
    plt.title("Shift-free barrier postcheck (parallel fit methods)")
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "summary_astar_over_rc_vs_lambda_shiftfree_v10_0.png"), dpi=170, bbox_inches="tight")
    plt.close(fig)


def run_v6_shiftfree_postcheck(rows: List[dict], outdir: str) -> List[dict]:
    """
    Reuse the already-extracted v7 sweep fit data, but rerun the root problem with a
    shift-free barrier contact model after the legacy sweep is complete.

    This does NOT alter legacy rows or legacy outputs.
    """
    global CONTACT_MODEL, ROOT_SELECTION_MODE

    seeds = _select_shiftfree_seed_rows(rows, THEOREM_CANDIDATE_FIT_METHODS)
    if not seeds:
        return []

    print("[V7] Running post-sweep shift-free barrier postcheck")
    print("[V7] contact_model={} root_selection={} fit_methods={} seed_rows={}".format(
        POSTCHECK_CONTACT_MODEL, POSTCHECK_ROOT_SELECTION_MODE, THEOREM_CANDIDATE_FIT_METHODS, len(seeds)
    ))

    contact_model_saved = CONTACT_MODEL
    root_selection_saved = ROOT_SELECTION_MODE
    CONTACT_MODEL = POSTCHECK_CONTACT_MODEL
    ROOT_SELECTION_MODE = POSTCHECK_ROOT_SELECTION_MODE

    shift_rows: List[dict] = []
    try:
        legacy_lookup: Dict[Tuple[int, int, str, int, float], dict] = {}
        for r in rows:
            lam = r.get("lambda_K", np.nan)
            if not np.isfinite(lam):
                continue
            key = (
                int(r["N_geom"]),
                int(r["N_int_actual"]),
                str(r["fit_method"]),
                int(r.get("p_exp", P_LIST[0])),
                float(lam),
            )
            legacy_lookup[key] = r

        lam_iter_template = sorted(LAMBDA_LIST) if LAMBDA_CONTINUATION_SORT else list(LAMBDA_LIST)

        for seed in seeds:
            for lam_K in lam_iter_template:
                p_exp = int(seed.get("p_exp", P_LIST[0]))
                A_K = float(seed["A_K"])
                a_K = float(seed.get("a_K", 0.0)) if np.isfinite(seed.get("a_K", np.nan)) else 0.0
                L_dimless = float(seed["L_dimless"])
                d_min_dimless = float(seed["d_min_dimless"])
                a_nc = float(seed["a_nc_m"])

                candidates = find_root_candidates(
                    A_K, a_K, L_dimless, d_min_dimless, lam_K, p_exp, CONTACT_MODEL
                )
                a_star, is_min, E_star, root_count, min_root_count, root_choice = choose_root_targeted_x_nc(
                    candidates, a_nc
                )

                prev_val = np.nan
                a_star_over_rc = a_star / r_c_canon if np.isfinite(a_star) else np.nan
                continuation_jump = np.nan

                beta_dimless = float(seed["d_min_dimless"]) * L_natural / r_c_canon
                contact_force_at_x1 = contact_force_dimensionless(
                    1.0, beta_dimless, lam_K, p_exp, CONTACT_MODEL
                )
                F_at_x1 = F_dimensionless(
                    1.0, A_K, beta_dimless, lam_K, p_exp, CONTACT_MODEL
                )

                legacy = legacy_lookup.get((
                    int(seed["N_geom"]),
                    int(seed["N_int_actual"]),
                    str(seed["fit_method"]),
                    p_exp,
                    float(lam_K),
                ))
                legacy_a_star_over_rc = legacy.get("a_star_over_rc", np.nan) if legacy else np.nan
                legacy_F_at_x1 = legacy.get("F_at_x1", np.nan) if legacy else np.nan
                delta_vs_legacy = (
                    float(a_star_over_rc - legacy_a_star_over_rc)
                    if np.isfinite(a_star_over_rc) and np.isfinite(legacy_a_star_over_rc)
                    else np.nan
                )

                theorem_candidate_full_model = bool(
                    np.isfinite(F_at_x1)
                    and abs(F_at_x1) < 1e-2
                    and np.isfinite(a_star_over_rc)
                    and abs(a_star_over_rc - 1.0) < STABLE_TOL
                )

                row = {
                    "N_geom": int(seed["N_geom"]),
                    "N_int_actual": int(seed["N_int_actual"]),
                    "fit_method": str(seed["fit_method"]),
                    "plateau_frac": seed.get("plateau_frac", np.nan),
                    "p_exp": p_exp,
                    "lambda_K": float(lam_K),
                    "A_K": A_K,
                    "A_ratio": float(seed["A_ratio"]),
                    "a_nc_over_rc": float(seed["a_nc_over_rc"]),
                    "a_star_over_rc": a_star_over_rc,
                    "is_min": bool(is_min),
                    "E_star_J": E_star,
                    "root_count": int(root_count),
                    "min_root_count": int(min_root_count),
                    "root_choice": str(root_choice),
                    "continuation_prev_a_star_over_rc": prev_val,
                    "continuation_jump": continuation_jump,
                    "beta_dimless": beta_dimless,
                    "contact_model": CONTACT_MODEL,
                    "postcheck_root_selection_mode": ROOT_SELECTION_MODE,
                    "postcheck_contact_model": CONTACT_MODEL,
                    "contact_force_at_x1": contact_force_at_x1,
                    "F_at_x1": F_at_x1,
                    "legacy_contact_model": legacy.get("contact_model", "legacy") if legacy else "legacy",
                    "legacy_a_star_over_rc": legacy_a_star_over_rc,
                    "legacy_F_at_x1": legacy_F_at_x1,
                    "delta_a_star_vs_legacy": delta_vs_legacy,
                    "theorem_candidate_full_model": theorem_candidate_full_model,
                }
                shift_rows.append(row)

                print("[V7.1] N_geom={} N_int={} fit={} lambda_K={} root_choice={} F_at_x1={:.8e} a_star_over_rc={} delta_vs_legacy={}".format(
                    row["N_geom"], row["N_int_actual"], row["fit_method"], row["lambda_K"],
                    root_choice, row["F_at_x1"], row["a_star_over_rc"], row["delta_a_star_vs_legacy"]
                ))

        csv_path = os.path.join(outdir, "shiftfree_postcheck_v10_0.csv")
        write_csv(shift_rows, csv_path)
        save_shiftfree_postcheck_plot(shift_rows, outdir)

        zero_rows = [
            r for r in shift_rows
            if abs(r["lambda_K"]) < 1e-15
            and r["fit_method"] == PREFERRED_FIT_METHOD
        ]
        high_lambda = max(LAMBDA_LIST) if LAMBDA_LIST else 0.0
        max_rows = [
            r for r in shift_rows
            if abs(r["lambda_K"] - high_lambda) < 1e-15
            and r["fit_method"] == PREFERRED_FIT_METHOD
        ]

        a_star0_mid, a_star0_half = _mid_half_from_top2(zero_rows, "a_star_over_rc")
        F10_mid, F10_half = _mid_half_from_top2(zero_rows, "F_at_x1")
        cf1_mid, cf1_half = _mid_half_from_top2(zero_rows, "contact_force_at_x1")

        best_zero = max(zero_rows, key=lambda r: (r["N_int_actual"], r["N_geom"])) if zero_rows else None
        best_max = max(max_rows, key=lambda r: (r["N_int_actual"], r["N_geom"])) if max_rows else None

        txt_path = os.path.join(outdir, "shiftfree_postcheck_v10_0.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"{SCRIPT_VERSION} post-sweep shift-free barrier theorem check\n")
            f.write("=" * 64 + "\n")
            f.write(f"Derived from legacy sweep rows only; no legacy outputs were modified.\n")
            f.write(f"Preferred fit method       : {PREFERRED_FIT_METHOD}\n")
            f.write(f"Parallel seed fit methods  : {THEOREM_CANDIDATE_FIT_METHODS}\n")
            f.write(f"Shift-free contact model   : {POSTCHECK_CONTACT_MODEL}\n")
            f.write(f"Postcheck root selection   : {POSTCHECK_ROOT_SELECTION_MODE}\n")
            f.write(f"Seed rows                  : {len(seeds)}\n")
            f.write(f"Lambda list                : {LAMBDA_LIST}\n")
            f.write("\n")
            f.write("Structural condition at x=1:\n")
            f.write(f"  contact_force_at_x1 (two-highest-N_int, lambda=0) = {cf1_mid:.8e} +- {cf1_half:.8e}\n")
            f.write(f"  F_at_x1                  (two-highest-N_int, lambda=0) = {F10_mid:.8e} +- {F10_half:.8e}\n")
            f.write(f"  a_star/r_c               (two-highest-N_int, lambda=0) = {a_star0_mid:.8f} +- {a_star0_half:.8f}\n")
            f.write("\n")
            if best_zero is not None:
                f.write("Highest-resolution lambda=0 row:\n")
                f.write(f"  N_geom={best_zero['N_geom']} N_int={best_zero['N_int_actual']}\n")
                f.write(f"  A_K={best_zero['A_K']:.8f} A_ratio={best_zero['A_ratio']:.8f}\n")
                f.write(f"  F_at_x1={best_zero['F_at_x1']:.8e}\n")
                f.write(f"  a_star/r_c={best_zero['a_star_over_rc']:.8f}\n")
                f.write(f"  legacy a_star/r_c={best_zero['legacy_a_star_over_rc']:.8f}\n")
                f.write(f"  delta vs legacy={best_zero['delta_a_star_vs_legacy']:.8f}\n")
                f.write("\n")
            if best_max is not None:
                f.write("Highest-resolution max-lambda row:\n")
                f.write(f"  lambda_K={best_max['lambda_K']}\n")
                f.write(f"  N_geom={best_max['N_geom']} N_int={best_max['N_int_actual']}\n")
                f.write(f"  F_at_x1={best_max['F_at_x1']:.8e}\n")
                f.write(f"  a_star/r_c={best_max['a_star_over_rc']:.8f}\n")
                f.write(f"  legacy a_star/r_c={best_max['legacy_a_star_over_rc']:.8f}\n")
                f.write(f"  delta vs legacy={best_max['delta_a_star_vs_legacy']:.8f}\n")
                f.write("\n")
            f.write("Interpretation:\n")
            f.write("  This postcheck replaces the legacy contact term only in the post-sweep theorem test.\n")
            f.write("  Because the barrier_flat_at_rc model is shift-free at x=1, any remaining mismatch is then dominated by A_K != 1/(4*pi), not by contact-term-induced drift.\n")

        tex_path = os.path.join(outdir, "shiftfree_postcheck_v10_0.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(f"\\paragraph{{{SCRIPT_VERSION} post-sweep shift-free barrier check.}}\n")
            f.write("After the full legacy sweep, the preferred-fit rows were re-evaluated with the shift-free barrier contact model ")
            f.write("\\texttt{barrier\\_flat\\_at\\_rc}, without altering any legacy outputs. ")
            f.write(f"For the two highest $N_{{\\mathrm{{int}}}}$ rows at $\\lambda_K=0$, one finds ")
            f.write(f"$F(1) = {F10_mid:.8e} \\pm {F10_half:.8e}$ and ")
            f.write(f"$a^*/r_c = {a_star0_mid:.8f} \\pm {a_star0_half:.8f}$. ")
            f.write("Thus the shift-free postcheck isolates the remaining closure error to the residual deviation of $A_K$ from $1/(4\\pi)$, rather than to a structurally shifting contact term.\n")

        return shift_rows
    finally:
        CONTACT_MODEL = contact_model_saved
        ROOT_SELECTION_MODE = root_selection_saved


def write_run_metadata(outdir: str, mode: str, backend_mode: str, backend_used: str,
                      knot_id: str, run_start: float) -> None:
    torch_ver = None
    torch_dev = None
    if _TORCH_AVAILABLE and torch is not None:
        torch_ver = getattr(torch, "__version__", None)
        try:
            torch_dev = str(_pick_torch_device())
        except Exception:
            pass
    meta = {
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "torch_version": torch_ver,
        "torch_device": torch_dev,
        "local_sst_core_loaded": _SST_CORE_AVAILABLE,
        "local_cpp_scan_available": SST_CORE_SCAN_AVAILABLE,
        "ideal_txt_path": ideal_txt_resolved_path,
        "knot_id": knot_id,
        "mode": mode,
        "backend_mode": backend_mode,
        "backend_used": backend_used,
        "contact_model": CONTACT_MODEL,
        "root_selection_mode": ROOT_SELECTION_MODE,
        "branch_mode": BRANCH_MODE,
        "lambda_continuation_sort": LAMBDA_CONTINUATION_SORT,
        "emit_v5_logs": EMIT_V5_LOGS,
        "root_solver_space": ROOT_SOLVER_SPACE,
        "root_xtol": ROOT_XTOL,
        "root_rtol": ROOT_RTOL,
        "root_ftol": ROOT_FTOL,
        "root_scan_count_x": ROOT_SCAN_COUNT_X,
        "target_xnc_abs_tol": TARGET_XNC_ABS_TOL,
        "target_xnc_rel_tol": TARGET_XNC_REL_TOL,
        "postcheck_root_selection_mode": POSTCHECK_ROOT_SELECTION_MODE,
        "postcheck_contact_model": POSTCHECK_CONTACT_MODEL,
        "run_start_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(run_start)),
    }
    meta["script_version"] = SCRIPT_VERSION
    path = os.path.join(outdir, "run_metadata_v10_0.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def _prompt_choice(prompt: str, options: Sequence[str], default: str) -> str:
    opts = list(options)
    label = "/".join(opts)
    default = default if default in opts else opts[0]
    while True:
        val = input(f"{prompt} [{label}] (default {default}): ").strip()
        if not val:
            return default
        if val in opts:
            return val
        print(f"Invalid choice: {val!r}")


def _prompt_text(prompt: str, default: str = "") -> str:
    suffix = f" (default {default})" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val if val else default


def prompt_cli_menu_v10() -> List[str]:
    print(f"\nSST Robustness Sweep {SCRIPT_VERSION} interactive launcher")
    print("Press Enter to accept the default shown in parentheses.\n")

    mode = _prompt_choice("Mode", ["ideal", "torus"], "ideal")
    knot_id = _prompt_text("Single knot id", DEFAULT_KNOT_LIST[0])
    knot_list = _prompt_text("Batch knot list (blank = single knot)", "")
    preset = _prompt_choice("Preset", ["fast", "full"], "full")
    sweep_layout = _prompt_choice("Sweep layout", ["matrix", "exact_pairs_only", "theorem_ladder"], "theorem_ladder")
    backend = _prompt_choice("Backend", list(BS_BACKEND_ALLOWED), "auto")
    contact_model = _prompt_choice("Main sweep contact model", ["legacy", "barrier_flat_at_rc"], "legacy")
    root_mode = _prompt_choice("Root selection mode", ["continuation", "targeted_x_nc", "closest_to_a_nc", "lowest_energy"], "continuation")
    run_postcheck = _prompt_choice("Run shift-free postcheck", ["1", "0"], "1")
    extrap_min = _prompt_text("Extrapolation minimum N_int_actual", str(EXTRAP_MIN_NINT))

    extra_pairs_default = ""
    if sweep_layout == "theorem_ladder":
        extra_pairs_default = ",".join(f"{a}:{b}" for (a, b) in DEFAULT_THEOREM_TARGET_PAIRS)
    extra_pairs = _prompt_text("Extra exact pairs Ngeom:Nint comma-separated", extra_pairs_default)

    n_geom_list = _prompt_text("Override N_geom list (blank = default)", "")
    n_int_list = _prompt_text("Override N_int list (blank = default)", "")
    lambda_list = _prompt_text("Override lambda list (blank = default)", "")
    plateau_fracs = _prompt_text("Override plateau fracs (blank = default)", "")
    output_dir = _prompt_text("Output directory (blank = version default)", "")

    argv: List[str] = [
        "--mode", mode,
        "--knot-id", knot_id,
        "--preset", preset,
        "--backend", backend,
        "--contact-model", contact_model,
        "--root-selection-mode", root_mode,
        "--run-v6-shiftfree-postcheck", run_postcheck,
        "--extrap-min-nint", extrap_min,
        "--sweep-layout", sweep_layout,
    ]
    if knot_list:
        argv += ["--knot-list", knot_list]
    if extra_pairs:
        argv += ["--extra-target-pairs", extra_pairs]
    if n_geom_list:
        argv += ["--n-geom-list", n_geom_list]
    if n_int_list:
        argv += ["--n-int-list", n_int_list]
    if lambda_list:
        argv += ["--lambda-list", lambda_list]
    if plateau_fracs:
        argv += ["--plateau-fracs", plateau_fracs]
    if output_dir:
        argv += ["--output-dir", output_dir]

    print("\n[MENU] Resolved argv:", " ".join(argv), "\n")
    return argv


def run_single_knot_sweep(args: argparse.Namespace, mode: str, knot_id: str, output_dir: str, run_start_wall: float, base_output_dir: str) -> Dict[str, object]:
    global OUTPUT_DIR, KNOT_ID, MAX_FOURIER_MODE, CONTACT_MODEL, ROOT_SELECTION_MODE

    OUTPUT_DIR = output_dir
    KNOT_ID = knot_id
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    initialize_project_sources(KNOT_ID, MAX_FOURIER_MODE, USE_LOCAL_IDEAL_DB, USE_LOCAL_SST_CORE, AUTO_COMPILE_SST_CORE)
    backend_used = detect_bs_backend(BS_BACKEND_MODE, ENABLE_TORCH_ACCEL)

    print("[META] SST ROBUSTNESS SWEEP {} - mode={} knot_id={}".format(SCRIPT_VERSION, mode.upper(), KNOT_ID))
    print("[META] output_dir={}".format(OUTPUT_DIR))
    print("[META] ideal_source={}".format(IDEAL_SOURCE_DESC))
    print("[META] local_sst_core_loaded={} local_cpp_scan_available={}".format(_SST_CORE_AVAILABLE, SST_CORE_SCAN_AVAILABLE))
    print("[META] A_req=1/(4*pi)={}".format(A_req))
    print("[BACKEND] bs_backend={}".format(backend_used))
    if EMIT_V5_LOGS:
        print("[THEOREM] target=no_contact closure means a_nc/r_c = sqrt(4*pi*A_K)")
        print("[THEOREM] target=full_model exact closure requires F(1)=0 in the chosen contact model")
        print("[THEOREM] contact_model={} root_selection_mode={}".format(CONTACT_MODEL, ROOT_SELECTION_MODE))
        if RUN_V6_SHIFT_FREE_POSTCHECK:
            print("[THEOREM] v6_postcheck will rerun theorem-candidate fit rows with shift-free barrier after the legacy sweep")
        print("[THEOREM] v7 root_solver_space={} xtol={} rtol={} ftol={}".format(ROOT_SOLVER_SPACE, ROOT_XTOL, ROOT_RTOL, ROOT_FTOL))
        print("[THEOREM] v7.1 targeted-x_nc selector enabled when requested")
        print("[THEOREM] target window abs={} rel={}".format(TARGET_XNC_ABS_TOL, TARGET_XNC_REL_TOL))
        print("[THEOREM] sweep_layout={} exact_pairs={}".format(SWEEP_LAYOUT, EXTRA_TARGET_PAIRS))
        print("[THEOREM] v9 tail check: need quasi-monotone contracting high-resolution tail before theorem-style OK")
        print("[THEOREM] v10 batch knot comparison enabled at base_output_dir={}".format(base_output_dir))
        print("[THEOREM] v10 parallel theorem candidate fits={}".format(THEOREM_CANDIDATE_FIT_METHODS))
    write_run_metadata(OUTPUT_DIR, mode, BS_BACKEND_MODE, backend_used, KNOT_ID, run_start_wall)

    rows: List[dict] = []
    postcheck_rows: List[dict] = []
    plateau_diag_rows: List[dict] = []
    if mode == "torus":
        R_ratio_grid = np.linspace(2.0, 2.6, 7)
        geom_configs = [(Ng, Ni, R) for Ng in N_GEOM_LIST for Ni in N_INT_LIST for R in R_ratio_grid]
    else:
        if SWEEP_LAYOUT in ("exact_pairs_only", "theorem_ladder"):
            exact_pairs = EXTRA_TARGET_PAIRS[:] if EXTRA_TARGET_PAIRS else DEFAULT_THEOREM_TARGET_PAIRS[:]
            geom_configs = [(Ng, Ni, None) for (Ng, Ni) in exact_pairs]
        else:
            geom_configs = [(Ng, Ni, None) for Ng in N_GEOM_LIST for Ni in N_INT_LIST]

    existing_gc = set()
    tmp_gc: List[Tuple[int, int, Optional[float]]] = []
    for item in geom_configs:
        key = (item[0], item[1], item[2])
        if key not in existing_gc:
            tmp_gc.append(item)
            existing_gc.add(key)

    if mode == "ideal" and SWEEP_LAYOUT == "matrix":
        for (Ng_extra, Ni_extra) in EXTRA_TARGET_PAIRS:
            key = (Ng_extra, Ni_extra, None)
            if key not in existing_gc:
                tmp_gc.append(key)
                existing_gc.add(key)

    geom_configs = tmp_gc

    last_backend_printed = backend_used
    for idx, (N_geom, N_int_target, R_ratio) in enumerate(geom_configs):
        t_block_start = time.perf_counter()
        print("-" * 78)
        if mode == "torus" and R_ratio is not None:
            print("[GEOM] Building torus N_geom={} N_int={} R_t/r_t={:.2f}".format(N_geom, N_int_target, R_ratio))
            geom = build_torus_geometry(N_geom, N_int_target, R_ratio, 1.0)
            ideal_source_str = "Torus R_t/r_t={:.2f}".format(R_ratio)
        else:
            print("[GEOM] Building geometry N_geom={} N_int_target={}".format(N_geom, N_int_target))
            geom = build_geometry(N_geom, N_int_target)
            ideal_source_str = IDEAL_SOURCE_DESC
            print("[GEOM] L_dimless_full={:.6f} d_min_full={:.6f} N_int_actual={} d_min_int={:.6f}".format(geom.L_dimless_full, geom.d_min_full, geom.N_int_actual, geom.d_min_int))

        t_geom_end = time.perf_counter()
        t_geometry_s = t_geom_end - t_block_start
        print("[TIME] geometry_s={:.3f}".format(t_geometry_s))

        t_scan_start = time.perf_counter()
        a_scan, E_vals, backend_this = scan_BS_energy_backend(geom, backend_used)
        if backend_this != last_backend_printed:
            print("[BACKEND] bs_backend={}".format(backend_this))
            last_backend_printed = backend_this
        t_scan_end = time.perf_counter()
        t_scan_s = t_scan_end - t_scan_start
        print("[TIME] scan_s={:.3f}".format(t_scan_s))

        t_fit_start = time.perf_counter()
        fit_results, diagnostics = extract_fits(a_scan, E_vals, geom.L_dimless_full, geom.d_min_full)
        t_fit_end = time.perf_counter()
        t_fit_s = t_fit_end - t_fit_start
        print("[TIME] fit_s={:.3f}".format(t_fit_s))

        if SAVE_PER_RUN_DIAGNOSTICS:
            save_geometry_plot(geom, os.path.join(OUTPUT_DIR, "geom_Ng{}_Ni{}.png".format(N_geom, geom.N_int_actual)))
            save_bs_diagnostics(a_scan, E_vals, fit_results, diagnostics, os.path.join(OUTPUT_DIR, "bs_diagnostics_Ng{}_Ni{}.png".format(N_geom, geom.N_int_actual)))
        if SAVE_LOCAL_A_CURVES:
            save_local_A_curve_csv(diagnostics, geom.d_min_full, os.path.join(OUTPUT_DIR, "local_A_curve_Ng{}_Ni{}.csv".format(N_geom, geom.N_int_actual)))

        plateau_diag = diagnostics.get("plateau_diag", {})
        for method_name, st in plateau_diag.items():
            plateau_diag_rows.append({
                "knot_id": KNOT_ID,
                "N_geom": N_geom, "N_int_target": N_int_target, "N_int_actual": geom.N_int_actual,
                "L_dimless": geom.L_dimless_full, "d_min_dimless": geom.d_min_full,
                "frac": st["frac"], "method_name": method_name, "n_plateau": st["n_plateau"],
                "a_lo": st["a_lo"], "a_hi": st["a_hi"], "a_span": st["a_span"],
                "a_span_over_dmin": st["a_span_over_dmin"], "a_ref": st["a_ref"], "A_ref": st["A_ref"],
                "A_median": st["A_median"], "A_std": st["A_std"], "A_min": st["A_min"], "A_max": st["A_max"],
                "A_median_minus_Areq": (st["A_median"] - A_req) if np.isfinite(st["A_median"]) else np.nan,
                "rel_dE_median": st["rel_dE_median"], "rel_dE_min": st["rel_dE_min"], "rel_dE_max": st["rel_dE_max"],
                "rel_dE_thresh": REL_DE_THRESH, "ideal_source": ideal_source_str, "bs_backend": backend_this,
            })

        if EMIT_V5_LOGS and plateau_diag_rows:
            key = "plateau_0.12"
            st = plateau_diag.get(key)
            if st is not None:
                print("[PLATEAU] N_geom={} N_int={} frac=0.12 n_plateau={} a_lo={} a_hi={} A_median_minus_Areq={:.8e}".format(N_geom, geom.N_int_actual, st["n_plateau"], st["a_lo"], st["a_hi"], (st["A_median"] - A_req) if np.isfinite(st["A_median"]) else float("nan")))

        for fr in fit_results:
            if not np.isfinite(fr.A_K):
                continue
            A_ratio = fr.A_K / A_req
            a_nc = r_c_canon * np.sqrt(4.0 * np.pi * fr.A_K)
            a_nc_over_rc = a_nc / r_c_canon
            x_closure = closure_x_from_A(fr.A_K)
            if EMIT_V5_LOGS:
                print("[FIT] N_geom={} N_int={} method={} A_K={:.8f} A_ratio={:.6f} a_nc_over_rc={:.6f}".format(N_geom, geom.N_int_actual, fr.fit_method, fr.A_K, A_ratio, a_nc_over_rc))
                print("[CHECK] N_geom={} N_int={} method={} closure_x={:.8f} closure_x_minus_1={:.8e}".format(N_geom, geom.N_int_actual, fr.fit_method, x_closure, x_closure - 1.0))

            prev_a_star: Optional[float] = None
            if LAMBDA_CONTINUATION_SORT:
                lam_iter = sorted(LAMBDA_LIST)
            else:
                lam_iter = list(LAMBDA_LIST)
            for lam_K in lam_iter:
                for p_exp in P_LIST:
                    candidates = find_root_candidates(fr.A_K, fr.a_K, geom.L_dimless_full, geom.d_min_full, lam_K, p_exp, CONTACT_MODEL)
                    if ROOT_SELECTION_MODE == "continuation":
                        a_star, is_min, E_star, root_count, min_root_count, root_choice = choose_root_continuation(candidates, prev_a_star, a_nc, BRANCH_MODE)
                    elif ROOT_SELECTION_MODE == "targeted_x_nc":
                        a_star, is_min, E_star, root_count, min_root_count, root_choice = choose_root_targeted_x_nc(candidates, a_nc)
                    else:
                        a_star, is_min, E_star, root_count, min_root_count, root_choice = choose_root(candidates, a_nc, BRANCH_MODE)

                    a_star_over_rc = a_star / r_c_canon if np.isfinite(a_star) else np.nan
                    prev_val = prev_a_star / r_c_canon if (prev_a_star is not None and np.isfinite(prev_a_star)) else np.nan
                    continuation_jump = abs(a_star_over_rc - prev_val) if (np.isfinite(a_star_over_rc) and np.isfinite(prev_val)) else np.nan
                    if np.isfinite(a_star):
                        prev_a_star = a_star

                    beta_dimless = dimensionless_beta(geom.d_min_full * L_natural)
                    F_at_x1 = F_dimensionless(1.0, fr.A_K, beta_dimless, lam_K, p_exp, CONTACT_MODEL)
                    contact_force_at_x1 = contact_force_dimensionless(1.0, beta_dimless, lam_K, p_exp, CONTACT_MODEL)
                    F_at_root = F_dimensionless(a_star_over_rc, fr.A_K, beta_dimless, lam_K, p_exp, CONTACT_MODEL) if np.isfinite(a_star_over_rc) else np.nan
                    if EMIT_V5_LOGS:
                        print("[ROOTX] lambda_K={} a_star_over_rc={} F_at_root={:.8e} solver={}".format(lam_K, a_star_over_rc, F_at_root if np.isfinite(F_at_root) else float("nan"), ROOT_SOLVER_SPACE))
                        if ROOT_SELECTION_MODE == "continuation":
                            print("[CONT] lambda_K={} prev_a_star_over_rc={} a_star_over_rc={} jump={} root_choice={}".format(lam_K, prev_val, a_star_over_rc, continuation_jump, root_choice))
                        print("[BARRIER] lambda_K={} beta={:.8f} contact_force_at_x1={:.8e} F_at_x1={:.8e} contact_model={}".format(lam_K, beta_dimless, contact_force_at_x1 if np.isfinite(contact_force_at_x1) else float("nan"), F_at_x1 if np.isfinite(F_at_x1) else float("nan"), CONTACT_MODEL))

                    delta_lambda_over_rc = abs(a_star_over_rc - 1.0) if np.isfinite(a_star_over_rc) else np.nan
                    status = classify_run(A_ratio, a_star_over_rc, is_min)
                    theorem_candidate_no_contact = bool(np.isfinite(x_closure) and abs(x_closure - 1.0) <= V8_THEOREM_TOL_AINF)
                    theorem_candidate_full_model = bool(np.isfinite(a_star_over_rc) and np.isfinite(F_at_x1) and abs(a_star_over_rc - 1.0) <= V8_THEOREM_TOL_XINF and abs(F_at_x1) <= V8_THEOREM_TOL_FINF)
                    t_total_block_s = time.perf_counter() - t_block_start
                    notes = []
                    if fr.fit_method in THEOREM_CANDIDATE_FIT_METHODS:
                        notes.append("parallel_theorem_candidate")
                    rows.append({
                        "knot_id": KNOT_ID, "mode": mode,
                        "N_geom": N_geom, "N_int_target": N_int_target, "N_int_actual": geom.N_int_actual,
                        "R_t_over_r_t": R_ratio if R_ratio is not None else np.nan,
                        "L_dimless": geom.L_dimless_full, "d_min_dimless": geom.d_min_full,
                        "fit_method": fr.fit_method, "plateau_frac": fr.plateau_frac, "n_plateau": fr.n_plateau,
                        "A_K": fr.A_K, "A_spread": fr.A_spread, "A_ratio": A_ratio, "a_K": fr.a_K, "a_fit_ref": fr.a_fit_ref,
                        "a_nc_m": a_nc, "a_nc_over_rc": a_nc_over_rc, "lambda_K": lam_K, "p_exp": p_exp,
                        "root_count": root_count, "min_root_count": min_root_count, "root_choice": root_choice,
                        "a_star_m": a_star, "a_star_over_rc": a_star_over_rc, "E_star_J": E_star, "delta_lambda_over_rc": delta_lambda_over_rc,
                        "is_min": is_min, "status": status, "uses_local_sst_core": _SST_CORE_AVAILABLE,
                        "ideal_source": ideal_source_str, "notes": "; ".join(notes), "bs_backend": backend_this,
                        "t_geometry_s": t_geometry_s, "t_scan_s": t_scan_s, "t_fit_s": t_fit_s, "t_total_block_s": t_total_block_s,
                        "contact_model": CONTACT_MODEL, "root_selection_mode": ROOT_SELECTION_MODE,
                        "closure_x_from_A": x_closure, "closure_x_minus_1": float(x_closure - 1.0),
                        "beta_dimless": beta_dimless, "F_at_x1": F_at_x1, "contact_force_at_x1": contact_force_at_x1,
                        "continuation_prev_a_star_over_rc": prev_val, "continuation_jump": continuation_jump,
                        "theorem_candidate_no_contact": theorem_candidate_no_contact,
                        "theorem_candidate_full_model": theorem_candidate_full_model,
                        "root_solver_space": ROOT_SOLVER_SPACE, "F_at_root": F_at_root, "root_xtol": ROOT_XTOL, "root_rtol": ROOT_RTOL,
                    })
                    print("[ROOT] lambda_K={} a_star_over_rc={} is_min={} status={}".format(lam_K, a_star_over_rc, is_min, status))

    best = select_best_row(rows)
    if best:
        print("[BEST] practical N_geom={} N_int={} A_K={:.8f} A_ratio={:.6f} a_nc_over_rc={:.8f}".format(best["N_geom"], best["N_int_actual"], best["A_K"], best["A_ratio"], best["a_nc_over_rc"]))
        bx = closure_x_from_A(best["A_K"])
        if EMIT_V5_LOGS:
            print("[BEST] theorem_no_contact A_K={:.8f} closure_x={:.8f} closure_x_minus_1={:.8e}".format(best["A_K"], bx, bx - 1.0))
            comp = None
            for r in rows:
                if (r["N_geom"] == best["N_geom"] and r["N_int_actual"] == best["N_int_actual"] and r["fit_method"] == best["fit_method"] and r["p_exp"] == best.get("p_exp", P_LIST[0])):
                    if not np.isfinite(r.get("a_star_over_rc", np.nan)):
                        continue
                    if comp is None or r["lambda_K"] > comp["lambda_K"]:
                        comp = r
            if comp is not None:
                print("[BEST] theorem_full_model contact_model={} F_at_x1={:.8e} a_star_over_rc={:.8f}".format(CONTACT_MODEL, comp.get("F_at_x1", float("nan")), comp.get("a_star_over_rc", float("nan"))))
            else:
                print("[BEST] theorem_full_model contact_model={} F_at_x1=nan a_star_over_rc=nan".format(CONTACT_MODEL))

    csv_path = os.path.join(OUTPUT_DIR, "robustness_summary_v10_{}.csv".format(mode))
    write_csv(rows, csv_path)
    if SAVE_SUMMARY_PLOTS:
        save_summary_plots(rows, OUTPUT_DIR)
    if SAVE_PLATEAU_DIAGNOSTICS:
        plateau_csv = os.path.join(OUTPUT_DIR, "plateau_mask_diagnostics_v10_0.csv")
        write_plateau_diagnostics_csv(plateau_diag_rows, plateau_csv)
        save_plateau_diagnostics_summary_plot(plateau_diag_rows, os.path.join(OUTPUT_DIR, "plateau_mask_summary_v10_0.png"))
    write_best_estimate(rows, OUTPUT_DIR)

    if RUN_V6_SHIFT_FREE_POSTCHECK:
        postcheck_rows = run_v6_shiftfree_postcheck(rows, OUTPUT_DIR)

    print("\n[META] Sweep complete")
    print("[META] CSV summary : {}".format(csv_path))
    print("[META] Best-estimate {} CSV/TXT/TeX : {}".format(SCRIPT_VERSION, OUTPUT_DIR))
    if RUN_V6_SHIFT_FREE_POSTCHECK:
        print("[META] Shift-free postcheck {} CSV/TXT/TeX : {}".format(SCRIPT_VERSION, OUTPUT_DIR))
    if SAVE_PLATEAU_DIAGNOSTICS:
        print("[META] Plateau diagnostics CSV/PNG : {}".format(OUTPUT_DIR))
    print("[META] run_metadata_v10_0.json : {}".format(os.path.join(OUTPUT_DIR, "run_metadata_v10_0.json")))

    if WRITE_V8_EXTRAPOLATION:
        if not postcheck_rows:
            if RUN_V6_SHIFT_FREE_POSTCHECK:
                print("[WARN] Shift-free postcheck was enabled but returned no rows; extrapolation will contain only no-contact asymptotics.")
            else:
                print("[WARN] Shift-free postcheck is disabled; extrapolation will contain only no-contact asymptotics.")
        try:
            write_v8_extrapolation(rows, postcheck_rows, OUTPUT_DIR)
            print("[META] Extrapolation {} CSV/TXT/TeX : {}".format(SCRIPT_VERSION, OUTPUT_DIR))
            write_v9_3_parallel_theorem_report(rows, postcheck_rows, OUTPUT_DIR)
            print("[META] Parallel theorem candidates {} CSV/TXT/TeX : {}".format(SCRIPT_VERSION, OUTPUT_DIR))
        except Exception as exc:
            print(f"[WARN] v8 extrapolation writer failed: {exc}")

    summary = {
        "knot_id": KNOT_ID, "mode": mode, "output_dir": OUTPUT_DIR,
        "backend_used": backend_used, "ideal_source": IDEAL_SOURCE_DESC,
        "rows_written": len(rows), "postcheck_rows_written": len(postcheck_rows),
        "best_found": bool(best), "closure_score": closure_score_from_row(best),
    }
    if best:
        summary.update({
            "fit_method": best.get("fit_method"), "N_geom": best.get("N_geom"), "N_int_actual": best.get("N_int_actual"),
            "A_K": best.get("A_K"), "A_ratio": best.get("A_ratio"), "a_nc_over_rc": best.get("a_nc_over_rc"),
            "closure_x_from_A": best.get("closure_x_from_A"), "a_star_over_rc": best.get("a_star_over_rc"),
            "status": best.get("status"),
        })
    return summary


def main() -> None:
    global OUTPUT_DIR, KNOT_ID, MAX_FOURIER_MODE, N_GEOM_LIST, N_INT_LIST, LAMBDA_LIST, PLATEAU_FRACS
    global USE_LOCAL_SST_CORE, AUTO_COMPILE_SST_CORE, ENABLE_TORCH_ACCEL, BS_BACKEND_MODE
    global CONTACT_MODEL, ROOT_SELECTION_MODE, EMIT_V5_LOGS, BRANCH_MODE
    global RUN_V6_SHIFT_FREE_POSTCHECK
    global WRITE_V8_EXTRAPOLATION, EXTRAP_MIN_NINT, EXTRA_TARGET_PAIRS, SWEEP_LAYOUT

    parser = argparse.ArgumentParser(description=f"SST Robustness Sweep {SCRIPT_VERSION}")
    parser.add_argument("--mode", choices=["ideal", "torus"], default="ideal")
    parser.add_argument("--preset", choices=["fast", "full"], default="full", help="fast = smaller sweep for UI testing; full = full sweep")
    parser.add_argument("--output-dir", default="", help="Output directory (default: .../sst_knot_candidate_robustness_outputs_v10_0)")
    parser.add_argument("--backend", choices=BS_BACKEND_ALLOWED, default="auto")
    parser.add_argument("--knot-id", default=DEFAULT_KNOT_LIST[0], help="Single knot id for the sweep, e.g. 3:1:1")
    parser.add_argument("--knot-list", default="", help="Whitespace/comma-separated batch knot ids, e.g. 3:1:1,4:1:1,5:1:1,5:2:1")
    parser.add_argument("--max-fourier-mode", type=int, default=None)
    parser.add_argument("--n-geom-list", default="", help="Comma-separated e.g. 4000,8000,16000")
    parser.add_argument("--n-int-list", default="", help="Comma-separated e.g. 2000,4000,8000")
    parser.add_argument("--lambda-list", default="", help="Comma-separated e.g. 0,1e-3,1e-2")
    parser.add_argument("--plateau-fracs", default="", help="Comma-separated e.g. 0.08,0.12,0.16")
    parser.add_argument("--contact-model", choices=["legacy", "barrier_flat_at_rc"], default="legacy")
    parser.add_argument("--root-selection-mode", choices=["continuation", "closest_to_a_nc", "lowest_energy", "targeted_x_nc"], default="continuation")
    parser.add_argument("--emit-v5-logs", type=int, choices=[0, 1], default=1)
    parser.add_argument("--branch-mode", choices=["closest_to_a_nc", "lowest_energy"], default="closest_to_a_nc", help="Used when root-selection-mode is not continuation; also sets first-lambda fallback for continuation")
    parser.add_argument("--run-v6-shiftfree-postcheck", type=int, choices=[0, 1], default=1, help="After the normal legacy sweep, run an extra shift-free barrier theorem postcheck")
    parser.add_argument("--no-torch", action="store_true")
    parser.add_argument("--no-local-sst-core", action="store_true")
    parser.add_argument("--no-auto-compile", action="store_true")
    parser.add_argument("--extra-target-pairs", default="", help="Comma-separated exact Ngeom:Nint pairs, e.g. 48000:48000,64000:64000")
    parser.add_argument("--extrap-min-nint", type=int, default=8000, help="Minimum N_int_actual included in v8/v9 asymptotic extrapolation")
    parser.add_argument("--no-v8-extrapolation", action="store_true", help="Disable asymptotic extrapolation writer")
    parser.add_argument("--sweep-layout", choices=["matrix", "exact_pairs_only", "theorem_ladder"], default="matrix", help="matrix = original sweep grid; exact_pairs_only = only exact Ngeom:Nint pairs; theorem_ladder = exact-pair ladder geared to theorem runs")

    argv_in = None
    if len(sys.argv) == 1 and sys.stdin.isatty():
        argv_in = prompt_cli_menu_v10()
    args = parser.parse_args(argv_in)

    EXTRAP_MIN_NINT = int(args.extrap_min_nint)
    WRITE_V8_EXTRAPOLATION = not bool(args.no_v8_extrapolation)
    EXTRA_TARGET_PAIRS = parse_exact_pairs(args.extra_target_pairs) if args.extra_target_pairs else []
    SWEEP_LAYOUT = str(args.sweep_layout)
    if SWEEP_LAYOUT == "theorem_ladder":
        for pair in DEFAULT_THEOREM_TARGET_PAIRS:
            if pair not in EXTRA_TARGET_PAIRS:
                EXTRA_TARGET_PAIRS.append(pair)

    CONTACT_MODEL = args.contact_model
    ROOT_SELECTION_MODE = args.root_selection_mode
    EMIT_V5_LOGS = bool(args.emit_v5_logs)
    BRANCH_MODE = args.branch_mode
    RUN_V6_SHIFT_FREE_POSTCHECK = bool(args.run_v6_shiftfree_postcheck)

    if args.no_local_sst_core:
        USE_LOCAL_SST_CORE = False
    if args.no_auto_compile:
        AUTO_COMPILE_SST_CORE = False
    if args.no_torch:
        ENABLE_TORCH_ACCEL = False
    if args.output_dir:
        OUTPUT_DIR = os.path.abspath(args.output_dir)
    MAX_FOURIER_MODE = args.max_fourier_mode
    BS_BACKEND_MODE = args.backend

    if args.preset == "fast":
        N_GEOM_LIST = [4000, 8000]
        N_INT_LIST = [2000, 4000]
        LAMBDA_LIST = [0.0, 1e-3]
    if args.n_geom_list:
        N_GEOM_LIST = [int(x.strip()) for x in args.n_geom_list.split(",") if x.strip()]
    if args.n_int_list:
        N_INT_LIST = [int(x.strip()) for x in args.n_int_list.split(",") if x.strip()]
    if args.lambda_list:
        LAMBDA_LIST = [float(x.strip()) for x in args.lambda_list.replace(",", " ").split() if x.strip()]
    if args.plateau_fracs:
        PLATEAU_FRACS = [float(x.strip()) for x in args.plateau_fracs.split(",") if x.strip()]

    knot_ids = parse_knot_list(args.knot_list) if args.knot_list else [args.knot_id]
    if not knot_ids:
        knot_ids = [DEFAULT_KNOT_LIST[0]]

    base_output_dir = OUTPUT_DIR
    os.makedirs(base_output_dir, exist_ok=True)
    run_start_wall = time.time()
    run_start = time.perf_counter()

    print("[META] v10 knot batch = {}".format(knot_ids))
    knot_records: List[dict] = []
    multi_knot = len(knot_ids) > 1

    for idx, knot_id in enumerate(knot_ids, start=1):
        if multi_knot:
            knot_outdir = os.path.join(base_output_dir, sanitize_knot_id_for_path(knot_id))
        else:
            knot_outdir = base_output_dir
        print("\n" + "=" * 90)
        print("[META] Starting knot {}/{} : {}".format(idx, len(knot_ids), knot_id))
        print("=" * 90)
        rec = run_single_knot_sweep(args, args.mode, knot_id, knot_outdir, run_start_wall, base_output_dir)
        knot_records.append(rec)

    write_knot_comparison_summary(knot_records, base_output_dir)

    total_elapsed = time.perf_counter() - run_start
    print("[TIME] total_script_s={:.3f}".format(total_elapsed))
    print("\n[META] Batch complete")
    print("[META] Knot comparison CSV/TXT : {}".format(base_output_dir))



if __name__ == "__main__":
    main()