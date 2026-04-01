from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Iterable, Optional, Sequence, Dict, Any

import numpy as np

C_LIGHT = 299_792_458.0


def _candidate_dirs(extra_search_dirs: Optional[Iterable[os.PathLike | str]] = None) -> list[Path]:
    out: list[Path] = []
    seen: set[str] = set()
    for raw in (extra_search_dirs or []):
        p = Path(raw).resolve()
        key = str(p).lower()
        if p.is_dir() and key not in seen:
            seen.add(key)
            out.append(p)
    return out


def try_import_sstcore(extra_search_dirs: Optional[Iterable[os.PathLike | str]] = None):
    """Import swirl_string_core / sstbindings / sstcore, optionally searching local folders.

    Returns
    -------
    module or None
    """
    module_names = ("swirl_string_core", "sstbindings", "sstcore")

    for name in module_names:
        try:
            return importlib.import_module(name)
        except Exception:
            pass

    suffixes = (".pyd", ".so", ".dll", ".dylib")
    search_dirs = _candidate_dirs(extra_search_dirs)
    for folder in search_dirs:
        for name in module_names:
            matches = sorted(folder.glob(f"{name}*"))
            for path in matches:
                if path.suffix.lower() not in suffixes and not any(str(path).lower().endswith(s) for s in suffixes):
                    continue
                try:
                    spec = importlib.util.spec_from_file_location(name, str(path))
                    if spec is None or spec.loader is None:
                        continue
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[name] = module
                    spec.loader.exec_module(module)
                    return module
                except Exception:
                    continue
    return None


def _call_biot_velocity_grid(module, curve_xyz: np.ndarray, grid_xyz: np.ndarray, circulation: float) -> np.ndarray:
    curve_xyz = np.ascontiguousarray(curve_xyz, dtype=float)
    grid_xyz = np.ascontiguousarray(grid_xyz, dtype=float)

    if hasattr(module, "biot_savart_velocity_grid"):
        # Current source tree exposes no circulation arg here, so we scale in Python.
        return circulation * np.asarray(module.biot_savart_velocity_grid(curve_xyz, grid_xyz), dtype=float)

    if hasattr(module, "compute_biot_savart_velocity_grid"):
        return circulation * np.asarray(module.compute_biot_savart_velocity_grid(curve_xyz, grid_xyz), dtype=float)

    if hasattr(module, "BiotSavart") and hasattr(module.BiotSavart, "compute_velocity"):
        return circulation * np.asarray(module.BiotSavart.compute_velocity(curve_xyz.tolist(), grid_xyz.tolist()), dtype=float)

    raise AttributeError("No usable Biot–Savart grid API found in SSTcore module.")


def curve_midpoints(curve_xyz: np.ndarray) -> np.ndarray:
    curve_xyz = np.asarray(curve_xyz, dtype=float)
    return 0.5 * (curve_xyz + np.roll(curve_xyz, -1, axis=0))


def segment_lengths(curve_xyz: np.ndarray) -> np.ndarray:
    curve_xyz = np.asarray(curve_xyz, dtype=float)
    return np.linalg.norm(np.roll(curve_xyz, -1, axis=0) - curve_xyz, axis=1)


def compute_curve_midpoint_velocity(
    curve_xyz: np.ndarray,
    circulation: float,
    extra_search_dirs: Optional[Iterable[os.PathLike | str]] = None,
) -> Dict[str, Any]:
    """Fast Biot–Savart on segment midpoints.

    This is the most natural drop-in for scripts that already work with a sampled polyline.
    """
    module = try_import_sstcore(extra_search_dirs=extra_search_dirs)
    if module is None:
        return {"ok": False, "reason": "sstcore_not_found"}

    curve_xyz = np.ascontiguousarray(curve_xyz, dtype=float)
    mids = curve_midpoints(curve_xyz)
    vel = _call_biot_velocity_grid(module, curve_xyz, mids, circulation)
    ds = segment_lengths(curve_xyz)

    return {
        "ok": True,
        "backend": getattr(module, "__name__", "sstcore"),
        "midpoints": mids,
        "velocity_midpoints": vel,
        "segment_lengths": ds,
        "speed_midpoints": np.linalg.norm(vel, axis=1),
    }


def _chunked_min_sq_distance(points_xyz: np.ndarray, cloud_xyz: np.ndarray, chunk: int = 2048) -> np.ndarray:
    points_xyz = np.ascontiguousarray(points_xyz, dtype=float)
    cloud_xyz = np.ascontiguousarray(cloud_xyz, dtype=float)
    out = np.full(points_xyz.shape[0], np.inf, dtype=float)
    for i0 in range(0, points_xyz.shape[0], chunk):
        slab = points_xyz[i0:i0 + chunk]
        diff = slab[:, None, :] - cloud_xyz[None, :, :]
        sq = np.einsum("ijk,ijk->ij", diff, diff)
        out[i0:i0 + chunk] = np.min(sq, axis=1)
    return out


def compute_grid_energy_diagnostic(
    curve_xyz: np.ndarray,
    circulation: float,
    rho_f: float,
    grid_size: int = 32,
    padding: float = 2.0,
    exclusion_radius: Optional[float] = None,
    extra_search_dirs: Optional[Iterable[os.PathLike | str]] = None,
) -> Dict[str, Any]:
    """Auxiliary hydrodynamic diagnostic for a final trefoil candidate.

    Notes
    -----
    This is *not* a replacement for a geometric ropelength/min-distance sweep.
    It is an additional field-space diagnostic based on the C++ Biot–Savart backend.
    """
    module = try_import_sstcore(extra_search_dirs=extra_search_dirs)
    if module is None:
        return {"ok": False, "reason": "sstcore_not_found"}

    curve_xyz = np.ascontiguousarray(curve_xyz, dtype=float)
    seg_len = segment_lengths(curve_xyz)
    h = float(np.mean(seg_len)) if seg_len.size else 1.0
    pad = float(padding) * h

    box_min = np.min(curve_xyz, axis=0) - pad
    box_max = np.max(curve_xyz, axis=0) + pad
    xs = np.linspace(box_min[0], box_max[0], int(grid_size), dtype=float)
    ys = np.linspace(box_min[1], box_max[1], int(grid_size), dtype=float)
    zs = np.linspace(box_min[2], box_max[2], int(grid_size), dtype=float)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    grid_xyz = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])

    vel = _call_biot_velocity_grid(module, curve_xyz, grid_xyz, circulation)

    dx = float(xs[1] - xs[0]) if len(xs) > 1 else 1.0
    dy = float(ys[1] - ys[0]) if len(ys) > 1 else 1.0
    dz = float(zs[1] - zs[0]) if len(zs) > 1 else 1.0
    dV = dx * dy * dz

    mids = curve_midpoints(curve_xyz)
    if exclusion_radius is None:
        exclusion_radius = 1.5 * max(dx, dy, dz)
    exclusion_radius = float(exclusion_radius)

    min_sq = _chunked_min_sq_distance(grid_xyz, mids)
    keep = min_sq >= exclusion_radius * exclusion_radius

    v2 = np.einsum("ij,ij->i", vel, vel)
    E_fluid = 0.5 * float(rho_f) * dV * float(np.sum(v2[keep]))
    M_fluid = E_fluid / C_LIGHT**2

    return {
        "ok": True,
        "backend": getattr(module, "__name__", "sstcore"),
        "grid_points": grid_xyz,
        "velocity_grid": vel,
        "keep_mask": keep,
        "spacing": (dx, dy, dz),
        "dV": dV,
        "E_fluid": E_fluid,
        "M_fluid": M_fluid,
        "excluded_points": int(np.size(keep) - np.count_nonzero(keep)),
        "grid_size": int(grid_size),
        "exclusion_radius": exclusion_radius,
    }


def load_ideal_ab_curve(
    ab_id: str = "3:1:1",
    n_pts: int = 4000,
    ideal_text_path: Optional[os.PathLike | str] = None,
    extra_search_dirs: Optional[Iterable[os.PathLike | str]] = None,
) -> np.ndarray:
    """Load an ideal AB curve using SSTcore parsing helpers.

    Falls back to parse_ideal_txt_from_string + index_of_ideal_id when the direct helper is absent.
    """
    module = try_import_sstcore(extra_search_dirs=extra_search_dirs)
    if module is None:
        raise RuntimeError("sstcore_not_found")

    if ideal_text_path is None:
        ideal_text_path = Path("ideal.txt")
    text = Path(ideal_text_path).read_text(encoding="utf-8", errors="ignore")

    if hasattr(module, "parse_ideal_ab_by_id_from_string"):
        ab = module.parse_ideal_ab_by_id_from_string(text, ab_id)
    else:
        blocks = module.parse_ideal_txt_from_string(text)
        idx = module.index_of_ideal_id(blocks, ab_id)
        if idx < 0:
            raise ValueError(f"AB Id not found: {ab_id}")
        ab = blocks[idx]

    s = np.linspace(0.0, 2.0 * np.pi, int(n_pts), endpoint=False)
    if hasattr(module, "evaluate_ideal_ab_components"):
        curves = module.evaluate_ideal_ab_components(ab, s)
        curve = np.asarray(curves[0], dtype=float)
    else:
        curve = np.asarray(module.evaluate_fourier_block(ab.fourier, s.tolist()), dtype=float)
    return curve
