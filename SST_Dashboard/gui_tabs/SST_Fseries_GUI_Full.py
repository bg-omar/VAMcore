# SST_Fseries_GUI_Full.py
# GUI voor volledige SST Ideal.txt -> Hamiltonian relax -> .fseries pipeline
# Niets verdwijnt: alle functies blijven aanwezig en zijn afzonderlijk aanroepbaar.

import os
import re
import gzip
import shutil
import threading
import queue
from pathlib import Path
import numpy as np
try:
    from sst_exports import get_exports_dir
except ImportError:
    get_exports_dir = None

# requests is handig maar niet verplicht; fallback naar urllib
try:
    import requests
    HAVE_REQUESTS = True
except Exception:
    HAVE_REQUESTS = False
    import urllib.request

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# matplotlib voor preview plots (optioneel)
HAVE_MPL = True
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:
    HAVE_MPL = False


# ---------------------------
# CORE FUNCTIES (NIET VERLOREN)
# ---------------------------

def prepare_database(url="https://katlas.org/images/d/d2/Ideal.txt.gz",
                     gz_name="Ideal.txt.gz",
                     txt_name="Ideal.txt",
                     log_fn=None):
    """Autonome acquisitie en extractie van de topologische referentiedatabase."""
    gz_path = Path(gz_name)
    txt_path = Path(txt_name)

    def log(msg):
        if log_fn:
            log_fn(msg)

    if not txt_path.exists():
        if not gz_path.exists():
            log(f"[*] Acquireren van referentiedatabase via {url}...")
            if HAVE_REQUESTS:
                r = requests.get(url, timeout=60)
                r.raise_for_status()
                gz_path.write_bytes(r.content)
            else:
                with urllib.request.urlopen(url, timeout=60) as resp:
                    gz_path.write_bytes(resp.read())

        log("[*] Decomprimeren van database archief...")
        with gzip.open(gz_path, "rb") as f_in, open(txt_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return str(txt_path)


def extract_ab_block(text: str, ab_id: str):
    """Extracteert AB block uit volledige XML tekst."""
    m = re.search(rf'<AB\s+Id="{re.escape(ab_id)}"[^>]*>', text)
    if not m:
        raise ValueError(f"AB Id '{ab_id}' niet gevonden in de database.")
    end = text.find("</AB>", m.end())
    if end == -1:
        raise ValueError("AB block niet correct afgesloten (</AB> ontbreekt).")
    return text[m.start(): end + len("</AB>")]


def parse_coeffs(ab_block: str):
    """Parset <Coeff I=".." A="ax,ay,az" B="bx,by,bz"/> regels."""
    coeffs = {}
    for m in re.finditer(r'<Coeff\s+I="\s*([0-9]+)"\s+A="\s*([^"]+)"\s+B="\s*([^"]+)"\s*/>', ab_block):
        i = int(m.group(1))
        A = list(map(float, m.group(2).replace(" ", "").split(",")))
        B = list(map(float, m.group(3).replace(" ", "").split(",")))
        coeffs[i] = (A, B)
    return coeffs


def normalize_arclength(points, N):
    """Resample punten naar uniforme booglengte."""
    dp = np.diff(np.vstack((points, [points[0]])), axis=0)
    ds = np.linalg.norm(dp, axis=1)
    s = np.zeros(len(points) + 1)
    s[1:] = np.cumsum(ds)
    L = s[-1]
    s_target = np.linspace(0, L, N, endpoint=False)
    pts_uniform = np.zeros((N, 3))
    for dim in range(3):
        pts_uniform[:, dim] = np.interp(s_target, s, np.append(points[:, dim], points[0, dim]))
    return pts_uniform


def calculate_fourier(coord, s, maxJ, num_points):
    """Discrete Fourier projectie naar a_j,b_j voor j=1..maxJ."""
    a, b = np.zeros(maxJ), np.zeros(maxJ)
    for j in range(1, maxJ + 1):
        a[j - 1] = (2 / num_points) * np.sum(coord * np.cos(j * s))
        b[j - 1] = (2 / num_points) * np.sum(coord * np.sin(j * s))
    return a, b


def hamiltonian_relax(points, iterations=1500, k_spring=5.0, q_repulse=0.05, alpha=0.005,
                      grad_clip=5.0, log_fn=None):
    """Hamiltoniaanse gradient-afstroming (elastisch + repulsie)."""
    pts = points.copy()
    N = len(pts)

    def log(msg):
        if log_fn:
            log_fn(msg)

    log(f"[*] Minimaliseren van interactie-energie ({iterations} iteraties)...")
    for step in range(iterations):
        lengths = np.linalg.norm(np.diff(np.vstack((pts, [pts[0]])), axis=0), axis=1)
        l0 = np.mean(lengths)

        pts_next = np.roll(pts, -1, axis=0)
        pts_prev = np.roll(pts, 1, axis=0)

        v_next = pts_next - pts
        d_next = np.linalg.norm(v_next, axis=1, keepdims=True)
        f_next = k_spring * (d_next - l0) * (v_next / (d_next + 1e-9))

        v_prev = pts_prev - pts
        d_prev = np.linalg.norm(v_prev, axis=1, keepdims=True)
        f_prev = k_spring * (d_prev - l0) * (v_prev / (d_prev + 1e-9))

        f_elastic = f_next + f_prev

        diff = pts[:, np.newaxis, :] - pts[np.newaxis, :, :]
        dist = np.linalg.norm(diff, axis=2)

        mask = np.ones((N, N), dtype=bool)
        np.fill_diagonal(mask, False)
        for i in range(N):
            mask[i, (i + 1) % N] = False
            mask[i, (i - 1) % N] = False

        dist[~mask] = 1e9
        f_rep_mag = q_repulse / (dist ** 3 + 1e-9)
        f_rep_mag[~mask] = 0.0

        f_repulsion = np.sum(diff * f_rep_mag[:, :, np.newaxis], axis=1)

        grad = -f_elastic - f_repulsion
        grad_norm = np.linalg.norm(grad, axis=1, keepdims=True)
        grad = np.where(grad_norm > grad_clip, grad * (grad_clip / (grad_norm + 1e-12)), grad)

        pts -= alpha * grad
        pts -= np.mean(pts, axis=0)  # keep centered

        # optioneel: beperkte progress logging
        if (step + 1) % max(1, iterations // 10) == 0:
            log(f"    iter {step + 1}/{iterations}")

    return pts


def generate_sst_pipeline(ab_id, knot_name,
                          url="https://katlas.org/images/d/d2/Ideal.txt.gz",
                          gz_name="Ideal.txt.gz",
                          txt_name="Ideal.txt",
                          max_j_out=50, iterations=1500, num_points=300,
                          k_spring=5.0, q_repulse=0.05, alpha=0.005, grad_clip=5.0,
                          do_arclength_pre=True, do_arclength_post=True,
                          do_center_post=True,
                          out_dir=(str(get_exports_dir()) if get_exports_dir else "."),
                          insert_j0_row=False,
                          canonicalize_out=False,
                          log_fn=None):
    """Volledige pipeline: Ideal DB -> punten -> arclength -> relax -> Fourier -> export."""
    def log(msg):
        if log_fn:
            log_fn(msg)

    log(f"\n[*] Start SST-integratie pipeline: {knot_name} (AB Id: {ab_id})")
    db_path = prepare_database(url=url, gz_name=gz_name, txt_name=txt_name, log_fn=log_fn)
    ideal_data = Path(db_path).read_text(encoding="utf-8", errors="ignore")

    block = extract_ab_block(ideal_data, ab_id)
    raw_coeffs = parse_coeffs(block)
    if not raw_coeffs:
        raise ValueError("Geen Coeff records gevonden in AB block.")

    max_j_in = max(raw_coeffs.keys())
    log(f"[*] Gevonden Fourier-coeffs in DB: j=1..{max_j_in}")

    # Ruimtelijke reconstructie
    t = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    pts = np.zeros((num_points, 3))
    for j in range(1, max_j_in + 1):
        if j in raw_coeffs:
            A, B = raw_coeffs[j]
            ax, ay, az = A
            bx, by, bz = B
            cos_jt = np.cos(j * t)
            sin_jt = np.sin(j * t)
            pts[:, 0] += ax * cos_jt + bx * sin_jt
            pts[:, 1] += ay * cos_jt + by * sin_jt
            pts[:, 2] += az * cos_jt + bz * sin_jt

    if do_arclength_pre:
        pts = normalize_arclength(pts, num_points)

    # Relax
    pts = hamiltonian_relax(pts, iterations=iterations, k_spring=k_spring, q_repulse=q_repulse,
                            alpha=alpha, grad_clip=grad_clip, log_fn=log_fn)

    if do_arclength_post:
        pts = normalize_arclength(pts, num_points)

    if do_center_post:
        pts -= np.mean(pts, axis=0)

    # Fourier projectie (j=1..max_j_out)
    log(f"[*] Transformeren naar SST Canon format (j_max = {max_j_out})...")
    s_param = np.linspace(0, 2 * np.pi, num_points, endpoint=False)

    ax, bx = calculate_fourier(pts[:, 0], s_param, max_j_out, num_points)
    ay, by = calculate_fourier(pts[:, 1], s_param, max_j_out, num_points)
    az, bz = calculate_fourier(pts[:, 2], s_param, max_j_out, num_points)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{knot_name}_sst.fseries"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"% (Fourier projection from Ideal database for SST Canon: {knot_name} | AB Id: {ab_id})\n")
        f.write("% lines  a_x(j) b_x(j)  a_y(j) b_y(j)  a_z(j) b_z(j)\n")

        if insert_j0_row:
            f.write(f"{0.0: 9.6f} {0.0: 9.6f} {0.0: 9.6f} {0.0: 9.6f} {0.0: 9.6f} {0.0: 9.6f}\n")

        for j in range(max_j_out):
            f.write(f"{ax[j]: 9.6f} {bx[j]: 9.6f} {ay[j]: 9.6f} {by[j]: 9.6f} {az[j]: 9.6f} {bz[j]: 9.6f}\n")

    if canonicalize_out:
        canonicalize_fseries_to_j0(str(out_path), out_path=str(out_path), tol=1e-12)

    log(f"[+] Succes! Geoptimaliseerde inbedding weggeschreven naar '{out_path}'")
    return str(out_path), pts, raw_coeffs


def read_fseries(path):
    """Leest .fseries: headers (%) + numeric rows (6 kolommen)."""
    headers = []
    rows = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.strip():
                continue
            if line.lstrip().startswith("%"):
                headers.append(line.rstrip("\n"))
                continue
            parts = line.split()
            if len(parts) != 6:
                raise ValueError(f"{path}: verwacht 6 kolommen, kreeg {len(parts)}")
            rows.append(list(map(float, parts)))
    arr = np.array(rows, dtype=float)
    return headers, arr


def canonicalize_fseries_to_j0(in_path, out_path=None, tol=1e-12):
    """Voegt j=0 nulrij toe als die ontbreekt (robuste standaardisatie)."""
    if out_path is None:
        out_path = in_path

    headers, arr = read_fseries(in_path)
    if arr.size == 0:
        raise ValueError(f"{in_path}: geen data rijen gevonden")

    # Als eerste rij al ~0: beschouw die als j=0
    if not np.all(np.abs(arr[0]) < tol):
        arr = np.vstack([np.zeros(6), arr])

    with open(out_path, "w", encoding="utf-8") as f:
        for h in headers:
            f.write(h + "\n")
        for r in arr:
            f.write(f"{r[0]: .6f} {r[1]: .6f} {r[2]: .6f} {r[3]: .6f} {r[4]: .6f} {r[5]: .6f}\n")

    return out_path


def eval_fourier_block(coeffs, s, mode="auto", tol=1e-12):
    """
    Evaluator voor 6-kolom fseries arrays (coeffs = Nx6 array).
    fseries_compat convention: file row index = harmonic index j; evaluators use j=0..N-1.
    mode:
      - "auto": detect j0 row via b(0) ~ 0 → then n=j
      - "j0": forceer n=j (row index = j)
      - "j1": forceer n=j+1 (legacy)
    """
    ax = coeffs[:, 0]; bx = coeffs[:, 1]
    ay = coeffs[:, 2]; by = coeffs[:, 3]
    az = coeffs[:, 4]; bz = coeffs[:, 5]

    if mode == "auto":
        row0_sine_mag = abs(bx[0]) + abs(by[0]) + abs(bz[0])
        uses_j0_row = (row0_sine_mag < tol)
    elif mode == "j0":
        uses_j0_row = True
    elif mode == "j1":
        uses_j0_row = False
    else:
        raise ValueError("mode must be auto|j0|j1")

    x = np.zeros_like(s, dtype=float)
    y = np.zeros_like(s, dtype=float)
    z = np.zeros_like(s, dtype=float)

    for j in range(len(ax)):
        n = j if uses_j0_row else (j + 1)
        x += ax[j] * np.cos(n * s) + bx[j] * np.sin(n * s)
        y += ay[j] * np.cos(n * s) + by[j] * np.sin(n * s)
        z += az[j] * np.cos(n * s) + bz[j] * np.sin(n * s)

    return np.stack((x, y, z), axis=1)


# ---------------------------
# GUI
# ---------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SST Ideal -> Hamiltonian -> fseries (Full GUI)")
        self.geometry("1200x800")

        self.log_q = queue.Queue()
        self.worker = None

        self._build_ui()
        self.after(100, self._drain_log_queue)

    def log(self, msg):
        self.log_q.put(msg)

    def _drain_log_queue(self):
        try:
            while True:
                msg = self.log_q.get_nowait()
                self.txt_log.configure(state="normal")
                self.txt_log.insert("end", msg + "\n")
                self.txt_log.see("end")
                self.txt_log.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self._drain_log_queue)

    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # Tabs
        self.tab_db = ttk.Frame(nb)
        self.tab_extract = ttk.Frame(nb)
        self.tab_single = ttk.Frame(nb)
        self.tab_batch = ttk.Frame(nb)
        self.tab_tools = ttk.Frame(nb)
        self.tab_log = ttk.Frame(nb)

        nb.add(self.tab_db, text="Database")
        nb.add(self.tab_extract, text="Extract/Inspect")
        nb.add(self.tab_single, text="Single Pipeline")
        nb.add(self.tab_batch, text="Batch")
        nb.add(self.tab_tools, text="Tools (fseries)")
        nb.add(self.tab_log, text="Log")

        self._build_db_tab()
        self._build_extract_tab()
        self._build_single_tab()
        self._build_batch_tab()
        self._build_tools_tab()
        self._build_log_tab()

    # -------- Database Tab --------
    def _build_db_tab(self):
        frm = self.tab_db

        self.var_url = tk.StringVar(value="https://katlas.org/images/d/d2/Ideal.txt.gz")
        self.var_gz = tk.StringVar(value="Ideal.txt.gz")
        self.var_txt = tk.StringVar(value="Ideal.txt")

        row = 0
        ttk.Label(frm, text="URL Ideal.txt.gz:").grid(row=row, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_url, width=100).grid(row=row, column=1, sticky="we", padx=8, pady=6)
        row += 1

        ttk.Label(frm, text="Local .gz path:").grid(row=row, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_gz, width=60).grid(row=row, column=1, sticky="w", padx=8, pady=6)
        ttk.Button(frm, text="Browse", command=self._browse_gz).grid(row=row, column=2, sticky="w", padx=8, pady=6)
        row += 1

        ttk.Label(frm, text="Local .txt path:").grid(row=row, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_txt, width=60).grid(row=row, column=1, sticky="w", padx=8, pady=6)
        ttk.Button(frm, text="Browse", command=self._browse_txt).grid(row=row, column=2, sticky="w", padx=8, pady=6)
        row += 1

        btns = ttk.Frame(frm)
        btns.grid(row=row, column=0, columnspan=3, sticky="w", padx=8, pady=10)

        ttk.Button(btns, text="Prepare (download+decompress if needed)", command=self._db_prepare).pack(side="left", padx=6)
        ttk.Button(btns, text="Check exists", command=self._db_check).pack(side="left", padx=6)

        frm.columnconfigure(1, weight=1)

    def _browse_gz(self):
        p = filedialog.askopenfilename(title="Select Ideal.txt.gz", filetypes=[("GZ", "*.gz"), ("All", "*.*")])
        if p:
            self.var_gz.set(p)

    def _browse_txt(self):
        p = filedialog.askopenfilename(title="Select Ideal.txt", filetypes=[("TXT", "*.txt"), ("All", "*.*")])
        if p:
            self.var_txt.set(p)

    def _db_prepare(self):
        self._run_threaded(self._db_prepare_worker)

    def _db_prepare_worker(self):
        try:
            dbp = prepare_database(url=self.var_url.get(),
                                   gz_name=self.var_gz.get(),
                                   txt_name=self.var_txt.get(),
                                   log_fn=self.log)
            self.log(f"[+] DB ready: {dbp}")
        except Exception as e:
            self.log(f"[!] DB prepare error: {e}")

    def _db_check(self):
        gz = Path(self.var_gz.get())
        tx = Path(self.var_txt.get())
        self.log(f"[*] gz exists: {gz.exists()}  | {gz}")
        self.log(f"[*] txt exists: {tx.exists()} | {tx}")

    # -------- Extract Tab --------
    def _build_extract_tab(self):
        frm = self.tab_extract

        self.var_abid = tk.StringVar(value="9:1:2")

        top = ttk.Frame(frm)
        top.pack(fill="x", padx=8, pady=8)

        ttk.Label(top, text="AB Id:").pack(side="left")
        ttk.Entry(top, textvariable=self.var_abid, width=20).pack(side="left", padx=6)
        ttk.Button(top, text="Extract AB block", command=self._extract_ab).pack(side="left", padx=6)
        ttk.Button(top, text="Parse Coeffs", command=self._parse_ab).pack(side="left", padx=6)

        self.txt_ab = ScrolledText(frm, height=25)
        self.txt_ab.pack(fill="both", expand=True, padx=8, pady=8)

        self.lbl_coeff_info = ttk.Label(frm, text="Coeff info: -")
        self.lbl_coeff_info.pack(anchor="w", padx=8, pady=4)

        self._last_ab_block = None
        self._last_coeffs = None

    def _extract_ab(self):
        self._run_threaded(self._extract_ab_worker)

    def _extract_ab_worker(self):
        try:
            dbp = prepare_database(url=self.var_url.get(),
                                   gz_name=self.var_gz.get(),
                                   txt_name=self.var_txt.get(),
                                   log_fn=self.log)
            ideal_data = Path(dbp).read_text(encoding="utf-8", errors="ignore")
            block = extract_ab_block(ideal_data, self.var_abid.get().strip())
            self._last_ab_block = block
            self.log("[+] AB block extracted.")
            self._ui_set_text(self.txt_ab, block[:200000])  # cap preview
        except Exception as e:
            self.log(f"[!] Extract error: {e}")

    def _parse_ab(self):
        if not self._last_ab_block:
            messagebox.showwarning("No AB block", "Extract eerst een AB block.")
            return
        try:
            coeffs = parse_coeffs(self._last_ab_block)
            self._last_coeffs = coeffs
            if coeffs:
                mx = max(coeffs.keys())
                self.lbl_coeff_info.config(text=f"Coeff info: {len(coeffs)} records, max j = {mx}")
                self.log(f"[+] Parsed coeffs: count={len(coeffs)}, max j={mx}")
            else:
                self.lbl_coeff_info.config(text="Coeff info: 0 records")
                self.log("[!] Parsed coeffs: 0 records")
        except Exception as e:
            self.log(f"[!] Parse error: {e}")

    def _ui_set_text(self, widget, text):
        def do():
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.insert("end", text)
            widget.configure(state="normal")
        self.after(0, do)

    # -------- Single Pipeline Tab --------
    def _build_single_tab(self):
        frm = self.tab_single

        self.var_knot_name = tk.StringVar(value="knot_9_2")
        default_outdir = str(get_exports_dir()) if get_exports_dir else str(Path(".").resolve())
        self.var_outdir = tk.StringVar(value=default_outdir)
        self.var_maxj = tk.IntVar(value=50)
        self.var_iters = tk.IntVar(value=1500)
        self.var_npts = tk.IntVar(value=300)

        self.var_k_spring = tk.DoubleVar(value=5.0)
        self.var_q_repulse = tk.DoubleVar(value=0.05)
        self.var_alpha = tk.DoubleVar(value=0.005)
        self.var_grad_clip = tk.DoubleVar(value=5.0)

        self.var_pre_arc = tk.BooleanVar(value=True)
        self.var_post_arc = tk.BooleanVar(value=True)
        self.var_center_post = tk.BooleanVar(value=True)

        self.var_insert_j0 = tk.BooleanVar(value=False)
        self.var_canon_out = tk.BooleanVar(value=False)

        self.var_preview_after = tk.StringVar(value="post")  # none|pre|post

        grid = ttk.Frame(frm)
        grid.pack(fill="both", expand=False, padx=8, pady=8)

        r = 0
        ttk.Label(grid, text="Knot name:").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(grid, textvariable=self.var_knot_name, width=30).grid(row=r, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(grid, text="AB Id:").grid(row=r, column=2, sticky="w", padx=6, pady=4)
        ttk.Entry(grid, textvariable=self.var_abid, width=15).grid(row=r, column=3, sticky="w", padx=6, pady=4)
        r += 1

        ttk.Label(grid, text="Output dir:").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(grid, textvariable=self.var_outdir, width=80).grid(row=r, column=1, columnspan=2, sticky="we", padx=6, pady=4)
        ttk.Button(grid, text="Browse", command=self._browse_outdir).grid(row=r, column=3, sticky="w", padx=6, pady=4)
        r += 1

        ttk.Label(grid, text="max_j_out:").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(grid, textvariable=self.var_maxj, width=10).grid(row=r, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(grid, text="iterations:").grid(row=r, column=2, sticky="w", padx=6, pady=4)
        ttk.Entry(grid, textvariable=self.var_iters, width=10).grid(row=r, column=3, sticky="w", padx=6, pady=4)
        r += 1

        ttk.Label(grid, text="num_points:").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(grid, textvariable=self.var_npts, width=10).grid(row=r, column=1, sticky="w", padx=6, pady=4)
        r += 1

        sep = ttk.Separator(grid, orient="horizontal")
        sep.grid(row=r, column=0, columnspan=4, sticky="we", pady=8)
        r += 1

        ttk.Label(grid, text="k_spring:").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(grid, textvariable=self.var_k_spring, width=10).grid(row=r, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(grid, text="q_repulse:").grid(row=r, column=2, sticky="w", padx=6, pady=4)
        ttk.Entry(grid, textvariable=self.var_q_repulse, width=10).grid(row=r, column=3, sticky="w", padx=6, pady=4)
        r += 1

        ttk.Label(grid, text="alpha:").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(grid, textvariable=self.var_alpha, width=10).grid(row=r, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(grid, text="grad_clip:").grid(row=r, column=2, sticky="w", padx=6, pady=4)
        ttk.Entry(grid, textvariable=self.var_grad_clip, width=10).grid(row=r, column=3, sticky="w", padx=6, pady=4)
        r += 1

        sep2 = ttk.Separator(grid, orient="horizontal")
        sep2.grid(row=r, column=0, columnspan=4, sticky="we", pady=8)
        r += 1

        ttk.Checkbutton(grid, text="Arclength pre", variable=self.var_pre_arc).grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Checkbutton(grid, text="Arclength post", variable=self.var_post_arc).grid(row=r, column=1, sticky="w", padx=6, pady=4)
        ttk.Checkbutton(grid, text="Center post", variable=self.var_center_post).grid(row=r, column=2, sticky="w", padx=6, pady=4)
        r += 1

        ttk.Checkbutton(grid, text="Insert j=0 zero row in export", variable=self.var_insert_j0).grid(row=r, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        ttk.Checkbutton(grid, text="Canonicalize output to j0 (force)", variable=self.var_canon_out).grid(row=r, column=2, columnspan=2, sticky="w", padx=6, pady=4)
        r += 1

        ttk.Label(grid, text="Preview points:").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(grid, textvariable=self.var_preview_after, values=["none", "pre", "post"], width=10, state="readonly").grid(row=r, column=1, sticky="w", padx=6, pady=4)
        r += 1

        btns = ttk.Frame(frm)
        btns.pack(fill="x", padx=8, pady=8)
        ttk.Button(btns, text="RUN Single Pipeline", command=self._run_single).pack(side="left", padx=6)
        ttk.Button(btns, text="Open output dir", command=self._open_outdir).pack(side="left", padx=6)

        grid.columnconfigure(1, weight=1)

        # last outputs
        self.var_last_out = tk.StringVar(value="-")
        ttk.Label(frm, textvariable=self.var_last_out).pack(anchor="w", padx=10, pady=6)

    def _browse_outdir(self):
        p = filedialog.askdirectory(title="Select output directory")
        if p:
            self.var_outdir.set(p)

    def _open_outdir(self):
        p = self.var_outdir.get()
        if p and Path(p).exists():
            try:
                os.startfile(p)  # Windows
            except Exception:
                messagebox.showinfo("Info", f"Open handmatig: {p}")

    def _run_single(self):
        self._run_threaded(self._run_single_worker)

    def _run_single_worker(self):
        try:
            out_path, pts, raw_coeffs = generate_sst_pipeline(
                ab_id=self.var_abid.get().strip(),
                knot_name=self.var_knot_name.get().strip(),
                url=self.var_url.get().strip(),
                gz_name=self.var_gz.get().strip(),
                txt_name=self.var_txt.get().strip(),
                max_j_out=int(self.var_maxj.get()),
                iterations=int(self.var_iters.get()),
                num_points=int(self.var_npts.get()),
                k_spring=float(self.var_k_spring.get()),
                q_repulse=float(self.var_q_repulse.get()),
                alpha=float(self.var_alpha.get()),
                grad_clip=float(self.var_grad_clip.get()),
                do_arclength_pre=bool(self.var_pre_arc.get()),
                do_arclength_post=bool(self.var_post_arc.get()),
                do_center_post=bool(self.var_center_post.get()),
                out_dir=self.var_outdir.get().strip(),
                insert_j0_row=bool(self.var_insert_j0.get()),
                canonicalize_out=bool(self.var_canon_out.get()),
                log_fn=self.log
            )
            self.after(0, lambda: self.var_last_out.set(f"Last output: {out_path}"))

            # preview points (optional)
            mode = self.var_preview_after.get()
            if mode != "none" and HAVE_MPL:
                self._plot_points(pts, title=f"{self.var_knot_name.get()} ({mode})")
            elif mode != "none" and not HAVE_MPL:
                self.log("[!] matplotlib not available -> preview disabled.")
        except Exception as e:
            self.log(f"[!] Single pipeline error: {e}")

    # -------- Batch Tab --------
    def _build_batch_tab(self):
        frm = self.tab_batch

        top = ttk.Frame(frm)
        top.pack(fill="x", padx=8, pady=8)

        ttk.Button(top, text="Load default catalog", command=self._batch_load_default).pack(side="left", padx=6)
        ttk.Button(top, text="Add row", command=self._batch_add_row).pack(side="left", padx=6)
        ttk.Button(top, text="Remove selected", command=self._batch_remove_selected).pack(side="left", padx=6)
        ttk.Button(top, text="RUN Batch", command=self._batch_run).pack(side="left", padx=6)

        cols = ("name", "ab_id", "enabled")
        self.tree = ttk.Treeview(frm, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=200 if c != "enabled" else 80, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        self._batch_load_default()

    def _batch_load_default(self):
        self.tree.delete(*self.tree.get_children())
        knopen_catalogus = {
            "knot_3_1": "3:1:1",
            "knot_4_1": "4:1:1",
            "knot_5_1": "5:1:1",
            "knot_5_2": "5:1:2",
            "knot_6_1": "6:1:1",
            "knot_7_1": "7:1:1",
            "knot_7_2": "7:1:2",
            "knot_8_1": "8:1:1",
            "knot_9_1": "9:1:1",
            "knot_9_2": "9:1:2",
            "knot_10_1": "10:1:1",
        }
        for name, ab in knopen_catalogus.items():
            self.tree.insert("", "end", values=(name, ab, "yes"))

    def _batch_add_row(self):
        self.tree.insert("", "end", values=("knot_new", "0:0:0", "yes"))

    def _batch_remove_selected(self):
        sel = self.tree.selection()
        for it in sel:
            self.tree.delete(it)

    def _batch_run(self):
        self._run_threaded(self._batch_run_worker)

    def _batch_run_worker(self):
        items = []
        for it in self.tree.get_children():
            name, ab, en = self.tree.item(it, "values")
            if str(en).lower() in ("yes", "true", "1", "on"):
                items.append((name, ab))

        self.log(f"\n[*] Start batch-verwerking van {len(items)} topologieën...")
        for idx, (name, ab) in enumerate(items, start=1):
            try:
                self.log(f"--- [{idx}/{len(items)}] {name} ({ab}) ---")
                generate_sst_pipeline(
                    ab_id=ab,
                    knot_name=name,
                    url=self.var_url.get().strip(),
                    gz_name=self.var_gz.get().strip(),
                    txt_name=self.var_txt.get().strip(),
                    max_j_out=int(self.var_maxj.get()),
                    iterations=int(self.var_iters.get()),
                    num_points=int(self.var_npts.get()),
                    k_spring=float(self.var_k_spring.get()),
                    q_repulse=float(self.var_q_repulse.get()),
                    alpha=float(self.var_alpha.get()),
                    grad_clip=float(self.var_grad_clip.get()),
                    do_arclength_pre=bool(self.var_pre_arc.get()),
                    do_arclength_post=bool(self.var_post_arc.get()),
                    do_center_post=bool(self.var_center_post.get()),
                    out_dir=self.var_outdir.get().strip(),
                    insert_j0_row=bool(self.var_insert_j0.get()),
                    canonicalize_out=bool(self.var_canon_out.get()),
                    log_fn=self.log
                )
            except Exception as e:
                self.log(f"[!] Batch error for {name} ({ab}): {e}")

        self.log("\n[+] Batch-executie voltooid.")

    # -------- Tools Tab --------
    def _build_tools_tab(self):
        frm = self.tab_tools

        self.var_fseries_path = tk.StringVar(value="")
        self.var_eval_mode = tk.StringVar(value="auto")
        self.var_plot_n = tk.IntVar(value=600)

        top = ttk.Frame(frm)
        top.pack(fill="x", padx=8, pady=8)

        ttk.Label(top, text="fseries file:").pack(side="left")
        ttk.Entry(top, textvariable=self.var_fseries_path, width=80).pack(side="left", padx=6)
        ttk.Button(top, text="Browse", command=self._browse_fseries).pack(side="left", padx=6)

        actions = ttk.Frame(frm)
        actions.pack(fill="x", padx=8, pady=8)

        ttk.Button(actions, text="Read & Preview (first 200 lines)", command=self._tool_preview).pack(side="left", padx=6)
        ttk.Button(actions, text="Canonicalize -> j0", command=self._tool_canonicalize).pack(side="left", padx=6)

        ttk.Label(actions, text="Eval mode:").pack(side="left", padx=10)
        ttk.Combobox(actions, textvariable=self.var_eval_mode, values=["auto", "j0", "j1"], state="readonly", width=8).pack(side="left")
        ttk.Label(actions, text="Plot N:").pack(side="left", padx=10)
        ttk.Entry(actions, textvariable=self.var_plot_n, width=8).pack(side="left")
        ttk.Button(actions, text="Evaluate & Plot", command=self._tool_plot).pack(side="left", padx=6)

        self.txt_tools = ScrolledText(frm, height=25)
        self.txt_tools.pack(fill="both", expand=True, padx=8, pady=8)

    def _browse_fseries(self):
        p = filedialog.askopenfilename(title="Select .fseries", filetypes=[("FSERIES", "*.fseries"), ("All", "*.*")])
        if p:
            self.var_fseries_path.set(p)

    def _tool_preview(self):
        p = self.var_fseries_path.get().strip()
        if not p:
            messagebox.showwarning("No file", "Selecteer eerst een .fseries bestand.")
            return
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for i, line in enumerate(f):
                    lines.append(line.rstrip("\n"))
                    if i >= 199:
                        break
            self._ui_set_text(self.txt_tools, "\n".join(lines))
            self.log(f"[+] Preview loaded: {p}")
        except Exception as e:
            self.log(f"[!] Preview error: {e}")

    def _tool_canonicalize(self):
        p = self.var_fseries_path.get().strip()
        if not p:
            messagebox.showwarning("No file", "Selecteer eerst een .fseries bestand.")
            return
        try:
            canonicalize_fseries_to_j0(p, out_path=p, tol=1e-12)
            self.log(f"[+] Canonicalized (j0) in-place: {p}")
        except Exception as e:
            self.log(f"[!] Canonicalize error: {e}")

    def _tool_plot(self):
        if not HAVE_MPL:
            messagebox.showwarning("No matplotlib", "matplotlib ontbreekt. Installeer: pip install matplotlib")
            return
        p = self.var_fseries_path.get().strip()
        if not p:
            messagebox.showwarning("No file", "Selecteer eerst een .fseries bestand.")
            return
        try:
            headers, arr = read_fseries(p)
            N = int(self.var_plot_n.get())
            s = np.linspace(0, 2 * np.pi, N, endpoint=False)
            pts = eval_fourier_block(arr, s, mode=self.var_eval_mode.get(), tol=1e-12)
            self._plot_points(pts, title=f"Eval {Path(p).name} [{self.var_eval_mode.get()}]")
        except Exception as e:
            self.log(f"[!] Plot error: {e}")

    # -------- Log Tab --------
    def _build_log_tab(self):
        frm = self.tab_log
        self.txt_log = ScrolledText(frm, height=40)
        self.txt_log.pack(fill="both", expand=True, padx=8, pady=8)
        self.txt_log.configure(state="disabled")

    # -------- threading helper --------
    def _run_threaded(self, target):
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("Busy", "Er draait al een worker thread.")
            return
        self.worker = threading.Thread(target=target, daemon=True)
        self.worker.start()

    # -------- plot helper --------
    def _plot_points(self, pts, title="preview"):
        if not HAVE_MPL:
            return
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("900x700")

        fig = Figure(figsize=(7, 6), dpi=100)
        ax = fig.add_subplot(111, projection="3d")
        ax.plot(pts[:, 0], pts[:, 1], pts[:, 2])
        ax.set_title(title)

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()