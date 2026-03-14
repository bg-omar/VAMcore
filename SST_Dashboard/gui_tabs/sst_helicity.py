#!/usr/bin/env python3
"""
Canonical SST helicity module: Biot–Savart velocity, vorticity/curl, and a_mu from .fseries.

Use this module as the main import path for helicity computations. For legacy compatibility,
HelicityCalculationVAMcore.py re-exports this API.

Backend: tries swirl_string_core, then sstcore, then sstbindings for compiled
biot_savart_velocity_grid and curl3d_central; falls back to pure Python otherwise.
"""
import os
import re
from typing import NamedTuple, Tuple, Any

import numpy as np

# --- Robust imports (package-relative then local for direct script execution) ---
try:
    from .sst_exports import get_exports_dir
except ImportError:
    try:
        from sst_exports import get_exports_dir
    except ImportError:
        get_exports_dir = None  # type: ignore[assignment]

try:
    from .fseries_compat import parse_fseries_multi, eval_fourier_block
except ImportError:
    try:
        from fseries_compat import parse_fseries_multi, eval_fourier_block
    except ImportError:
        parse_fseries_multi = None  # type: ignore[assignment]
        eval_fourier_block = None  # type: ignore[assignment]

# --- Backend loader: first module that provides biot_savart_velocity_grid and curl3d_central ---
_biot_savart_fn = None
_curl3d_fn = None
HAVE_SST = False
for _mod_name in ("swirl_string_core", "sstcore", "sstbindings"):
    try:
        _mod = __import__(_mod_name)
        if hasattr(_mod, "biot_savart_velocity_grid") and hasattr(_mod, "curl3d_central"):
            _biot_savart_fn = _mod.biot_savart_velocity_grid
            _curl3d_fn = _mod.curl3d_central
            HAVE_SST = True
            break
    except Exception:
        continue


class HelicityResult(NamedTuple):
    """Stable result from compute_a_mu_for_file (Python path). Supports tuple unpacking."""

    a_mu: float
    Hc: float
    Hm: float


def compute_biot_savart_velocity(x, y, z, grid_points):
    """
    Biot–Savart velocity on grid_points from closed polyline (x, y, z).
    Uses compiled backend when available, else midpoint-rule fallback.
    """
    if HAVE_SST and _biot_savart_fn is not None:
        poly = np.stack([x, y, z], axis=1).astype(float)
        return _biot_savart_fn(poly, grid_points.astype(float))
    # fallback: midpoint rule
    N = len(x)
    velocity = np.zeros_like(grid_points, dtype=float)
    for i in range(N):
        r0 = np.array([x[i], y[i], z[i]], dtype=float)
        r1 = np.array([x[(i + 1) % N], y[(i + 1) % N], z[(i + 1) % N]], dtype=float)
        dl = r1 - r0
        r_mid = 0.5 * (r0 + r1)
        R = grid_points - r_mid
        invR3 = 1.0 / (np.linalg.norm(R, axis=1) ** 3 + 1e-18)
        velocity += np.cross(dl, R) * invR3[:, None]
    return velocity * (1.0 / (4.0 * np.pi))


def compute_vorticity_full_grid(velocity, shape, spacing):
    """
    Curl of velocity field on grid (shape, spacing). Uses compiled backend when available.
    """
    if HAVE_SST and _curl3d_fn is not None:
        vel3 = velocity.reshape(*shape, 3).astype(float)
        curl3 = _curl3d_fn(vel3, float(spacing))
        return np.asarray(curl3).reshape(-1, 3)
    # fallback: periodic central differences
    vx = velocity[:, 0].reshape(shape)
    vy = velocity[:, 1].reshape(shape)
    vz = velocity[:, 2].reshape(shape)
    h2 = 2 * spacing
    curl_x = (np.roll(vz, -1, 1) - np.roll(vz, 1, 1)) / h2 - (np.roll(vy, -1, 2) - np.roll(vy, 1, 2)) / h2
    curl_y = (np.roll(vx, -1, 2) - np.roll(vx, 1, 2)) / h2 - (np.roll(vz, -1, 0) - np.roll(vz, 1, 0)) / h2
    curl_z = (np.roll(vy, -1, 0) - np.roll(vy, 1, 0)) / h2 - (np.roll(vx, -1, 1) - np.roll(vx, 1, 1)) / h2
    return np.stack([curl_x, curl_y, curl_z], axis=-1).reshape(-1, 3)


def extract_interior_field(field, shape, interior_slice):
    """Extract interior slice of a 3D vector field (flattened to Nx3)."""
    return (
        field.reshape(*shape, 3)[interior_slice, :, :][:, interior_slice, :][:, :, interior_slice].reshape(
            -1, 3
        )
    )


def helicity_at(grid_size=32, spacing=0.1, interior=8):
    """
    Grid points, shape, r_sq (interior), and interior slice for helicity integration.
    Returns (grid_points, grid_shape, r_sq, interior_slice).
    """
    grid_range = spacing * (np.arange(grid_size) - grid_size // 2)
    X, Y, Z = np.meshgrid(grid_range, grid_range, grid_range, indexing="ij")
    grid_points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=-1)
    Xf, Yf, Zf = np.meshgrid(
        grid_range[interior:-interior],
        grid_range[interior:-interior],
        grid_range[interior:-interior],
        indexing="ij",
    )
    r_sq = (Xf**2 + Yf**2 + Zf**2).ravel()
    grid_shape = (grid_size, grid_size, grid_size)
    return grid_points, grid_shape, r_sq, slice(interior, -interior)


def compute_a_mu_for_file(
    path, grid_size=32, spacing=0.1, interior=8
) -> HelicityResult:
    """
    Compute a_mu, Hc, Hm from a .fseries file. Returns HelicityResult (unpackable as a_mu, Hc, Hm).

    Raises a clear error if the file has no valid .fseries blocks.
    """
    if parse_fseries_multi is None or eval_fourier_block is None:
        raise RuntimeError("sst_helicity: fseries_compat (parse_fseries_multi, eval_fourier_block) not available")
    blocks = parse_fseries_multi(path)
    if not blocks:
        raise ValueError(f"No valid .fseries blocks in file: {path}")
    # Filter blocks that have coeffs with a_x
    valid_blocks = [
        b
        for b in blocks
        if isinstance(b, (tuple, list))
        and len(b) >= 2
        and isinstance(b[1], dict)
        and "a_x" in b[1]
        and hasattr(b[1]["a_x"], "size")
        and b[1]["a_x"].size > 0
    ]
    if not valid_blocks:
        raise ValueError(f"No valid .fseries blocks (with a_x coefficients) in file: {path}")
    header, coeffs = max(valid_blocks, key=lambda b: b[1]["a_x"].size)
    s = np.linspace(0, 2 * np.pi, 1000, endpoint=False)
    x, y, z = eval_fourier_block(coeffs, s)
    gp, gs, r2, inner = helicity_at(grid_size, spacing, interior)
    vel = compute_biot_savart_velocity(x, y, z, gp)
    vort = compute_vorticity_full_grid(vel, gs, spacing)
    v_sub = extract_interior_field(vel, gs, inner)
    w_sub = extract_interior_field(vort, gs, inner)
    Hc = np.einsum("ij,ij->", v_sub, w_sub)
    Hm = np.sum(np.linalg.norm(w_sub, axis=1) ** 2 * r2)
    a_mu = 0.5 * (Hc / Hm - 1.0)
    return HelicityResult(a_mu=a_mu, Hc=float(Hc), Hm=float(Hm))


def base_id(fname):
    """Extract base knot ID from filename (e.g. knot.4_1.fseries -> 4_1)."""
    s = os.path.basename(fname).replace("knot.", "").replace(".fseries", "")
    m = re.match(r"(\d+(?:a|n)?_\d+|15331)", s)
    return m.group(1) if m else s


# --- Self-check when run as script ---
if __name__ == "__main__":
    import sys

    ok = 0
    try:
        import sst_helicity as m
        ok += 1
        assert hasattr(m, "compute_a_mu_for_file")
        assert hasattr(m, "helicity_at")
        assert hasattr(m, "HelicityResult")
        # Unpacking
        r = m.HelicityResult(0.0, 1.0, 2.0)
        a, b, c = r
        assert (a, b, c) == (0.0, 1.0, 2.0)
        print("sst_helicity: import and API OK")
    except Exception as e:
        print("sst_helicity:", e)
        sys.exit(1)
    try:
        import HelicityCalculationVAMcore as leg
        ok += 1
        assert hasattr(leg, "compute_a_mu_for_file")
        print("HelicityCalculationVAMcore: import and compute_a_mu_for_file OK")
    except Exception as e:
        print("HelicityCalculationVAMcore:", e)
    sys.exit(0 if ok >= 1 else 1)
