# sst_knot_gui.py
# GUI wrapper + anti-aliasing + optional topology-preserving barrier
# Keeps your original functions (extended, not simplified).

import requests
import gzip
import shutil
import numpy as np
import re
import os
import threading
import queue
from pathlib import Path

# Optional preview
try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    HAS_MPL = True
except Exception:
    HAS_MPL = False

# GUI
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


# -----------------------------
# Original functions (kept)
# -----------------------------

def prepare_database(
        url="https://katlas.org/images/d/d2/Ideal.txt.gz",
        gz_name="Ideal.txt.gz",
        txt_name="Ideal.txt"
):
    """Autonome acquisitie en extractie van de topologische referentiedatabase."""
    gz_path = Path(gz_name)
    txt_path = Path(txt_name)

    if not txt_path.exists():
        if not gz_path.exists():
            print(f"[*] Acquireren van referentiedatabase via {url}...")
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            gz_path.write_bytes(r.content)

        print(f"[*] Decomprimeren van database archief...")
        with gzip.open(gz_path, "rb") as f_in, open(txt_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return str(txt_path)


def extract_ab_block(text: str, ab_id: str) -> str:
    m = re.search(rf'<AB\s+Id="{re.escape(ab_id)}"[^>]*>', text)
    if not m:
        raise ValueError(f"AB Id '{ab_id}' niet gevonden in de database.")
    end = text.find("</AB>", m.end())
    return text[m.start(): end + len("</AB>")]


def parse_coeffs(ab_block: str):
    coeffs = {}
    for m in re.finditer(
            r'<Coeff\s+I="\s*([0-9]+)"\s+A="\s*([^"]+)"\s+B="\s*([^"]+)"\s*/>',
            ab_block
    ):
        i = int(m.group(1))
        A = list(map(float, m.group(2).replace(" ", "").split(",")))
        B = list(map(float, m.group(3).replace(" ", "").split(",")))
        # Expect A=(ax,ay,az), B=(bx,by,bz)
        if len(A) != 3 or len(B) != 3:
            raise ValueError(f"Coeff I={i} heeft onverwachte lengte: len(A)={len(A)}, len(B)={len(B)}")
        coeffs[i] = (A, B)
    return coeffs


# -----------------------------
# Helpers (new, non-destructive additions)
# -----------------------------

IDEAL_TEXT_CACHE = {"path": None, "text": None}

def load_ideal_text_cached(db_path: str) -> str:
    """Cache Ideal.txt in memory once (speeds up batch & GUI)."""
    if IDEAL_TEXT_CACHE["path"] == db_path and IDEAL_TEXT_CACHE["text"] is not None:
        return IDEAL_TEXT_CACHE["text"]
    text = Path(db_path).read_text(encoding="utf-8", errors="ignore")
    IDEAL_TEXT_CACHE["path"] = db_path
    IDEAL_TEXT_CACHE["text"] = text
    return text


def normalize_arclength(points, N):
    dp = np.diff(np.vstack((points, [points[0]])), axis=0)
    ds = np.linalg.norm(dp, axis=1)
    s = np.zeros(len(points) + 1)
    s[1:] = np.cumsum(ds)
    L = s[-1]
    if L <= 0:
        raise ValueError("Arclength normalisatie faalt: totale lengte is 0.")
    s_target = np.linspace(0, L, N, endpoint=False)
    pts_uniform = np.zeros((N, 3))
    for dim in range(3):
        pts_uniform[:, dim] = np.interp(s_target, s, np.append(points[:, dim], points[0, dim]))
    return pts_uniform


def calculate_fourier(coord, s, maxJ, num_points):
    a, b = np.zeros(maxJ), np.zeros(maxJ)
    for j in range(1, maxJ + 1):
        a[j - 1] = (2 / num_points) * np.sum(coord * np.cos(j * s))
        b[j - 1] = (2 / num_points) * np.sum(coord * np.sin(j * s))
    return a, b


def plot_curve_3d(points, title="curve", equal_aspect=True):
    if not HAS_MPL:
        print("[!] Matplotlib niet beschikbaar; preview overgeslagen.")
        return
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(points[:, 0], points[:, 1], points[:, 2], lw=1.5)
    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    if equal_aspect:
        # Equal aspect in 3D (best-effort)
        mins = points.min(axis=0)
        maxs = points.max(axis=0)
        spans = maxs - mins
        span = float(np.max(spans)) if np.max(spans) > 0 else 1.0
        centers = (mins + maxs) / 2
        ax.set_xlim(centers[0] - span / 2, centers[0] + span / 2)
        ax.set_ylim(centers[1] - span / 2, centers[1] + span / 2)
        ax.set_zlim(centers[2] - span / 2, centers[2] + span / 2)
    plt.show()


# -----------------------------
# Your pipeline (extended, not simplified)
# -----------------------------

def generate_sst_pipeline(
        ab_id,
        knot_name,
        max_j_out=50,
        iterations=1500,
        num_points=300,

        # New anti-aliasing controls (defaults chosen to be safe)
        recon_oversample_factor=8,     # reconstruct using N_recon = max(num_points, factor * jmax_in)
        j_in_cap=None,                 # optional hard cap on j during reconstruction
        enforce_nyquist=True,          # ensures j <= N_recon//2 - 1

        # Relaxation controls (keeps old behavior by default)
        do_relax=True,
        k_spring=5.0,
        q_repulse=0.05,
        alpha=0.005,
        max_grad_norm=5.0,

        # New "anti-crossing" barrier / step clamp (optional)
        barrier_min_sep=0.0,           # if >0, adds extra repulsion when dist < barrier_min_sep
        step_max_frac=0.15,            # clamp displacement per step to step_max_frac * l0 (helps preserve topology)
        center_each_step=True,

        # IO controls
        url="https://katlas.org/images/d/d2/Ideal.txt.gz",
        gz_name="Ideal.txt.gz",
        txt_name="Ideal.txt",
        out_dir=".",
        stop_event=None,
        return_points=False,
        verbose=True,
        log_every=200
):
    if verbose:
        print(f"\n[*] Start SST-integratie pipeline: {knot_name} (AB Id: {ab_id})")

    db_path = prepare_database(url=url, gz_name=gz_name, txt_name=txt_name)
    ideal_data = load_ideal_text_cached(db_path)

    try:
        block = extract_ab_block(ideal_data, ab_id)
        raw_coeffs = parse_coeffs(block)
    except Exception as e:
        print(f"[!] Extractiefout: {e}")
        return None

    # -------------------------
    # Reconstruct (anti-aliasing)
    # -------------------------
    max_j_in = max(raw_coeffs.keys())
    N_recon = max(num_points, int(recon_oversample_factor * max_j_in))
    if enforce_nyquist:
        # Ensure we don't exceed Nyquist in discrete sampling
        j_nyq = max(1, (N_recon // 2) - 1)
    else:
        j_nyq = max_j_in

    j_use = min(max_j_in, j_nyq)
    if j_in_cap is not None:
        j_use = min(j_use, int(j_in_cap))

    if verbose:
        print(f"[*] Reconstructie: j_in={max_j_in}, N_recon={N_recon}, j_use={j_use}")

    t = np.linspace(0, 2 * np.pi, N_recon, endpoint=False)
    pts = np.zeros((N_recon, 3), dtype=float)

    for j in range(1, j_use + 1):
        if stop_event is not None and stop_event.is_set():
            print("[!] Stop gevraagd. Reconstructie afgebroken.")
            return None
        if j in raw_coeffs:
            A, B = raw_coeffs[j]
            ax, ay, az = A
            bx, by, bz = B
            cos_jt = np.cos(j * t)
            sin_jt = np.sin(j * t)
            pts[:, 0] += ax * cos_jt + bx * sin_jt
            pts[:, 1] += ay * cos_jt + by * sin_jt
            pts[:, 2] += az * cos_jt + bz * sin_jt

    # Resample to uniform arclength at the working resolution (num_points)
    pts = normalize_arclength(pts, num_points)

    # -------------------------
    # Relaxation (optional)
    # -------------------------
    if do_relax and iterations > 0:
        if verbose:
            print(f"[*] Minimaliseren van interactie-energie ({iterations} iteraties)...")

        N = num_points
        mask = np.ones((N, N), dtype=bool)
        np.fill_diagonal(mask, False)
        for i in range(N):
            mask[i, (i + 1) % N] = False
            mask[i, (i - 1) % N] = False

        for step in range(iterations):
            if stop_event is not None and stop_event.is_set():
                print("[!] Stop gevraagd. Relaxatie afgebroken.")
                return None

            # Neighbor spring forces
            seg = np.diff(np.vstack((pts, [pts[0]])), axis=0)
            lengths = np.linalg.norm(seg, axis=1)
            l0 = float(np.mean(lengths)) if np.mean(lengths) > 0 else 1.0

            pts_next = np.roll(pts, -1, axis=0)
            pts_prev = np.roll(pts, 1, axis=0)

            v_next = pts_next - pts
            d_next = np.linalg.norm(v_next, axis=1, keepdims=True)
            f_next = k_spring * (d_next - l0) * (v_next / (d_next + 1e-12))

            v_prev = pts_prev - pts
            d_prev = np.linalg.norm(v_prev, axis=1, keepdims=True)
            f_prev = k_spring * (d_prev - l0) * (v_prev / (d_prev + 1e-12))

            f_elastic = f_next + f_prev

            # Pairwise repulsion (point-point)
            diff = pts[:, np.newaxis, :] - pts[np.newaxis, :, :]
            dist = np.linalg.norm(diff, axis=2)
            dist[~mask] = 1e9  # ignore neighbors and self

            # Base repulsion
            f_rep_mag = q_repulse / (dist**3 + 1e-12)
            f_rep_mag[~mask] = 0.0

            # Optional barrier to prevent near-crossings
            if barrier_min_sep and barrier_min_sep > 0.0:
                # Strong extra repulsion when closer than barrier_min_sep
                close = (dist < barrier_min_sep) & mask
                if np.any(close):
                    # Add a steeper term ~ 1/r^6 for close pairs
                    f_rep_mag[close] += (q_repulse * 10.0) / (dist[close]**6 + 1e-12)

            f_repulsion = np.sum(diff * f_rep_mag[:, :, np.newaxis], axis=1)

            # Combine forces (forces already act like descent directions)
            force = f_elastic + f_repulsion

            # Clamp force norm
            fnorm = np.linalg.norm(force, axis=1, keepdims=True)
            force = np.where(fnorm > max_grad_norm, force * (max_grad_norm / (fnorm + 1e-12)), force)

            # Step clamp (critical for preserving knot type)
            delta = alpha * force
            dnorm = np.linalg.norm(delta, axis=1, keepdims=True)
            max_step = step_max_frac * l0
            delta = np.where(dnorm > max_step, delta * (max_step / (dnorm + 1e-12)), delta)

            pts = pts + delta

            if center_each_step:
                pts = pts - np.mean(pts, axis=0)

            if verbose and (step % max(1, log_every) == 0):
                # simple diagnostic: min non-neighbor distance
                dtmp = dist.copy()
                dmin = float(np.min(dtmp[mask])) if np.any(mask) else float("nan")
                print(f"    iter={step:5d}  l0={l0:.6g}  min_nonnb_dist={dmin:.6g}")

        pts = normalize_arclength(pts, num_points)

    # -------------------------
    # Fourier projection (output)
    # -------------------------
    if max_j_out > (num_points // 2 - 1):
        # Fourier estimation above Nyquist is meaningless: cap it safely
        if verbose:
            print(f"[!] max_j_out={max_j_out} > Nyquist={num_points//2-1}. Cappen.")
        max_j_out = max(1, num_points // 2 - 1)

    if verbose:
        print(f"[*] Transformeren naar SST Canon format (j_max = {max_j_out})...")

    s_param = np.linspace(0, 2 * np.pi, num_points, endpoint=False)

    ax, bx = calculate_fourier(pts[:, 0], s_param, max_j_out, num_points)
    ay, by = calculate_fourier(pts[:, 1], s_param, max_j_out, num_points)
    az, bz = calculate_fourier(pts[:, 2], s_param, max_j_out, num_points)

    out_dir = str(out_dir) if out_dir else "."
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{knot_name}_sst.fseries")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"% (Fourier projection from Ideal database for SST Canon: {knot_name} | AB Id: {ab_id})\n")
        f.write("% lines  a_x(j) b_x(j)  a_y(j) b_y(j)  a_z(j) b_z(j)\n")
        for j in range(max_j_out):
            f.write(f"{ax[j]: 9.6f} {bx[j]: 9.6f} {ay[j]: 9.6f} {by[j]: 9.6f} {az[j]: 9.6f} {bz[j]: 9.6f}\n")

    if verbose:
        print(f"[+] Succes! Geoptimaliseerde inbedding weggeschreven naar '{out_path}'")

    if return_points:
        return {"out_path": out_path, "points": pts}
    return {"out_path": out_path}


# -----------------------------
# Default AB Id catalog (same idea as yours)
# -----------------------------

DEFAULT_KNOT_CATALOG = {
    "3_1": "3:1:1",
    "4_1": "4:1:1",
    "5_1": "5:1:1",
    "5_2": "5:1:2",
    "6_1": "6:1:1",
    "7_1": "7:1:1",
    "7_2": "7:1:2",
    "8_1": "8:1:1",
    "9_1": "9:1:1",
    "9_2": "9:1:2",
    "10_1": "10:1:1",
}


# -----------------------------
# GUI
# -----------------------------

class TextRedirector:
    def __init__(self, text_widget: ScrolledText, q: queue.Queue):
        self.text_widget = text_widget
        self.q = q

    def write(self, s):
        self.q.put(s)

    def flush(self):
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SST Knot Ideal → .fseries Pipeline (GUI)")
        self.geometry("1100x720")

        self.log_q = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = None

        self._build_ui()
        self._poll_log_queue()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self)
        right = ttk.Frame(self)

        left.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        right.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        left.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        # Notebook with tabs
        nb = ttk.Notebook(left)
        nb.grid(row=0, column=0, sticky="nsew")

        tab_general = ttk.Frame(nb)
        tab_single = ttk.Frame(nb)
        tab_batch = ttk.Frame(nb)

        nb.add(tab_general, text="General")
        nb.add(tab_single, text="Single")
        nb.add(tab_batch, text="Batch")

        for tab in (tab_general, tab_single, tab_batch):
            tab.columnconfigure(1, weight=1)

        # -------- General tab
        self.var_url = tk.StringVar(value="https://katlas.org/images/d/d2/Ideal.txt.gz")
        self.var_gz = tk.StringVar(value="Ideal.txt.gz")
        self.var_txt = tk.StringVar(value="Ideal.txt")
        self.var_out_dir = tk.StringVar(value=os.path.abspath("."))

        r = 0
        ttk.Label(tab_general, text="Database URL").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_general, textvariable=self.var_url).grid(row=r, column=1, sticky="ew", padx=6, pady=4)
        r += 1

        ttk.Label(tab_general, text="GZ filename").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_general, textvariable=self.var_gz).grid(row=r, column=1, sticky="ew", padx=6, pady=4)
        r += 1

        ttk.Label(tab_general, text="TXT filename").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_general, textvariable=self.var_txt).grid(row=r, column=1, sticky="ew", padx=6, pady=4)
        r += 1

        ttk.Label(tab_general, text="Output directory").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        out_row = ttk.Frame(tab_general)
        out_row.grid(row=r, column=1, sticky="ew", padx=6, pady=4)
        out_row.columnconfigure(0, weight=1)
        ttk.Entry(out_row, textvariable=self.var_out_dir).grid(row=0, column=0, sticky="ew")
        ttk.Button(out_row, text="Browse...", command=self._browse_outdir).grid(row=0, column=1, padx=6)
        r += 1

        ttk.Button(tab_general, text="Download/Prepare Database", command=self._prepare_db_clicked).grid(
            row=r, column=0, columnspan=2, sticky="ew", padx=6, pady=10
        )

        # -------- Single tab
        self.var_preset = tk.StringVar(value="3_1")
        self.var_ab_id = tk.StringVar(value=DEFAULT_KNOT_CATALOG["3_1"])
        self.var_knot_name = tk.StringVar(value="knot_3_1")

        self.var_max_j_out = tk.IntVar(value=50)
        self.var_iterations = tk.IntVar(value=1500)
        self.var_num_points = tk.IntVar(value=300)

        self.var_recon_factor = tk.IntVar(value=8)
        self.var_j_in_cap = tk.StringVar(value="")  # empty = None
        self.var_enforce_nyquist = tk.BooleanVar(value=True)

        self.var_do_relax = tk.BooleanVar(value=True)
        self.var_k_spring = tk.DoubleVar(value=5.0)
        self.var_q_repulse = tk.DoubleVar(value=0.05)
        self.var_alpha = tk.DoubleVar(value=0.005)
        self.var_max_grad_norm = tk.DoubleVar(value=5.0)

        self.var_barrier_sep = tk.DoubleVar(value=0.0)
        self.var_step_max_frac = tk.DoubleVar(value=0.15)
        self.var_center_each = tk.BooleanVar(value=True)

        rr = 0
        ttk.Label(tab_single, text="Preset knot").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        preset_row = ttk.Frame(tab_single)
        preset_row.grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        preset_row.columnconfigure(1, weight=1)
        preset = ttk.Combobox(preset_row, textvariable=self.var_preset, values=list(DEFAULT_KNOT_CATALOG.keys()), width=10)
        preset.grid(row=0, column=0, sticky="w")
        ttk.Button(preset_row, text="Load AB Id", command=self._load_preset_abid).grid(row=0, column=1, sticky="w", padx=8)
        rr += 1

        ttk.Label(tab_single, text="AB Id").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_ab_id).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        ttk.Label(tab_single, text="Knot name").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_knot_name).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        sep = ttk.Separator(tab_single, orient="horizontal")
        sep.grid(row=rr, column=0, columnspan=2, sticky="ew", pady=10)
        rr += 1

        ttk.Label(tab_single, text="max_j_out").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_max_j_out).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        ttk.Label(tab_single, text="iterations").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_iterations).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        ttk.Label(tab_single, text="num_points").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_num_points).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        sep = ttk.Separator(tab_single, orient="horizontal")
        sep.grid(row=rr, column=0, columnspan=2, sticky="ew", pady=10)
        rr += 1

        ttk.Label(tab_single, text="recon_oversample_factor").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_recon_factor).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        ttk.Label(tab_single, text="j_in_cap (optional)").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_j_in_cap).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        ttk.Checkbutton(tab_single, text="enforce_nyquist", variable=self.var_enforce_nyquist).grid(
            row=rr, column=0, columnspan=2, sticky="w", padx=6, pady=4
        )
        rr += 1

        sep = ttk.Separator(tab_single, orient="horizontal")
        sep.grid(row=rr, column=0, columnspan=2, sticky="ew", pady=10)
        rr += 1

        ttk.Checkbutton(tab_single, text="do_relax", variable=self.var_do_relax).grid(
            row=rr, column=0, columnspan=2, sticky="w", padx=6, pady=4
        )
        rr += 1

        ttk.Label(tab_single, text="k_spring").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_k_spring).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        ttk.Label(tab_single, text="q_repulse").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_q_repulse).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        ttk.Label(tab_single, text="alpha").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_alpha).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        ttk.Label(tab_single, text="max_grad_norm").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_max_grad_norm).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        sep = ttk.Separator(tab_single, orient="horizontal")
        sep.grid(row=rr, column=0, columnspan=2, sticky="ew", pady=10)
        rr += 1

        ttk.Label(tab_single, text="barrier_min_sep (0=off)").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_barrier_sep).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        ttk.Label(tab_single, text="step_max_frac").grid(row=rr, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(tab_single, textvariable=self.var_step_max_frac).grid(row=rr, column=1, sticky="ew", padx=6, pady=4)
        rr += 1

        ttk.Checkbutton(tab_single, text="center_each_step", variable=self.var_center_each).grid(
            row=rr, column=0, columnspan=2, sticky="w", padx=6, pady=4
        )
        rr += 1

        btn_row = ttk.Frame(tab_single)
        btn_row.grid(row=rr, column=0, columnspan=2, sticky="ew", padx=6, pady=10)
        btn_row.columnconfigure(0, weight=1)
        btn_row.columnconfigure(1, weight=1)
        btn_row.columnconfigure(2, weight=1)

        ttk.Button(btn_row, text="Generate Single", command=self._run_single_clicked).grid(row=0, column=0, sticky="ew", padx=4)
        ttk.Button(btn_row, text="Preview Points (3D)", command=self._preview_single_clicked).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(btn_row, text="STOP", command=self._stop_clicked).grid(row=0, column=2, sticky="ew", padx=4)

        # -------- Batch tab
        self.batch_text = tk.StringVar(value=self._catalog_to_text(DEFAULT_KNOT_CATALOG))

        ttk.Label(tab_batch, text="Catalog (one per line: name=ABID)").grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        self.catalog_box = ScrolledText(tab_batch, height=18)
        self.catalog_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=4)
        tab_batch.rowconfigure(1, weight=1)
        self.catalog_box.insert("1.0", self.batch_text.get())

        batch_btns = ttk.Frame(tab_batch)
        batch_btns.grid(row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=10)
        batch_btns.columnconfigure(0, weight=1)
        batch_btns.columnconfigure(1, weight=1)
        batch_btns.columnconfigure(2, weight=1)

        ttk.Button(batch_btns, text="Generate Batch", command=self._run_batch_clicked).grid(row=0, column=0, sticky="ew", padx=4)
        ttk.Button(batch_btns, text="Load Default Catalog", command=self._load_default_catalog).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(batch_btns, text="STOP", command=self._stop_clicked).grid(row=0, column=2, sticky="ew", padx=4)

        # -------- Right side: log output
        self.log = ScrolledText(right, wrap="word")
        self.log.grid(row=0, column=0, sticky="nsew")
        self.log.configure(state="disabled")

        # Redirect print to log
        import sys
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = TextRedirector(self.log, self.log_q)
        sys.stderr = TextRedirector(self.log, self.log_q)

    def destroy(self):
        # restore stdout/stderr
        import sys
        sys.stdout = self._stdout
        sys.stderr = self._stderr
        super().destroy()

    def _poll_log_queue(self):
        try:
            while True:
                s = self.log_q.get_nowait()
                self.log.configure(state="normal")
                self.log.insert("end", s)
                self.log.see("end")
                self.log.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(80, self._poll_log_queue)

    def _browse_outdir(self):
        d = filedialog.askdirectory(initialdir=self.var_out_dir.get() or ".")
        if d:
            self.var_out_dir.set(d)

    def _prepare_db_clicked(self):
        self._start_worker(self._prepare_db_worker)

    def _prepare_db_worker(self):
        self.stop_event.clear()
        try:
            prepare_database(
                url=self.var_url.get(),
                gz_name=self.var_gz.get(),
                txt_name=self.var_txt.get()
            )
            print("[+] Database is klaar.")
        except Exception as e:
            print(f"[!] Database prepare faalde: {e}")

    def _load_preset_abid(self):
        key = self.var_preset.get().strip()
        if key in DEFAULT_KNOT_CATALOG:
            self.var_ab_id.set(DEFAULT_KNOT_CATALOG[key])
            self.var_knot_name.set(f"knot_{key}")
        else:
            messagebox.showwarning("Preset", f"Onbekende preset: {key}")

    def _stop_clicked(self):
        self.stop_event.set()
        print("[!] Stop requested door gebruiker.")

    def _start_worker(self, target_fn):
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("Busy", "Er draait al een job. Druk STOP of wacht.")
            return
        self.worker_thread = threading.Thread(target=target_fn, daemon=True)
        self.worker_thread.start()

    def _get_single_params(self):
        jcap = self.var_j_in_cap.get().strip()
        jcap_val = int(jcap) if jcap else None
        return dict(
            ab_id=self.var_ab_id.get().strip(),
            knot_name=self.var_knot_name.get().strip(),
            max_j_out=int(self.var_max_j_out.get()),
            iterations=int(self.var_iterations.get()),
            num_points=int(self.var_num_points.get()),

            recon_oversample_factor=int(self.var_recon_factor.get()),
            j_in_cap=jcap_val,
            enforce_nyquist=bool(self.var_enforce_nyquist.get()),

            do_relax=bool(self.var_do_relax.get()),
            k_spring=float(self.var_k_spring.get()),
            q_repulse=float(self.var_q_repulse.get()),
            alpha=float(self.var_alpha.get()),
            max_grad_norm=float(self.var_max_grad_norm.get()),

            barrier_min_sep=float(self.var_barrier_sep.get()),
            step_max_frac=float(self.var_step_max_frac.get()),
            center_each_step=bool(self.var_center_each.get()),

            url=self.var_url.get().strip(),
            gz_name=self.var_gz.get().strip(),
            txt_name=self.var_txt.get().strip(),
            out_dir=self.var_out_dir.get().strip(),
            stop_event=self.stop_event,
            verbose=True
        )

    def _run_single_clicked(self):
        self._start_worker(self._run_single_worker)

    def _run_single_worker(self):
        self.stop_event.clear()
        try:
            params = self._get_single_params()
            res = generate_sst_pipeline(**params)
            if res:
                print(f"[+] Output: {res['out_path']}")
        except Exception as e:
            print(f"[!] Single run faalde: {e}")

    def _preview_single_clicked(self):
        if not HAS_MPL:
            messagebox.showwarning("Preview", "Matplotlib niet beschikbaar.")
            return
        # Preview runs in foreground to avoid matplotlib/thread issues
        self.stop_event.clear()
        try:
            params = self._get_single_params()
            params["return_points"] = True
            res = generate_sst_pipeline(**params)
            if not res:
                return
            pts = res["points"]
            plot_curve_3d(pts, title=f"{params['knot_name']} (AB {params['ab_id']})")
        except Exception as e:
            messagebox.showerror("Preview error", str(e))

    def _catalog_to_text(self, catalog: dict) -> str:
        lines = []
        for k, v in catalog.items():
            lines.append(f"{k}={v}")
        return "\n".join(lines) + "\n"

    def _parse_catalog_text(self, text: str) -> dict:
        cat = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"Ongeldige regel (geen '='): {line}")
            name, abid = line.split("=", 1)
            name = name.strip()
            abid = abid.strip()
            if not name or not abid:
                raise ValueError(f"Ongeldige regel: {line}")
            cat[name] = abid
        return cat

    def _load_default_catalog(self):
        self.catalog_box.delete("1.0", "end")
        self.catalog_box.insert("1.0", self._catalog_to_text(DEFAULT_KNOT_CATALOG))

    def _run_batch_clicked(self):
        self._start_worker(self._run_batch_worker)

    def _run_batch_worker(self):
        self.stop_event.clear()
        try:
            cat_text = self.catalog_box.get("1.0", "end")
            catalog = self._parse_catalog_text(cat_text)
            print(f"\n[*] Start batch-verwerking van {len(catalog)} SST topologieën...\n")

            base = self._get_single_params()
            # In batch we override knot_name & ab_id per item
            for name, abid in catalog.items():
                if self.stop_event.is_set():
                    print("[!] Batch gestopt.")
                    return
                knot_name = f"knot_{name}"
                print(f"\n--- {name} -> {abid} ---")
                res = generate_sst_pipeline(
                    ab_id=abid,
                    knot_name=knot_name,
                    max_j_out=base["max_j_out"],
                    iterations=base["iterations"],
                    num_points=base["num_points"],
                    recon_oversample_factor=base["recon_oversample_factor"],
                    j_in_cap=base["j_in_cap"],
                    enforce_nyquist=base["enforce_nyquist"],
                    do_relax=base["do_relax"],
                    k_spring=base["k_spring"],
                    q_repulse=base["q_repulse"],
                    alpha=base["alpha"],
                    max_grad_norm=base["max_grad_norm"],
                    barrier_min_sep=base["barrier_min_sep"],
                    step_max_frac=base["step_max_frac"],
                    center_each_step=base["center_each_step"],
                    url=base["url"],
                    gz_name=base["gz_name"],
                    txt_name=base["txt_name"],
                    out_dir=base["out_dir"],
                    stop_event=self.stop_event,
                    verbose=True
                )
                if res:
                    print(f"[+] Output: {res['out_path']}")

            print("\n[+] Batch-executie voltooid.")
        except Exception as e:
            print(f"[!] Batch run faalde: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()