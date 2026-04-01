#!/usr/bin/env python3
# Refactor: use SSTcore PyBind11 bindings for Fourier eval, Biot–Savart, and curl
# Bindings used:
#   fourier_knot_eval(a_x,b_x,a_y,b_y,a_z,b_z, s)     ← ./src_bindings/py_fourier_knot.cpp
#   biot_savart_velocity_grid(polyline[N,3], grid[G,3]) ← ./src_bindings/py_biot_savart.cpp
#   curl3d_central(vel[Nx,Ny,Nz,3], spacing)           ← ./src_bindings/py_field_ops.cpp
# For the usages of .fseries in the Canon papers, see the source of the files https://david.fremlin.de/knots/index.htm.
# % lines a_x(j) b_x(j) a_y(j) b_y(j) a_z(j) b_z(j)
# % corresponding to x(s) = sum a_x(j)cos(js)+b_x(j)sin(js) etc

import os, glob, re
import numpy as np
import pandas as pd
from sst_exports import get_exports_dir

# --- SSTCORE bindings (with safe fallbacks if module is missing) ---
try:
    import swirl_string_core as sstcore
except ImportError:
    try:
        import sstbindings as sstcore
    except ImportError:
        sstcore = None
try:
    from sstcore import biot_savart_velocity_grid, curl3d_central
    HAVE_SST = True
except Exception:
    HAVE_SST = False

from fseries_compat import parse_fseries_multi, eval_fourier_block

# ---------------------------
# Biot–Savart on arbitrary points (SST)
# ---------------------------
def compute_biot_savart_velocity(x, y, z, grid_points):
    if HAVE_SST:
        poly = np.stack([x,y,z], axis=1).astype(float)
        return biot_savart_velocity_grid(poly, grid_points.astype(float))
    # fallback: midpoint rule
    N = len(x); velocity = np.zeros_like(grid_points, dtype=float)
    for i in range(N):
        r0 = np.array([x[i], y[i], z[i]], dtype=float)
        r1 = np.array([x[(i+1)%N], y[(i+1)%N], z[(i+1)%N]], dtype=float)
        dl = r1 - r0
        r_mid = 0.5 * (r0 + r1)
        R = grid_points - r_mid
        invR3 = 1.0 / (np.linalg.norm(R, axis=1)**3 + 1e-18)
        velocity += np.cross(dl, R) * invR3[:, None]
    return velocity * (1.0 / (4.0*np.pi))

# ---------------------------
# Curl on grid (SST)
# ---------------------------
def compute_vorticity_full_grid(velocity, shape, spacing):
    if HAVE_SST:
        vel3 = velocity.reshape(*shape, 3).astype(float)
        curl3 = curl3d_central(vel3, float(spacing))
        return np.asarray(curl3).reshape(-1, 3)
    # fallback: periodic central differences
    vx = velocity[:, 0].reshape(shape)
    vy = velocity[:, 1].reshape(shape)
    vz = velocity[:, 2].reshape(shape)
    h2 = 2*spacing
    curl_x = (np.roll(vz,-1,1)-np.roll(vz,1,1))/h2 - (np.roll(vy,-1,2)-np.roll(vy,1,2))/h2
    curl_y = (np.roll(vx,-1,2)-np.roll(vx,1,2))/h2 - (np.roll(vz,-1,0)-np.roll(vz,1,0))/h2
    curl_z = (np.roll(vy,-1,0)-np.roll(vy,1,0))/h2 - (np.roll(vx,-1,1)-np.roll(vx,1,1))/h2
    return np.stack([curl_x, curl_y, curl_z], axis=-1).reshape(-1, 3)

# ---------------------------
# Utilities
# ---------------------------
def extract_interior_field(field, shape, interior_slice):
    return field.reshape(*shape, 3)[interior_slice, :, :][:, interior_slice, :][:, :, interior_slice].reshape(-1, 3)

def helicity_at(grid_size=32, spacing=0.1, interior=8):
    grid_range = spacing * (np.arange(grid_size) - grid_size // 2)
    X, Y, Z = np.meshgrid(grid_range, grid_range, grid_range, indexing='ij')
    grid_points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=-1)
    Xf, Yf, Zf = np.meshgrid(grid_range[interior:-interior],
                             grid_range[interior:-interior],
                             grid_range[interior:-interior], indexing='ij')
    r_sq = (Xf**2 + Yf**2 + Zf**2).ravel()
    grid_shape = (grid_size, grid_size, grid_size)
    return grid_points, grid_shape, r_sq, slice(interior, -interior)

def compute_a_mu_for_file(path, grid_size=32, spacing=0.1, interior=8):
    blocks = parse_fseries_multi(path)
    header, coeffs = max(blocks, key=lambda b: b[1]['a_x'].size)
    s = np.linspace(0, 2*np.pi, 1000, endpoint=False)
    x, y, z = eval_fourier_block(coeffs, s)
    gp, gs, r2, inner = helicity_at(grid_size, spacing, interior)
    vel  = compute_biot_savart_velocity(x, y, z, gp)
    vort = compute_vorticity_full_grid(vel, gs, spacing)
    v_sub = extract_interior_field(vel,  gs, inner)
    w_sub = extract_interior_field(vort, gs, inner)
    Hc = np.einsum('ij,ij->', v_sub, w_sub)
    Hm = np.sum(np.linalg.norm(w_sub, axis=1)**2 * r2)
    return 0.5 * (Hc / Hm - 1.0), Hc, Hm

def base_id(fname):
    s = os.path.basename(fname).replace("knot.", "").replace(".fseries", "")
    m = re.match(r"(\d+(?:a|n)?_\d+|15331)", s)
    return m.group(1) if m else s

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    # Setup grid
    grid_size = 32
    spacing   = 0.1
    interior  = slice(8, -8)
    grid_range = spacing * (np.arange(grid_size) - grid_size // 2)
    X, Y, Z = np.meshgrid(grid_range, grid_range, grid_range, indexing='ij')
    grid_points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=-1)
    Xf, Yf, Zf = np.meshgrid(grid_range[interior], grid_range[interior], grid_range[interior], indexing='ij')
    r_sq = (Xf**2 + Yf**2 + Zf**2).ravel()
    grid_shape = (grid_size, grid_size, grid_size)

    paths = sorted(glob.glob("./Knots_FourierSeries/**/*.fseries", recursive=True))
    print("\n=== Compute against another ===")
    for path in paths:
        print(f"========== {os.path.basename(path)} ============")
        for (G,S,I) in [(32,0.1,8),(48,0.08,12),(64,0.06,16)]:
            a_mu, Hc, Hm = compute_a_mu_for_file(path, G, S, I)
            print(f"{os.path.basename(path)}:  a_mu({G}) = {a_mu:.8f}   [Hc={Hc:.3e}, Hm={Hm:.3e}]")

    print("\n=== SST Muon Anomaly via Helicity ===")
    rows = []
    for path in paths:
        blocks = parse_fseries_multi(path)
        if not blocks:
            print(f"{path}: [no valid blocks]"); continue
        header, coeffs = max(blocks, key=lambda b: b[1]['a_x'].size)
        x, y, z = eval_fourier_block(coeffs, np.linspace(0, 2*np.pi, 1000, endpoint=False))
        velocity  = compute_biot_savart_velocity(x, y, z, grid_points)
        vorticity = compute_vorticity_full_grid(velocity, grid_shape, spacing)
        v_sub = extract_interior_field(velocity,  grid_shape, interior)
        w_sub = extract_interior_field(vorticity, grid_shape, interior)
        Hc = np.einsum('ij,ij->', v_sub, w_sub)
        Hm = np.sum(np.linalg.norm(w_sub, axis=1)**2 * r_sq)
        a_mu = 0.5 * (Hc / Hm - 1.0)
        print(f"{os.path.basename(path)}:  a_mu^SST = {a_mu:.8f}  [Hc={Hc:.2f}, Hm={Hm:.2f}]")
        rows.append({"file": os.path.basename(path).replace("knot.","").replace(".fseries",""),
                     "base": base_id(path), "a_mu": a_mu, "Hc": Hc, "Hm": Hm})

    AMPHI = {"4_1","6_3","8_3","8_9","8_12","12a_1202","15331"}
    df = pd.DataFrame(rows)

    out_dir = get_exports_dir()
    if df.empty or "base" not in df.columns:
        print("No valid helicity rows found; skipping grouped summary by base.")
        if not df.empty:
            path = out_dir / "SST_helicity_by_file.csv"
            df.to_csv(path, index=False)
            print(f"Wrote {path}")
    else:
        g = df.groupby("base")["a_mu"].agg(["mean","std","count"]).reset_index()
        g["is_amphi"] = g["base"].isin(AMPHI)
        g["flag"] = np.where(
            g["is_amphi"] & (np.abs(g["mean"] + 0.5) > 0.02),
            "WARN(amphi≠−0.5)",
            ""
        )
        path = out_dir / "SST_helicity_by_base.csv"
        g.to_csv(path, index=False)
        print(f"Wrote {path}")