# SST Fourier-Series Batch Processor GUI
# - Auto-scan on startup and when the root folder changes
# - Instant preview on selecting a row
# - Optional column cleanup (drop all-NaN and constant columns) before saving/showing results
#
# Requirements: Python 3.9+, numpy, pandas, tkinter, matplotlib

import os, sys, math, glob, csv, threading, traceback, struct, re
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Matplotlib for preview plots
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from sst_exports import get_exports_dir
except ImportError:
    get_exports_dir = None

# Optional companion tools (best-effort import; GUI degrades gracefully)
try:
    import generate_knot_fseries as _genknot
    HAVE_GENKNOT = True
except Exception:
    HAVE_GENKNOT = False

try:
    import SST_Fseries_GUI_Full as _sst_full
    HAVE_SSTFULL = True
except Exception:
    HAVE_SSTFULL = False

try:
    import sst_helicity as _hel
    HAVE_HELICITY = True
except Exception:
    try:
        import HelicityCalculationVAMcore as _hel
        HAVE_HELICITY = True
    except Exception:
        HAVE_HELICITY = False

# ---------- SST constants (Canon-aligned names; values user-provided) ----------
# House naming:
#   v_swirl  := characteristic swirl speed  (m/s)
#   r_c      := core radius                 (m)
#   rho_f    := effective fluid density     (kg/m^3)
#   rho_E    := swirl energy density        (J/m^3)
#   alpha_fs := fine-structure constant     (dimensionless)
v_swirl = 1_093_845.63         # m/s
r_c     = 1.40897017e-15       # m
rho_f   = 7.0e-7               # kg/m^3
rho_E   = 3.49924562e35        # J/m^3
c       = 299_792_458.0        # m/s
alpha_fs = 7.2973525643e-3     # fine-structure constant (CODATA); = 1/137.035999084...


phi  = (1 + 5**0.5) / 2
phi2 = np.exp(np.arcsinh(0.5))   # asinh, not sinh

# If you want to sanity-check the identity φ = exp(asinh(1/2)), set to True.
DEBUG_CONST_CHECK = False
if DEBUG_CONST_CHECK:
    print("phi", phi, "phi2", phi2, "|diff|", abs(phi - phi2))

# Fixed-point equation: varphi = coth(1.5 * ln(varphi))
def varphi_fixed_point(varphi):
    return 1 / np.tanh(1.5 * np.log(varphi))


VOL_BASELINE_VALUE = 2.029883212819307  # Vol(4_1)

# Derived per-meter coefficients (kg/m)
E_density_fluid = 0.5 * rho_f * v_swirl**2
tube_area = math.pi * r_c**2
# In SST terms, these are "mass per arclength" couplings for two density choices:
#  - K_rhof : uses rho_f via (1/2) rho_f v_swirl^2
#  - K_rhoE : uses rho_E directly (already J/m^3)
K_rhof  = (4/(alpha_fs*phi)) * (E_density_fluid / c**2) * tube_area   # kg/m
K_rhoE  = (4/(alpha_fs*phi)) * (rho_E / c**2) * tube_area             # kg/m

# ---------- Core computations ----------
def load_matrix_fseries(path):
    """Load .fseries coefficients. Pad/truncate to 6 columns, fill missing with 0.0 (not NaN)."""
    rows = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            parts = ln.replace(",", " ").split()
            vals = []
            for x in parts[:6]:
                try:
                    vals.append(float(x))
                except Exception:
                    vals.append(0.0)
            while len(vals) < 6:
                vals.append(0.0)
            rows.append(vals)
    if not rows:
        return np.zeros((0,6), dtype=float)
    arr = np.asarray(rows, dtype=float)
    arr[~np.isfinite(arr)] = 0.0
    return arr

def load_fseries_best_block(path):
    """Parse .fseries into blocks separated by '%' or blank lines.
    Keep only the block with the most rows. Each row must have 6 floats.
    """
    blocks = []
    cur = []
    def flush():
        nonlocal cur, blocks
        if cur:
            arr = np.asarray(cur, dtype=float)
            if arr.ndim == 2 and arr.shape[1] == 6 and np.any(np.abs(arr) > 0):
                blocks.append(arr)
            cur = []

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            ln = raw.strip()
            if not ln or ln.startswith('%'):
                flush()
                continue
            parts = ln.replace(",", " ").split()
            if len(parts) != 6:
                # ignore non-6-length rows entirely (do NOT pad with zeros)
                continue
            try:
                row = [float(p) for p in parts]
            except ValueError:
                continue
            cur.append(row)
    flush()

    if not blocks:
        return np.zeros((0, 6), dtype=float)

    # Choose the densest block (most harmonics)
    return max(blocks, key=lambda a: a.shape[0])


def eval_series(coeffs, t, tol=1e-12):
    """
    Return r(t) and r'(t) from Fourier coefficients.

    Supports BOTH conventions:
      A) row0 is j=0 (constant term present):     x(t)=Σ_{j=0..N-1} a_x(j)cos(jt)+b_x(j)sin(jt)
      B) row0 is j=1 (no constant row provided):  x(t)=Σ_{j=1..N}   a_x(j)cos(jt)+b_x(j)sin(jt)

    coeffs shape: (N,6) with columns [a_x, b_x, a_y, b_y, a_z, b_z]
    """
    if coeffs.size == 0:
        return np.zeros((t.size, 3)), np.zeros((t.size, 3))

    N = coeffs.shape[0]

    Ax, Bx, Ay, By, Az, Bz = [coeffs[:, i].reshape(-1, 1) for i in range(6)]

    # Detect indexing convention:
    # If row0 is truly j=0, its sine coefficients should be ~0 because sin(0*t)=0.
    row0_sine_mag = float(abs(Bx[0, 0]) + abs(By[0, 0]) + abs(Bz[0, 0]))
    uses_j0_row = (row0_sine_mag < tol)

    # n grid: either 0..N-1 (includes constant) or 1..N
    n = (np.arange(0, N, dtype=float) if uses_j0_row else np.arange(1, N + 1, dtype=float)).reshape(-1, 1)

    nt = n * t.reshape(1, -1)
    cos_nt = np.cos(nt)
    sin_nt = np.sin(nt)

    x = (Ax * cos_nt + Bx * sin_nt).sum(axis=0)
    y = (Ay * cos_nt + By * sin_nt).sum(axis=0)
    z = (Az * cos_nt + Bz * sin_nt).sum(axis=0)

    # derivatives: d/dt cos(n t) = -n sin(n t), d/dt sin(n t) =  n cos(n t)
    x_t = ((-n * Ax) * sin_nt + (n * Bx) * cos_nt).sum(axis=0)
    y_t = ((-n * Ay) * sin_nt + (n * By) * cos_nt).sum(axis=0)
    z_t = ((-n * Az) * sin_nt + (n * Bz) * cos_nt).sum(axis=0)

    r = np.stack([x, y, z], axis=1)
    r_t = np.stack([x_t, y_t, z_t], axis=1)
    return r, r_t


def resample_closed_polyline(points, M):
    """Resample a closed polyline to M points, uniformly in arclength."""
    P = np.asarray(points, dtype=float)
    if P.shape[0] < 3:
        raise ValueError("Need at least 3 points in .short")
    # Ensure closed by appending first if not close
    if np.linalg.norm(P[0]-P[-1]) > 1e-12:
        P = np.vstack([P, P[0]])
    seg = P[1:] - P[:-1]
    seglen = np.linalg.norm(seg, axis=1)
    s = np.concatenate([[0.0], np.cumsum(seglen)])
    L = s[-1]
    if L <= 0:
        raise ValueError("Zero length polyline")
    u = np.linspace(0, L, M+1)[:-1]  # M points, periodic
    r = np.empty((M,3), dtype=float)
    j = 0
    for i,ui in enumerate(u):
        while j+1 < s.size and ui > s[j+1]:
            j += 1
        if j >= seg.shape[0]:
            j = seg.shape[0]-1
        t = (ui - s[j]) / (seglen[j] if seglen[j] > 0 else 1.0)
        r[i] = P[j] + t * seg[j]
    return r

def derivatives_from_uniform_samples(r):
    """Central-difference derivative r'(t) assuming uniform t-grid on [0,2pi)."""
    M = r.shape[0]
    dt = 2*math.pi / M
    rp = np.roll(r, -1, axis=0)
    rm = np.roll(r, 1, axis=0)
    r_t = (rp - rm) / (2*dt)
    return r_t, dt

def writhe_gauss(r, r_t, dt, maxM=500):
    """Discretized Gauss integral. Costs O(M^2); downsample to maxM points."""
    M = r.shape[0]
    if M > maxM:
        idx = np.linspace(0, M-1, maxM, dtype=int)
        r = r[idx]; r_t = r_t[idx]
        M = maxM
        dt = 2*math.pi / M
    Ri = r[:,None,:]; Rj = r[None,:,:]
    dR = Ri - Rj
    dist = np.linalg.norm(dR, axis=2)
    mask = dist > 1e-6
    Ti = r_t[:,None,:]; Tj = r_t[None,:,:]
    cross = np.cross(Ti, Tj)
    num = (cross * dR).sum(axis=2)
    kernel = np.zeros_like(num)
    kernel[mask] = num[mask] / (dist[mask]**3)
    Wr = (dt*dt) * kernel.sum() / (4*math.pi)
    return float(Wr)

def random_unit_vectors(k, seed=12345):
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(k,3))
    v /= np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
    return v

def estimate_crossing_number(r, directions=24, maxM=280, seed=12345):
    """Projection-based crossing estimator. Downsample to maxM for speed."""
    M = r.shape[0]
    if M > maxM:
        idx = np.linspace(0, M-1, maxM, dtype=int)
        r = r[idx]
        M = maxM
    P = r
    Q = np.roll(r, -1, axis=0)
    min_cross = None
    for d in random_unit_vectors(directions, seed=seed):
        w = d / (np.linalg.norm(d) + 1e-12)
        tmp = np.array([1.0,0.0,0.0])
        if abs(np.dot(tmp,w)) > 0.9:
            tmp = np.array([0.0,1.0,0.0])
        u = np.cross(w, tmp); u /= np.linalg.norm(u) + 1e-12
        v = np.cross(w, u)
        P2 = np.stack([P@u, P@v], axis=1)
        Q2 = np.stack([Q@u, Q@v], axis=1)
        count = 0
        for i in range(M):
            p1, p2 = P2[i], Q2[i]
            pminx, pmaxx = min(p1[0], p2[0]), max(p1[0], p2[0])
            pminy, pmaxy = min(p1[1], p2[1]), max(p1[1], p2[1])
            for j in range(i+2, M):
                if j == (i-1) % M:
                    continue
                q1, q2 = P2[j], Q2[j]
                if (pmaxx < min(q1[0], q2[0]) or max(q1[0], q2[0]) < pminx or
                    pmaxy < min(q1[1], q2[1]) or max(q1[1], q2[1]) < pminy):
                    continue
                def orient(a,b,c):
                    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
                o1 = orient(p1,p2,q1); o2 = orient(p1,p2,q2)
                o3 = orient(q1,q2,p1); o4 = orient(q1,q2,p2)
                if (o1==0 and o2==0 and o3==0 and o4==0):
                    continue
                if (o1*o2<0) and (o3*o4<0):
                    count += 1
        if (min_cross is None) or (count < min_cross):
            min_cross = count
    return int(min_cross if min_cross is not None else 0)

def parse_knot_id_from_filename(fname):
    base = os.path.basename(fname)
    name = os.path.splitext(base)[0]
    parts = name.split(".")
    for p in parts[::-1]:
        if "_" in p:
            return p
    return name


def parse_crossing_true_from_knot_id(knot_id: str):
    """Parse crossing number from IDs like '10_1', '9_2d', '7_2p', '4_1z'."""
    if not knot_id:
        return None
    m = re.match(r"^\s*(\d+)\s*_", str(knot_id))
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None

# --- STL loader (ASCII or binary; minimal) ---
def load_stl(path, max_tris=200000):
    with open(path, "rb") as f:
        head = f.read(80)
        rest = f.read()
    # Try binary STL
    if len(rest) >= 4:
        num_tris = struct.unpack("<I", rest[:4])[0]
        expected = 4 + num_tris*50
        if len(rest) >= expected:
            tris = []
            off = 4
            n = min(num_tris, max_tris)
            for _ in range(n):
                chunk = rest[off:off+50]
                if len(chunk) < 50:
                    break
                data = struct.unpack("<12fH", chunk)
                v1 = data[3:6]; v2 = data[6:9]; v3 = data[9:12]
                tris.append([v1, v2, v3])
                off += 50
            return np.array(tris, dtype=float)  # (T,3,3)
    # Fallback: ASCII STL
    try:
        text = (head + rest).decode("utf-8", errors="ignore")
    except Exception:
        text = ""
    verts = []
    for line in text.splitlines():
        line = line.strip().lower()
        if line.startswith("vertex"):
            parts = line.split()
            if len(parts) >= 4:
                try:
                    x,y,z = float(parts[1]), float(parts[2]), float(parts[3])
                    verts.append((x,y,z))
                except Exception:
                    pass
    tris = []
    for i in range(0, len(verts), 3):
        tris.append(verts[i:i+3])
    if tris:
        return np.array(tris, dtype=float)
    raise ValueError("Failed to parse STL (binary or ASCII)")

# ---------- Batch engine ----------
def run_batch(root_dir, out_csv, scale=1.0, xi=1.0, b0=3.0, samples=1500,
              wr_maxM=520, cr_dirs=28, cr_maxM=260,
              sigma_mode="meta", h_mode="auto",
              meta_csv="", wr_tol=5e-3, emit_meta_path=""):
    # Recursively find *.fseries and *.short
    files = sorted(glob.glob(os.path.join(root_dir, "**", "*.fseries"), recursive=True))
    files += sorted(glob.glob(os.path.join(root_dir, "**", "*.short"), recursive=True))
    if not files:
        raise RuntimeError(f"No .fseries or .short files found under: {root_dir}")

    # Emit meta skeleton if requested
    if emit_meta_path:
        ids = discover_ids(files)
        with open(emit_meta_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["knot_id","chiral","sigma","type","hyperbolic_volume"])
            for kid in ids:
                w.writerow([kid, "", "", "", ""])

    # Load meta if provided
    meta = None
    if meta_csv and os.path.exists(meta_csv):
        meta = pd.read_csv(meta_csv)
        meta_cols = {c.lower():c for c in meta.columns}
        def col(name):
            key = name.lower()
            return meta[meta_cols[key]] if key in meta_cols else None
        std = pd.DataFrame()
        std["knot_id"] = col("knot_id").astype(str) if col("knot_id") is not None else ""
        std["chiral"] = col("chiral").astype(str).str.lower() if col("chiral") is not None else ""
        std["sigma"] = col("sigma") if col("sigma") is not None else np.nan
        std["type"] = col("type") if col("type") is not None else ""
        std["hyperbolic_volume"] = col("hyperbolic_volume") if col("hyperbolic_volume") is not None else np.nan
        meta = std.set_index("knot_id")

    rows = []
    root_abs = os.path.abspath(root_dir)

    for path in files:
        ext = os.path.splitext(path)[1].lower()
        relpath = os.path.relpath(path, root_abs)
        knot_id = parse_knot_id_from_filename(path)
        crossing_true = parse_crossing_true_from_knot_id(knot_id)

        # Evaluate r(t), r'(t)
        closure_true = np.nan
        closure_input = np.nan
        if ext == ".fseries":
            t = np.linspace(0, 2*math.pi, samples, endpoint=False)
            coeffs = load_fseries_best_block(path)
            r, r_t = eval_series(coeffs, t)
            dt = 2*math.pi / samples
            try:
                r_ep, _ = eval_series(coeffs, np.array([0.0, 2*math.pi], dtype=float))
                closure_true = float(np.linalg.norm(r_ep[0] - r_ep[1]))
            except Exception:
                closure_true = np.nan
        elif ext == ".short":
            points = []
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln:
                        continue
                    try:
                        xyz = [float(x) for x in ln.replace(",", " ").split()[:3]]
                        if len(xyz) == 3:
                            points.append(xyz)
                    except Exception:
                        pass
            if len(points) < 3:
                # skip file
                print(f"Skipping {relpath}: not enough points")
                continue
            try:
                p0 = np.asarray(points[0], dtype=float)
                pn = np.asarray(points[-1], dtype=float)
                closure_input = float(np.linalg.norm(p0 - pn))
            except Exception:
                closure_input = np.nan
            r = resample_closed_polyline(points, samples)
            r_t, dt = derivatives_from_uniform_samples(r)
        else:
            continue  # ignore other types here

        end_step = float(np.linalg.norm(r[0]-r[-1]))
        # polygonal length proxy in series units
        L_series = float(np.sum(np.linalg.norm(np.roll(r, -1, axis=0)-r, axis=1)))
        Wr = writhe_gauss(r, r_t, dt, maxM=wr_maxM)
        cr_est = estimate_crossing_number(r, directions=cr_dirs, maxM=cr_maxM)

        sigma_meta = np.nan; chiral_meta = ""; vol_meta = np.nan; type_meta = ""
        if meta is not None and knot_id in meta.index:
            rowm = meta.loc[knot_id]
            chiral_meta = str(rowm.get("chiral",""))
            type_meta = str(rowm.get("type",""))
            try:
                sigma_meta = float(rowm.get("sigma", np.nan))
            except Exception:
                sigma_meta = np.nan
            try:
                vol_meta = float(rowm.get("hyperbolic_volume", np.nan))
            except Exception:
                vol_meta = np.nan

        if sigma_mode == "meta":
            if isinstance(sigma_meta, float) and np.isnan(sigma_meta):
                sigma = 0.0 if abs(Wr) <= wr_tol else (1.0 if Wr>0 else -1.0)
                sigma_source = "writhe_fallback"
            else:
                try:
                    sigma = float(sigma_meta)
                except Exception:
                    sigma = 0.0 if abs(Wr) <= wr_tol else (1.0 if Wr>0 else -1.0)
                    sigma_source = "writhe_fallback"
                else:
                    sigma_source = "meta"
        else:
            sigma = 0.0 if abs(Wr) <= wr_tol else (1.0 if Wr>0 else -1.0)
            sigma_source = "writhe"

        HvX_est = sigma * max(cr_est - b0, 0.0)  # dimensionless swirl-helicity proxy (crossing-based)
        HvX_id = np.nan
        if crossing_true is not None:
            HvX_id = sigma * max(float(crossing_true) - b0, 0.0)

        h_mode_norm = str(h_mode).strip().lower()
        if h_mode_norm not in ("auto", "id", "est"):
            h_mode_norm = "auto"

        if h_mode_norm == "est":
            HvX = HvX_est
            H_source = "crossing_est"
        elif h_mode_norm == "id":
            if crossing_true is not None:
                HvX = float(HvX_id)
                H_source = "knot_id"
            else:
                HvX = HvX_est
                H_source = "crossing_est_fallback"
        else:
            if crossing_true is not None:
                HvX = float(HvX_id)
                H_source = "knot_id"
            else:
                HvX = HvX_est
                H_source = "crossing_est"

        HvVol = np.nan
        if not np.isnan(vol_meta) and sigma != 0.0:
            HvVol = sigma * (vol_meta / VOL_BASELINE_VALUE)

        # Physical scaling
        L_phys = scale * L_series
        H_used = HvX if np.isnan(HvVol) else HvVol
        M_rhof  = xi * H_used * K_rhof * L_phys
        M_rhoE  = xi * H_used * K_rhoE * L_phys

        rows.append({
            "file": os.path.basename(path),
            "relative_path": relpath,
            "ext": ext,
            "knot_id": knot_id,
            "closure_error": end_step,
            "end_step": end_step,
            "closure_true": closure_true,
            "closure_input": closure_input,
            "length_series_units": L_series,
            "scale_m_per_unit": scale,
            "length_m": L_phys,
            "writhe": Wr,
            "crossing_est": int(cr_est),
            "crossing_true": (int(crossing_true) if crossing_true is not None else np.nan),
            "sigma": sigma,
            "sigma_source": sigma_source,
            "H_source": H_source,
            "Hswirl_Xest(b0={:.0f})".format(b0): HvX_est,
            "Hswirl_Xid(b0={:.0f})".format(b0): HvX_id,
            "Hswirl_X(b0={:.0f})".format(b0): HvX,
            "hyperbolic_volume_meta": vol_meta,
            "Hswirl_Vol(Vol/Vol(4_1))": HvVol,
            "xi": xi,
            "K_rhof_kg_per_m": K_rhof,
            "K_rhoE_kg_per_m": K_rhoE,
            "mass_rhof_kg": M_rhof,
            "mass_rhoE_kg": M_rhoE,
            "type_meta": type_meta,
            "chiral_meta": chiral_meta,
        })

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    return df

# DataFrame cleaning
def clean_dataframe(df: pd.DataFrame):
    # Drop all-NaN columns
    df2 = df.dropna(axis=1, how="all").copy()

    # Identify constant columns (single unique value or all values equal ignoring NaN)
    keep_cols = {"file","relative_path","ext","knot_id"}  # always keep identifiers
    const_cols = []
    for col in df2.columns:
        if col in keep_cols:
            continue
        series = df2[col]
        # consider NaNs equal by dropping them first
        vals = series.dropna().unique()
        if len(vals) <= 1:
            const_cols.append(col)

    if const_cols:
        df2 = df2.drop(columns=const_cols)

    return df2

# Quick single-file preview helper (lightweight)
def quick_preview_any(path, profile, b0=3.0, wr_tol=5e-3):
    ext = os.path.splitext(path)[1].lower()
    prof = profile
    closure_true = np.nan
    closure_input = np.nan
    if ext == ".fseries":
        coeffs = load_fseries_best_block(path)
        if coeffs.size == 0:
            raise RuntimeError("Empty .fseries")
        t = np.linspace(0, 2*math.pi, prof["samples"], endpoint=False)
        r, r_t = eval_series(coeffs, t)
        dt = 2*math.pi / prof["samples"]
        try:
            r_ep, _ = eval_series(coeffs, np.array([0.0, 2*math.pi], dtype=float))
            closure_true = float(np.linalg.norm(r_ep[0] - r_ep[1]))
        except Exception:
            closure_true = np.nan
    elif ext == ".short":
        pts = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    xyz = [float(x) for x in ln.replace(",", " ").split()[:3]]
                    if len(xyz) == 3:
                        pts.append(xyz)
                except Exception:
                    pass
        if len(pts) < 3:
            raise RuntimeError("Not enough points in .short")
        try:
            p0 = np.asarray(pts[0], dtype=float)
            pn = np.asarray(pts[-1], dtype=float)
            closure_input = float(np.linalg.norm(p0 - pn))
        except Exception:
            closure_input = np.nan
        r = resample_closed_polyline(pts, prof["samples"])
        r_t, dt = derivatives_from_uniform_samples(r)
    elif ext == ".stl":
        tris = load_stl(path)
        return {"stl_tris": tris.shape[0]}
    else:
        raise RuntimeError(f"Unsupported extension: {ext}")

    if not np.all(np.isfinite(r)):
        raise RuntimeError("Non-finite coordinates (check coefficients/points)")

    end_step = float(np.linalg.norm(r[0]-r[-1]))
    L_series = float(np.sum(np.linalg.norm(np.roll(r, -1, axis=0)-r, axis=1)))
    Wr = writhe_gauss(r, r_t, dt, maxM=prof["wr_maxM"])
    cr_est = estimate_crossing_number(r, directions=prof["cr_dirs"], maxM=prof["cr_maxM"])
    sigma_est = 0.0 if abs(Wr) <= wr_tol else (1.0 if Wr>0 else -1.0)
    HvX = sigma_est * max(cr_est - b0, 0.0)
    return {
        "closure_error": end_step,
        "end_step": end_step,
        "closure_true": closure_true,
        "closure_input": closure_input,
        "length_series_units": L_series,
        "writhe": Wr,
        "crossing_est": int(cr_est),
        "sigma_from_writhe": sigma_est,
        "Hswirl_X_est(b0={:.0f})".format(b0): HvX,
        "r": r, "r_t": r_t
    }

# Quick status check for scan
def quick_status(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".fseries":
            coeffs = load_fseries_best_block(path)
            if coeffs.size == 0:
                return "empty_fseries"
            if not np.any(np.abs(coeffs) > 0):
                return "all_zero_coeffs"
            return "ok"
        elif ext == ".short":
            pts = []
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln:
                        continue
                    parts = ln.replace(",", " ").split()
                    if len(parts) >= 3:
                        try:
                            x,y,z = float(parts[0]), float(parts[1]), float(parts[2])
                            pts.append((x,y,z))
                        except Exception:
                            pass
            if len(pts) < 3:
                return "insufficient_points"
            P = np.asarray(pts, dtype=float)
            if not np.all(np.isfinite(P)):
                return "nonfinite_points"
            return "ok"
        elif ext == ".stl":
            base = os.path.splitext(path)[0]
            sib = None
            for cand_ext in (".short", ".fseries"):
                cand = base + cand_ext
                if os.path.exists(cand):
                    sib = cand; break
            return "stl_curve_ok" if sib else "stl_no_sibling_curve"
        else:
            return "ignored"
    except Exception as e:
        return f"error:{type(e).__name__}"

# ---------- GUI ----------
QUALITY_PROFILES = {
    "Ultra Fast": dict(samples=600,  wr_maxM=240, cr_dirs=10, cr_maxM=160),
    "Fast":       dict(samples=900,  wr_maxM=360, cr_dirs=14, cr_maxM=200),
    "Balanced":   dict(samples=1500, wr_maxM=520, cr_dirs=28, cr_maxM=260),
    "High Quality": dict(samples=2400, wr_maxM=700, cr_dirs=48, cr_maxM=360),
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SST Fourier-Series Processor")
        self.geometry("1320x880")
        self.resizable(True, True)

        # Defaults: data root under CWD; output CSVs in exports if available
        default_root = os.path.join(os.getcwd(), "Knots_FourierSeries")
        _exp = get_exports_dir() if get_exports_dir else None
        _out_dir = str(_exp) if _exp else default_root
        default_out = os.path.join(_out_dir, "fseries_batch_results.csv")
        default_meta = os.path.join(_out_dir, "knot_meta.csv")
        default_emit = os.path.join(_out_dir, "knot_meta_skeleton.csv")

        # Variables
        self.var_root = tk.StringVar(value=default_root)
        self.var_out = tk.StringVar(value=default_out)
        self.var_meta = tk.StringVar(value=default_meta)
        self.var_emit_meta = tk.StringVar(value=default_emit)

        self.var_scale = tk.DoubleVar(value=1.0)
        self.var_xi = tk.DoubleVar(value=1.0)
        self.var_b0 = tk.DoubleVar(value=3.0)
        self.var_samples = tk.IntVar(value=1500)
        self.var_wr_maxM = tk.IntVar(value=520)
        self.var_cr_dirs = tk.IntVar(value=28)
        self.var_cr_maxM = tk.IntVar(value=260)
        self.var_wr_tol = tk.DoubleVar(value=5e-3)
        self.var_sigma_mode = tk.StringVar(value="meta")  # 'meta' or 'writhe'
        self.var_h_mode = tk.StringVar(value="auto")      # 'auto', 'est', 'id'
        self.var_quality = tk.StringVar(value="Balanced")
        self.var_plot_preview = tk.BooleanVar(value=True)
        self.var_clean_cols = tk.BooleanVar(value=True)  # drop all-NaN & constants

        # Generator tab vars
        self.var_ideal_path = tk.StringVar(value="")
        self.var_gen_outdir = tk.StringVar(value=_out_dir)
        self.var_gen_name = tk.StringVar(value="knot.custom")
        self.var_gen_abid = tk.StringVar(value="")
        self.var_gen_jmax = tk.IntVar(value=12)
        self.var_gen_samples = tk.IntVar(value=2048)
        self.var_gen_relax_iters = tk.IntVar(value=600)
        self.var_gen_insert_j0 = tk.BooleanVar(value=True)

        # Helicity tab vars
        self.var_h_grid = tk.IntVar(value=48)
        self.var_h_spacing = tk.DoubleVar(value=0.08)
        self.var_h_interior = tk.IntVar(value=12)
        self.var_h_export_csv = tk.StringVar(value=os.path.join(_out_dir, "SST_helicity_gui.csv") if _exp else os.path.join(os.getcwd(), "SST_helicity_gui.csv"))

        self.last_df = None  # store last results dataframe
        self._scan_after_id = None  # debounce id

        # Build UI
        self._build_widgets()

        # Bind root changes to auto-rescan (debounced)
        self.var_root.trace_add("write", self._on_root_change)

        # Auto-scan on boot
        self.after(200, self.on_scan)

    def _build_widgets(self):
        pad = {'padx': 6, 'pady': 4}

        # Paths frame
        frm_paths = ttk.LabelFrame(self, text="Paths")
        frm_paths.pack(fill="x", **pad)

        ttk.Label(frm_paths, text="Knot root folder:").grid(row=0, column=0, sticky="w")
        e_root = ttk.Entry(frm_paths, textvariable=self.var_root, width=80)
        e_root.grid(row=0, column=1, sticky="we")
        ttk.Button(frm_paths, text="Browse…", command=self.browse_root).grid(row=0, column=2, sticky="we", padx=4)

        ttk.Label(frm_paths, text="Output CSV:").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm_paths, textvariable=self.var_out, width=80).grid(row=1, column=1, sticky="we")
        ttk.Button(frm_paths, text="Save As…", command=self.browse_out).grid(row=1, column=2, sticky="we", padx=4)

        ttk.Label(frm_paths, text="Meta CSV (optional):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm_paths, textvariable=self.var_meta, width=80).grid(row=2, column=1, sticky="we")
        ttk.Button(frm_paths, text="Browse…", command=self.browse_meta).grid(row=2, column=2, sticky="we", padx=4)

        ttk.Label(frm_paths, text="Emit meta skeleton to (optional):").grid(row=3, column=0, sticky="w")
        ttk.Entry(frm_paths, textvariable=self.var_emit_meta, width=80).grid(row=3, column=1, sticky="we")
        ttk.Button(frm_paths, text="Save As…", command=self.browse_emit_meta).grid(row=3, column=2, sticky="we", padx=4)

        for i in range(3):
            frm_paths.columnconfigure(i, weight=1 if i==1 else 0)

        # Options frame
        frm_opts = ttk.LabelFrame(self, text="Options")
        frm_opts.pack(fill="x", **pad)

        # Row 0
        ttk.Label(frm_opts, text="Quality:").grid(row=0, column=0, sticky="w")
        cmb = ttk.Combobox(frm_opts, textvariable=self.var_quality, state="readonly",
                           values=list(QUALITY_PROFILES.keys()), width=18)
        cmb.grid(row=0, column=1, sticky="w")
        cmb.bind("<<ComboboxSelected>>", self.on_quality_change)

        ttk.Label(frm_opts, text="Scale (m per series unit):").grid(row=0, column=2, sticky="w")
        ttk.Entry(frm_opts, textvariable=self.var_scale, width=10).grid(row=0, column=3, sticky="w")
        ttk.Label(frm_opts, text="ξ (coherence):").grid(row=0, column=4, sticky="w")
        ttk.Entry(frm_opts, textvariable=self.var_xi, width=10).grid(row=0, column=5, sticky="w")

        # Row 1
        ttk.Label(frm_opts, text="b₀ (crossing offset):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm_opts, textvariable=self.var_b0, width=10).grid(row=1, column=1, sticky="w")
        ttk.Label(frm_opts, text="Samples (t-grid):").grid(row=1, column=2, sticky="w")
        ttk.Entry(frm_opts, textvariable=self.var_samples, width=10).grid(row=1, column=3, sticky="w")
        ttk.Label(frm_opts, text="Wr max points:").grid(row=1, column=4, sticky="w")
        ttk.Entry(frm_opts, textvariable=self.var_wr_maxM, width=10).grid(row=1, column=5, sticky="w")

        # Row 2
        ttk.Label(frm_opts, text="Crossing dirs:").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm_opts, textvariable=self.var_cr_dirs, width=10).grid(row=2, column=1, sticky="w")
        ttk.Label(frm_opts, text="Crossing max points:").grid(row=2, column=2, sticky="w")
        ttk.Entry(frm_opts, textvariable=self.var_cr_maxM, width=10).grid(row=2, column=3, sticky="w")
        ttk.Label(frm_opts, text="Wr tolerance:").grid(row=2, column=4, sticky="w")
        ttk.Entry(frm_opts, textvariable=self.var_wr_tol, width=10).grid(row=2, column=5, sticky="w")

        ttk.Checkbutton(frm_opts, text="Plot preview", variable=self.var_plot_preview).grid(row=3, column=0, sticky="w")
        ttk.Checkbutton(
            frm_opts,
            text="Clean columns for display (save full CSV + write *_clean.csv)",
            variable=self.var_clean_cols,
        ).grid(row=3, column=1, columnspan=3, sticky="w")

        ttk.Label(frm_opts, text="σ mode:").grid(row=3, column=4, sticky="e")
        cmb_sigma = ttk.Combobox(frm_opts, textvariable=self.var_sigma_mode, state="readonly",
                                 values=["meta", "writhe"], width=10)
        cmb_sigma.grid(row=3, column=5, sticky="w")

        ttk.Label(frm_opts, text="H mode:").grid(row=4, column=0, sticky="w")
        cmb_h = ttk.Combobox(frm_opts, textvariable=self.var_h_mode, state="readonly",
                             values=["auto", "est", "id"], width=10)
        cmb_h.grid(row=4, column=1, sticky="w")

        for j in range(6):
            frm_opts.columnconfigure(j, weight=1 if j%2==1 else 0)

        # Actions frame
        frm_actions = ttk.LabelFrame(self, text="Actions")
        frm_actions.pack(fill="x", **pad)
        ttk.Button(frm_actions, text="Emit Meta Skeleton", command=self.on_emit_meta).grid(row=0, column=0, padx=4, pady=6, sticky="w")
        ttk.Button(frm_actions, text="Scan for Files", command=self.on_scan).grid(row=0, column=1, padx=4, pady=6, sticky="w")
        # Keep button in case; but instant preview also bound to selection
        ttk.Button(frm_actions, text="Preview Selected", command=self.on_preview_selected).grid(row=0, column=2, padx=4, pady=6, sticky="w")
        ttk.Button(frm_actions, text="Run Batch", command=self.on_run).grid(row=0, column=3, padx=4, pady=6, sticky="w")
        ttk.Button(frm_actions, text="Show Results Window", command=self.on_show_results).grid(row=0, column=4, padx=4, pady=6, sticky="w")

        self.progress = ttk.Progressbar(frm_actions, mode="indeterminate")
        self.progress.grid(row=0, column=5, padx=8, pady=6, sticky="we")
        frm_actions.columnconfigure(5, weight=1)

        # Split pane: left file list, right preview/log
        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, **pad)

        # Left: file list with status
        frm_left = ttk.LabelFrame(paned, text="Discovered files")
        self.tree = ttk.Treeview(frm_left, columns=("ext","knot_id","relpath","status"), show="headings", height=20)
        for col, text, w in (("ext","ext",60), ("knot_id","knot_id",120), ("relpath","relative path",640), ("status","status",160)):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="w")
        vsb = ttk.Scrollbar(frm_left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.tag_configure("status_err", foreground="red")
        self.tree.tag_configure("status_warn", foreground="orange")
        self.tree.tag_configure("status_ok", foreground="gray20")
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        paned.add(frm_left, weight=2)

        # Instant preview on selection
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Right: notebook with multiple functional tabs
        frm_right = ttk.LabelFrame(paned, text="Tools")
        nb = ttk.Notebook(frm_right)
        nb.pack(fill="both", expand=True)

        # --- Tab 1: Preview & Log ---
        tab_preview = ttk.Frame(nb)
        nb.add(tab_preview, text="Preview")

        self.fig = Figure(figsize=(5,4), dpi=100)
        self.ax3d = self.fig.add_subplot(111, projection="3d")
        self.ax3d.set_xlabel("X"); self.ax3d.set_ylabel("Y"); self.ax3d.set_zlabel("Z")
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab_preview)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        self.txt = tk.Text(tab_preview, height=10)
        self.txt.pack(fill="x", expand=False)

        # --- Tab 2: Generator / Relax ---
        tab_gen = ttk.Frame(nb)
        nb.add(tab_gen, text="Generate")
        self._build_generate_tab(tab_gen)

        # --- Tab 3: Helicity / Export ---
        tab_hel = ttk.Frame(nb)
        nb.add(tab_hel, text="Helicity")
        self._build_helicity_tab(tab_hel)

        # --- Tab 4: Utilities / Canonicalize ---
        tab_util = ttk.Frame(nb)
        nb.add(tab_util, text="Utilities")
        self._build_util_tab(tab_util)

        paned.add(frm_right, weight=3)

        # Footer
        footer = ttk.Frame(self)
        footer.pack(fill="x", **pad)
        ttk.Label(footer, text=f"K_rhof={K_rhof:.6e} kg/m,  K_rhoE={K_rhoE:.6e} kg/m").pack(side="left")

        # Apply initial quality
        self.apply_quality_profile(self.var_quality.get())

    # ---- Tabs ----
    def _build_generate_tab(self, parent):
        pad = {'padx': 6, 'pady': 4}
        frm = ttk.LabelFrame(parent, text="Ideal.txt → Relax → .fseries")
        frm.pack(fill="x", **pad)

        ttk.Label(frm, text="Ideal.txt (optional; otherwise auto-download):").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.var_ideal_path, width=70).grid(row=0, column=1, sticky="we")
        ttk.Button(frm, text="Browse…", command=self._browse_ideal).grid(row=0, column=2, padx=4)

        ttk.Label(frm, text="Output folder:").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.var_gen_outdir, width=70).grid(row=1, column=1, sticky="we")
        ttk.Button(frm, text="Browse…", command=self._browse_gen_outdir).grid(row=1, column=2, padx=4)

        ttk.Label(frm, text="AB Id:").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.var_gen_abid, width=16).grid(row=2, column=1, sticky="w")
        ttk.Label(frm, text="Knot name:").grid(row=2, column=2, sticky="w")
        ttk.Entry(frm, textvariable=self.var_gen_name, width=24).grid(row=2, column=3, sticky="w")

        opt = ttk.LabelFrame(parent, text="Generator options")
        opt.pack(fill="x", **pad)
        ttk.Label(opt, text="j_max:").grid(row=0, column=0, sticky="w")
        ttk.Entry(opt, textvariable=self.var_gen_jmax, width=8).grid(row=0, column=1, sticky="w")
        ttk.Label(opt, text="samples:").grid(row=0, column=2, sticky="w")
        ttk.Entry(opt, textvariable=self.var_gen_samples, width=8).grid(row=0, column=3, sticky="w")
        ttk.Label(opt, text="relax iters:").grid(row=0, column=4, sticky="w")
        ttk.Entry(opt, textvariable=self.var_gen_relax_iters, width=8).grid(row=0, column=5, sticky="w")
        ttk.Checkbutton(opt, text="insert j=0 row", variable=self.var_gen_insert_j0).grid(row=1, column=0, columnspan=3, sticky="w")

        btns = ttk.Frame(parent)
        btns.pack(fill="x", **pad)
        ttk.Button(btns, text="Run generator (single)", command=self.on_generate).pack(side="left")
        ttk.Button(btns, text="Generate all knots from catalog", command=self.on_generate_all_catalog).pack(side="left", padx=6)
        ttk.Label(btns, text=f"Gen module: {'OK' if HAVE_GENKNOT else 'missing'}  |  Full GUI module: {'OK' if HAVE_SSTFULL else 'missing'}").pack(side="left", padx=10)

        self.txt_gen = tk.Text(parent, height=12)
        self.txt_gen.pack(fill="both", expand=True, **pad)

    def _build_helicity_tab(self, parent):
        pad = {'padx': 6, 'pady': 4}
        frm = ttk.LabelFrame(parent, text="Compute helicity metrics for selected .fseries")
        frm.pack(fill="x", **pad)

        ttk.Label(frm, text="grid size:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.var_h_grid, width=8).grid(row=0, column=1, sticky="w")
        ttk.Label(frm, text="spacing:").grid(row=0, column=2, sticky="w")
        ttk.Entry(frm, textvariable=self.var_h_spacing, width=8).grid(row=0, column=3, sticky="w")
        ttk.Label(frm, text="interior:").grid(row=0, column=4, sticky="w")
        ttk.Entry(frm, textvariable=self.var_h_interior, width=8).grid(row=0, column=5, sticky="w")

        ttk.Label(frm, text="export CSV:").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.var_h_export_csv, width=70).grid(row=1, column=1, columnspan=4, sticky="we")
        ttk.Button(frm, text="Save As…", command=self._browse_helicity_csv).grid(row=1, column=5, padx=4)

        btns = ttk.Frame(parent)
        btns.pack(fill="x", **pad)
        ttk.Button(btns, text="Compute for selected", command=self.on_helicity_selected).pack(side="left")
        ttk.Button(btns, text="Compute for ALL .fseries in root", command=self.on_helicity_all).pack(side="left", padx=6)
        ttk.Label(btns, text=f"Helicity module: {'OK' if HAVE_HELICITY else 'missing'}").pack(side="left", padx=10)

        self.txt_hel = tk.Text(parent, height=14)
        self.txt_hel.pack(fill="both", expand=True, **pad)

    def _build_util_tab(self, parent):
        pad = {'padx': 6, 'pady': 4}
        frm = ttk.LabelFrame(parent, text="Utilities")
        frm.pack(fill="x", **pad)

        ttk.Label(frm, text="Canonicalize selected .fseries to include explicit j=0 row (recommended for proof runs).")\
            .grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Button(frm, text="Canonicalize selected", command=self.on_canonicalize_selected).grid(row=1, column=0, sticky="w", padx=4, pady=4)
        ttk.Button(frm, text="Canonicalize ALL .fseries in root", command=self.on_canonicalize_all).grid(row=1, column=1, sticky="w", padx=4, pady=4)
        ttk.Label(frm, text="(Writes *_j0.fseries next to original)").grid(row=1, column=2, sticky="w")

        self.txt_util = tk.Text(parent, height=16)
        self.txt_util.pack(fill="both", expand=True, **pad)

    # ---- UI helpers & events ----
    def _on_root_change(self, *_):
        # Debounced auto-scan when root path changes
        if self._scan_after_id is not None:
            try:
                self.after_cancel(self._scan_after_id)
            except Exception:
                pass
            self._scan_after_id = None
        self._scan_after_id = self.after(600, self.on_scan)

    def browse_root(self):
        d = filedialog.askdirectory(title="Select knot root folder", initialdir=self.var_root.get())
        if d:
            self.var_root.set(d)  # triggers auto-scan

    def browse_out(self):
        p = filedialog.asksaveasfilename(title="Save results CSV as", defaultextension=".csv",
                                         filetypes=[("CSV","*.csv"), ("All files","*.*")],
                                         initialdir=self.var_root.get())
        if p:
            self.var_out.set(p)

    def browse_meta(self):
        p = filedialog.askopenfilename(title="Select meta CSV",
                                       filetypes=[("CSV","*.csv"), ("All files","*.*")],
                                       initialdir=self.var_root.get())
        if p:
            self.var_meta.set(p)

    def browse_emit_meta(self):
        p = filedialog.asksaveasfilename(title="Save meta skeleton as", defaultextension=".csv",
                                         filetypes=[("CSV","*.csv"), ("All files","*.*")],
                                         initialdir=self.var_root.get())
        if p:
            self.var_emit_meta.set(p)

    def log(self, msg):
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")
        self.update_idletasks()

    def set_busy(self, busy=True):
        if busy:
            self.progress.start(80)
        else:
            self.progress.stop()

    def on_quality_change(self, _evt=None):
        self.apply_quality_profile(self.var_quality.get())

    def apply_quality_profile(self, name):
        prof = QUALITY_PROFILES.get(name, QUALITY_PROFILES["Balanced"])
        self.var_samples.set(prof["samples"])
        self.var_wr_maxM.set(prof["wr_maxM"])
        self.var_cr_dirs.set(prof["cr_dirs"])
        self.var_cr_maxM.set(prof["cr_maxM"])
        self.log(f"Quality → {name}: samples={prof['samples']}, wr_maxM={prof['wr_maxM']}, cr_dirs={prof['cr_dirs']}, cr_maxM={prof['cr_maxM']}")

    # ---- Actions ----
    def on_emit_meta(self):
        try:
            root = self.var_root.get().strip()
            emit_path = self.var_emit_meta.get().strip()
            if not root:
                messagebox.showwarning("Missing", "Please select a knot root folder.")
                return
            if not emit_path:
                messagebox.showwarning("Missing", "Please choose where to save the meta skeleton.")
                return
            self.set_busy(True)
            self.log("Scanning for *.fseries / *.short...")
            files = sorted(glob.glob(os.path.join(root, "**", "*.fseries"), recursive=True))
            files += sorted(glob.glob(os.path.join(root, "**", "*.short"), recursive=True))
            if not files:
                self.log("No .fseries or .short files found.")
                messagebox.showinfo("Done", "No .fseries or .short files found.")
                return
            ids = []
            seen = set()
            for p in files:
                kid = parse_knot_id_from_filename(p)
                if kid not in seen:
                    seen.add(kid); ids.append(kid)
            with open(emit_path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["knot_id","chiral","sigma","type","hyperbolic_volume"])
                for kid in ids:
                    w.writerow([kid, "", "", "", ""])
            self.log(f"Wrote meta skeleton: {emit_path}  (ids: {len(ids)})")
            messagebox.showinfo("Done", f"Meta skeleton written:\n{emit_path}\nIDs: {len(ids)}")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed: {e}")
        finally:
            self.set_busy(False)

    def on_scan(self):
        try:
            root = self.var_root.get().strip()
            if not root:
                messagebox.showwarning("Missing", "Please select a knot root folder.")
                return
            self.set_busy(True)
            self.log("Scanning recursively for *.fseries / *.short / *.stl ...")
            files = []
            files += sorted(glob.glob(os.path.join(root, "**", "*.fseries"), recursive=True))
            files += sorted(glob.glob(os.path.join(root, "**", "*.short"), recursive=True))
            files += sorted(glob.glob(os.path.join(root, "**", "*.stl"), recursive=True))
            self.tree.delete(*self.tree.get_children())
            root_abs = os.path.abspath(root)
            for p in files:
                rel = os.path.relpath(p, root_abs)
                kid = parse_knot_id_from_filename(p)
                ext = os.path.splitext(p)[1].lower()
                status = quick_status(p)
                tag = "status_ok"
                if status.startswith("error") or status in ("empty_fseries","insufficient_points","nonfinite_points"):
                    tag = "status_err"
                elif status in ("stl_no_sibling_curve","all_zero_coeffs"):
                    tag = "status_warn"
                self.tree.insert("", "end", values=(ext, kid, rel, status), tags=(tag,))
            self.log(f"Discovered files: {len(files)} (problematic rows are colored)")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Scan failed:\n{e}")
        finally:
            self.set_busy(False)

    def _on_tree_select(self, _evt=None):
        # Instant preview when a row is selected
        self.on_preview_selected()

    def on_preview_selected(self):
        try:
            sel = self.tree.selection()
            if not sel:
                return
            item = self.tree.item(sel[0])
            ext, kid, rel, status = item["values"]
            root = self.var_root.get().strip()
            path = os.path.join(root, rel)
            prof = QUALITY_PROFILES.get(self.var_quality.get(), QUALITY_PROFILES["Balanced"])
            self.set_busy(True)
            self.log(f"Previewing: {rel}  [status={status}]")

            self.ax3d.clear()
            self.ax3d.set_xlabel("X"); self.ax3d.set_ylabel("Y"); self.ax3d.set_zlabel("Z")

            if ext == ".stl":
                tris = load_stl(path)
                for tri in tris[:2000]:
                    X = [tri[0][0], tri[1][0], tri[2][0], tri[0][0]]
                    Y = [tri[0][1], tri[1][1], tri[2][1], tri[0][1]]
                    Z = [tri[0][2], tri[1][2], tri[2][2], tri[0][2]]
                    self.ax3d.plot(X, Y, Z, linewidth=0.5)
                base = os.path.splitext(path)[0]
                sib = None
                for cand_ext in (".short", ".fseries"):
                    cand = base + cand_ext
                    if os.path.exists(cand):
                        sib = cand; break
                if sib:
                    d = quick_preview_any(sib, prof, b0=float(self.var_b0.get()), wr_tol=float(self.var_wr_tol.get()))
                    self.log("---- Preview (from sibling curve) ----")
                    for k in ["closure_error","length_series_units","writhe","crossing_est","sigma_from_writhe"]:
                        if k in d:
                            self.log(f"{k}: {d[k]}")
                else:
                    self.log("No sibling .short/.fseries found for invariants.")
            else:
                d = quick_preview_any(path, prof, b0=float(self.var_b0.get()), wr_tol=float(self.var_wr_tol.get()))
                if self.var_plot_preview.get() and "r" in d:
                    r = d["r"]
                    self.ax3d.plot(r[:,0], r[:,1], r[:,2], linewidth=1.0)
                self.log("---- Preview ----")
                keys = [
                    "closure_true",
                    "closure_input",
                    "end_step",
                    "length_series_units",
                    "writhe",
                    "crossing_est",
                    "sigma_from_writhe",
                    "Hswirl_X_est(b0={:.0f})".format(float(self.var_b0.get())),
                ]
                for k in keys:
                    if k in d:
                        self.log(f"{k}: {d[k]}")

            self.canvas.draw()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Preview failed:\n{e}")
        finally:
            self.set_busy(False)

    def on_run(self):
        threading.Thread(target=self._run_batch_thread, daemon=True).start()

    def _run_batch_thread(self):
        try:
            root = self.var_root.get().strip()
            out_csv = self.var_out.get().strip()
            meta_csv = self.var_meta.get().strip()
            emit_meta = self.var_emit_meta.get().strip()

            if not root:
                messagebox.showwarning("Missing", "Please select a knot root folder.")
                return
            if not out_csv:
                messagebox.showwarning("Missing", "Please choose an output CSV path.")
                return

            kwargs = dict(
                root_dir=root,
                out_csv=out_csv,
                scale=float(self.var_scale.get()),
                xi=float(self.var_xi.get()),
                b0=float(self.var_b0.get()),
                samples=int(self.var_samples.get()),
                wr_maxM=int(self.var_wr_maxM.get()),
                cr_dirs=int(self.var_cr_dirs.get()),
                cr_maxM=int(self.var_cr_maxM.get()),
                sigma_mode=self.var_sigma_mode.get(),
                h_mode=self.var_h_mode.get(),
                meta_csv=meta_csv,
                wr_tol=float(self.var_wr_tol.get()),
                emit_meta_path=emit_meta,
            )

            self.set_busy(True)
            self.log("Starting batch...")
            for k, v in kwargs.items():
                self.log(f"  {k} = {v}")
            df_full = run_batch(**kwargs)

            df_full.to_csv(out_csv, index=False)

            df_show = df_full
            if self.var_clean_cols.get():
                df_show = clean_dataframe(df_full)
                base, ext = os.path.splitext(out_csv)
                out_csv_clean = base + "_clean" + ext
                df_show.to_csv(out_csv_clean, index=False)
                self.log(f"Wrote cleaned results: {out_csv_clean}")

            self.last_df = df_show
            self.log(f"Processed rows (full): {len(df_full)}")
            self.log(f"Wrote full results: {out_csv}")
            if self.var_clean_cols.get():
                base, ext = os.path.splitext(out_csv)
                messagebox.showinfo(
                    "Done",
                    f"Processed rows: {len(df_full)}\nSaved (full): {out_csv}\nSaved (clean): {base}_clean{ext}",
                )
            else:
                messagebox.showinfo("Done", f"Processed rows: {len(df_full)}\nSaved: {out_csv}")
            self.show_results_window(df_show)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Batch failed:\n{e}")
        finally:
            self.set_busy(False)

    def on_show_results(self):
        if self.last_df is None:
            out_csv = self.var_out.get().strip()
            if os.path.exists(out_csv):
                try:
                    df = pd.read_csv(out_csv)
                    self.last_df = df
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load results CSV:\n{e}")
                    return
            else:
                messagebox.showinfo("Results", "No results to show yet.")
                return
        self.show_results_window(self.last_df)

    def show_results_window(self, df: pd.DataFrame):
        # NOTE: this window shows the batch processor output. Additional tools (Generate/Helicity)
        # have their own export paths and logs in their dedicated tabs.
        top = tk.Toplevel(self)
        top.title("Batch Results")
        top.geometry("1200x600")

        # Toolbar
        bar = ttk.Frame(top)
        bar.pack(fill="x")
        ttk.Button(bar, text="Save As…", command=lambda: self.save_df_as(df)).pack(side="left", padx=4, pady=4)
        ttk.Button(bar, text="Close", command=top.destroy).pack(side="right", padx=4, pady=4)

        # Table
        cols = list(df.columns)
        tree = ttk.Treeview(top, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=140, anchor="w")
        vsb = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(top, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        max_rows = 5000
        data = df.head(max_rows).itertuples(index=False, name=None)
        for row in data:
            tree.insert("", "end", values=row)

        if len(df) > max_rows:
            note = ttk.Label(top, text=f"Showing first {max_rows} rows of {len(df)} (open the CSV for full data).")
            note.pack(side="bottom", anchor="w", padx=6, pady=4)

    def save_df_as(self, df: pd.DataFrame):
        p = filedialog.asksaveasfilename(title="Save results as", defaultextension=".csv",
                                         filetypes=[("CSV","*.csv"), ("All files","*.*")],
                                         initialdir=self.var_root.get())
        if p:
            try:
                df.to_csv(p, index=False)
                messagebox.showinfo("Saved", f"Results saved:\n{p}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{e}")

    # -------------------------
    # Generate tab actions
    # -------------------------
    def _browse_ideal(self):
        p = filedialog.askopenfilename(title="Select Ideal.txt or Ideal.txt.gz (optional)",
                                       filetypes=[("Ideal DB","Ideal.txt*"), ("All files","*.*")])
        if p:
            self.var_ideal_path.set(p)

    def _browse_gen_outdir(self):
        d = filedialog.askdirectory(title="Select output folder", initialdir=self.var_gen_outdir.get() or os.getcwd())
        if d:
            self.var_gen_outdir.set(d)

    def _log_gen(self, msg: str):
        try:
            self.txt_gen.insert("end", msg.rstrip() + "\n")
            self.txt_gen.see("end")
        except Exception:
            pass

    def on_generate(self):
        """Run the Ideal→Relax→Fourier pipeline (from SST_Fseries_GUI_Full/generate_knot_fseries)."""
        ab_id = (self.var_gen_abid.get() or "").strip()
        name = (self.var_gen_name.get() or "").strip()
        outdir = (self.var_gen_outdir.get() or "").strip()
        jmax = int(self.var_gen_jmax.get())
        nsamp = int(self.var_gen_samples.get())
        iters = int(self.var_gen_relax_iters.get())
        insert_j0 = bool(self.var_gen_insert_j0.get())

        if not name:
            messagebox.showerror("Generate", "Please provide a knot name.")
            return
        if not ab_id:
            messagebox.showerror("Generate", "Please provide an AB Id (from Ideal database).")
            return
        if not outdir:
            messagebox.showerror("Generate", "Please choose an output folder.")
            return

        self._log_gen("\n=== Generate pipeline ===")
        self._log_gen(f"AB Id: {ab_id} | name: {name} | outdir: {outdir}")
        self._log_gen(f"jmax={jmax}, samples={nsamp}, relax_iters={iters}, insert_j0={insert_j0}")

        def worker():
            try:
                if HAVE_SSTFULL:
                    # Use the richer pipeline (supports canonicalize + insert j0 row)
                    out_path, _, _ = _sst_full.generate_sst_pipeline(
                        ab_id=ab_id,
                        knot_name=name,
                        max_j_out=jmax,
                        iterations=iters,
                        num_points=nsamp,
                        out_dir=outdir,
                        insert_j0_row=insert_j0,
                        canonicalize_out=insert_j0,
                        log_fn=self._log_gen,
                    )
                    self._log_gen(f"[OK] Wrote: {out_path}")
                elif HAVE_GENKNOT:
                    # Fallback: simpler generator
                    _genknot.generate_sst_pipeline(ab_id=ab_id, knot_name=name, max_j_out=jmax, iterations=iters, num_points=nsamp)
                    self._log_gen("[OK] Generator completed (see console output).")
                else:
                    self._log_gen("[ERR] No generator modules available. Place generate_knot_fseries.py and SST_Fseries_GUI_Full.py next to this GUI.")
            except Exception as e:
                self._log_gen("[ERR] " + str(e))
                self._log_gen(traceback.format_exc())
            finally:
                try:
                    self.after(0, self.on_scan)
                except Exception:
                    pass

        threading.Thread(target=worker, daemon=True).start()

    def on_generate_all_catalog(self):
        """Genereer .fseries voor alle knopen uit de Ideal.txt-catalogus (batch); alleen op verzoek, niet bij start."""
        outdir = (self.var_gen_outdir.get() or "").strip()
        if not outdir:
            messagebox.showerror("Generate all", "Kies eerst een output folder.")
            return
        jmax = int(self.var_gen_jmax.get())
        nsamp = int(self.var_gen_samples.get())
        iters = int(self.var_gen_relax_iters.get())
        insert_j0 = bool(self.var_gen_insert_j0.get())

        def worker():
            try:
                if HAVE_SSTFULL:
                    catalog = getattr(_genknot, "knopen_catalogus", None) if HAVE_GENKNOT else None
                    if not catalog:
                        catalog = {"3_1": "3:1:1", "4_1": "4:1:1", "5_1": "5:1:1", "5_2": "5:1:2",
                                   "6_1": "6:1:1", "7_1": "7:1:1", "7_2": "7:1:2", "8_1": "8:1:1",
                                   "9_1": "9:1:1", "9_2": "9:1:2", "10_1": "10:1:1"}  # fallback
                    self._log_gen(f"\n=== Batch: alle knopen uit catalogus ({len(catalog)} stuks) ===\n")
                    for naam, ab_id in catalog.items():
                        self._log_gen(f"  [{naam}] {ab_id} ...")
                        try:
                            out_path, _, _ = _sst_full.generate_sst_pipeline(
                                ab_id=ab_id,
                                knot_name=f"knot_{naam}",
                                max_j_out=jmax,
                                iterations=iters,
                                num_points=nsamp,
                                out_dir=outdir,
                                insert_j0_row=insert_j0,
                                canonicalize_out=insert_j0,
                                log_fn=self._log_gen,
                            )
                            self._log_gen(f"    -> {out_path}\n")
                        except Exception as e:
                            self._log_gen(f"    [ERR] {e}\n")
                elif HAVE_GENKNOT:
                    self._log_gen("\n=== Batch via generate_knot_fseries ===\n")
                    _genknot.run_batch_from_catalog(
                        max_j_out=jmax, iterations=iters, num_points=nsamp, out_dir=outdir
                    )
                    self._log_gen("\n[OK] Batch voltooid.\n")
                else:
                    self._log_gen("[ERR] Geen generator beschikbaar (generate_knot_fseries of SST_Fseries_GUI_Full).\n")
            except Exception as e:
                self._log_gen("[ERR] " + str(e) + "\n")
                self._log_gen(traceback.format_exc())
            finally:
                try:
                    self.after(0, self.on_scan)
                except Exception:
                    pass

        threading.Thread(target=worker, daemon=True).start()

    # -------------------------
    # Helicity tab actions
    # -------------------------
    def _browse_helicity_csv(self):
        p = filedialog.asksaveasfilename(title="Save helicity CSV as", defaultextension=".csv",
                                         filetypes=[("CSV","*.csv"), ("All files","*.*")],
                                         initialdir=os.path.dirname(self.var_h_export_csv.get() or os.getcwd()))
        if p:
            self.var_h_export_csv.set(p)

    def _log_hel(self, msg: str):
        try:
            self.txt_hel.insert("end", msg.rstrip() + "\n")
            self.txt_hel.see("end")
        except Exception:
            pass

    def _selected_path_if_ext(self, ext: str):
        sel = self.tree.selection()
        if not sel:
            return None
        item = self.tree.item(sel[0], "values")
        # values are (ext, knot_id, relpath, status)
        if not item or len(item) < 3:
            return None
        if item[0].lower() != ext.lower():
            return None
        return os.path.join(self.var_root.get(), item[2])

    def on_helicity_selected(self):
        if not HAVE_HELICITY:
            messagebox.showerror("Helicity", "Helicity module (sst_helicity / HelicityCalculationVAMcore) not found/importable.")
            return
        path = self._selected_path_if_ext(".fseries")
        if not path:
            messagebox.showinfo("Helicity", "Select a .fseries row in the file list.")
            return
        G = int(self.var_h_grid.get())
        S = float(self.var_h_spacing.get())
        I = int(self.var_h_interior.get())
        out_csv = (self.var_h_export_csv.get() or "").strip()

        self._log_hel("\n=== Helicity (selected) ===")
        self._log_hel(f"file: {os.path.basename(path)} | grid={G} spacing={S} interior={I}")

        def worker():
            try:
                a_mu, Hc, Hm = _hel.compute_a_mu_for_file(path, grid_size=G, spacing=S, interior=I)
                self._log_hel(f"a_mu = {a_mu:.10f}   Hc={Hc:.6e}   Hm={Hm:.6e}")
                df = pd.DataFrame([{
                    "file": os.path.basename(path),
                    "grid": G, "spacing": S, "interior": I,
                    "a_mu": a_mu, "Hc": Hc, "Hm": Hm,
                }])
                if out_csv:
                    df.to_csv(out_csv, index=False)
                    self._log_hel(f"[OK] wrote {out_csv}")
            except Exception as e:
                self._log_hel("[ERR] " + str(e))
                self._log_hel(traceback.format_exc())

        threading.Thread(target=worker, daemon=True).start()

    def on_helicity_all(self):
        if not HAVE_HELICITY:
            messagebox.showerror("Helicity", "Helicity module (sst_helicity / HelicityCalculationVAMcore) not found/importable.")
            return
        root = self.var_root.get()
        out_csv = (self.var_h_export_csv.get() or "").strip()
        G = int(self.var_h_grid.get())
        S = float(self.var_h_spacing.get())
        I = int(self.var_h_interior.get())

        paths = sorted(glob.glob(os.path.join(root, "**", "*.fseries"), recursive=True))
        if not paths:
            messagebox.showinfo("Helicity", "No .fseries files found under root.")
            return

        self._log_hel("\n=== Helicity (ALL) ===")
        self._log_hel(f"count: {len(paths)} | grid={G} spacing={S} interior={I}")

        def worker():
            rows = []
            try:
                for p in paths:
                    try:
                        a_mu, Hc, Hm = _hel.compute_a_mu_for_file(p, grid_size=G, spacing=S, interior=I)
                        rows.append({"file": os.path.basename(p), "grid": G, "spacing": S, "interior": I,
                                     "a_mu": a_mu, "Hc": Hc, "Hm": Hm})
                    except Exception:
                        rows.append({"file": os.path.basename(p), "grid": G, "spacing": S, "interior": I,
                                     "a_mu": np.nan, "Hc": np.nan, "Hm": np.nan})
                df = pd.DataFrame(rows)
                if out_csv:
                    df.to_csv(out_csv, index=False)
                    self._log_hel(f"[OK] wrote {out_csv}")
                self._log_hel(df.describe(include='all').to_string())
            except Exception as e:
                self._log_hel("[ERR] " + str(e))
                self._log_hel(traceback.format_exc())

        threading.Thread(target=worker, daemon=True).start()

    # -------------------------
    # Utilities tab actions
    # -------------------------
    def _log_util(self, msg: str):
        try:
            self.txt_util.insert("end", msg.rstrip() + "\n")
            self.txt_util.see("end")
        except Exception:
            pass

    def _canonicalize_one(self, in_path: str) -> str:
        """Write a *_j0.fseries next to in_path, adding an explicit j=0 row if needed."""
        base, ext = os.path.splitext(in_path)
        out_path = base + "_j0" + ext
        if HAVE_SSTFULL:
            _sst_full.canonicalize_fseries_to_j0(in_path, out_path=out_path)
            return out_path
        # Minimal fallback: prepend an all-zero row if first row is not ~0
        headers = []
        rows = []
        with open(in_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                if line.lstrip().startswith("%"):
                    headers.append(line.rstrip("\n"))
                    continue
                parts = line.split()
                if len(parts) != 6:
                    continue
                rows.append([float(p) for p in parts])
        arr = np.asarray(rows, dtype=float)
        if arr.size == 0:
            raise ValueError(f"{in_path}: no numeric rows")
        if not np.all(np.abs(arr[0]) < 1e-12):
            arr = np.vstack([np.zeros(6), arr])
        with open(out_path, "w", encoding="utf-8") as f:
            for h in headers:
                f.write(h + "\n")
            for r in arr:
                f.write(f"{r[0]: .6f} {r[1]: .6f} {r[2]: .6f} {r[3]: .6f} {r[4]: .6f} {r[5]: .6f}\n")
        return out_path

    def on_canonicalize_selected(self):
        path = self._selected_path_if_ext(".fseries")
        if not path:
            messagebox.showinfo("Canonicalize", "Select a .fseries row in the file list.")
            return
        try:
            outp = self._canonicalize_one(path)
            self._log_util(f"[OK] {os.path.basename(path)} → {os.path.basename(outp)}")
            self.on_scan()
        except Exception as e:
            self._log_util("[ERR] " + str(e))

    def on_canonicalize_all(self):
        root = self.var_root.get()
        paths = sorted(glob.glob(os.path.join(root, "**", "*.fseries"), recursive=True))
        if not paths:
            messagebox.showinfo("Canonicalize", "No .fseries files found under root.")
            return
        self._log_util(f"\n=== Canonicalize ALL ({len(paths)} files) ===")

        def worker():
            ok = 0
            for p in paths:
                try:
                    outp = self._canonicalize_one(p)
                    ok += 1
                    self._log_util(f"[OK] {os.path.basename(p)} → {os.path.basename(outp)}")
                except Exception as e:
                    self._log_util(f"[ERR] {os.path.basename(p)}: {e}")
            self._log_util(f"Done. OK={ok}/{len(paths)}")
            try:
                self.after(0, self.on_scan)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

def discover_ids(files):
    ids = []
    seen = set()
    for f in files:
        kid = parse_knot_id_from_filename(f)
        if kid not in seen:
            seen.add(kid); ids.append(kid)
    return ids

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()