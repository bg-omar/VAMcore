
#!/usr/bin/env python3
"""
SST ideal-trefoil robustness sweep v3 (project-integrated)
=========================================================

Project integration upgrades:
- loads Fourier coefficients directly from local `ideal.txt` (Gilbert database),
- optionally auto-compiles and imports local `sst_core.cpp`,
- keeps the PyTorch/XPU/CUDA/MPS accelerated Biot-Savart kernel,
- keeps the cleaned no-contact naming: a_nc instead of a0.

Important:
- The local `sst_core.cpp` is NOT a drop-in replacement for the cutoff-scanned
  Biot-Savart kernel used in this closure analysis. Its exposed
  `calculate_neumann_self_energy(points, rc)` uses a different regularization.
  So this script uses sst_core only for optional project-native diagnostics
  (length / writhe / curvature / alternate Neumann-style energy), not as the
  main closure kernel.

This script is designed to live in the same folder as:
- ideal.txt
- sst_core.cpp

Typical use:
    python sst_ideal_trefoil_robustness_sweep_v3_project.py
"""

from __future__ import annotations

import csv
import glob
import math
import os
import re
import sys
import argparse
import importlib
from dataclasses import dataclass
from setuptools import Extension, setup
from typing import Dict, List, Optional, Tuple

# Preserve the user's Intel/XPU hint.
os.environ.setdefault("ONEAPI_DEVICE_SELECTOR", "level_zero:0")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq

try:
    import torch  # type: ignore[import]
    _TORCH_AVAILABLE = True
except Exception:
    torch = None  # type: ignore[assignment]
    _TORCH_AVAILABLE = False

# -----------------------------------------------------------------------------
# 0. Local project files / integration
# -----------------------------------------------------------------------------
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
IDEAL_DB_PATH = os.path.join(SCRIPT_DIR, "ideal.txt")
SST_CORE_CPP_PATH = os.path.join(SCRIPT_DIR, "sst_core.cpp")

USE_LOCAL_IDEAL_DB = True
USE_LOCAL_SST_CORE = True
AUTO_COMPILE_SST_CORE = True

# Knot selection from Gilbert database.
KNOT_ID = "3:1:1"
MAX_FOURIER_MODE: Optional[int] = None   # None = use all coeffs in ideal.txt

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
# 2. Built-in fallback Fourier coefficients (first 30 modes of Gilbert 3:1:1)
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

# Will be filled by the loader below.
ideal_trefoil_coeffs: List[Tuple[int, float, float, float, float, float, float]] = []
IDEAL_L_REF: float = 16.371637
IDEAL_D_REF: float = 1.0
IDEAL_SOURCE_DESC: str = "fallback hardcoded 30-mode coefficients"

# Optional local C++ extension
sst_core = None
_SST_CORE_AVAILABLE = False

# For 2C/2D (must be defined before the blocks below)
IDEAL_TXT_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "ideal.txt"))
USE_LOCAL_IDEAL_TXT = True
SST_CORE_MODULE_NAME = "sst_core"


def _parse_vec3(text: str) -> Tuple[float, float, float]:
    vals = [float(x.strip()) for x in text.split(",")]
    if len(vals) != 3:
        raise ValueError(f"Expected 3-vector, got: {text}")
    return float(vals[0]), float(vals[1]), float(vals[2])


def load_gilbert_coeffs_from_ideal_txt(path: str, knot_id: str) -> Tuple[List[Tuple[int, float, float, float, float, float, float]], dict]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    ab_pat = re.compile(
        rf'<AB\s+Id="{re.escape(knot_id)}"[^>]*L="([^"]+)"[^>]*D="([^"]+)"[^>]*>(.*?)</AB>',
        re.DOTALL,
    )
    m = ab_pat.search(text)
    if not m:
        raise ValueError(f"Knot Id={knot_id} not found in {path}")

    L_ref = float(m.group(1).strip())
    D_ref = float(m.group(2).strip())
    block = m.group(3)

    coeff_pat = re.compile(r'<Coeff\s+I="\s*([0-9]+)"\s+A="([^"]+)"\s+B="([^"]+)"\s*/>')
    coeffs: List[Tuple[int, float, float, float, float, float, float]] = []
    for cm in coeff_pat.finditer(block):
        k = int(cm.group(1))
        Ax, Ay, Az = _parse_vec3(cm.group(2))
        Bx, By, Bz = _parse_vec3(cm.group(3))
        coeffs.append((k, Ax, Ay, Az, Bx, By, Bz))

    if not coeffs:
        raise ValueError(f"No coefficients parsed for knot Id={knot_id}")

    coeffs.sort(key=lambda row: row[0])
    meta = {
        "source": os.path.abspath(path),
        "knot_id": knot_id,
        "L_ref": L_ref,
        "D_ref": D_ref,
        "n_modes": len(coeffs),
    }
    return coeffs, meta


# Default to fallback so IDEAL_META.n_modes and rest of script have data if we don't load
ideal_trefoil_coeffs = list(FALLBACK_IDEAL_TREFOIL_COEFFS)

IDEAL_META = {
    "source": "hardcoded",
    "knot_id": KNOT_ID,
    "L_ref": float("nan"),
    "D_ref": float("nan"),
    "n_modes": len(ideal_trefoil_coeffs),
}

if USE_LOCAL_IDEAL_TXT and os.path.exists(IDEAL_TXT_PATH):
    try:
        ideal_trefoil_coeffs, IDEAL_META = load_gilbert_coeffs_from_ideal_txt(IDEAL_TXT_PATH, KNOT_ID)
        IDEAL_L_REF = IDEAL_META["L_ref"]
        IDEAL_D_REF = IDEAL_META["D_ref"]
        IDEAL_SOURCE_DESC = str(IDEAL_META["source"])
        print(f"[ideal.txt] Loaded knot {KNOT_ID} from {IDEAL_META['source']} with L={IDEAL_META['L_ref']:.6f}, D={IDEAL_META['D_ref']:.6f}")
    except Exception as exc:
        print(f"[ideal.txt] WARNING: failed to load {KNOT_ID} from {IDEAL_TXT_PATH}: {exc}")
        print("[ideal.txt] Falling back to hardcoded coefficients.")
        ideal_trefoil_coeffs = list(FALLBACK_IDEAL_TREFOIL_COEFFS)


def needs_recompile(cpp_file: str = "sst_core.cpp", module_name: str = SST_CORE_MODULE_NAME) -> bool:
    if not os.path.exists(cpp_file):
        return False
    compiled_files = glob.glob(f"{module_name}.*")
    binaries = [f for f in compiled_files if f.endswith(".pyd") or f.endswith(".so")]
    if not binaries:
        return True
    latest_binary = max(binaries, key=os.path.getmtime)
    return os.path.getmtime(cpp_file) > os.path.getmtime(latest_binary)


def build_local_sst_core(cpp_file: str = "sst_core.cpp", module_name: str = SST_CORE_MODULE_NAME) -> None:
    import pybind11

    if sys.platform == "win32":
        c_args = ["/O2", "/std:c++17"]
        link_args: List[str] = []
        if os.environ.get("SST_CORE_OPENMP", "0") == "1":
            c_args.append("/openmp")
    else:
        c_args = ["-O3", "-std=c++17"]
        link_args = []
        if os.environ.get("SST_CORE_OPENMP", "0") == "1":
            c_args.append("-fopenmp")
            link_args.append("-fopenmp")

    ext_modules = [
        Extension(
            module_name,
            [cpp_file],
            include_dirs=[pybind11.get_include()],
            language="c++",
            extra_compile_args=c_args,
            extra_link_args=link_args,
        ),
    ]
    setup(
        name=module_name,
        ext_modules=ext_modules,
        script_args=["build_ext", "--inplace"],
    )


def try_load_local_sst_core() -> Optional[object]:
    if not USE_LOCAL_SST_CORE:
        return None
    cpp_path = os.path.abspath(os.path.join(SCRIPT_DIR, "sst_core.cpp"))
    if not os.path.exists(cpp_path):
        return None
    try:
        if needs_recompile(cpp_path, SST_CORE_MODULE_NAME):
            print("[sst_core] Recompiling local sst_core.cpp ...")
            build_local_sst_core(cpp_path, SST_CORE_MODULE_NAME)
        return importlib.import_module(SST_CORE_MODULE_NAME)
    except Exception as exc:
        print(f"[sst_core] WARNING: local sst_core unavailable: {exc}")
        return None


SST_CORE = try_load_local_sst_core()
SST_CORE_SCAN_AVAILABLE = bool(
    SST_CORE is not None and hasattr(SST_CORE, "calculate_bs_cutoff_energy_scan")
)

# -----------------------------------------------------------------------------
# 3. Sweep controls
# -----------------------------------------------------------------------------
OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "sst_ideal_trefoil_robustness_outputs_v3"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

IDEAL_TXT_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "ideal.txt"))
KNOT_ID = "3:1:1"
USE_LOCAL_IDEAL_TXT = True
USE_LOCAL_SST_CORE = True
SST_CORE_MODULE_NAME = "sst_core"

N_GEOM_LIST = [4000, 8000, 16000, 32000]
N_INT_LIST = [2000, 4000, 8000, 16000, 32000]
A_SCAN_COUNT = 24
PLATEAU_FRACS = [0.08, 0.12, 0.16]
REL_DE_THRESH = 1e-4
LAMBDA_LIST = [0.0, 1e-3, 3e-3, 1e-2]
P_LIST = [2]
BS_BLOCK = 512

ENABLE_TORCH_ACCEL = True
SAVE_PER_RUN_DIAGNOSTICS = False
SAVE_SUMMARY_PLOTS = True

# Root selection among multiple minima / stationary branches:
#   "closest_to_a_nc" or "lowest_energy"
BRANCH_MODE = "closest_to_a_nc"

# Preferred fit method for final best estimate.
PREFERRED_FIT_METHOD = "plateau_0.12"

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
    a_fit_ref: float
    n_plateau: int


@dataclass
class RootCandidate:
    a_star: float
    is_min: bool
    E_star: float


# -----------------------------------------------------------------------------
# 4. Local project integration helpers
# -----------------------------------------------------------------------------
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


def needs_recompile(cpp_file: str = SST_CORE_CPP_PATH, module_name: str = "sst_core") -> bool:
    if not os.path.exists(cpp_file):
        return False
    compiled_files = glob.glob(os.path.join(SCRIPT_DIR, f"{module_name}.*"))
    binaries = [f for f in compiled_files if f.endswith(".pyd") or f.endswith(".so")]
    if not binaries:
        return True
    latest_binary = max(binaries, key=os.path.getmtime)
    return os.path.getmtime(cpp_file) > os.path.getmtime(latest_binary)


def build_sst_core() -> None:
    import pybind11
    from setuptools import Extension, setup

    if sys.platform == "win32":
        c_args = ["/O2", "/std:c++14"]
    else:
        c_args = ["-O3", "-std=c++14"]

    ext_modules = [
        Extension(
            "sst_core",
            [SST_CORE_CPP_PATH],
            include_dirs=[pybind11.get_include()],
            language="c++",
            extra_compile_args=c_args,
        ),
    ]

    old_argv = list(sys.argv)
    try:
        sys.argv = ["setup.py", "build_ext", "--inplace"]
        setup(
            name="sst_core",
            ext_modules=ext_modules,
            script_args=["build_ext", "--inplace"],
        )
    finally:
        sys.argv = old_argv


def try_enable_local_sst_core() -> None:
    global sst_core, _SST_CORE_AVAILABLE
    if not USE_LOCAL_SST_CORE:
        return
    if not os.path.exists(SST_CORE_CPP_PATH):
        return
    try:
        if AUTO_COMPILE_SST_CORE and needs_recompile():
            print("Re-compiling local sst_core.cpp ...")
            build_sst_core()
        import importlib
        sst_core = importlib.import_module("sst_core")
        _SST_CORE_AVAILABLE = True
    except Exception as exc:
        print(f"[warn] Local sst_core unavailable: {exc}")
        sst_core = None
        _SST_CORE_AVAILABLE = False


def initialize_project_sources() -> None:
    global ideal_trefoil_coeffs, IDEAL_L_REF, IDEAL_D_REF, IDEAL_SOURCE_DESC

    if USE_LOCAL_IDEAL_DB:
        try:
            coeffs, L_ref, D_ref = load_coeffs_from_ideal_txt(IDEAL_DB_PATH, KNOT_ID, MAX_FOURIER_MODE)
            ideal_trefoil_coeffs = coeffs
            IDEAL_L_REF = L_ref
            IDEAL_D_REF = D_ref
            max_k = max(k for k, *_ in coeffs)
            IDEAL_SOURCE_DESC = f"ideal.txt ({KNOT_ID}, {len(coeffs)} modes, k_max={max_k})"
        except Exception as exc:
            print(f"[warn] Could not load ideal.txt coefficients: {exc}")
            ideal_trefoil_coeffs = list(FALLBACK_IDEAL_TREFOIL_COEFFS)
            IDEAL_L_REF = 16.371637
            IDEAL_D_REF = 1.0
            IDEAL_SOURCE_DESC = "fallback hardcoded 30-mode coefficients"
    else:
        ideal_trefoil_coeffs = list(FALLBACK_IDEAL_TREFOIL_COEFFS)
        IDEAL_L_REF = 16.371637
        IDEAL_D_REF = 1.0
        IDEAL_SOURCE_DESC = "fallback hardcoded 30-mode coefficients"

    try_enable_local_sst_core()


# -----------------------------------------------------------------------------
# 5. Fourier evaluation
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


# -----------------------------------------------------------------------------
# 5b. Torus T(2,3) evaluation (Advanced Sweep)
# -----------------------------------------------------------------------------
def eval_torus_trefoil(t_arr: np.ndarray, R_t: float, r_t: float) -> np.ndarray:
    """Analytic (p,q)=(2,3) torus trefoil embedding on a torus of radii R_t, r_t."""

    p, q = 2.0, 3.0
    theta = 2.0 * np.pi * p * t_arr
    phi = 2.0 * np.pi * q * t_arr
    X = np.zeros((len(t_arr), 3), dtype=float)
    X[:, 0] = (R_t + r_t * np.cos(phi)) * np.cos(theta)
    X[:, 1] = (R_t + r_t * np.cos(phi)) * np.sin(theta)
    X[:, 2] = r_t * np.sin(phi)
    return X


def eval_torus_trefoil_deriv(t_arr: np.ndarray, R_t: float, r_t: float) -> np.ndarray:
    """Derivative with respect to dimensionless parameter t for T(2,3) torus trefoil."""

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


def build_torus_geometry(N_geom: int, N_int_target: int, R_t: float, r_t: float) -> GeometryData:
    """Build geometry data for an analytic T(2,3) torus trefoil.

    The interface mirrors build_geometry so the downstream sweep code can remain
    unchanged, aside from mode selection.
    """

    # Sample parameter uniformly on [0,1)
    t_full = np.linspace(0.0, 1.0, N_geom, endpoint=False)

    # Evaluate curve and its derivative
    pts_full = eval_torus_trefoil(t_full, R_t, r_t)
    dpts_dt = eval_torus_trefoil_deriv(t_full, R_t, r_t)

    # Local speed and discrete arc-length spacing (dimensionless)
    speed = np.linalg.norm(dpts_dt, axis=1)
    dt = 1.0 / N_geom
    ds_full = speed * dt
    tangents_full = dpts_dt / speed[:, None]

    L_dimless_full = float(np.sum(ds_full))

    # Subsample for interaction geometry, trying to hit ~N_int_target points
    if N_int_target >= N_geom:
        stride = 1
    else:
        stride = max(1, int(math.ceil(N_geom / N_int_target)))

    pts_int = pts_full[::stride]
    tangents_int = tangents_full[::stride]
    ds_int = ds_full[::stride] * stride

    # Fix final segment to ensure total matches L_dimless_full exactly
    ds_int[-1] += L_dimless_full - np.sum(ds_int)

    # Coarse minimum self-distances for diagnostics
    excl_int = max(5, len(pts_int) // 15)
    d_min_int = coarse_min_self_distance(pts_int, excl_int)

    # For d_min_full, cap sampling similarly to build_geometry
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


# -----------------------------------------------------------------------------
# 6. Geometry helpers
# -----------------------------------------------------------------------------
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
    if _SST_CORE_AVAILABLE:
        try:
            L_dimless_cpp = float(sst_core.calculate_length(np.asarray(pts_full, dtype=np.float64)))
            # Prefer the independent local computation for continuity, but print
            # the project-native diagnostic if it is finite and close.
            if np.isfinite(L_dimless_cpp):
                pass
        except Exception:
            pass

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


# -----------------------------------------------------------------------------
# 7. Torch-accelerated Biot-Savart kernel
# -----------------------------------------------------------------------------
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


def compute_E_BS_norm_scan_local_cpp(a_scan: np.ndarray, pts: np.ndarray, tangents: np.ndarray, ds_arr: np.ndarray) -> Optional[np.ndarray]:
    if not SST_CORE_SCAN_AVAILABLE:
        return None
    try:
        out = SST_CORE.calculate_bs_cutoff_energy_scan(
            np.ascontiguousarray(pts, dtype=np.float64),
            np.ascontiguousarray(tangents, dtype=np.float64),
            np.ascontiguousarray(ds_arr, dtype=np.float64),
            np.ascontiguousarray(a_scan, dtype=np.float64),
        )
        return np.asarray(out, dtype=float)
    except Exception as exc:
        print(f"[sst_core] WARNING: C++ cutoff scan failed, falling back: {exc}")
        return None


# -----------------------------------------------------------------------------
# 8. Biot-Savart scan and fit extraction
# -----------------------------------------------------------------------------
def scan_BS_energy(geom: GeometryData) -> Tuple[np.ndarray, np.ndarray]:
    ds_med = float(np.median(geom.ds_int))
    a_lo = max(3.0 * ds_med, geom.d_min_int * 5e-4)
    a_hi = geom.d_min_int * 0.35
    a_scan = np.logspace(np.log10(a_lo), np.log10(a_hi), A_SCAN_COUNT)
    # Fast path: use local C++ cutoff-scan backend if present.
    E_cpp = compute_E_BS_norm_scan_local_cpp(a_scan, geom.pts_int, geom.tangents_int, geom.ds_int)
    if E_cpp is not None and len(E_cpp) == len(a_scan):
        return a_scan, E_cpp
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
            a_fit_ref = float(a_mid[idx_ref])
            a_K = y_ref - A_plateau * np.log(L_dimless / a_fit_ref)
            out.append(FitResult(f"plateau_{frac:.2f}", frac, A_plateau, A_spread, float(a_K), a_fit_ref, int(np.sum(mask))))
        else:
            out.append(FitResult(f"plateau_{frac:.2f}", frac, np.nan, np.nan, np.nan, np.nan, 0))

    diagnostics = {
        "a_mid": a_mid,
        "A_local": A_local,
        "x_scan": x_scan,
        "y_scan": y_scan,
    }
    return out, diagnostics


# -----------------------------------------------------------------------------
# 9. Route-2 stationary radius / regularized model
# -----------------------------------------------------------------------------
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
    changes = np.where((signs[:-1] * signs[1:] < 0) |
                       ((signs[:-1] == 0) & (signs[1:] != 0)) |
                       ((signs[:-1] != 0) & (signs[1:] == 0)))[0]

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


def choose_root(candidates: List[RootCandidate], a_nc: float, branch_mode: str) -> Tuple[float, bool, float, int, int, str]:
    if not candidates:
        return np.nan, False, np.inf, 0, 0, "none"
    mins = [c for c in candidates if c.is_min]
    pool = mins if mins else candidates
    if branch_mode == "lowest_energy":
        chosen = min(pool, key=lambda c: c.E_star)
        choice = "lowest_energy"
    else:
        chosen = min(pool, key=lambda c: abs(c.a_star - a_nc))
        choice = "closest_to_a_nc"
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


# -----------------------------------------------------------------------------
# 10. Diagnostics, CSV, summary plots
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


def write_best_estimate(rows: List[dict], outdir: str) -> None:
    best = select_best_row(rows)
    if best is None:
        return

    no_contact = [r for r in rows if r["lambda_K"] == 0.0 and np.isfinite(r["A_K"]) and np.isfinite(r["a_nc_over_rc"])]
    A_sys = robust_half_range([r["A_K"] for r in no_contact])
    A_ratio_sys = robust_half_range([r["A_ratio"] for r in no_contact])
    a_nc_sys = robust_half_range([r["a_nc_over_rc"] for r in no_contact])

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
        "a_nc_over_rc_best": best["a_nc_over_rc"],
        "a_nc_over_rc_systematic_half_range": a_nc_sys,
        "a_star_over_rc_provisional_center": a_star_center,
        "a_star_over_rc_provisional_half_range": a_star_sys,
        "branch_mode": BRANCH_MODE,
        "ideal_source": IDEAL_SOURCE_DESC,
        "uses_local_sst_core": _SST_CORE_AVAILABLE,
        "comment": "Quote A_K_best and a_nc_over_rc_best as the cleanest current estimates. Treat a_star_over_rc as provisional until branch sensitivity is reduced.",
    }

    csv_path = os.path.join(outdir, "final_best_estimate.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.keys()))
        writer.writeheader()
        writer.writerow(result)

    txt_path = os.path.join(outdir, "final_best_estimate.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("SST ideal-trefoil final best-estimate (v3 project-integrated)\n")
        f.write("=" * 64 + "\n")
        f.write(f"Ideal source                : {IDEAL_SOURCE_DESC}\n")
        f.write(f"Local sst_core available    : {_SST_CORE_AVAILABLE}\n")
        f.write(f"Preferred fit method        : {best['fit_method']}\n")
        f.write(f"Best grid                   : N_geom={best['N_geom']}, N_int={best['N_int_actual']}\n")
        f.write(f"A_K_best                    : {best['A_K']:.8f} +- {A_sys:.8f} (systematic half-range)\n")
        f.write(f"A_ratio_best                : {best['A_ratio']:.8f} +- {A_ratio_sys:.8f}\n")
        f.write(f"a_nc/r_c_best               : {best['a_nc_over_rc']:.8f} +- {a_nc_sys:.8f}\n")
        if np.isfinite(a_star_center):
            f.write(f"a*/r_c provisional center   : {a_star_center:.8f} +- {a_star_sys:.8f}\n")
        else:
            f.write("a*/r_c provisional center   : nan\n")
        f.write(f"Branch mode                 : {BRANCH_MODE}\n\n")
        f.write("Interpretation: A_K_best and a_nc/r_c_best are the cleanest current closure estimates. ")
        f.write("The full-model a*/r_c remains provisional until branch sensitivity and Biot-Savart resolution are better constrained.\n")

    tex_path = os.path.join(outdir, "final_best_estimate.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\\paragraph{Final best-estimate from the present v3 project-integrated sweep.}\n")
        f.write("Using the ideal trefoil from the local Gilbert database, the preferred current estimate is taken from the selected best no-contact run at the preferred fit window. ")
        f.write(f"This gives\n\\[\nA_K^{{\\mathrm{{best}}}} = {best['A_K']:.8f} \\pm {A_sys:.8f}_{{\\mathrm{{syst}}}},\n\\]\n")
        f.write(f"relative to $1/(4\\pi)={A_req:.8f}$, i.e.\n\\[\n\\frac{{A_K^{{\\mathrm{{best}}}}}}{{1/(4\\pi)}} = {best['A_ratio']:.8f} \\pm {A_ratio_sys:.8f}_{{\\mathrm{{syst}}}}.\n\\]\n")
        f.write(f"The corresponding no-contact radius estimate is\n\\[\n\\left(\\frac{{a_{{\\mathrm{{nc}}}}}}{{r_c}}\\right)^{{\\mathrm{{best}}}} = {best['a_nc_over_rc']:.8f} \\pm {a_nc_sys:.8f}_{{\\mathrm{{syst}}}}.\n\\]\n")
        if np.isfinite(a_star_center):
            f.write(f"For the present regularized model, a provisional summary of the selected branch gives\n\\[\n\\left(\\frac{{a^*}}{{r_c}}\\right)_{{\\mathrm{{prov}}}} = {a_star_center:.8f} \\pm {a_star_sys:.8f}.\n\\]\n")
        f.write("These numbers should be interpreted as numerical support for percent-level closure, not yet as a parameter-free derivation.\n")


# -----------------------------------------------------------------------------
# 11. Main
# -----------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="SST Robustness Sweep V3")
    parser.add_argument(
        "--mode",
        choices=["ideal", "torus"],
        default="ideal",
        help="Select 'ideal' for Gilbert database or 'torus' for analytical R_t/r_t scan.",
    )
    args = parser.parse_args()

    initialize_project_sources()

    print("=" * 78)
    print(f"SST ROBUSTNESS SWEEP V3 (PROJECT-INTEGRATED) - MODE: {args.mode.upper()}")
    print("=" * 78)
    print(f"Output directory : {OUTPUT_DIR}")
    print(f"Ideal source     : {IDEAL_META['source']}")
    print(f"Local sst_core   : {'yes' if SST_CORE_SCAN_AVAILABLE else 'no'}")
    print(f"Gamma_0_input    : {Gamma_0_input:.8e} m^2/s")
    print(f"v_swirl          : {v_swirl:.8e} m/s")
    print(f"r_c_canon        : {r_c_canon:.8e} m")
    print(f"A_req            : 1/(4*pi) = {A_req:.8f}")
    print(f"Branch mode      : {BRANCH_MODE}")
    print(f"Preferred fit    : {PREFERRED_FIT_METHOD}")
    if _TORCH_AVAILABLE and ENABLE_TORCH_ACCEL:
        try:
            dev = _pick_torch_device()
            print(f"Torch device     : {dev}")
        except Exception:
            print("Torch device     : unavailable (fallback to NumPy)")
    else:
        print("Torch device     : disabled / unavailable")
    print()

    rows: List[dict] = []

    # Determine sweep geometry configurations based on mode
    if args.mode == "torus":
        # Sweep R_t / r_t in a modest range around 2 (a standard trefoil torus ratio)
        R_ratio_grid = np.linspace(2.0, 2.6, 7)
        geom_configs = [
            (N_geom, N_int_target, R_ratio)
            for N_geom in N_GEOM_LIST
            for N_int_target in N_INT_LIST
            for R_ratio in R_ratio_grid
        ]
    else:
        geom_configs = [
            (N_geom, N_int_target, None)
            for N_geom in N_GEOM_LIST
            for N_int_target in N_INT_LIST
        ]

    for N_geom, N_int_target, R_ratio in geom_configs:
        print("-" * 78)
        if args.mode == "torus":
            assert R_ratio is not None
            print(
                f"Building Torus geometry for N_geom={N_geom}, "
                f"N_int={N_int_target}, R_t/r_t={R_ratio:.2f}"
            )
            geom = build_torus_geometry(N_geom, N_int_target, R_ratio, 1.0)
        else:
            print(f"Building geometry for N_geom={N_geom}, N_int_target={N_int_target}")
            geom = build_geometry(N_geom, N_int_target)
            print(f"  L_dimless_full = {geom.L_dimless_full:.6f}   (Gilbert ref: {IDEAL_L_REF:.6f})")
            print(f"  d_min_full     = {geom.d_min_full:.6f}   (Gilbert D: {IDEAL_D_REF:.6f})")
            print(f"  N_int_actual   = {geom.N_int_actual}")
            print(f"  d_min_int      = {geom.d_min_int:.6f}")

            if _SST_CORE_AVAILABLE:
                try:
                    L_cpp = float(sst_core.calculate_length(np.asarray(geom.pts_full, dtype=np.float64)))
                    Wr_cpp = float(sst_core.calculate_writhe(np.asarray(geom.pts_int, dtype=np.float64), r_c_canon))
                    print(f"  sst_core L     = {L_cpp:.6f}   (diagnostic)")
                    print(f"  sst_core Wr    = {Wr_cpp:.6f}   (diagnostic)")
                except Exception as exc:
                    print(f"  [warn] sst_core diagnostics failed: {exc}")

            if SAVE_PER_RUN_DIAGNOSTICS:
                save_geometry_plot(geom, os.path.join(OUTPUT_DIR, f"geom_Ng{N_geom}_Ni{geom.N_int_actual}.png"))

            print("  Scanning Biot-Savart energy...")
            a_scan, E_vals = scan_BS_energy(geom)
            fit_results, diagnostics = extract_fits(a_scan, E_vals, geom.L_dimless_full, geom.d_min_full)

            if SAVE_PER_RUN_DIAGNOSTICS:
                save_bs_diagnostics(
                    a_scan, E_vals, fit_results, diagnostics,
                    os.path.join(OUTPUT_DIR, f"bs_diagnostics_Ng{N_geom}_Ni{geom.N_int_actual}.png")
                )

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
                        "a_fit_ref_dimless": np.nan,
                        "a_nc_m": np.nan,
                        "a_nc_over_rc": np.nan,
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
                        "uses_local_sst_core": _SST_CORE_AVAILABLE,
                        "ideal_source": (
                            IDEAL_SOURCE_DESC
                            if args.mode == "ideal"
                            else f"Torus R_t/r_t={R_ratio:.2f}"
                        ),
                        "notes": "A_K extraction failed for this window",
                    })
                    continue

                a_nc = math.sqrt(fr.A_K / np.pi) * Gamma_0_input / v_swirl
                a_nc_over_rc = a_nc / r_c_canon
                A_ratio = fr.A_K / A_req
                print(f"  Fit {fr.fit_method:>12s}: A_K={fr.A_K:.8f}, A/A_req={A_ratio:.6f}, a_nc/r_c={a_nc_over_rc:.6f}")

                for lam_K in LAMBDA_LIST:
                    for p_exp in P_LIST:
                        candidates = find_root_candidates(fr.A_K, fr.a_K, geom.L_dimless_full, geom.d_min_full, lam_K, p_exp)
                        a_star, is_min, E_star, root_count, min_root_count, root_choice = choose_root(candidates, a_nc, BRANCH_MODE)
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
                            "a_fit_ref_dimless": fr.a_fit_ref,
                            "a_nc_m": a_nc,
                            "a_nc_over_rc": a_nc_over_rc,
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
                            "uses_local_sst_core": _SST_CORE_AVAILABLE,
                            "ideal_source": (
                                IDEAL_SOURCE_DESC
                                if args.mode == "ideal"
                                else f"Torus R_t/r_t={R_ratio:.2f}"
                            ),
                            "notes": "; ".join(notes),
                        })

    # Ensure the output directory exists; if creation fails, fall back to CWD.
    out_dir = OUTPUT_DIR
    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as exc:
        print(f"[warn] Could not create OUTPUT_DIR={out_dir!r}: {exc}. Falling back to current directory.")
        out_dir = os.getcwd()

    csv_path = os.path.join(out_dir, f"robustness_summary_v3_{args.mode}.csv")
    write_csv(rows, csv_path)
    if SAVE_SUMMARY_PLOTS:
        save_summary_plots(rows, out_dir)
    write_best_estimate(rows, out_dir)

    print("\n" + "=" * 78)
    print("Sweep complete")
    print(f"CSV summary        : {csv_path}")
    print(f"Best-estimate CSV  : {os.path.join(out_dir, 'final_best_estimate.csv')}")
    print(f"Best-estimate TXT  : {os.path.join(out_dir, 'final_best_estimate.txt')}")
    print(f"Best-estimate TeX  : {os.path.join(out_dir, 'final_best_estimate.tex')}")
    print(f"Plots              : {out_dir}")
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