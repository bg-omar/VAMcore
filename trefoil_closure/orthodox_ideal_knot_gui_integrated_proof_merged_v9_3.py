#!/usr/bin/env python3
"""
Orthodox ideal-knot filament benchmark GUI with 3D preview
----------------------------------------------------------
Scans local ideal*.txt databases, lists available knots/links, runs a
regularized filament benchmark on the selected entry, and shows a live 3D
preview tab for the selected ideal knot/link.

Orthodox framing:
  - dimensionless logarithmic coefficient A_K
  - A_K / (1/(4*pi))
  - no-contact stationary scale a_nc / r_ref
  - optional regularized stationary scale a* / r_ref

Reference radius is defined generically by
    r_ref = Gamma_ref / (2*pi*U_ref).
"""
from __future__ import annotations

import csv
import importlib.util
import math
import os
import re
import sys
import traceback
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import brentq

try:
    import torch  # type: ignore
    TORCH_AVAILABLE = True
except Exception:
    torch = None  # type: ignore
    TORCH_AVAILABLE = False

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QPlainTextEdit, QCheckBox, QSplitter, QTabWidget, QProgressBar
)

A_REQ = 1.0 / (4.0 * math.pi)
DEFAULT_U_REF = 1.09384563e6
DEFAULT_GAMMA_REF = 9.68361918e-9
DEFAULT_RHO = 7.0e-7
REL_DE_THRESH = 1e-4
PLATEAU_FRACS = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16]
PLATEAU_DIAGNOSTIC_FRACS = list(PLATEAU_FRACS)
A_SCAN_COUNT = 24
BS_BLOCK = 512
DEFAULT_PREVIEW_POINTS = 900
QUIVER_COUNT = 48
POINT_PRESETS = [500, 1000, 2000, 4000, 8000, 16000, 32000, 64000]
WARNING_PRESETS = {32000, 64000}

SCRIPT_VERSION = "orthodox-v10-merge-patch"
PREFERRED_FIT_METHOD = "plateau_0.12"
CLOSURE_CANDIDATE_FIT_METHODS = ["plateau_0.04", "plateau_0.06", "plateau_0.08", "plateau_0.10", "plateau_0.12"]
EXTRAP_MIN_NINT_DEFAULT = 8000
SWEEP_LAYOUT_ALLOWED = ("exact_pairs_only", "matrix")

BS_BACKEND_ALLOWED = ("auto", "local_cpp_scan", "torch", "numpy")
ROOT_SELECTION_ALLOWED = ("continuation", "closest_to_a_nc", "lowest_energy", "targeted_x_nc")
REGULARIZER_ALLOWED = ("legacy", "shift_free_barrier")

ROOT_XTOL = 1e-14
ROOT_RTOL = 1e-13
ROOT_FTOL = 1e-12
ROOT_SCAN_COUNT_X = 4096
ROOT_TARGET_BRACKET_FRAC = 2.0e-3
ROOT_TARGET_MAX_EXPANSIONS = 32
TARGET_XNC_ABS_TOL = 5e-3
TARGET_XNC_REL_TOL = 5e-3

LOCAL_CPP_SCAN_AVAILABLE = False
SST_CORE_SCAN = None


class RunCancelled(Exception):
    pass


def check_cancel(cancel_cb: Optional[Callable[[], bool]]) -> None:
    if cancel_cb is not None and cancel_cb():
        raise RunCancelled("Run cancelled by user")


@dataclass
class ComponentSeries:
    coeffs: List[Tuple[int, np.ndarray, np.ndarray]]  # (k, A3, B3)


@dataclass
class IdealEntry:
    source_file: Path
    knot_id: str
    conway: str
    L_ref: float
    D_ref: float
    n_components: int
    components: List[ComponentSeries]


@dataclass
class GeometryData:
    total_points_full: int
    total_points_int: int
    n_components: int
    points_full: np.ndarray
    tangents_full: np.ndarray
    ds_full: np.ndarray
    comp_full: np.ndarray
    local_full: np.ndarray
    ncomp_full: np.ndarray
    L_dimless_full: float
    d_min_full: float
    points_int: np.ndarray
    tangents_int: np.ndarray
    ds_int: np.ndarray
    comp_int: np.ndarray
    local_int: np.ndarray
    ncomp_int: np.ndarray
    d_min_int: float


@dataclass
class FitResult:
    method: str
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
    root_space_value: float


@dataclass
class SweepResult:
    N_geom: int
    N_int: int
    backend: str
    fits: List[FitResult]
    plateau_diag: Dict[str, Dict[str, float]]



def log_prefix(msg: str) -> str:
    return msg if msg.startswith("[") else f"[LOG] {msg}"


def natural_knot_id_key(knot_id: str) -> tuple:
    parts = [p.strip() for p in knot_id.split(":") if p.strip()]
    out = []
    for p in parts:
        if re.fullmatch(r"\d+", p):
            out.append((0, int(p)))
        else:
            out.append((1, p.lower()))
    return tuple(out)


def family_tags(entry: IdealEntry) -> List[str]:
    tags: List[str] = []

    TORUS_IDS = {
        "3:1:1",
        "5:1:1",
        "7:1:1",
        "9:1:1",
        "11:1:1",
    }

    TWIST_IDS = {
        "6:1:1",
        "7:1:2",
        "8:1:1",
        "9:1:2",
        "10:1:1",
        "11:1:2",
    }

    kid = entry.knot_id.strip()

    if kid in TORUS_IDS:
        tags.append("torus")

    if kid in TWIST_IDS:
        tags.append("twist")

    return tags


def family_filter_match(entry: IdealEntry, mode: str) -> bool:
    tags = family_tags(entry)
    if mode == "Torus preset":
        return "torus" in tags
    if mode == "Twist preset":
        return "twist" in tags
    if mode == "Unmarked only":
        return len(tags) == 0
    return True


def format_entry_label(entry: IdealEntry) -> str:
    tags = family_tags(entry)
    tag_text = f" [{' / '.join(tags)}]" if tags else ""
    return f"{entry.knot_id}{tag_text} | Conway {entry.conway or '-'} | L={entry.L_ref:.6f} | n={entry.n_components}"


def find_ideal_files(search_roots: List[Path]) -> List[Path]:
    found: List[Path] = []
    seen = set()
    for root in search_roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("ideal*.txt")):
            key = str(path.resolve())
            if key not in seen:
                seen.add(key)
                found.append(path)
    return found


_AB_RE = re.compile(r'<AB\s+([^>]*)>(.*?)</AB>', re.S)
_ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
_COMP_RE = re.compile(r'<Component\s+([^>]*)>(.*?)</Component>', re.S)
_COEFF_RE = re.compile(r'<Coeff\s+([^>]*)/?>', re.S)


def _parse_attrs(attr_text: str) -> Dict[str, str]:
    return {m.group(1): m.group(2).strip() for m in _ATTR_RE.finditer(attr_text)}


def _parse_vec(text: str) -> np.ndarray:
    parts = [p.strip() for p in text.split(',')]
    vals = [float(p) for p in parts]
    if len(vals) != 3:
        raise ValueError(f"Expected 3-vector, got: {text}")
    return np.array(vals, dtype=float)


def parse_ideal_file(path: Path) -> List[IdealEntry]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries: List[IdealEntry] = []
    for ab_match in _AB_RE.finditer(text):
        ab_attrs = _parse_attrs(ab_match.group(1))
        body = ab_match.group(2)
        knot_id = ab_attrs.get("Id", "")
        conway = ab_attrs.get("Conway", "")
        L_ref = float(ab_attrs.get("L", "nan"))
        D_ref = float(ab_attrs.get("D", "nan"))
        comp_matches = list(_COMP_RE.finditer(body))
        components: List[ComponentSeries] = []
        if comp_matches:
            for cm in comp_matches:
                comp_body = cm.group(2)
                coeffs: List[Tuple[int, np.ndarray, np.ndarray]] = []
                for cf in _COEFF_RE.finditer(comp_body):
                    attrs = _parse_attrs(cf.group(1))
                    k = int(attrs.get("I", "0"))
                    A = _parse_vec(attrs.get("A", "0,0,0"))
                    B = _parse_vec(attrs.get("B", "0,0,0"))
                    coeffs.append((k, A, B))
                coeffs.sort(key=lambda x: x[0])
                components.append(ComponentSeries(coeffs))
        else:
            coeffs = []
            for cf in _COEFF_RE.finditer(body):
                attrs = _parse_attrs(cf.group(1))
                k = int(attrs.get("I", "0"))
                A = _parse_vec(attrs.get("A", "0,0,0"))
                B = _parse_vec(attrs.get("B", "0,0,0"))
                coeffs.append((k, A, B))
            coeffs.sort(key=lambda x: x[0])
            components.append(ComponentSeries(coeffs))
        entries.append(IdealEntry(
            source_file=path,
            knot_id=knot_id,
            conway=conway,
            L_ref=L_ref,
            D_ref=D_ref,
            n_components=len(components),
            components=components,
        ))
    entries.sort(key=lambda e: natural_knot_id_key(e.knot_id))
    return entries


def eval_component_series(t_arr: np.ndarray, comp: ComponentSeries) -> Tuple[np.ndarray, np.ndarray]:
    X = np.zeros((len(t_arr), 3), dtype=float)
    dX = np.zeros((len(t_arr), 3), dtype=float)
    for k, A, B in comp.coeffs:
        if k == 0:
            X += A[None, :]
            continue
        phase = 2.0 * np.pi * k * t_arr
        c = np.cos(phase)[:, None]
        s = np.sin(phase)[:, None]
        X += c * A[None, :] + s * B[None, :]
        w = 2.0 * np.pi * k
        dX += w * (-s * A[None, :] + c * B[None, :])
    return X, dX


def eval_component_series_second_deriv(t_arr: np.ndarray, comp: ComponentSeries) -> np.ndarray:
    ddX = np.zeros((len(t_arr), 3), dtype=float)
    for k, A, B in comp.coeffs:
        if k == 0:
            continue
        phase = 2.0 * np.pi * k * t_arr
        c = np.cos(phase)[:, None]
        s = np.sin(phase)[:, None]
        w2 = (2.0 * np.pi * k) ** 2
        ddX += -w2 * (c * A[None, :] + s * B[None, :])
    return ddX


def circular_index_distance(ii: np.ndarray, jj: np.ndarray, n: int) -> np.ndarray:
    d = np.abs(ii[:, None] - jj[None, :])
    return np.minimum(d, n - d)


def coarse_min_self_distance(points: np.ndarray, comp_ids: np.ndarray, local_idx: np.ndarray, n_per_comp: np.ndarray, excl_same_comp: int, cancel_cb: Optional[Callable[[], bool]] = None, progress_cb: Optional[Callable[[float], None]] = None) -> float:
    n = len(points)
    d_min = np.inf
    outer_steps = max(1, math.ceil(n / BS_BLOCK))
    outer_idx = 0
    for i0 in range(0, n, BS_BLOCK):
        check_cancel(cancel_cb)
        check_cancel(cancel_cb)
        check_cancel(cancel_cb)
        i1 = min(i0 + BS_BLOCK, n)
        Pi = points[i0:i1]
        ci = comp_ids[i0:i1]
        li = local_idx[i0:i1]
        for j0 in range(i0, n, BS_BLOCK):
            check_cancel(cancel_cb)
            j1 = min(j0 + BS_BLOCK, n)
            Pj = points[j0:j1]
            cj = comp_ids[j0:j1]
            lj = local_idx[j0:j1]
            diff = Pi[:, None, :] - Pj[None, :, :]
            dist = np.linalg.norm(diff, axis=2)
            same_comp = ci[:, None] == cj[None, :]
            idx_mask = np.ones_like(dist, dtype=bool)
            if np.any(same_comp):
                for ii in range(i1 - i0):
                    for jj in range(j1 - j0):
                        if same_comp[ii, jj]:
                            nloc = int(n_per_comp[i0 + ii])
                            dd = abs(int(li[ii]) - int(lj[jj]))
                            dd = min(dd, nloc - dd)
                            if dd <= excl_same_comp:
                                idx_mask[ii, jj] = False
            if j0 == i0:
                idx_mask &= np.triu(np.ones_like(idx_mask, dtype=bool), k=1)
            if np.any(idx_mask):
                local = np.min(dist[idx_mask])
                if local < d_min:
                    d_min = local
        outer_idx += 1
        if progress_cb is not None:
            progress_cb(min(1.0, outer_idx / outer_steps))
    return float(d_min)


def build_geometry(entry: IdealEntry, points_per_component: int, int_points_per_component: int, cancel_cb: Optional[Callable[[], bool]] = None, progress_cb: Optional[Callable[[float, str], None]] = None) -> GeometryData:
    pts_full_list = []
    tan_full_list = []
    ds_full_list = []
    comp_full_list = []
    local_full_list = []
    ncomp_full_list = []

    pts_int_list = []
    tan_int_list = []
    ds_int_list = []
    comp_int_list = []
    local_int_list = []
    ncomp_int_list = []

    for comp_idx, comp in enumerate(entry.components):
        check_cancel(cancel_cb)
        t = np.linspace(0.0, 1.0, points_per_component, endpoint=False)
        X, dX = eval_component_series(t, comp)
        speed = np.linalg.norm(dX, axis=1)
        ds = speed * (1.0 / points_per_component)
        tan = dX / np.maximum(speed[:, None], 1e-300)

        pts_full_list.append(X)
        tan_full_list.append(tan)
        ds_full_list.append(ds)
        comp_full_list.append(np.full(points_per_component, comp_idx, dtype=int))
        local_full_list.append(np.arange(points_per_component, dtype=int))
        ncomp_full_list.append(np.full(points_per_component, points_per_component, dtype=int))

        stride = max(1, int(math.ceil(points_per_component / int_points_per_component))) if int_points_per_component < points_per_component else 1
        X_i = X[::stride]
        tan_i = tan[::stride]
        ds_i = ds[::stride] * stride
        ds_i[-1] += float(np.sum(ds) - np.sum(ds_i))
        n_i = len(X_i)
        pts_int_list.append(X_i)
        tan_int_list.append(tan_i)
        ds_int_list.append(ds_i)
        comp_int_list.append(np.full(n_i, comp_idx, dtype=int))
        local_int_list.append(np.arange(0, points_per_component, stride, dtype=int)[:n_i])
        ncomp_int_list.append(np.full(n_i, points_per_component, dtype=int))

    points_full = np.vstack(pts_full_list)
    tangents_full = np.vstack(tan_full_list)
    ds_full = np.concatenate(ds_full_list)
    comp_full = np.concatenate(comp_full_list)
    local_full = np.concatenate(local_full_list)
    ncomp_full = np.concatenate(ncomp_full_list)

    points_int = np.vstack(pts_int_list)
    tangents_int = np.vstack(tan_int_list)
    ds_int = np.concatenate(ds_int_list)
    comp_int = np.concatenate(comp_int_list)
    local_int = np.concatenate(local_int_list)
    ncomp_int = np.concatenate(ncomp_int_list)

    L_dimless_full = float(np.sum(ds_full))
    d_min_full = coarse_min_self_distance(
        points_full, comp_full, local_full, ncomp_full, max(5, points_per_component // 15),
        cancel_cb=cancel_cb,
        progress_cb=(lambda f: progress_cb(0.25 * f, "geometry: d_min(full)")) if progress_cb is not None else None,
    )
    d_min_int = coarse_min_self_distance(
        points_int, comp_int, local_int, ncomp_int, max(5, points_per_component // 15),
        cancel_cb=cancel_cb,
        progress_cb=(lambda f: progress_cb(0.25 + 0.25 * f, "geometry: d_min(int)")) if progress_cb is not None else None,
    )

    return GeometryData(
        total_points_full=len(points_full),
        total_points_int=len(points_int),
        n_components=entry.n_components,
        points_full=points_full,
        tangents_full=tangents_full,
        ds_full=ds_full,
        comp_full=comp_full,
        local_full=local_full,
        ncomp_full=ncomp_full,
        L_dimless_full=L_dimless_full,
        d_min_full=d_min_full,
        points_int=points_int,
        tangents_int=tangents_int,
        ds_int=ds_int,
        comp_int=comp_int,
        local_int=local_int,
        ncomp_int=ncomp_int,
        d_min_int=d_min_int,
    )


def build_preview_data(entry: IdealEntry, points_per_component: int, cancel_cb: Optional[Callable[[], bool]] = None) -> List[Dict[str, np.ndarray]]:
    previews: List[Dict[str, np.ndarray]] = []
    for comp_idx, comp in enumerate(entry.components):
        check_cancel(cancel_cb)
        t = np.linspace(0.0, 1.0, points_per_component, endpoint=False)
        X, dX = eval_component_series(t, comp)
        ddX = eval_component_series_second_deriv(t, comp)
        speed = np.linalg.norm(dX, axis=1)
        tangents = dX / np.maximum(speed[:, None], 1e-300)
        cross = np.cross(dX, ddX)
        curvature = np.linalg.norm(cross, axis=1) / np.maximum(speed, 1e-300) ** 3
        previews.append({
            "component": np.full(points_per_component, comp_idx, dtype=int),
            "X": X,
            "dX": dX,
            "ddX": ddX,
            "tangents": tangents,
            "curvature": curvature,
        })
    return previews


def _pick_torch_device() -> "torch.device":  # type: ignore[name-defined]
    assert TORCH_AVAILABLE and torch is not None
    if hasattr(torch, "xpu") and getattr(torch, "xpu").is_available():
        return torch.device("xpu")
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _bs_energy_numpy(a_dimless: float, geom: GeometryData, cancel_cb: Optional[Callable[[], bool]] = None) -> float:
    delta = float(a_dimless)
    pts = geom.points_int
    tans = geom.tangents_int
    ds = geom.ds_int
    comp = geom.comp_int
    loc = geom.local_int
    ncomp = geom.ncomp_int
    n = len(pts)
    total = 0.0
    outer_steps = max(1, math.ceil(n / BS_BLOCK))
    outer_idx = 0
    for i0 in range(0, n, BS_BLOCK):
        check_cancel(cancel_cb)
        check_cancel(cancel_cb)
        i1 = min(i0 + BS_BLOCK, n)
        Pi = pts[i0:i1]
        Ti = tans[i0:i1]
        dsi = ds[i0:i1]
        ci = comp[i0:i1]
        li = loc[i0:i1]
        ni = ncomp[i0:i1]
        row_sum = np.zeros(i1 - i0, dtype=float)
        for j0 in range(0, n, BS_BLOCK):
            check_cancel(cancel_cb)
            j1 = min(j0 + BS_BLOCK, n)
            Pj = pts[j0:j1]
            Tj = tans[j0:j1]
            dsj = ds[j0:j1]
            cj = comp[j0:j1]
            lj = loc[j0:j1]
            diff = Pj[None, :, :] - Pi[:, None, :]
            dist = np.linalg.norm(diff, axis=2)
            dot_tt = Ti @ Tj.T
            mask = (dist > delta)
            for ii in range(i1 - i0):
                for jj in range(j1 - j0):
                    if ci[ii] == cj[jj]:
                        nloc = int(ni[ii])
                        dd = abs(int(li[ii]) - int(lj[jj]))
                        dd = min(dd, nloc - dd)
                        if dd == 0:
                            mask[ii, jj] = False
            contrib = np.where(mask, dot_tt / np.maximum(dist, 1e-300), 0.0)
            row_sum += contrib @ dsj
        total += np.sum(row_sum * dsi)
    return float(total / (8.0 * math.pi))


def _bs_energy_torch(a_dimless: float, geom: GeometryData, device: "torch.device", cancel_cb: Optional[Callable[[], bool]] = None) -> float:  # type: ignore[name-defined]
    assert torch is not None
    dtype = torch.float32 if device.type in ["xpu", "mps"] else torch.float64
    pts = torch.tensor(geom.points_int, dtype=dtype, device=device)
    tans = torch.tensor(geom.tangents_int, dtype=dtype, device=device)
    ds = torch.tensor(geom.ds_int, dtype=dtype, device=device)
    comp = torch.tensor(geom.comp_int, dtype=torch.int64, device=device)
    loc = torch.tensor(geom.local_int, dtype=torch.int64, device=device)
    ncomp = torch.tensor(geom.ncomp_int, dtype=torch.int64, device=device)
    n = pts.shape[0]
    total = 0.0
    outer_steps = max(1, math.ceil(n / BS_BLOCK))
    outer_idx = 0
    for i0 in range(0, n, BS_BLOCK):
        check_cancel(cancel_cb)
        i1 = min(i0 + BS_BLOCK, n)
        Pi = pts[i0:i1]
        Ti = tans[i0:i1]
        dsi = ds[i0:i1]
        ci = comp[i0:i1].unsqueeze(1)
        li = loc[i0:i1].unsqueeze(1)
        ni = ncomp[i0:i1].unsqueeze(1)
        for j0 in range(0, n, BS_BLOCK):
            check_cancel(cancel_cb)
            j1 = min(j0 + BS_BLOCK, n)
            Pj = pts[j0:j1]
            Tj = tans[j0:j1]
            dsj = ds[j0:j1]
            cj = comp[j0:j1].unsqueeze(0)
            lj = loc[j0:j1].unsqueeze(0)
            diff = Pj.unsqueeze(0) - Pi.unsqueeze(1)
            dist = torch.norm(diff, dim=2)
            dot_tt = torch.sum(Ti.unsqueeze(1) * Tj.unsqueeze(0), dim=2)
            same_comp = ci == cj
            dd = torch.abs(li - lj)
            cyc = torch.minimum(dd, ni - dd)
            mask = (dist > a_dimless) & (~(same_comp & (cyc == 0)))
            contrib = torch.where(mask, dot_tt / torch.clamp(dist, min=1e-30), torch.zeros_like(dist))
            block_sum = torch.sum(contrib * dsj.unsqueeze(0) * dsi.unsqueeze(1))
            total += float(block_sum.item())
    return total / (8.0 * math.pi)




def _try_load_local_cpp_scan() -> bool:
    global LOCAL_CPP_SCAN_AVAILABLE, SST_CORE_SCAN
    if LOCAL_CPP_SCAN_AVAILABLE:
        return True
    candidates = [
        Path(__file__).resolve().with_name("sst_core.py"),
        Path(__file__).resolve().with_name("sst_core.pyd"),
        Path(__file__).resolve().with_name("sst_core.so"),
    ]
    for candidate in candidates:
        try:
            if not candidate.exists():
                continue
            if candidate.suffix == ".py":
                spec = importlib.util.spec_from_file_location("sst_core", str(candidate))
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                import importlib
                module = importlib.import_module("sst_core")
            scan_fn = getattr(module, "scan_bs_energy", None)
            if callable(scan_fn):
                SST_CORE_SCAN = scan_fn
                LOCAL_CPP_SCAN_AVAILABLE = True
                return True
        except Exception:
            continue
    return False


def detect_bs_backend(mode: str, enable_torch: bool) -> str:
    if mode == "local_cpp_scan":
        if _try_load_local_cpp_scan():
            return "local_cpp_scan"
        return "torch" if (enable_torch and TORCH_AVAILABLE) else "numpy"
    if mode == "torch":
        return "torch" if (enable_torch and TORCH_AVAILABLE) else "numpy"
    if mode == "numpy":
        return "numpy"
    if _try_load_local_cpp_scan():
        return "local_cpp_scan"
    if enable_torch and TORCH_AVAILABLE:
        return "torch"
    return "numpy"


def closure_x_from_A(A_K: float) -> float:
    return float(math.sqrt(max(0.0, 4.0 * math.pi * A_K)))


def a_nc_from_A(A_K: float, r_ref: float) -> float:
    return float(closure_x_from_A(A_K) * r_ref)


def _plateau_stats_for_frac(
    a_mid: np.ndarray,
    A_local: np.ndarray,
    rel_dE: np.ndarray,
    d_min_dimless: float,
    frac: float,
) -> Dict[str, float]:
    mask = (A_local > 0.0) & (rel_dE > REL_DE_THRESH) & (a_mid < frac * d_min_dimless)
    idxs = np.where(mask)[0]
    if idxs.size == 0:
        return {
            "n_plateau": 0,
            "a_lo": np.nan,
            "a_hi": np.nan,
            "A_median": np.nan,
            "A_spread": np.nan,
            "a_ref": np.nan,
            "idx_ref": -1,
        }
    idx_ref = int(idxs[len(idxs) // 2])
    return {
        "n_plateau": int(idxs.size),
        "a_lo": float(a_mid[idxs[0]]),
        "a_hi": float(a_mid[idxs[-1]]),
        "A_median": float(np.median(A_local[idxs])),
        "A_spread": float(np.std(A_local[idxs])),
        "a_ref": float(a_mid[idx_ref]),
        "idx_ref": idx_ref,
    }


def _scan_local_cpp(a_scan: np.ndarray, geom: GeometryData) -> Optional[np.ndarray]:
    if not _try_load_local_cpp_scan() or SST_CORE_SCAN is None:
        return None
    try:
        out = SST_CORE_SCAN(
            np.asarray(a_scan, dtype=float),
            np.asarray(geom.points_int, dtype=float),
            np.asarray(geom.tangents_int, dtype=float),
            np.asarray(geom.ds_int, dtype=float),
        )
        arr = np.asarray(out, dtype=float)
        if arr.shape == a_scan.shape and np.all(np.isfinite(arr)):
            return arr
    except Exception:
        return None
    return None



def compute_bs_energy(a_dimless: float, geom: GeometryData, backend: str,
                      cancel_cb: Optional[Callable[[], bool]] = None) -> float:
    if backend == "torch" and TORCH_AVAILABLE:
        try:
            dev = _pick_torch_device()
            return _bs_energy_torch(a_dimless, geom, dev, cancel_cb=cancel_cb)
        except RunCancelled:
            raise
        except Exception:
            return _bs_energy_numpy(a_dimless, geom, cancel_cb=cancel_cb)
    return _bs_energy_numpy(a_dimless, geom, cancel_cb=cancel_cb)


def scan_bs_energy(geom: GeometryData, backend_mode: str, enable_torch: bool,
                   cancel_cb: Optional[Callable[[], bool]] = None,
                   progress_cb: Optional[Callable[[float, str], None]] = None) -> Tuple[np.ndarray, np.ndarray, str]:
    ds_med = float(np.median(geom.ds_int))
    a_lo = max(3.0 * ds_med, geom.d_min_int * 5e-4)
    a_hi = geom.d_min_int * 0.35
    a_scan = np.logspace(np.log10(a_lo), np.log10(a_hi), A_SCAN_COUNT)
    backend_used = detect_bs_backend(backend_mode, enable_torch)
    if backend_used == "local_cpp_scan":
        E_cpp = _scan_local_cpp(a_scan, geom)
        if E_cpp is not None:
            return a_scan, E_cpp, "local_cpp_scan"
        backend_used = "torch" if (enable_torch and TORCH_AVAILABLE) else "numpy"
    E_vals = np.array([compute_bs_energy(a, geom, backend_used, cancel_cb=cancel_cb) for a in a_scan], dtype=float)
    return a_scan, E_vals, backend_used


def extract_fits(a_scan: np.ndarray, E_vals: np.ndarray, L_dimless: float, d_min_dimless: float
                 ) -> Tuple[List[FitResult], Dict[str, Dict[str, float]]]:
    x_scan = -np.log(a_scan)
    y_scan = E_vals / L_dimless
    a_mid = np.sqrt(a_scan[:-1] * a_scan[1:])
    A_local = np.diff(y_scan) / np.diff(x_scan)
    rel_dE = np.abs(np.diff(E_vals)) / np.maximum(np.abs(E_vals[:-1]), 1e-300)
    out: List[FitResult] = []
    coeffs = np.polyfit(x_scan, y_scan, 1)
    A_glob = float(coeffs[0])
    b_glob = float(coeffs[1])
    a_K_glob = b_glob - A_glob * np.log(L_dimless)
    out.append(FitResult("global", None, A_glob, np.nan, a_K_glob, float(a_scan[len(a_scan)//2]), 0))

    plateau_diag: Dict[str, Dict[str, float]] = {}
    for frac in PLATEAU_FRACS:
        method = f"plateau_{frac:.2f}"
        stats = _plateau_stats_for_frac(a_mid, A_local, rel_dE, d_min_dimless, frac)
        plateau_diag[method] = stats
        if stats["n_plateau"] > 0:
            idx_ref = int(stats["idx_ref"])
            y_ref = float(0.5 * (y_scan[idx_ref] + y_scan[idx_ref + 1]))
            a_ref = float(stats["a_ref"])
            A = float(stats["A_median"])
            a_K = y_ref - A * np.log(L_dimless / a_ref)
            out.append(FitResult(method, float(frac), A, float(stats["A_spread"]), float(a_K), a_ref, int(stats["n_plateau"])))
        else:
            out.append(FitResult(method, float(frac), np.nan, np.nan, np.nan, np.nan, 0))
    return out, plateau_diag



def dE_da(a: float, A_K: float, L_phys: float, d_min_phys: float, rho: float, Gamma_ref: float,
          U_ref: float, lam: float, p_exp: int, regularizer: str = "legacy") -> float:
    if a <= 0.0 or 2.0 * a >= d_min_phys:
        return np.nan
    dE_bs = -rho * Gamma_ref**2 * L_phys * A_K / a
    dE_core = math.pi * rho * U_ref**2 * a * L_phys
    if lam == 0.0:
        dE_cont = 0.0
    else:
        xc = 2.0 * a / (d_min_phys - 2.0 * a)
        if regularizer == "shift_free_barrier":
            if xc <= 1.0:
                dE_cont = 0.0
            else:
                dE_cont = lam * rho * Gamma_ref**2 * L_phys * p_exp * (xc - 1.0) ** (p_exp - 1) * (2.0 * d_min_phys / (d_min_phys - 2.0 * a) ** 2)
        else:
            dx_da = 2.0 * d_min_phys / (d_min_phys - 2.0 * a) ** 2
            dE_cont = lam * rho * Gamma_ref**2 * L_phys * p_exp * xc ** (p_exp - 1) * dx_da
    return dE_bs + dE_core + dE_cont


def E_phys(a: float, A_K: float, a_K: float, L_phys: float, d_min_phys: float, rho: float,
           Gamma_ref: float, U_ref: float, lam: float, p_exp: int, regularizer: str = "legacy") -> float:
    if a <= 0.0 or 2.0 * a >= d_min_phys:
        return np.inf
    E_bs = rho * Gamma_ref**2 * L_phys * (A_K * math.log(L_phys / a) + a_K)
    E_core = 0.5 * math.pi * rho * U_ref**2 * a * a * L_phys
    if lam == 0.0:
        E_cont = 0.0
    else:
        xc = 2.0 * a / (d_min_phys - 2.0 * a)
        E_cont = lam * rho * Gamma_ref**2 * L_phys * ((max(xc - 1.0, 0.0) ** p_exp) if regularizer == "shift_free_barrier" else (xc ** p_exp))
    return E_bs + E_core + E_cont


def F_dimensionless(x: float, A_K: float, beta_dimless: float, lam: float, p_exp: int,
                    regularizer: str = "legacy") -> float:
    if x <= 0.0 or x >= 0.98:
        return np.nan
    y = 1.0 - x
    base = -A_K / x + beta_dimless * x
    if lam == 0.0:
        return base
    xc = x / y
    if regularizer == "shift_free_barrier":
        if xc <= 1.0:
            return base
        barrier = lam * p_exp * (xc - 1.0) ** (p_exp - 1) / (y * y)
    else:
        barrier = lam * p_exp * xc ** (p_exp - 1) / (y * y)
    return base + barrier


def stationary_candidates_dimensionless(
    A_K: float,
    a_K: float,
    L_dimless: float,
    d_min_dimless: float,
    rho: float,
    Gamma_ref: float,
    U_ref: float,
    lam: float,
    p_exp: int,
    regularizer: str = "legacy",
) -> List[RootCandidate]:
    r_ref = Gamma_ref / (2.0 * math.pi * U_ref)
    L_phys = L_dimless * (Gamma_ref / U_ref)
    d_min_phys = d_min_dimless * (Gamma_ref / U_ref)
    beta_dimless = 2.0 * math.pi * math.pi * (r_ref ** 2)
    x_vals = np.logspace(-6.0, np.log10(0.98), ROOT_SCAN_COUNT_X)
    F_vals = np.array([F_dimensionless(x, A_K, beta_dimless, lam, p_exp, regularizer) for x in x_vals], dtype=float)
    valid = np.isfinite(F_vals)
    xv = x_vals[valid]
    Fv = F_vals[valid]
    signs = np.sign(Fv)
    changes = np.where((signs[:-1] * signs[1:] < 0) | ((signs[:-1] == 0) & (signs[1:] != 0)) | ((signs[:-1] != 0) & (signs[1:] == 0)))[0]
    roots: List[RootCandidate] = []
    for i in changes:
        try:
            x_root = float(brentq(
                F_dimensionless, float(xv[i]), float(xv[i + 1]),
                args=(A_K, beta_dimless, lam, p_exp, regularizer),
                xtol=ROOT_XTOL, rtol=ROOT_RTOL,
            ))
        except Exception:
            continue
        a_root = x_root * r_ref
        h = max(x_root * 1e-6, 1e-10)
        fp = F_dimensionless(min(0.979999, x_root + h), A_K, beta_dimless, lam, p_exp, regularizer)
        fm = F_dimensionless(max(1e-12, x_root - h), A_K, beta_dimless, lam, p_exp, regularizer)
        d2 = (fp - fm) / (2.0 * h)
        is_min = bool(np.isfinite(d2) and d2 > 0.0)
        roots.append(RootCandidate(
            a_star=a_root,
            is_min=is_min,
            E_star=E_phys(a_root, A_K, a_K, L_phys, d_min_phys, rho, Gamma_ref, U_ref, lam, p_exp, regularizer),
            root_space_value=x_root,
        ))
    return roots


def choose_root_continuation(candidates: List[RootCandidate], prev_a_star: Optional[float], a_nc: float) -> Tuple[float, bool, float, int, int, str]:
    root_count = len(candidates)
    min_root_count = sum(1 for c in candidates if c.is_min)
    if not candidates:
        return np.nan, False, np.nan, 0, 0, "none"
    mins = [c for c in candidates if c.is_min]
    pool = mins if mins else candidates
    target = prev_a_star if (prev_a_star is not None and np.isfinite(prev_a_star)) else a_nc
    chosen = min(pool, key=lambda c: abs(c.a_star - target))
    return chosen.a_star, chosen.is_min, chosen.E_star, root_count, min_root_count, "continuation"


def choose_root(candidates: List[RootCandidate], a_nc: float, branch_mode: str) -> Tuple[float, bool, float, int, int, str]:
    root_count = len(candidates)
    min_root_count = sum(1 for c in candidates if c.is_min)
    if not candidates:
        return np.nan, False, np.nan, 0, 0, "none"
    mins = [c for c in candidates if c.is_min]
    pool = mins if mins else candidates
    chosen = min(pool, key=(lambda c: c.E_star) if branch_mode == "lowest_energy" else (lambda c: abs(c.a_star - a_nc)))
    return chosen.a_star, chosen.is_min, chosen.E_star, root_count, min_root_count, branch_mode


def choose_root_targeted_x_nc(candidates: List[RootCandidate], a_nc: float) -> Tuple[float, bool, float, int, int, str]:
    root_count = len(candidates)
    min_root_count = sum(1 for c in candidates if c.is_min)
    if not candidates:
        return np.nan, False, np.nan, 0, 0, "none"
    mins = [c for c in candidates if c.is_min]
    pool = mins if mins else candidates
    tol = max(TARGET_XNC_ABS_TOL * max(a_nc, 1e-30), TARGET_XNC_REL_TOL * max(a_nc, 1e-30))
    close = [c for c in pool if abs(c.a_star - a_nc) <= tol]
    chosen_pool = close if close else pool
    chosen = min(chosen_pool, key=lambda c: abs(c.a_star - a_nc))
    return chosen.a_star, chosen.is_min, chosen.E_star, root_count, min_root_count, "targeted_x_nc"


def find_stationary_radius(A_K: float, a_K: float, L_dimless: float, d_min_dimless: float, rho: float,
                           Gamma_ref: float, U_ref: float, lam: float, p_exp: int, a_nc: float,
                           regularizer: str = "legacy", root_selection_mode: str = "closest_to_a_nc",
                           prev_a_star: Optional[float] = None) -> Tuple[float, bool, float, int, int, str]:
    candidates = stationary_candidates_dimensionless(
        A_K, a_K, L_dimless, d_min_dimless, rho, Gamma_ref, U_ref, lam, p_exp, regularizer
    )
    if root_selection_mode == "continuation":
        return choose_root_continuation(candidates, prev_a_star, a_nc)
    if root_selection_mode == "targeted_x_nc":
        return choose_root_targeted_x_nc(candidates, a_nc)
    branch = "lowest_energy" if root_selection_mode == "lowest_energy" else "closest_to_a_nc"
    return choose_root(candidates, a_nc, branch)


def parse_exact_pairs(text: str) -> List[Tuple[int, int]]:
    pairs: List[Tuple[int, int]] = []
    if not text.strip():
        return pairs
    for a_str, b_str in re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", text):
        pairs.append((int(a_str), int(b_str)))
    if pairs:
        return pairs
    for token in text.replace(",", " ").split():
        if ":" not in token:
            continue
        left, right = token.split(":", 1)
        if left.strip().isdigit() and right.strip().isdigit():
            pairs.append((int(left.strip()), int(right.strip())))
    return pairs


def _fit_lookup(fits: Sequence[FitResult]) -> Dict[str, FitResult]:
    return {fr.method: fr for fr in fits}


def select_preferred_fit(fits: Sequence[FitResult], preferred_method: str = PREFERRED_FIT_METHOD) -> Optional[FitResult]:
    lookup = _fit_lookup(fits)
    fr = lookup.get(preferred_method)
    if fr is not None and np.isfinite(fr.A_K):
        return fr
    finite = [x for x in fits if np.isfinite(x.A_K)]
    if not finite:
        return None
    return min(finite, key=lambda x: abs(x.A_K - A_REQ))


def _last2_half_range(vals: Sequence[float]) -> float:
    arr = np.asarray([v for v in vals if np.isfinite(v)], dtype=float)
    if arr.size < 2:
        return float("nan")
    return 0.5 * float(np.max(arr[-2:]) - np.min(arr[-2:]))


def _quasi_monotone_tail(vals: Sequence[float], target: float, relax: float = 0.05, abs_eps: float = 1e-6) -> bool:
    arr = np.asarray([v for v in vals if np.isfinite(v)], dtype=float)
    if arr.size < 3:
        return False
    err = np.abs(arr - target)
    for i in range(1, len(err)):
        if err[i] > err[i - 1] + max(abs_eps, relax * err[i - 1]):
            return False
    return True


def summarize_sweep_runs(sweeps: Sequence[SweepResult], preferred_method: str = PREFERRED_FIT_METHOD, extrap_min_nint: int = EXTRAP_MIN_NINT_DEFAULT) -> Dict[str, object]:
    if not sweeps:
        return {}
    rows = []
    for sw in sweeps:
        fr = select_preferred_fit(sw.fits, preferred_method)
        if fr is None:
            continue
        rows.append({
            "N_geom": sw.N_geom,
            "N_int": sw.N_int,
            "backend": sw.backend,
            "method": fr.method,
            "A_K": float(fr.A_K),
            "A_ratio": float(fr.A_K / A_REQ),
            "x_nc": float(closure_x_from_A(fr.A_K)),
            "n_plateau": int(fr.n_plateau),
            "A_spread": float(fr.A_spread) if np.isfinite(fr.A_spread) else np.nan,
            "a_fit_ref": float(fr.a_fit_ref) if np.isfinite(fr.a_fit_ref) else np.nan,
        })
    if not rows:
        return {}
    rows = sorted(rows, key=lambda r: (r["N_geom"], r["N_int"]))
    tail = [r for r in rows if int(r["N_int"]) >= int(extrap_min_nint)]
    A_tail = [float(r["A_K"]) for r in tail]
    x_tail = [float(r["x_nc"]) for r in tail]
    return {
        "rows": rows,
        "preferred_method": preferred_method,
        "extrap_min_nint": int(extrap_min_nint),
        "A_last2_half_range": _last2_half_range(A_tail),
        "x_last2_half_range": _last2_half_range(x_tail),
        "A_tail_quasi_monotone": _quasi_monotone_tail(A_tail, A_REQ),
        "x_tail_quasi_monotone": _quasi_monotone_tail(x_tail, 1.0),
    }


class BenchmarkWorker(QThread):
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, str, str)

    def __init__(self, entry: IdealEntry, points_per_component: int, int_points_per_component: int,
                 U_ref: float, Gamma_ref: float, rho: float, lam: float, p_exp: int,
                 backend_mode: str, allow_torch: bool, root_selection_mode: str, regularizer: str,
                 sweep_enabled: bool = False, sweep_pairs_text: str = "",
                 sweep_layout: str = "exact_pairs_only", preferred_fit_method: str = PREFERRED_FIT_METHOD,
                 extrap_min_nint: int = EXTRAP_MIN_NINT_DEFAULT):
        super().__init__()
        self.entry = entry
        self.points_per_component = points_per_component
        self.int_points_per_component = int_points_per_component
        self.U_ref = U_ref
        self.Gamma_ref = Gamma_ref
        self.rho = rho
        self.lam = lam
        self.p_exp = p_exp
        self.backend_mode = backend_mode
        self.allow_torch = allow_torch
        self.root_selection_mode = root_selection_mode
        self.regularizer = regularizer
        self.sweep_enabled = sweep_enabled
        self.sweep_pairs_text = sweep_pairs_text
        self.sweep_layout = sweep_layout
        self.preferred_fit_method = preferred_fit_method
        self.extrap_min_nint = extrap_min_nint
        self._t0 = 0.0

    def _emit_progress(self, frac: float, phase: str):
        frac = max(0.0, min(1.0, float(frac)))
        elapsed = max(0.0, time.perf_counter() - self._t0)
        eta = float("nan")
        if frac > 1e-3:
            eta = elapsed * (1.0 - frac) / frac
        eta_text = "--" if not np.isfinite(eta) else f"{eta:.1f}s"
        self.progress_signal.emit(int(round(frac * 100.0)), phase, eta_text)

    def _single_run(self, entry: IdealEntry, n_geom: int, n_int: int, r_ref: float) -> dict:
        self.log_signal.emit(log_prefix(f"[META] file={entry.source_file.name} id={entry.knot_id} components={entry.n_components} L_ref={entry.L_ref:.6f}"))
        self.log_signal.emit(log_prefix(f"[META] family_tags={','.join(family_tags(entry)) or '-'}"))
        self.log_signal.emit(log_prefix(f"[META] r_ref = Gamma_ref/(2*pi*U_ref) = {r_ref:.8e} m"))
        geom = build_geometry(
            entry, n_geom, n_int,
            cancel_cb=self.isInterruptionRequested,
            progress_cb=lambda f, phase: self._emit_progress(0.05 + 0.35 * f, phase),
        )
        self.log_signal.emit(log_prefix(f"[GEOM] total_points_full={geom.total_points_full} total_points_int={geom.total_points_int} L_dimless={geom.L_dimless_full:.6f} d_min={geom.d_min_full:.6f}"))
        a_scan, E_vals, backend_used = scan_bs_energy(
            geom, self.backend_mode, self.allow_torch,
            cancel_cb=self.isInterruptionRequested,
            progress_cb=lambda f, phase: self._emit_progress(0.40 + 0.54 * f, phase),
        )
        self._emit_progress(0.96, "fit: extracting A_K")
        fits, plateau_diag = extract_fits(a_scan, E_vals, geom.L_dimless_full, geom.d_min_full)
        result = {
            "entry": entry,
            "geom": geom,
            "a_scan": a_scan,
            "E_vals": E_vals,
            "fits": fits,
            "plateau_diag": plateau_diag,
            "backend_used": backend_used,
            "r_ref": r_ref,
        }
        total_fits = max(1, len(fits))
        prev_a_star = None
        for fit_idx, fr in enumerate(fits, start=1):
            A_K = fr.A_K
            if not np.isfinite(A_K):
                continue
            a_nc = a_nc_from_A(A_K, r_ref)
            a_nc_over_rref = closure_x_from_A(A_K)
            self.log_signal.emit(log_prefix(f"[FIT] method={fr.method} A_K={A_K:.8f} A_ratio={A_K/A_REQ:.6f} a_nc_over_r_ref={a_nc_over_rref:.6f} n_plateau={fr.n_plateau}"))
            a_star, is_min, E_star, root_count, min_root_count, root_choice = find_stationary_radius(
                A_K, fr.a_K, geom.L_dimless_full, geom.d_min_full, self.rho, self.Gamma_ref, self.U_ref,
                self.lam, self.p_exp, a_nc, regularizer=self.regularizer,
                root_selection_mode=self.root_selection_mode, prev_a_star=prev_a_star
            )
            if self.root_selection_mode == "continuation" and np.isfinite(a_star):
                prev_a_star = a_star
            self.log_signal.emit(log_prefix(f"[ROOT] lambda={self.lam:g} method={fr.method} a_star_over_r_ref={a_star/r_ref:.6f} is_min={is_min} root_choice={root_choice} roots={root_count} minima={min_root_count} backend={backend_used}"))
            self._emit_progress(0.96 + 0.04 * (fit_idx / total_fits), f"fit/root: {fit_idx}/{total_fits}")
        return result

    def run(self):
        try:
            self._t0 = time.perf_counter()
            self._emit_progress(0.0, "starting")
            r_ref = self.Gamma_ref / (2.0 * math.pi * self.U_ref)
            result = self._single_run(self.entry, self.points_per_component, self.int_points_per_component, r_ref)
            if self.sweep_enabled:
                pairs = parse_exact_pairs(self.sweep_pairs_text)
                if not pairs:
                    pairs = [(self.points_per_component, self.int_points_per_component)]
                sweep_runs: List[SweepResult] = []
                total = len(pairs)
                for idx, (n_geom, n_int) in enumerate(pairs, start=1):
                    check_cancel(self.isInterruptionRequested)
                    self.log_signal.emit(log_prefix(f"[SWEEP] {idx}/{total} N_geom={n_geom} N_int={n_int}"))
                    sweep_result = self._single_run(self.entry, int(n_geom), int(n_int), r_ref)
                    sweep_runs.append(SweepResult(
                        N_geom=int(n_geom),
                        N_int=int(n_int),
                        backend=str(sweep_result.get("backend_used", "-")),
                        fits=list(sweep_result.get("fits", [])),
                        plateau_diag=dict(sweep_result.get("plateau_diag", {})),
                    ))
                result["sweep_runs"] = sweep_runs
                result["sweep_summary"] = summarize_sweep_runs(
                    sweep_runs,
                    preferred_method=self.preferred_fit_method,
                    extrap_min_nint=self.extrap_min_nint,
                )
            self._emit_progress(1.0, "complete")
            self.done_signal.emit(result)
        except RunCancelled:
            self.log_signal.emit("[META] run cancelled by user")
            self.done_signal.emit({"cancelled": True})
        except Exception as e:
            self.error_signal.emit(f"{e}\n\n{traceback.format_exc()}")


class Preview3DWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Preview mode"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Centerline", "Curvature", "Tangent quivers", "Tube surface"])
        controls.addWidget(self.mode_combo)
        controls.addWidget(QLabel("Preview points / component"))
        self.points_combo = QComboBox()
        for v in POINT_PRESETS:
            self.points_combo.addItem(str(v), v)
        if self.points_combo.findData(DEFAULT_PREVIEW_POINTS) < 0:
            self.points_combo.addItem(str(DEFAULT_PREVIEW_POINTS), DEFAULT_PREVIEW_POINTS)
        self.points_combo.setCurrentIndex(max(0, self.points_combo.findData(DEFAULT_PREVIEW_POINTS)))
        controls.addWidget(self.points_combo)
        self.refresh_btn = QPushButton("Refresh preview")
        controls.addWidget(self.refresh_btn)
        controls.addStretch(1)
        layout.addLayout(controls)

        self.figure = Figure(figsize=(7.2, 6.2), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas, 1)

        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setMaximumHeight(130)
        layout.addWidget(self.info)

        self._entry: Optional[IdealEntry] = None

    def set_entry(self, entry: Optional[IdealEntry]):
        self._entry = entry

    def render(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection="3d")
        entry = self._entry
        if entry is None:
            ax.text(0.5, 0.5, 0.5, "No entry selected", ha="center", va="center")
            self.info.setHtml("<i>No entry selected.</i>")
            self.canvas.draw_idle()
            return

        previews = build_preview_data(entry, int(self.points_combo.currentData()))
        mode = self.mode_combo.currentText()
        total_min = np.inf
        total_max = -np.inf
        kappa_all = []
        for pd in previews:
            X = pd["X"]
            total_min = min(total_min, float(np.min(X)))
            total_max = max(total_max, float(np.max(X)))
            if mode == "Centerline":
                ax.plot(X[:, 0], X[:, 1], X[:, 2], lw=1.6)
            elif mode == "Curvature":
                kappa = pd["curvature"]
                kappa_all.append(kappa)
                sc = ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=kappa, s=8, cmap="viridis")
            elif mode == "Tangent quivers":
                ax.plot(X[:, 0], X[:, 1], X[:, 2], lw=1.2, alpha=0.8)
                idx = np.linspace(0, len(X)-1, min(QUIVER_COUNT, len(X)), dtype=int)
                P = X[idx]
                T = pd["tangents"][idx]
                scale = 0.12 * np.max(np.ptp(X, axis=0))
                ax.quiver(P[:, 0], P[:, 1], P[:, 2], T[:, 0], T[:, 1], T[:, 2], length=scale, normalize=True)
            elif mode == "Tube surface":
                Xr = pd["X"]
                T = pd["tangents"]
                ddX = pd["ddX"]
                nvec = ddX - np.sum(ddX * T, axis=1, keepdims=True) * T
                nn = np.linalg.norm(nvec, axis=1, keepdims=True)
                bad = nn[:, 0] < 1e-12
                if np.any(bad):
                    fallback = np.cross(T[bad], np.array([0.0, 0.0, 1.0]))
                    fb_n = np.linalg.norm(fallback, axis=1, keepdims=True)
                    fallback[fb_n[:, 0] > 0] /= fb_n[fb_n[:, 0] > 0]
                    nvec[bad] = fallback
                    nn = np.linalg.norm(nvec, axis=1, keepdims=True)
                nvec = nvec / np.maximum(nn, 1e-12)
                bvec = np.cross(T, nvec)
                rr = 0.03 * np.max(np.ptp(Xr, axis=0))
                theta = np.linspace(0.0, 2.0 * np.pi, 18)
                Xt = Xr[:, 0, None] + rr * (np.cos(theta)[None, :] * nvec[:, 0, None] + np.sin(theta)[None, :] * bvec[:, 0, None])
                Yt = Xr[:, 1, None] + rr * (np.cos(theta)[None, :] * nvec[:, 1, None] + np.sin(theta)[None, :] * bvec[:, 1, None])
                Zt = Xr[:, 2, None] + rr * (np.cos(theta)[None, :] * nvec[:, 2, None] + np.sin(theta)[None, :] * bvec[:, 2, None])
                ax.plot_surface(Xt, Yt, Zt, rstride=1, cstride=1, linewidth=0, antialiased=False, alpha=0.85)

        if mode == "Curvature" and previews:
            cbar = self.figure.colorbar(sc, ax=ax, fraction=0.03, pad=0.04)
            cbar.set_label("curvature κ")

        all_points = np.vstack([pd["X"] for pd in previews])
        mins = np.min(all_points, axis=0)
        maxs = np.max(all_points, axis=0)
        center = 0.5 * (mins + maxs)
        radius = 0.55 * np.max(maxs - mins)
        ax.set_xlim(center[0] - radius, center[0] + radius)
        ax.set_ylim(center[1] - radius, center[1] + radius)
        ax.set_zlim(center[2] - radius, center[2] + radius)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_title(f"{entry.knot_id} | {mode}")

        if previews:
            L_est = 0.0
            for pd in previews:
                X = pd["X"]
                d = np.roll(X, -1, axis=0) - X
                L_est += float(np.sum(np.linalg.norm(d, axis=1)))
            html = [f"<b>{entry.knot_id}</b> from <b>{entry.source_file.name}</b><br>"]
            html.append(f"Conway: {entry.conway or '-'}<br>")
            html.append(f"Components: {entry.n_components}<br>")
            html.append(f"Database ropelength L/D: {entry.L_ref:.6f}<br>")
            html.append(f"Preview polygonal length (unnormalized): {L_est:.6f}<br>")
            if mode == "Curvature":
                kappa = np.concatenate([pd["curvature"] for pd in previews])
                html.append(f"κ range: [{np.min(kappa):.6g}, {np.max(kappa):.6g}]<br>")
                html.append(f"κ mean: {np.mean(kappa):.6g}<br>")
            elif mode == "Tangent quivers":
                html.append("Arrows show the local tangent direction along each component.<br>")
            elif mode == "Tube surface":
                html.append("Tube surface gives a quick visual cue for near-contacts and local framing.<br>")
            else:
                html.append("Centerline view of the selected ideal knot/link.<br>")
            self.info.setHtml("".join(html))
        self.canvas.draw_idle()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orthodox Ideal-Knot Filament Benchmark + 3D Preview")
        self.resize(1500, 940)
        self.entries_by_file: Dict[str, List[IdealEntry]] = {}
        self.current_worker: Optional[BenchmarkWorker] = None
        self.last_result: Optional[dict] = None
        self._setup_ui()
        self.scan_files()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        splitter = QSplitter(Qt.Horizontal)
        outer.addWidget(splitter)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        form = QGridLayout()
        row = 0

        form.addWidget(QLabel("ideal*.txt file"), row, 0)
        self.file_combo = QComboBox()
        self.file_combo.currentIndexChanged.connect(self.populate_ids)
        form.addWidget(self.file_combo, row, 1)
        self.scan_btn = QPushButton("Rescan")
        self.scan_btn.clicked.connect(self.scan_files)
        form.addWidget(self.scan_btn, row, 2)
        row += 1

        form.addWidget(QLabel("Filter id"), row, 0)
        self.filter_edit = QLineEdit()
        self.filter_edit.textChanged.connect(self.populate_ids)
        form.addWidget(self.filter_edit, row, 1, 1, 2)
        form.addWidget(QLabel("Family filter"), row, 3)
        self.family_combo = QComboBox()
        self.family_combo.addItems(["All entries", "Torus preset", "Twist preset", "Unmarked only"])
        self.family_combo.currentIndexChanged.connect(self.populate_ids)
        form.addWidget(self.family_combo, row, 4)
        row += 1

        form.addWidget(QLabel("Knot / link id"), row, 0)
        self.id_combo = QComboBox()
        self.id_combo.currentIndexChanged.connect(self.show_entry_info)
        form.addWidget(self.id_combo, row, 1, 1, 2)
        row += 1

        form.addWidget(QLabel("Points / component"), row, 0)
        self.n_geom_combo = QComboBox()
        for v in POINT_PRESETS:
            self.n_geom_combo.addItem(str(v), v)
        self.n_geom_combo.setCurrentIndex(max(0, self.n_geom_combo.findData(4000)))
        self.n_geom_combo.currentIndexChanged.connect(self.update_point_warnings)
        form.addWidget(self.n_geom_combo, row, 1)
        form.addWidget(QLabel("Integration points / component"), row, 2)
        self.n_int_combo = QComboBox()
        for v in POINT_PRESETS:
            self.n_int_combo.addItem(str(v), v)
        self.n_int_combo.setCurrentIndex(max(0, self.n_int_combo.findData(4000)))
        self.n_int_combo.currentIndexChanged.connect(self.update_point_warnings)
        form.addWidget(self.n_int_combo, row, 3)
        row += 1

        self.geom_warn = QLabel("")
        self.geom_warn.setStyleSheet("color: #c97a00;")
        form.addWidget(self.geom_warn, row, 0, 1, 2)
        self.int_warn = QLabel("")
        self.int_warn.setStyleSheet("color: #c97a00;")
        form.addWidget(self.int_warn, row, 2, 1, 2)
        row += 1

        form.addWidget(QLabel("U_ref [m/s]"), row, 0)
        self.u_spin = QDoubleSpinBox(); self.u_spin.setRange(1e-6, 1e12); self.u_spin.setDecimals(6); self.u_spin.setValue(DEFAULT_U_REF)
        form.addWidget(self.u_spin, row, 1)
        form.addWidget(QLabel("Gamma_ref [m^2/s]"), row, 2)
        self.gamma_spin = QDoubleSpinBox(); self.gamma_spin.setRange(1e-18, 1e6); self.gamma_spin.setDecimals(12); self.gamma_spin.setValue(DEFAULT_GAMMA_REF)
        form.addWidget(self.gamma_spin, row, 3)
        row += 1

        form.addWidget(QLabel("rho [kg/m^3]"), row, 0)
        self.rho_spin = QDoubleSpinBox(); self.rho_spin.setRange(0.0, 1e20); self.rho_spin.setDecimals(9); self.rho_spin.setValue(DEFAULT_RHO)
        form.addWidget(self.rho_spin, row, 1)
        form.addWidget(QLabel("lambda"), row, 2)
        self.lambda_spin = QDoubleSpinBox(); self.lambda_spin.setRange(0.0, 1e6); self.lambda_spin.setDecimals(6); self.lambda_spin.setValue(0.0)
        form.addWidget(self.lambda_spin, row, 3)
        row += 1

        form.addWidget(QLabel("p exponent"), row, 0)
        self.p_spin = QSpinBox(); self.p_spin.setRange(1, 20); self.p_spin.setValue(2)
        form.addWidget(self.p_spin, row, 1)
        form.addWidget(QLabel("Backend"), row, 2)
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(list(BS_BACKEND_ALLOWED))
        self.backend_combo.setCurrentText("auto")
        form.addWidget(self.backend_combo, row, 3)
        row += 1

        form.addWidget(QLabel("Branch selection"), row, 0)
        self.root_mode_combo = QComboBox()
        self.root_mode_combo.addItems(list(ROOT_SELECTION_ALLOWED))
        self.root_mode_combo.setCurrentText("continuation")
        form.addWidget(self.root_mode_combo, row, 1)
        form.addWidget(QLabel("Regularizer"), row, 2)
        self.regularizer_combo = QComboBox()
        self.regularizer_combo.addItems(list(REGULARIZER_ALLOWED))
        self.regularizer_combo.setCurrentText("legacy")
        form.addWidget(self.regularizer_combo, row, 3)
        row += 1

        self.torch_check = QCheckBox("Allow torch fallback if available")
        self.torch_check.setChecked(True)
        form.addWidget(self.torch_check, row, 0, 1, 2)
        self.sweep_check = QCheckBox("Enable exact-pair sweep")
        self.sweep_check.setChecked(False)
        form.addWidget(self.sweep_check, row, 2, 1, 2)
        row += 1

        form.addWidget(QLabel("Sweep pairs"), row, 0)
        self.sweep_pairs_edit = QLineEdit("(4000,4000),(8000,8000),(16000,16000)")
        form.addWidget(self.sweep_pairs_edit, row, 1, 1, 3)
        row += 1

        form.addWidget(QLabel("Sweep layout"), row, 0)
        self.sweep_layout_combo = QComboBox()
        self.sweep_layout_combo.addItems(list(SWEEP_LAYOUT_ALLOWED))
        self.sweep_layout_combo.setCurrentText("exact_pairs_only")
        form.addWidget(self.sweep_layout_combo, row, 1)
        form.addWidget(QLabel("Preferred fit"), row, 2)
        self.preferred_fit_combo = QComboBox()
        self.preferred_fit_combo.addItems(["global"] + list(CLOSURE_CANDIDATE_FIT_METHODS))
        self.preferred_fit_combo.setCurrentText(PREFERRED_FIT_METHOD)
        form.addWidget(self.preferred_fit_combo, row, 3)
        row += 1

        form.addWidget(QLabel("Extrapolation min N_int"), row, 0)
        self.extrap_min_spin = QSpinBox(); self.extrap_min_spin.setRange(1, 1000000); self.extrap_min_spin.setValue(EXTRAP_MIN_NINT_DEFAULT)
        form.addWidget(self.extrap_min_spin, row, 1)
        row += 1

        left_layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("Run benchmark")
        self.run_btn.clicked.connect(self.run_benchmark)
        btn_row.addWidget(self.run_btn)
        self.cancel_btn = QPushButton("Cancel current run")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_run)
        btn_row.addWidget(self.cancel_btn)
        self.preview_btn = QPushButton("Refresh 3D preview")
        self.preview_btn.clicked.connect(self.refresh_preview)
        btn_row.addWidget(self.preview_btn)
        self.open_btn = QPushButton("Open ideal file...")
        self.open_btn.clicked.connect(self.open_ideal_file)
        btn_row.addWidget(self.open_btn)
        self.export_btn = QPushButton("Export summary")
        self.export_btn.clicked.connect(self.export_summary)
        btn_row.addWidget(self.export_btn)
        left_layout.addLayout(btn_row)

        prog_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        prog_row.addWidget(self.progress_bar, 1)
        self.progress_label = QLabel("Idle")
        prog_row.addWidget(self.progress_label)
        left_layout.addLayout(prog_row)

        self.info_box = QTextEdit(); self.info_box.setReadOnly(True)
        left_layout.addWidget(QLabel("Selected entry / formulas"))
        left_layout.addWidget(self.info_box, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.tabs = QTabWidget()

        self.log_box = QPlainTextEdit(); self.log_box.setReadOnly(True)
        self.tabs.addTab(self.log_box, "Console log")

        self.result_box = QTextEdit(); self.result_box.setReadOnly(True)
        self.tabs.addTab(self.result_box, "Results")

        self.theorem_box = QTextEdit(); self.theorem_box.setReadOnly(True)
        self.tabs.addTab(self.theorem_box, "Closure / Continuation")

        self.fit_box = QTextEdit(); self.fit_box.setReadOnly(True)
        self.tabs.addTab(self.fit_box, "Fit Robustness")

        self.sweep_box = QTextEdit(); self.sweep_box.setReadOnly(True)
        self.tabs.addTab(self.sweep_box, "Resolution Sweep")

        self.preview_tab = Preview3DWidget()
        self.preview_tab.refresh_btn.clicked.connect(self.refresh_preview)
        self.preview_tab.mode_combo.currentIndexChanged.connect(self.refresh_preview)
        self.preview_tab.points_combo.currentIndexChanged.connect(self.refresh_preview)
        self.tabs.addTab(self.preview_tab, "3D Preview")

        right_layout.addWidget(self.tabs)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([520, 980])
        self.update_point_warnings()


    def current_geom_points(self) -> int:
        return int(self.n_geom_combo.currentData())

    def current_int_points(self) -> int:
        return int(self.n_int_combo.currentData())

    def update_point_warnings(self):
        g = self.current_geom_points()
        i = self.current_int_points()
        self.geom_warn.setText("Warning: 32000/64000 can be slow and memory-heavy." if g in WARNING_PRESETS else "")
        self.int_warn.setText("Warning: 32000/64000 can be very slow for integration." if i in WARNING_PRESETS else "")

    def set_run_ui_state(self, running: bool):
        self.run_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        if not running and self.progress_bar.value() == 0:
            self.progress_label.setText("Idle")

    def on_progress(self, pct: int, phase: str, eta_text: str):
        self.progress_bar.setValue(max(0, min(100, int(pct))))
        self.progress_label.setText(f"{phase} | ETA {eta_text}")

    def cancel_run(self):
        if self.current_worker and self.current_worker.isRunning():
            self.append_log("[META] cancellation requested by user")
            self.progress_label.setText("Cancelling...")
            self.current_worker.requestInterruption()

    def scan_files(self):
        roots = [Path.cwd(), Path(__file__).resolve().parent]
        files = find_ideal_files(roots)
        self.entries_by_file.clear()
        self.file_combo.blockSignals(True)
        self.file_combo.clear()
        for f in files:
            try:
                entries = parse_ideal_file(f)
            except Exception:
                continue
            self.entries_by_file[str(f)] = entries
            self.file_combo.addItem(f.name, str(f))
        self.file_combo.blockSignals(False)
        self.populate_ids()

    def open_ideal_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose ideal*.txt", str(Path.cwd()), "Text files (*.txt)")
        if not path:
            return
        p = Path(path)
        try:
            entries = parse_ideal_file(p)
        except Exception as e:
            QMessageBox.critical(self, "Parse failed", str(e))
            return
        self.entries_by_file[str(p)] = entries
        if self.file_combo.findData(str(p)) < 0:
            self.file_combo.addItem(p.name, str(p))
        self.file_combo.setCurrentIndex(self.file_combo.findData(str(p)))

    def populate_ids(self):
        self.id_combo.blockSignals(True)
        self.id_combo.clear()
        file_key = self.file_combo.currentData()
        if not file_key:
            self.id_combo.blockSignals(False)
            self.show_entry_info()
            return
        entries = sorted(self.entries_by_file.get(str(file_key), []), key=lambda e: natural_knot_id_key(e.knot_id))
        filt = self.filter_edit.text().strip().lower()
        family_mode = self.family_combo.currentText() if hasattr(self, "family_combo") else "All entries"
        for entry in entries:
            label = format_entry_label(entry)
            if filt and filt not in label.lower():
                continue
            if not family_filter_match(entry, family_mode):
                continue
            self.id_combo.addItem(label, entry.knot_id)
        self.id_combo.blockSignals(False)
        self.show_entry_info()

    def current_entry(self) -> Optional[IdealEntry]:
        file_key = self.file_combo.currentData()
        knot_id = self.id_combo.currentData()
        if not file_key or not knot_id:
            return None
        for entry in self.entries_by_file.get(str(file_key), []):
            if entry.knot_id == knot_id:
                return entry
        return None

    def show_entry_info(self):
        entry = self.current_entry()
        if entry is None:
            self.info_box.setHtml("<i>No entry selected.</i>")
            self.preview_tab.set_entry(None)
            self.preview_tab.render()
            self.update_theorem_tab(None)
            self.update_fit_robustness_tab(None)
            self.update_sweep_tab(None)
            return
        html = []
        html.append(f"<h3>{entry.knot_id}</h3>")
        html.append(f"<p><b>File:</b> {entry.source_file.name}<br>")
        html.append(f"<b>Conway:</b> {entry.conway}<br>")
        html.append(f"<b>Family tags:</b> {', '.join(family_tags(entry)) or '-'}<br>")
        html.append(f"<b>Components:</b> {entry.n_components}<br>")
        html.append(f"<b>L_ref:</b> {entry.L_ref:.6f} &nbsp; <b>D_ref:</b> {entry.D_ref:.6f}</p>")
        html.append("<p><b>Orthodox benchmark formulas</b></p>")
        html.append("<pre>r_ref = Gamma_ref / (2*pi*U_ref)\n"
                    "x_nc = sqrt(4*pi*A_K)\n"
                    "a_nc = x_nc * r_ref\n"
                    "benchmark target: A_K = 1/(4*pi)</pre>")
        html.append("<p>This GUI treats the selected knot/link as an ideal-geometry input to a regularized filament benchmark, without SST-specific interpretation.</p>")
        self.info_box.setHtml("\n".join(html))
        self.preview_tab.set_entry(entry)
        self.preview_tab.render()
        self.update_theorem_tab(self.last_result)
        self.update_sweep_tab(self.last_result)

    def update_theorem_tab(self, result: Optional[dict] = None):
        entry = self.current_entry()
        html = []
        html.append("<h3>Closure / Continuation</h3>")
        html.append(r"""<pre>A_{\mathrm{req}} = 1/(4\pi)
        x_{\mathrm{nc}} = \sqrt{4\pi A_K}
        r_{\mathrm{ref}} = \Gamma_{\mathrm{ref}}/(2\pi U_{\mathrm{ref}})
        a_{\mathrm{nc}} = x_{\mathrm{nc}}\,r_{\mathrm{ref}}</pre>""")
        if entry is not None:
            html.append(f"<p><b>Selected entry:</b> {entry.knot_id} &nbsp; <b>Conway:</b> {entry.conway or '-'} &nbsp; <b>Tags:</b> {', '.join(family_tags(entry)) or '-'} </p>")
        if result and not result.get('cancelled'):
            fits = result.get('fits', [])
            preferred_method = self.preferred_fit_combo.currentText() if hasattr(self, 'preferred_fit_combo') else PREFERRED_FIT_METHOD
            chosen = select_preferred_fit(fits, preferred_method)
            if chosen is not None:
                A_K = float(chosen.A_K)
                ratio = A_K / A_REQ
                anc_over = closure_x_from_A(A_K)
                resid = anc_over - 1.0
                html.append("<p><b>Chosen fit for closure summary:</b> " + chosen.method + "</p>")
                html.append("<table border='1' cellspacing='0' cellpadding='4'>")
                html.append("<tr><th>Quantity</th><th>Value</th></tr>")
                html.append(f"<tr><td>A_K</td><td>{A_K:.8f}</td></tr>")
                html.append(f"<tr><td>A_K / (1/(4π))</td><td>{ratio:.6f}</td></tr>")
                html.append(f"<tr><td>x_nc = a_nc / r_ref</td><td>{anc_over:.6f}</td></tr>")
                html.append(f"<tr><td>closure residual (x_nc - 1)</td><td>{resid:+.6e}</td></tr>")
                html.append(f"<tr><td>backend</td><td>{result.get('backend_used', '-')}</td></tr>")
                html.append(f"<tr><td>root mode</td><td>{self.root_mode_combo.currentText()}</td></tr>")
                html.append(f"<tr><td>regularizer</td><td>{self.regularizer_combo.currentText()}</td></tr>")
                html.append("</table>")
                lam = float(self.lambda_spin.value())
                pexp = int(self.p_spin.value())
                html.append(f"<p><b>Current regularized root settings:</b> λ = {lam:g}, p = {pexp}. The regularized root a* remains model-dependent; use the Results tab and console log for branch behavior.</p>")
            else:
                html.append("<p><i>No finite fit available yet.</i></p>")
        else:
            html.append("<p><i>Run the benchmark to populate closure / continuation diagnostics.</i></p>")
        self.theorem_box.setHtml('\n'.join(html))

    def update_fit_robustness_tab(self, result: Optional[dict] = None):
        html = ["<h3>Fit Robustness</h3>"]
        if not result or result.get("cancelled"):
            html.append("<p><i>Run the benchmark to populate plateau diagnostics and parallel fit comparisons.</i></p>")
            self.fit_box.setHtml("\n".join(html))
            return
        fits = result.get("fits", [])
        plateau_diag = result.get("plateau_diag", {})
        html.append("<table border='1' cellspacing='0' cellpadding='4'>")
        html.append("<tr><th>method</th><th>A_K</th><th>A ratio</th><th>x_nc</th><th>n_plateau</th><th>A spread</th><th>a_ref</th></tr>")
        for fr in fits:
            A_K = getattr(fr, "A_K", np.nan)
            ratio = (A_K / A_REQ) if np.isfinite(A_K) else np.nan
            x_nc = closure_x_from_A(A_K) if np.isfinite(A_K) else np.nan
            html.append(
                f"<tr><td>{fr.method}</td><td>{A_K:.8f}</td><td>{ratio:.6f}</td><td>{x_nc:.6f}</td>"
                f"<td>{fr.n_plateau}</td><td>{fr.A_spread:.3e}</td><td>{fr.a_fit_ref:.3e}</td></tr>"
            )
        html.append("</table>")
        if plateau_diag:
            html.append("<p><b>Plateau masks</b></p><table border='1' cellspacing='0' cellpadding='4'>")
            html.append("<tr><th>method</th><th>n_plateau</th><th>a_lo</th><th>a_hi</th><th>A_median</th><th>A_spread</th></tr>")
            for method in sorted(plateau_diag.keys()):
                st = plateau_diag[method]
                html.append(
                    f"<tr><td>{method}</td><td>{st.get('n_plateau', 0)}</td><td>{st.get('a_lo', np.nan):.3e}</td>"
                    f"<td>{st.get('a_hi', np.nan):.3e}</td><td>{st.get('A_median', np.nan):.8f}</td>"
                    f"<td>{st.get('A_spread', np.nan):.3e}</td></tr>"
                )
            html.append("</table>")
        self.fit_box.setHtml("\n".join(html))

    def update_sweep_tab(self, result: Optional[dict] = None):
        html = ["<h3>Resolution Sweep</h3>"]
        if not result or result.get("cancelled"):
            html.append("<p><i>Enable exact-pair sweep to populate resolution diagnostics.</i></p>")
            self.sweep_box.setHtml("\n".join(html))
            return
        summary = result.get("sweep_summary") or {}
        rows = summary.get("rows", [])
        if not rows:
            html.append("<p><i>No sweep rows recorded for this run.</i></p>")
            self.sweep_box.setHtml("\n".join(html))
            return
        html.append(f"<p><b>Preferred fit:</b> {summary.get('preferred_method', '-')} &nbsp; <b>Extrapolation min N_int:</b> {summary.get('extrap_min_nint', '-')}</p>")
        html.append("<table border='1' cellspacing='0' cellpadding='4'>")
        html.append("<tr><th>N_geom</th><th>N_int</th><th>backend</th><th>method</th><th>A_K</th><th>A ratio</th><th>x_nc</th><th>n_plateau</th></tr>")
        for row in rows:
            html.append(
                f"<tr><td>{row['N_geom']}</td><td>{row['N_int']}</td><td>{row['backend']}</td><td>{row['method']}</td>"
                f"<td>{row['A_K']:.8f}</td><td>{row['A_ratio']:.6f}</td><td>{row['x_nc']:.6f}</td><td>{row['n_plateau']}</td></tr>"
            )
        html.append("</table>")
        html.append("<p><b>Tail diagnostics</b></p>")
        html.append("<table border='1' cellspacing='0' cellpadding='4'>")
        html.append("<tr><th>quantity</th><th>value</th></tr>")
        html.append(f"<tr><td>last2 half-range A_K</td><td>{summary.get('A_last2_half_range', np.nan):.3e}</td></tr>")
        html.append(f"<tr><td>last2 half-range x_nc</td><td>{summary.get('x_last2_half_range', np.nan):.3e}</td></tr>")
        html.append(f"<tr><td>tail(A_K) quasi-monotone</td><td>{'yes' if summary.get('A_tail_quasi_monotone') else 'no'}</td></tr>")
        html.append(f"<tr><td>tail(x_nc) quasi-monotone</td><td>{'yes' if summary.get('x_tail_quasi_monotone') else 'no'}</td></tr>")
        html.append("</table>")
        self.sweep_box.setHtml("\n".join(html))

    def export_summary(self):
        if not self.last_result or self.last_result.get("cancelled"):
            QMessageBox.information(self, "No results", "Run the benchmark first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export summary", str(Path.cwd() / "orthodox_benchmark_summary.csv"), "CSV files (*.csv)")
        if not path:
            return
        fits = self.last_result.get("fits", [])
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["method", "A_K", "A_ratio", "x_nc", "n_plateau", "A_spread", "a_fit_ref", "backend", "root_mode", "regularizer"])
            for fr in fits:
                A_K = fr.A_K
                writer.writerow([
                    fr.method,
                    A_K,
                    (A_K / A_REQ) if np.isfinite(A_K) else np.nan,
                    closure_x_from_A(A_K) if np.isfinite(A_K) else np.nan,
                    fr.n_plateau,
                    fr.A_spread,
                    fr.a_fit_ref,
                    self.last_result.get("backend_used", "-"),
                    self.root_mode_combo.currentText(),
                    self.regularizer_combo.currentText(),
                ])
        txt_path = str(Path(path).with_suffix('.txt'))
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Orthodox ideal-knot benchmark summary {SCRIPT_VERSION}\n")
            f.write("=" * 72 + "\n")
            f.write(f"backend={self.last_result.get('backend_used', '-')}\n")
            f.write(f"root_mode={self.root_mode_combo.currentText()} regularizer={self.regularizer_combo.currentText()}\n")
            f.write(f"preferred_fit={self.preferred_fit_combo.currentText()}\n\n")
            for fr in fits:
                A_K = fr.A_K
                x_nc = closure_x_from_A(A_K) if np.isfinite(A_K) else np.nan
                f.write(
                    f"[{fr.method}] A_K={A_K:.10e} A_ratio={(A_K / A_REQ) if np.isfinite(A_K) else np.nan:.10e} "
                    f"x_nc={x_nc:.10e} n_plateau={fr.n_plateau} A_spread={fr.A_spread:.10e}\n"
                )
            summary = self.last_result.get('sweep_summary') or {}
            rows = summary.get('rows', [])
            if rows:
                f.write("\n[Resolution sweep]\n")
                f.write(f"preferred_method={summary.get('preferred_method')} extrap_min_nint={summary.get('extrap_min_nint')}\n")
                for row in rows:
                    f.write(
                        f"N_geom={row['N_geom']} N_int={row['N_int']} backend={row['backend']} method={row['method']} "
                        f"A_K={row['A_K']:.10e} x_nc={row['x_nc']:.10e}\n"
                    )
                f.write(f"tail_A_last2_half_range={summary.get('A_last2_half_range', np.nan):.10e}\n")
                f.write(f"tail_x_last2_half_range={summary.get('x_last2_half_range', np.nan):.10e}\n")
                f.write(f"tail_A_quasi_monotone={bool(summary.get('A_tail_quasi_monotone', False))}\n")
                f.write(f"tail_x_quasi_monotone={bool(summary.get('x_tail_quasi_monotone', False))}\n")
        self.append_log(f"[EXPORT] wrote summary to {path}")
        self.append_log(f"[EXPORT] wrote text summary to {txt_path}")

    def append_log(self, msg: str):
        self.log_box.appendPlainText(msg)
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    def refresh_preview(self):
        self.preview_tab.set_entry(self.current_entry())
        self.preview_tab.render()

    def run_benchmark(self):
        if self.current_worker and self.current_worker.isRunning():
            QMessageBox.warning(self, "Busy", "A run is already in progress.")
            return
        entry = self.current_entry()
        if entry is None:
            QMessageBox.warning(self, "No selection", "Choose a knot or link first.")
            return
        self.log_box.clear()
        self.result_box.clear()
        self.theorem_box.clear()
        self.fit_box.clear()
        self.last_result = None
        self.progress_bar.setValue(0)
        self.progress_label.setText("Preparing run...")
        self.current_worker = BenchmarkWorker(
            entry=entry,
            points_per_component=self.current_geom_points(),
            int_points_per_component=self.current_int_points(),
            U_ref=float(self.u_spin.value()),
            Gamma_ref=float(self.gamma_spin.value()),
            rho=float(self.rho_spin.value()),
            lam=float(self.lambda_spin.value()),
            p_exp=int(self.p_spin.value()),
            backend_mode=self.backend_combo.currentText(),
            allow_torch=bool(self.torch_check.isChecked()),
            root_selection_mode=self.root_mode_combo.currentText(),
            regularizer=self.regularizer_combo.currentText(),
            sweep_enabled=bool(self.sweep_check.isChecked()),
            sweep_pairs_text=self.sweep_pairs_edit.text().strip(),
            sweep_layout=self.sweep_layout_combo.currentText(),
            preferred_fit_method=self.preferred_fit_combo.currentText(),
            extrap_min_nint=int(self.extrap_min_spin.value()),
        )
        self.current_worker.log_signal.connect(self.append_log)
        self.current_worker.progress_signal.connect(self.on_progress)
        self.current_worker.done_signal.connect(self.on_done)
        self.current_worker.error_signal.connect(self.on_error)
        self.set_run_ui_state(True)
        self.current_worker.start()
        self.tabs.setCurrentIndex(0)

    def on_done(self, result: dict):
        self.set_run_ui_state(False)
        self.progress_bar.setValue(100 if not result.get("cancelled") else 0)
        self.progress_label.setText("Cancelled" if result.get("cancelled") else "Complete")
        if result.get("cancelled"):
            self.result_box.setHtml("<b>Run cancelled by user.</b>")
            self.update_theorem_tab(None)
            self.update_fit_robustness_tab(None)
            self.update_sweep_tab(None)
            self.tabs.setCurrentIndex(1)
            self.current_worker = None
            return
        self.last_result = result
        fits = result["fits"]
        r_ref = result["r_ref"]
        geom = result["geom"]
        backend_used = result.get("backend_used", "-")
        lines = []
        lines.append(f"<h3>Benchmark summary</h3>")
        lines.append(f"<p><b>Total points (full/int):</b> {geom.total_points_full} / {geom.total_points_int}<br>")
        lines.append(f"<b>L_dimless:</b> {geom.L_dimless_full:.6f}<br>")
        lines.append(f"<b>d_min:</b> {geom.d_min_full:.6f}<br>")
        lines.append(f"<b>r_ref:</b> {r_ref:.8e} m<br><b>backend:</b> {backend_used}<br><b>preferred fit:</b> {self.preferred_fit_combo.currentText()}</p>")
        lines.append("<table border='1' cellspacing='0' cellpadding='4'>")
        lines.append("<tr><th>method</th><th>A_K</th><th>A_K/(1/(4π))</th><th>a_nc / r_ref</th></tr>")
        for fr in fits:
            A_K = fr.A_K
            a_nc_over_rref = closure_x_from_A(A_K) if np.isfinite(A_K) else np.nan
            lines.append(f"<tr><td>{fr.method}</td><td>{A_K:.8f}</td><td>{A_K/A_REQ:.6f}</td><td>{a_nc_over_rref:.6f}</td></tr>")
        lines.append("</table>")
        self.result_box.setHtml("\n".join(lines))
        self.update_theorem_tab(result)
        self.update_fit_robustness_tab(result)
        self.update_sweep_tab(result)
        self.tabs.setCurrentIndex(1)
        self.append_log("[META] benchmark complete")
        self.current_worker = None

    def on_error(self, text: str):
        self.set_run_ui_state(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Failed")
        self.update_theorem_tab(None)
        self.update_fit_robustness_tab(None)
        self.update_sweep_tab(None)
        QMessageBox.critical(self, "Run failed", text)
        self.append_log("[ERROR] run failed; see popup")
        self.current_worker = None


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
