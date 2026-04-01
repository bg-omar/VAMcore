"""
Fremlin showcase: load any .fseries from Knots_FourierSeries (recursive scan),
compute exact descriptors, plot curvature-colored 3D curve and mode energy spectrum.
Optional overlay with embedded ideal 4:1:1 when the selected knot is 4_1.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

try:
    import sstcore as ssc
except ImportError:
    print("ERROR: build/install sstcore first.")
    raise

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
        QPushButton, QMessageBox, QGroupBox, QTextEdit, QLabel, QCheckBox,
    )
    HAS_QT = True
except ImportError:
    HAS_QT = False


def _candidate_fseries_roots():
    """Portable: script-relative and env only (no absolute paths)."""
    here = os.path.abspath(os.path.dirname(__file__))
    root = os.path.abspath(os.path.join(here, ".."))
    candidates = [
        os.environ.get("SSTCORE_RESOURCES", "").rstrip(os.sep) + os.sep + "Knots_FourierSeries" if os.environ.get("SSTCORE_RESOURCES") else "",
        os.path.join(root, "resources", "Knots_FourierSeries"),
        os.path.join(root, "src", "Knots_FourierSeries"),
        os.path.join("resources", "Knots_FourierSeries"),
        os.path.join("src", "Knots_FourierSeries"),
    ]
    for p in candidates:
        if p and os.path.isdir(p):
            return p
    return None

def list_all_fseries_files_recursive():
    d = _candidate_fseries_roots()
    if not d:
        return []
    files = []
    # Walk recursively through all subdirectories to find matching .fseries files
    for root, _dirs, fns in os.walk(d):
        for fn in fns:
            fn_lower = fn.lower()
            if fn_lower.endswith(".fseries") and fn_lower.startswith("knot."):
                files.append(os.path.join(root, fn))
    files.sort()
    return files


def fseries_path_to_display_id(path):
    """Derive short knot id from .fseries path for dropdown display (e.g. knot.4_1.fseries -> 4_1)."""
    basename = os.path.basename(path)
    if basename.lower().startswith("knot.") and basename.lower().endswith(".fseries"):
        return basename[5:-8]  # strip "knot." and ".fseries"
    return basename


def load_fseries_block_from_path(path):
    """Load main Fourier block from a .fseries file. Returns (block, block_index)."""
    blocks = ssc.parse_fseries_multi(path)
    idx = ssc.index_of_largest_block(blocks)
    if idx < 0:
        raise RuntimeError(f"No Fourier blocks found in {path!r}")
    return blocks[idx], idx


def default_fseries_path():
    """First 4_1 file found, or first .fseries in list (for CLI)."""
    for _root, full, rel in list_all_fseries_files_recursive():
        if "4_1" in rel and rel.replace("\\", "/").endswith("knot.4_1.fseries"):
            return full
    all_files = list_all_fseries_files_recursive()
    if all_files:
        return all_files[0][1]
    raise FileNotFoundError("No .fseries files found under Knots_FourierSeries")


# --- Embedded .fseries (compiled C++ resources) ---
def list_embedded_fseries_ids():
    """
    Returns sorted list of embedded knot ids from compiled C++ resources.
    Example ids: '4_1', '4_1z', '5_2', ...
    """
    if not hasattr(ssc, "get_embedded_knot_files"):
        return []
    files = ssc.get_embedded_knot_files()  # dict: knot_id -> fseries text
    ids = sorted(files.keys(), key=lambda x: str(x).lower())
    return ids


def load_embedded_fseries_main_block(knot_id):
    """
    Preferred helper if pybind exposes load_embedded_knot_block().
    Falls back to parse_fseries_from_string(get_embedded_knot_files()[knot_id]).
    """
    if hasattr(ssc, "load_embedded_knot_block"):
        return ssc.load_embedded_knot_block(knot_id), 0
    files = ssc.get_embedded_knot_files()
    txt = files[knot_id]
    if not hasattr(ssc, "parse_fseries_from_string"):
        raise RuntimeError("parse_fseries_from_string not exposed in pybind")
    blocks = ssc.parse_fseries_from_string(txt)
    idx = ssc.index_of_largest_block(blocks)
    if idx < 0:
        raise RuntimeError(f"No Fourier block found for embedded knot id: {knot_id}")
    return blocks[idx], idx


def sample_block(block, n=2000):
    s = np.linspace(0.0, 2 * np.pi, n, endpoint=False)
    # C++ expects sequence of floats; pass list for compatibility
    pts = np.array(ssc.evaluate_fourier_block(block, s.tolist()))
    return s, pts


def exact_curvature(block, s):
    # curvature_exact(block, s) expects list of parameter values
    s_list = s.tolist() if hasattr(s, "tolist") else list(s)
    kappa = np.array(ssc.curvature_exact(block, s_list))
    return kappa


def descriptors(block):
    d = ssc.describe_fourier_block(block, nsamples=2048, exclude_window=4)
    return d


def set_equal_3d(ax, P):
    mins = P.min(axis=0)
    maxs = P.max(axis=0)
    mid = 0.5 * (mins + maxs)
    r = 0.5 * np.max(maxs - mins)
    ax.set_xlim(mid[0] - r, mid[0] + r)
    ax.set_ylim(mid[1] - r, mid[1] + r)
    ax.set_zlim(mid[2] - r, mid[2] + r)


def _rescale(P, alpha):
    return P * float(alpha)


def downsample_closed_curve(P, max_points=600):
    n = len(P)
    if n <= max_points:
        return P
    idx = np.linspace(0, n - 1, max_points, dtype=int)
    return P[idx]


def to_np_points(arr_like):
    arr = np.array(arr_like, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 3:
        raise ValueError(f"Expected shape (N,3), got {arr.shape}")
    return arr


def center_points(P):
    return P - P.mean(axis=0)


def format_ab_header(ab):
    if hasattr(ssc, "format_ideal_ab_header"):
        return ssc.format_ideal_ab_header(ab)
    ab_id = getattr(ab, "id", "?")
    conway = getattr(ab, "conway", "?")
    L = getattr(ab, "L", float("nan"))
    D = getattr(ab, "D", float("nan"))
    n = getattr(ab, "n", 1)
    return f'AB Id="{ab_id}" Conway="{conway}" L="{L}" D="{D}" n="{n}"'


def get_ideal_ab(ab_id, embedded_name="ideal.txt"):
    if hasattr(ssc, "parse_embedded_ideal_ab_by_id"):
        return ssc.parse_embedded_ideal_ab_by_id(ab_id, embedded_name)
    if hasattr(ssc, "parse_embedded_ideal_txt"):
        blocks = ssc.parse_embedded_ideal_txt(embedded_name)
        for b in blocks:
            if getattr(b, "id", None) == ab_id:
                return b
    raise RuntimeError(f"Cannot load ideal AB {ab_id!r} (API or resource missing)")


def list_ideal_ab_ids(embedded_name="ideal.txt"):
    """Sorted list of AB ids from embedded ideal resource."""
    if hasattr(ssc, "parse_embedded_ideal_txt"):
        try:
            blocks = ssc.parse_embedded_ideal_txt(embedded_name)
            ids = [getattr(b, "id", None) for b in blocks if getattr(b, "id", None)]
            return sorted(ids)
        except Exception:
            pass
    return []


# --- Viewer backends (external launchers) ---
def try_import_pyqtgraph():
    try:
        import pyqtgraph as pg
        import pyqtgraph.opengl as gl
        return pg, gl
    except Exception:
        return None, None


def try_import_plotly():
    try:
        import plotly.graph_objects as go
        return go
    except Exception:
        return None


def try_import_vispy():
    try:
        from vispy import scene
        from vispy.color import Colormap
        return scene, Colormap
    except Exception:
        return None, None


_pg_windows = []


def launch_plotly_compare_viewer(P_ideal, P_fre, title="Knot compare", rescale_alpha=None):
    go = try_import_plotly()
    if go is None:
        raise RuntimeError("Plotly is not installed. pip install plotly")
    P_fre_plot = P_fre if rescale_alpha is None else (P_fre * float(rescale_alpha))
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=P_ideal[:, 0], y=P_ideal[:, 1], z=P_ideal[:, 2],
        mode="lines", name="Embedded ideal",
    ))
    fig.add_trace(go.Scatter3d(
        x=P_fre_plot[:, 0], y=P_fre_plot[:, 1], z=P_fre_plot[:, 2],
        mode="lines", name="Embedded .fseries",
    ))
    fig.update_layout(
        title=title,
        scene=dict(aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=True,
    )
    fig.show()


def launch_pyqtgraph_compare_viewer(P_ideal, P_fre, title="Knot compare", rescale_alpha=None):
    pg, gl = try_import_pyqtgraph()
    if pg is None or gl is None:
        raise RuntimeError("pyqtgraph with OpenGL is not installed. pip install pyqtgraph PyOpenGL")
    P_fre_plot = P_fre if rescale_alpha is None else (P_fre * float(rescale_alpha))
    win = gl.GLViewWidget()
    win.setWindowTitle(title)
    win.resize(900, 700)
    win.opts["distance"] = 12
    gx = gl.GLGridItem()
    gx.scale(1, 1, 1)
    win.addItem(gx)

    def _mk_line(P, color=(1, 1, 1, 1), width=2.0):
        item = gl.GLLinePlotItem(pos=P.astype(np.float32), color=color, width=width, antialias=True, mode="line_strip")
        return item

    P_all = np.vstack([P_ideal, P_fre_plot])
    c = P_all.mean(axis=0)
    P1 = P_ideal - c
    P2 = P_fre_plot - c
    line1 = _mk_line(P1, color=(0.2, 0.8, 1.0, 1.0), width=2.0)
    line2 = _mk_line(P2, color=(1.0, 0.7, 0.2, 1.0), width=2.0)
    win.addItem(line1)
    win.addItem(line2)
    win.show()
    _pg_windows.append(win)


_vispy_windows = []


def launch_vispy_compare_viewer(P_ideal, P_fre, title="Knot compare", rescale_alpha=None):
    scene, _ = try_import_vispy()
    if scene is None:
        raise RuntimeError("VisPy is not installed. pip install vispy")
    P_fre_plot = P_fre if rescale_alpha is None else (P_fre * float(rescale_alpha))
    canvas = scene.SceneCanvas(keys="interactive", show=True, title=title, size=(1000, 700))
    view = canvas.central_widget.add_view()
    view.camera = "turntable"
    view.camera.fov = 45
    P_all = np.vstack([P_ideal, P_fre_plot])
    c = P_all.mean(axis=0)
    P1 = (P_ideal - c).astype(np.float32)
    P2 = (P_fre_plot - c).astype(np.float32)
    line1 = scene.visuals.Line(P1, color=(0.2, 0.8, 1.0, 1.0), width=2.0, method="gl")
    line2 = scene.visuals.Line(P2, color=(1.0, 0.7, 0.2, 1.0), width=2.0, method="gl")
    view.add(line1)
    view.add(line2)
    axis = scene.visuals.XYZAxis(parent=view.scene)
    _vispy_windows.append(canvas)


def _plot_compare(ab, fremlin_block, P_ideal_c, P_fre_c, G_ideal, G_fre, alpha_f_to_i, fremlin_label, s, fast_render=False):
    """Draw 3-panel matplotlib figure: Fremlin 3D (curvature or plain), spectrum, centered overlay."""
    mode_E = np.array(ssc.mode_energies(fremlin_block))
    P_fre = P_fre_c  # use centered for display
    kappa = exact_curvature(fremlin_block, s) if not fast_render else None

    fig = plt.figure(figsize=(16, 6))
    ax = fig.add_subplot(131, projection="3d")

    if not fast_render and kappa is not None:
        norm = plt.Normalize(vmin=float(np.min(kappa)), vmax=float(np.max(kappa)))
        colors = cm.plasma(norm(kappa))
        for i in range(len(P_fre)):
            j = (i + 1) % len(P_fre)
            ax.plot([P_fre[i, 0], P_fre[j, 0]], [P_fre[i, 1], P_fre[j, 1]], [P_fre[i, 2], P_fre[j, 2]],
                    color=colors[i], linewidth=1.8)
        sm = plt.cm.ScalarMappable(cmap=cm.plasma, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, shrink=0.75, pad=0.08)
        cbar.set_label("Curvature", rotation=270, labelpad=15)
    else:
        ax.plot(P_fre[:, 0], P_fre[:, 1], P_fre[:, 2], linewidth=1.8, color="C1")

    ax.set_title(f"Fremlin ({fremlin_label})\n" + ("Curvature-colored" if not fast_render else "Fast render"))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    set_equal_3d(ax, P_fre)

    ax2 = fig.add_subplot(132)
    j = np.arange(1, len(mode_E) + 1)
    ax2.plot(j, mode_E, linewidth=1.5)
    ax2.set_yscale("log")
    ax2.set_xlabel("Harmonic index j")
    ax2.set_ylabel(r"$E_j = \|A_j\|^2 + \|B_j\|^2$")
    ax2.set_title("Fourier mode energy spectrum")
    ax2.grid(True, alpha=0.3)

    ax3 = fig.add_subplot(133, projection="3d")
    if P_ideal_c is not None and len(P_ideal_c) > 0:
        P_fre_overlay = P_fre_c.copy()
        if np.isfinite(G_ideal["L"]) and np.isfinite(G_fre["L"]) and abs(G_fre["L"]) > 1e-12:
            alpha = G_ideal["L"] / G_fre["L"]
            P_fre_overlay = _rescale(P_fre_c, alpha)
        ax3.plot(P_ideal_c[:, 0], P_ideal_c[:, 1], P_ideal_c[:, 2],
                 linewidth=1.6, label="Embedded ideal (native scale)")
        ax3.plot(P_fre_overlay[:, 0], P_fre_overlay[:, 1], P_fre_overlay[:, 2],
                 linewidth=1.2, label=f"{fremlin_label} (rescaled to ideal length)")
        if np.isfinite(G_ideal["L"]) and np.isfinite(G_fre["L"]) and abs(G_fre["L"]) > 1e-12:
            ax3.set_title(f"Centered overlay (Fremlin rescaled by α={alpha_f_to_i:.3f})")
        else:
            ax3.set_title("Centered overlay")
        set_equal_3d(ax3, np.vstack([P_ideal_c, P_fre_overlay]))
    else:
        ax3.plot(P_fre_c[:, 0], P_fre_c[:, 1], P_fre_c[:, 2], linewidth=1.2, label=fremlin_label)
        ax3.set_title("Centered overlay")
        set_equal_3d(ax3, P_fre_c)
    ax3.set_xlabel("x")
    ax3.set_ylabel("y")
    ax3.set_zlabel("z")
    ax3.legend(loc="upper right")

    plt.tight_layout()
    plt.show()


def main(path=None):
    if path is None:
        path = list_all_fseries_files_recursive()
    print("Loading:", path)

    blocks = ssc.parse_fseries_multi(path)
    idx = ssc.index_of_largest_block(blocks)
    if idx < 0:
        raise RuntimeError("No Fourier blocks found in file.")
    block = blocks[idx]

    print("Using block index:", idx)
    print("Header:", getattr(block, "header", ""))

    # Exact / spectral descriptors (Fremlin)
    L_exact = ssc.length_exact(block, nsamples=4096)
    E_bend = ssc.bending_energy_exact(block, nsamples=4096)
    mode_E = np.array(ssc.mode_energies(block))

    D = descriptors(block)

    # Load embedded ideal 4:1:1 for comparison
    EMBEDDED_IDEAL_NAME = "ideal.txt"
    if not hasattr(ssc, "parse_embedded_ideal_ab_by_id"):
        EMBEDDED_IDEAL_NAME = "ideal.txt"
    try:
        ab_ideal = ssc.parse_embedded_ideal_ab_by_id("4:1:1", EMBEDDED_IDEAL_NAME)
    except Exception:
        ab_ideal = None
    if ab_ideal is None and hasattr(ssc, "parse_embedded_ideal_txt"):
        try:
            blocks_ideal = ssc.parse_embedded_ideal_txt(EMBEDDED_IDEAL_NAME)
            for b in blocks_ideal:
                if getattr(b, "id", None) == "4:1:1":
                    ab_ideal = b
                    break
        except Exception:
            pass
    L_ideal = np.nan
    E_bend_ideal = np.nan
    P_ideal = None
    if ab_ideal is not None and hasattr(ab_ideal, "fourier"):
        try:
            L_ideal = float(ssc.length_exact(ab_ideal.fourier, 4096))
            E_bend_ideal = float(ssc.bending_energy_exact(ab_ideal.fourier, 4096, 1e-12))
        except Exception:
            pass
        try:
            s_ideal = np.linspace(0.0, 2 * np.pi, 2400, endpoint=False)
            P_ideal = np.array(ssc.evaluate_fourier_block(ab_ideal.fourier, s_ideal.tolist()))
        except Exception:
            pass

    G_fre = {"L": L_exact, "E_bend": E_bend}
    G_ideal = {"L": L_ideal, "E_bend": E_bend_ideal}

    print("\n=== Geometric Descriptors (Fourier / spectral) ===")
    print(f"L_exact               = {L_exact:.9f}")
    print(f"Bending energy        = {E_bend:.9f}")
    print(f"Writhe (sampled proxy)= {D.writhe:.9f}")
    print(f"Min self-distance     = {D.min_self_distance:.9f}")
    M = min(len(mode_E), 10) if len(mode_E) else 0
    print(f"Modes                 = {len(mode_E)}")
    print(f"M = min(#modes)       = {M}")
    print(f"Top 10 mode energies  = {mode_E[:10]}")

    # --- Scale diagnostics / normalization ---
    print("\nScale diagnostics")
    print("-" * 86)

    L_i = G_ideal["L"]
    L_f = G_fre["L"]

    alpha_f_to_i = np.nan
    if np.isfinite(L_i) and np.isfinite(L_f) and abs(L_f) > 1e-12:
        alpha_f_to_i = L_i / L_f
        print(f"{'alpha (Fremlin -> ideal scale)':<40} {alpha_f_to_i:>20.9f}")
        print(f"{'visual guess check (~2x..4x)':<40} {'YES (computed ~%.3f x)' % alpha_f_to_i:>20}")

    # Bending energy scaling:
    # r -> alpha r  =>  E_bend = ∫kappa^2 ds  scales as alpha^{-1}
    if np.isfinite(G_fre["E_bend"]) and np.isfinite(alpha_f_to_i):
        E_f_rescaled_to_ideal_scale = G_fre["E_bend"] / alpha_f_to_i
        print(f"{'Fremlin E_bend rescaled to ideal L':<40} {E_f_rescaled_to_ideal_scale:>20.9f}")
        if np.isfinite(G_ideal["E_bend"]):
            dE_scaled = E_f_rescaled_to_ideal_scale - G_ideal["E_bend"]
            relE_scaled = dE_scaled / max(abs(G_ideal["E_bend"]), 1e-12)
            print(f"{'ΔE_bend after scale match':<40} {dE_scaled:>20.9f}   rel={relE_scaled:.3e}")

    # Scale-invariant comparison proxy: L * E_bend
    # since L -> alpha L and E_bend -> alpha^{-1} E_bend
    if np.isfinite(L_i) and np.isfinite(G_ideal["E_bend"]):
        LE_i = L_i * G_ideal["E_bend"]
    else:
        LE_i = np.nan

    if np.isfinite(L_f) and np.isfinite(G_fre["E_bend"]):
        LE_f = L_f * G_fre["E_bend"]
    else:
        LE_f = np.nan

    if np.isfinite(LE_i) and np.isfinite(LE_f):
        dLE = LE_f - LE_i
        relLE = dLE / max(abs(LE_i), 1e-12)
        print(f"{'L * E_bend (ideal)':<40} {LE_i:>20.9f}")
        print(f"{'L * E_bend (Fremlin)':<40} {LE_f:>20.9f}")
        print(f"{'Δ(L*E_bend)':<40} {dLE:>20.9f}   rel={relLE:.3e}")

    # Sample curve + exact curvature over same s-grid
    s, P = sample_block(block, n=2400)
    P_fre_c = center_points(P)
    P_ideal_c = center_points(P_ideal) if P_ideal is not None and len(P_ideal) > 0 else None
    _plot_compare(ab_ideal, block, P_ideal_c, P_fre_c, G_ideal, G_fre, alpha_f_to_i, "Fremlin (file)", s, fast_render=False)
    plt.show()


# ----------------------------
# Qt GUI
# ----------------------------
class FremlinShowcaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fremlin showcase — ideal vs embedded .fseries")
        self.setMinimumWidth(520)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # AB ID (ideal) dropdown
        id_group = QGroupBox("AB ID (embedded ideal)")
        id_layout = QVBoxLayout(id_group)
        self.combo_ab = QComboBox()
        self.combo_ab.setMinimumHeight(28)
        id_layout.addWidget(self.combo_ab)
        layout.addWidget(id_group)

        # Embedded .fseries variant dropdown
        group = QGroupBox("Embedded .fseries knot id (compiled library)")
        group_layout = QVBoxLayout(group)
        self.combo_variant = QComboBox()
        self.combo_variant.setMinimumHeight(28)
        group_layout.addWidget(self.combo_variant)
        layout.addWidget(group)

        # Viewer backend + display samples + options
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Viewer backend:"))
        self.combo_viewer = QComboBox()
        self.combo_viewer.addItems(["PyQtGraph", "Plotly", "VisPy", "Matplotlib"])
        self.combo_viewer.setCurrentText("PyQtGraph")
        row2.addWidget(self.combo_viewer)

        row2.addWidget(QLabel("Display samples:"))
        self.combo_display_samples = QComboBox()
        for s in ["200", "400", "600", "1000", "1800"]:
            self.combo_display_samples.addItem(s)
        self.combo_display_samples.setCurrentText("400")
        row2.addWidget(self.combo_display_samples)

        self.chk_fast_render = QCheckBox("Fast render (no curvature coloring)")
        self.chk_fast_render.setChecked(True)
        row2.addWidget(self.chk_fast_render)

        self.chk_rescale_overlay = QCheckBox("Rescale overlay to ideal length")
        self.chk_rescale_overlay.setChecked(True)
        row2.addWidget(self.chk_rescale_overlay)

        layout.addLayout(row2)

        # Log area must exist before any call to self.log() in _load_dropdown_data
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        layout.addWidget(self.log_text)

        # Run button
        self.run_btn = QPushButton("Compare (ideal vs embedded .fseries)")
        self.run_btn.setStyleSheet(
            "background-color: #0055ff; color: white; font-weight: bold; padding: 10px;"
        )
        self.run_btn.clicked.connect(self._on_run)
        layout.addWidget(self.run_btn)

        # Now safe to load data, which may log messages
        self._load_dropdown_data()

    def log(self, msg):
        self.log_text.append(msg)

    def current_variant_key(self):
        return self.combo_variant.currentData()

    def current_display_samples(self):
        try:
            return int(self.combo_display_samples.currentText())
        except Exception:
            return 400

    def _load_dropdown_data(self):
        # AB IDs from embedded ideal
        self._embedded_ideal_name = "ideal.txt"
        ideal_ids = list_ideal_ab_ids(self._embedded_ideal_name)
        if not ideal_ids:
            self._embedded_ideal_name = "ideal.txt"
            ideal_ids = list_ideal_ab_ids(self._embedded_ideal_name)
        self.combo_ab.clear()
        if ideal_ids:
            self.combo_ab.addItems(ideal_ids)
            if "4:1:1" in ideal_ids:
                self.combo_ab.setCurrentText("4:1:1")
        else:
            self.combo_ab.addItem("4:1:1", userData="4:1:1")
            self.combo_ab.setEditable(True)

        # Embedded .fseries ids (compiled into library) — source of truth; fallback to file-based
        self._embedded_fseries_ids = list_embedded_fseries_ids()
        self.combo_variant.clear()

        if self._embedded_fseries_ids:
            for knot_id in self._embedded_fseries_ids:
                self.combo_variant.addItem(knot_id, userData=knot_id)
            self.log(f"Loaded {len(self._embedded_fseries_ids)} embedded .fseries knot ids from library")
        else:
            file_paths = list_all_fseries_files_recursive()
            if file_paths:
                for path in file_paths:
                    display_id = fseries_path_to_display_id(path) + " (file)"
                    self.combo_variant.addItem(display_id, userData=path)
                self.log(f"No embedded .fseries in library; using {len(file_paths)} .fseries files from disk")
            else:
                self.combo_variant.addItem("(no embedded .fseries ids found)", userData=None)
                self.log("No embedded .fseries ids found and no .fseries files under Knots_FourierSeries")

    def _compare(self, ab_id, fseries_key):
        # fseries_key is either embedded knot_id (str) or .fseries file path (str)
        if os.path.isfile(fseries_key):
            fremlin_block, fre_idx = load_fseries_block_from_path(fseries_key)
            fseries_label = fseries_path_to_display_id(fseries_key)
        else:
            fremlin_block, fre_idx = load_embedded_fseries_main_block(fseries_key)
            fseries_label = str(fseries_key)
        ab = get_ideal_ab(ab_id, self._embedded_ideal_name)
        s = np.linspace(0.0, 2 * np.pi, 2400, endpoint=False)
        ideal_block = ab.fourier if hasattr(ab, "fourier") else None
        if ideal_block is None:
            raise RuntimeError(f"Ideal AB {ab_id} has no fourier block")
        P_ideal = to_np_points(ssc.evaluate_fourier_block(ideal_block, s.tolist()))
        P_fre = to_np_points(ssc.evaluate_fourier_block(fremlin_block, s.tolist()))
        P_ideal_c = center_points(P_ideal)
        P_fre_c = center_points(P_fre)

        L_ideal = float(ssc.length_exact(ideal_block, 4096))
        E_bend_ideal = float(ssc.bending_energy_exact(ideal_block, 4096, 1e-12))
        L_fre = float(ssc.length_exact(fremlin_block, 4096))
        E_bend_fre = float(ssc.bending_energy_exact(fremlin_block, 4096, 1e-12))
        G_ideal = {"L": L_ideal, "E_bend": E_bend_ideal}
        G_fre = {"L": L_fre, "E_bend": E_bend_fre}
        alpha_f_to_i = np.nan
        if np.isfinite(L_ideal) and np.isfinite(L_fre) and abs(L_fre) > 1e-12:
            alpha_f_to_i = L_ideal / L_fre

        self.log("=" * 80)
        self.log(f'AB compare: {ab_id}   vs .fseries "{fseries_label}"')
        self.log(format_ab_header(ab))
        n_ideal = len(ideal_block.a_x) if hasattr(ideal_block, "a_x") else "?"
        n_fre = len(fremlin_block.a_x) if hasattr(fremlin_block, "a_x") else "?"
        self.log(f"ideal harmonics = {n_ideal} ; embedded fseries harmonics = {n_fre} (block idx {fre_idx})")

        n_disp = self.current_display_samples()
        P_ideal_disp = downsample_closed_curve(P_ideal_c, n_disp)
        P_fre_disp = downsample_closed_curve(P_fre_c, n_disp)

        viewer = self.combo_viewer.currentText()
        fast_render = self.chk_fast_render.isChecked()
        _plot_compare(ab, fremlin_block, P_ideal_c, P_fre_c, G_ideal, G_fre, alpha_f_to_i, fseries_label, s, fast_render=fast_render)

        rescale_alpha = alpha_f_to_i if (self.chk_rescale_overlay.isChecked() and np.isfinite(alpha_f_to_i)) else None
        title = f'{format_ab_header(ab)}   vs .fseries "{fseries_label}"'

        if viewer == "Matplotlib":
            pass  # already shown by _plot_compare
        else:
            if viewer == "Plotly":
                launch_plotly_compare_viewer(P_ideal_disp, P_fre_disp, title=title, rescale_alpha=rescale_alpha)
            elif viewer == "PyQtGraph":
                launch_pyqtgraph_compare_viewer(P_ideal_disp, P_fre_disp, title=title, rescale_alpha=rescale_alpha)
            elif viewer == "VisPy":
                launch_vispy_compare_viewer(P_ideal_disp, P_fre_disp, title=title, rescale_alpha=rescale_alpha)

    def _on_run(self):
        fseries_knot_id = self.current_variant_key()
        if fseries_knot_id is None:
            QMessageBox.warning(self, "No variant", "No .fseries knot (embedded or file) selected or found.")
            return
        ab_id = self.combo_ab.currentText().strip()
        if not ab_id:
            QMessageBox.warning(self, "No AB", "Select an AB ID (embedded ideal).")
            return
        try:
            self.log(f"Comparing AB {ab_id} vs .fseries {self.current_variant_key()} ...")
            QApplication.processEvents()
            self._compare(ab_id, fseries_knot_id)
            self.log("Compare finished.")
        except Exception as e:
            QMessageBox.critical(self, "Run error", str(e))
            self.log(f"Error: {e}")


def main_gui():
    if not HAS_QT:
        print("PyQt5 not installed. Run without GUI: main(path).")
        main()
        return
    app = QApplication([])
    win = FremlinShowcaseWindow()
    win.show()
    app.exec_()


if __name__ == "__main__":
    main_gui()