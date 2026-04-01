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

import math
import os
import re
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

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
    QPlainTextEdit, QCheckBox, QSplitter, QTabWidget
)

A_REQ = 1.0 / (4.0 * math.pi)
DEFAULT_U_REF = 1.09384563e6
DEFAULT_GAMMA_REF = 9.68361918e-9
DEFAULT_RHO = 7.0e-7
REL_DE_THRESH = 1e-4
PLATEAU_FRACS = [0.08, 0.12, 0.16]
A_SCAN_COUNT = 24
BS_BLOCK = 512
DEFAULT_PREVIEW_POINTS = 900
QUIVER_COUNT = 48
POINT_PRESETS = [500, 1000, 2000, 4000, 8000, 16000, 32000, 64000]
WARNING_PRESETS = {32000, 64000}


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


def log_prefix(msg: str) -> str:
    return msg if msg.startswith("[") else f"[LOG] {msg}"


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
    entries.sort(key=lambda e: e.knot_id)
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


def coarse_min_self_distance(points: np.ndarray, comp_ids: np.ndarray, local_idx: np.ndarray, n_per_comp: np.ndarray, excl_same_comp: int, cancel_cb: Optional[Callable[[], bool]] = None) -> float:
    n = len(points)
    d_min = np.inf
    for i0 in range(0, n, BS_BLOCK):
        check_cancel(cancel_cb)
        check_cancel(cancel_cb)
        i1 = min(i0 + BS_BLOCK, n)
        Pi = points[i0:i1]
        ci = comp_ids[i0:i1]
        li = local_idx[i0:i1]
        for j0 in range(i0, n, BS_BLOCK):
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
    return float(d_min)


def build_geometry(entry: IdealEntry, points_per_component: int, int_points_per_component: int, cancel_cb: Optional[Callable[[], bool]] = None) -> GeometryData:
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
    d_min_full = coarse_min_self_distance(points_full, comp_full, local_full, ncomp_full, max(5, points_per_component // 15), cancel_cb=cancel_cb)
    d_min_int = coarse_min_self_distance(points_int, comp_int, local_int, ncomp_int, max(5, points_per_component // 15), cancel_cb=cancel_cb)

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


def build_preview_data(entry: IdealEntry, points_per_component: int) -> List[Dict[str, np.ndarray]]:
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
    for i0 in range(0, n, BS_BLOCK):
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
    for i0 in range(0, n, BS_BLOCK):
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


def compute_bs_energy(a_dimless: float, geom: GeometryData, use_torch: bool, cancel_cb: Optional[Callable[[], bool]] = None) -> float:
    if use_torch and TORCH_AVAILABLE:
        try:
            dev = _pick_torch_device()
            return _bs_energy_torch(a_dimless, geom, dev, cancel_cb=cancel_cb)
        except RunCancelled:
            raise
        except Exception:
            return _bs_energy_numpy(a_dimless, geom, cancel_cb=cancel_cb)
    return _bs_energy_numpy(a_dimless, geom, cancel_cb=cancel_cb)


def scan_bs_energy(geom: GeometryData, use_torch: bool, cancel_cb: Optional[Callable[[], bool]] = None) -> Tuple[np.ndarray, np.ndarray]:
    ds_med = float(np.median(geom.ds_int))
    a_lo = max(3.0 * ds_med, geom.d_min_int * 5e-4)
    a_hi = geom.d_min_int * 0.35
    a_scan = np.logspace(np.log10(a_lo), np.log10(a_hi), A_SCAN_COUNT)
    E_vals = np.array([compute_bs_energy(a, geom, use_torch, cancel_cb=cancel_cb) for a in a_scan], dtype=float)
    return a_scan, E_vals


def extract_fits(a_scan: np.ndarray, E_vals: np.ndarray, L_dimless: float, d_min_dimless: float) -> List[Dict[str, float]]:
    x_scan = -np.log(a_scan)
    y_scan = E_vals / L_dimless
    a_mid = np.sqrt(a_scan[:-1] * a_scan[1:])
    A_local = np.diff(y_scan) / np.diff(x_scan)
    rel_dE = np.abs(np.diff(E_vals)) / np.maximum(np.abs(E_vals[:-1]), 1e-300)
    out: List[Dict[str, float]] = []
    coeffs = np.polyfit(x_scan, y_scan, 1)
    A_glob = float(coeffs[0])
    b_glob = float(coeffs[1])
    a_K_glob = b_glob - A_glob * np.log(L_dimless)
    out.append(dict(method="global", A_K=A_glob, A_spread=np.nan, a_K=a_K_glob, a_fit_ref=float(a_scan[len(a_scan)//2]), n_plateau=0))
    for frac in PLATEAU_FRACS:
        mask = (A_local > 0.0) & (rel_dE > REL_DE_THRESH) & (a_mid < frac * d_min_dimless)
        if np.any(mask):
            A = float(np.median(A_local[mask]))
            A_spread = float(np.std(A_local[mask]))
            idxs = np.where(mask)[0]
            idx_ref = int(idxs[len(idxs)//2])
            y_ref = float(0.5*(y_scan[idx_ref] + y_scan[idx_ref+1]))
            a_ref = float(a_mid[idx_ref])
            a_K = y_ref - A * np.log(L_dimless / a_ref)
            out.append(dict(method=f"plateau_{frac:.2f}", A_K=A, A_spread=A_spread, a_K=a_K, a_fit_ref=a_ref, n_plateau=int(np.sum(mask))))
    return out


def dE_da(a: float, A_K: float, L_phys: float, d_min_phys: float, rho: float, Gamma_ref: float, U_ref: float, lam: float, p_exp: int) -> float:
    if a <= 0.0 or 2.0 * a >= d_min_phys:
        return np.nan
    dE_bs = -rho * Gamma_ref**2 * L_phys * A_K / a
    dE_core = math.pi * rho * U_ref**2 * a * L_phys
    if lam == 0.0:
        dE_cont = 0.0
    else:
        xc = 2.0 * a / (d_min_phys - 2.0 * a)
        dx_da = 2.0 * d_min_phys / (d_min_phys - 2.0 * a)**2
        dE_cont = lam * rho * Gamma_ref**2 * L_phys * p_exp * xc**(p_exp - 1) * dx_da
    return dE_bs + dE_core + dE_cont


def E_phys(a: float, A_K: float, a_K: float, L_phys: float, d_min_phys: float, rho: float, Gamma_ref: float, U_ref: float, lam: float, p_exp: int) -> float:
    if a <= 0.0 or 2.0 * a >= d_min_phys:
        return np.inf
    E_bs = rho * Gamma_ref**2 * L_phys * (A_K * math.log(L_phys / a) + a_K)
    E_core = 0.5 * math.pi * rho * U_ref**2 * a*a * L_phys
    if lam == 0.0:
        E_cont = 0.0
    else:
        xc = 2.0 * a / (d_min_phys - 2.0 * a)
        E_cont = lam * rho * Gamma_ref**2 * L_phys * xc**p_exp
    return E_bs + E_core + E_cont


def find_stationary_radius(A_K: float, a_K: float, L_dimless: float, d_min_dimless: float, rho: float, Gamma_ref: float, U_ref: float, lam: float, p_exp: int, a_nc: float) -> Tuple[float, bool]:
    L_phys = L_dimless * (Gamma_ref / U_ref)
    d_min_phys = d_min_dimless * (Gamma_ref / U_ref)
    a_lo = max(d_min_phys * 1e-7, (Gamma_ref / U_ref) * 1e-8)
    a_hi = d_min_phys * 0.49
    a_vals = np.logspace(np.log10(a_lo), np.log10(a_hi), 1000)
    dE_vals = np.array([dE_da(a, A_K, L_phys, d_min_phys, rho, Gamma_ref, U_ref, lam, p_exp) for a in a_vals])
    valid = np.isfinite(dE_vals)
    av = a_vals[valid]
    dv = dE_vals[valid]
    signs = np.sign(dv)
    changes = np.where((signs[:-1] * signs[1:] < 0) | ((signs[:-1]==0) & (signs[1:]!=0)) | ((signs[:-1]!=0)&(signs[1:]==0)))[0]
    roots = []
    for i in changes:
        try:
            root = float(brentq(dE_da, float(av[i]), float(av[i+1]), args=(A_K, L_phys, d_min_phys, rho, Gamma_ref, U_ref, lam, p_exp)))
        except Exception:
            continue
        h = max(root * 1e-6, 1e-30)
        d2 = (dE_da(root+h, A_K, L_phys, d_min_phys, rho, Gamma_ref, U_ref, lam, p_exp) - dE_da(root-h, A_K, L_phys, d_min_phys, rho, Gamma_ref, U_ref, lam, p_exp)) / (2.0*h)
        is_min = bool(np.isfinite(d2) and d2 > 0)
        roots.append((root, is_min, E_phys(root, A_K, a_K, L_phys, d_min_phys, rho, Gamma_ref, U_ref, lam, p_exp)))
    if not roots:
        idx = int(np.argmin(np.abs(dv)))
        root = float(av[idx])
        return root, False
    mins = [r for r in roots if r[1]]
    pool = mins if mins else roots
    chosen = min(pool, key=lambda r: abs(r[0]-a_nc))
    return chosen[0], chosen[1]


class BenchmarkWorker(QThread):
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, entry: IdealEntry, points_per_component: int, int_points_per_component: int,
                 U_ref: float, Gamma_ref: float, rho: float, lam: float, p_exp: int, use_torch: bool):
        super().__init__()
        self.entry = entry
        self.points_per_component = points_per_component
        self.int_points_per_component = int_points_per_component
        self.U_ref = U_ref
        self.Gamma_ref = Gamma_ref
        self.rho = rho
        self.lam = lam
        self.p_exp = p_exp
        self.use_torch = use_torch

    def run(self):
        try:
            r_ref = self.Gamma_ref / (2.0 * math.pi * self.U_ref)
            self.log_signal.emit(log_prefix(f"[META] file={self.entry.source_file.name} id={self.entry.knot_id} components={self.entry.n_components} L_ref={self.entry.L_ref:.6f}"))
            self.log_signal.emit(log_prefix(f"[META] r_ref = Gamma_ref/(2*pi*U_ref) = {r_ref:.8e} m"))
            geom = build_geometry(self.entry, self.points_per_component, self.int_points_per_component, cancel_cb=self.isInterruptionRequested)
            self.log_signal.emit(log_prefix(f"[GEOM] total_points_full={geom.total_points_full} total_points_int={geom.total_points_int} L_dimless={geom.L_dimless_full:.6f} d_min={geom.d_min_full:.6f}"))
            a_scan, E_vals = scan_bs_energy(geom, self.use_torch, cancel_cb=self.isInterruptionRequested)
            fits = extract_fits(a_scan, E_vals, geom.L_dimless_full, geom.d_min_full)
            result = {
                "entry": self.entry,
                "geom": geom,
                "a_scan": a_scan,
                "E_vals": E_vals,
                "fits": fits,
                "r_ref": r_ref,
            }
            for fr in fits:
                A_K = fr["A_K"]
                a_nc = math.sqrt(A_K / math.pi) * self.Gamma_ref / self.U_ref
                a_nc_over_rref = a_nc / r_ref
                self.log_signal.emit(log_prefix(f"[FIT] method={fr['method']} A_K={A_K:.8f} A_ratio={A_K/A_REQ:.6f} a_nc_over_r_ref={a_nc_over_rref:.6f}"))
                a_star, is_min = find_stationary_radius(A_K, fr["a_K"], geom.L_dimless_full, geom.d_min_full, self.rho, self.Gamma_ref, self.U_ref, self.lam, self.p_exp, a_nc)
                self.log_signal.emit(log_prefix(f"[ROOT] lambda={self.lam:g} a_star_over_r_ref={a_star/r_ref:.6f} is_min={is_min}"))
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
        self.torch_check = QCheckBox("Use torch acceleration if available")
        self.torch_check.setChecked(True)
        form.addWidget(self.torch_check, row, 2, 1, 2)
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
        left_layout.addLayout(btn_row)

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

    def cancel_run(self):
        if self.current_worker and self.current_worker.isRunning():
            self.append_log("[META] cancellation requested by user")
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
        entries = self.entries_by_file.get(str(file_key), [])
        filt = self.filter_edit.text().strip().lower()
        for entry in entries:
            label = f"{entry.knot_id} | Conway {entry.conway} | L={entry.L_ref:.6f} | n={entry.n_components}"
            if filt and filt not in label.lower():
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
            return
        html = []
        html.append(f"<h3>{entry.knot_id}</h3>")
        html.append(f"<p><b>File:</b> {entry.source_file.name}<br>")
        html.append(f"<b>Conway:</b> {entry.conway}<br>")
        html.append(f"<b>Components:</b> {entry.n_components}<br>")
        html.append(f"<b>L_ref:</b> {entry.L_ref:.6f} &nbsp; <b>D_ref:</b> {entry.D_ref:.6f}</p>")
        html.append("<p><b>Orthodox benchmark formulas</b></p>")
        html.append("<pre>r_ref = Gamma_ref / (2*pi*U_ref)\n"
                    "a_nc = sqrt(A_K/pi) * Gamma_ref / U_ref\n"
                    "a_nc / r_ref = sqrt(4*pi*A_K)\n"
                    "benchmark target: A_K = 1/(4*pi)</pre>")
        html.append("<p>This GUI treats the selected knot/link as an ideal-geometry input to a regularized filament benchmark, without SST-specific interpretation.</p>")
        self.info_box.setHtml("\n".join(html))
        self.preview_tab.set_entry(entry)
        self.preview_tab.render()

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
        self.current_worker = BenchmarkWorker(
            entry=entry,
            points_per_component=self.current_geom_points(),
            int_points_per_component=self.current_int_points(),
            U_ref=float(self.u_spin.value()),
            Gamma_ref=float(self.gamma_spin.value()),
            rho=float(self.rho_spin.value()),
            lam=float(self.lambda_spin.value()),
            p_exp=int(self.p_spin.value()),
            use_torch=bool(self.torch_check.isChecked()),
        )
        self.current_worker.log_signal.connect(self.append_log)
        self.current_worker.done_signal.connect(self.on_done)
        self.current_worker.error_signal.connect(self.on_error)
        self.set_run_ui_state(True)
        self.current_worker.start()
        self.tabs.setCurrentIndex(0)

    def on_done(self, result: dict):
        self.set_run_ui_state(False)
        if result.get("cancelled"):
            self.result_box.setHtml("<b>Run cancelled by user.</b>")
            self.tabs.setCurrentIndex(1)
            return
        fits = result["fits"]
        r_ref = result["r_ref"]
        geom = result["geom"]
        lines = []
        lines.append(f"<h3>Benchmark summary</h3>")
        lines.append(f"<p><b>Total points (full/int):</b> {geom.total_points_full} / {geom.total_points_int}<br>")
        lines.append(f"<b>L_dimless:</b> {geom.L_dimless_full:.6f}<br>")
        lines.append(f"<b>d_min:</b> {geom.d_min_full:.6f}<br>")
        lines.append(f"<b>r_ref:</b> {r_ref:.8e} m</p>")
        lines.append("<table border='1' cellspacing='0' cellpadding='4'>")
        lines.append("<tr><th>method</th><th>A_K</th><th>A_K/(1/(4π))</th><th>a_nc / r_ref</th></tr>")
        for fr in fits:
            A_K = fr['A_K']
            a_nc_over_rref = math.sqrt(4.0*math.pi*A_K)
            lines.append(f"<tr><td>{fr['method']}</td><td>{A_K:.8f}</td><td>{A_K/A_REQ:.6f}</td><td>{a_nc_over_rref:.6f}</td></tr>")
        lines.append("</table>")
        self.result_box.setHtml("\n".join(lines))
        self.tabs.setCurrentIndex(1)
        self.append_log("[META] benchmark complete")

    def on_error(self, text: str):
        self.set_run_ui_state(False)
        QMessageBox.critical(self, "Run failed", text)
        self.append_log("[ERROR] run failed; see popup")


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
