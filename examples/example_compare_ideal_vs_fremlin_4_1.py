import os
import re
import sys
import math
import traceback
import numpy as np

# Try PySide6 first, fallback to PyQt5
QT_API = None
try:
    from PySide6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QComboBox, QTextEdit, QMessageBox, QCheckBox
    )
    from PySide6.QtCore import Qt
    QT_API = "PySide6"
except ImportError:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QComboBox, QTextEdit, QMessageBox, QCheckBox
    )
    from PyQt5.QtCore import Qt
    QT_API = "PyQt5"

import matplotlib
# Qt backend
if QT_API == "PySide6":
    matplotlib.use("QtAgg")
else:
    matplotlib.use("Qt5Agg")

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

try:
    import swirl_string_core as ssc
except ImportError:
    import sstbindings as ssc


IDEAL_EMBEDDED_NAME = "ideal.txt"
DEFAULT_AB_ID = "4:1:1"


def to_np_points(points_like):
    arr = np.array(points_like, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 3:
        raise ValueError(f"Expected (N,3), got {arr.shape}")
    return arr


def center_points(P):
    return P - P.mean(axis=0, keepdims=True)


def set_equal_3d(ax, P):
    mins = P.min(axis=0)
    maxs = P.max(axis=0)
    mid = 0.5 * (mins + maxs)
    r = max(0.5 * np.max(maxs - mins), 1e-6)
    ax.set_xlim(mid[0] - r, mid[0] + r)
    ax.set_ylim(mid[1] - r, mid[1] + r)
    ax.set_zlim(mid[2] - r, mid[2] + r)


def rescale_points(P, alpha):
    return P * float(alpha)


def format_ab_header(ab):
    if hasattr(ssc, "format_ideal_ab_header"):
        return ssc.format_ideal_ab_header(ab)
    return f'AB Id="{ab.id}" Conway="{ab.conway}" L="{ab.L}" D="{ab.D}" n="{getattr(ab, "n", 1)}"'


def embedded_ideal_ids_and_headers(name="ideal.txt", limit=None):
    """
    Build dropdown list from embedded ideal.txt.
    Returns list of tuples: (ab_id, display_label)
    """
    if hasattr(ssc, "parse_embedded_ideal_txt"):
        blocks = ssc.parse_embedded_ideal_txt(name)
    else:
        txt = ssc.load_embedded_ideal_text(name)
        blocks = ssc.parse_ideal_txt_from_string(txt)

    out = []
    for b in blocks:
        ab_id = getattr(b, "id", "")
        conway = getattr(b, "conway", "")
        L = getattr(b, "L", float("nan"))
        D = getattr(b, "D", float("nan"))
        n = getattr(b, "n", 1)
        label = f'{ab_id}   | Conway={conway} | L={L:.6f} | D={D:.0f} | n={n}'
        out.append((ab_id, label))

    # Sort by numeric AB id if possible: a:b:c
    def parse_key(item):
        ab_id = item[0]
        m = re.match(r"^(\d+):(\d+):(\d+)$", ab_id)
        if m:
            return tuple(int(x) for x in m.groups())
        return (10**9, 10**9, 10**9)

    out.sort(key=parse_key)
    if limit is not None:
        out = out[:limit]
    return out


def parse_ab_by_id_embedded(ab_id, name="ideal.txt"):
    if hasattr(ssc, "parse_embedded_ideal_ab_by_id"):
        return ssc.parse_embedded_ideal_ab_by_id(ab_id, name)

    # fallback parse-all then filter
    if hasattr(ssc, "parse_embedded_ideal_txt"):
        blocks = ssc.parse_embedded_ideal_txt(name)
    else:
        txt = ssc.load_embedded_ideal_text(name)
        blocks = ssc.parse_ideal_txt_from_string(txt)

    if hasattr(ssc, "index_of_ideal_id"):
        idx = ssc.index_of_ideal_id(blocks, ab_id)
        if idx >= 0:
            return blocks[idx]
    for b in blocks:
        if getattr(b, "id", "") == ab_id:
            return b
    raise RuntimeError(f"AB Id not found: {ab_id}")


def evaluate_ab_curve(ab, s):
    # Prefer component-aware evaluator if available
    if hasattr(ssc, "evaluate_ideal_ab_components"):
        curves = ssc.evaluate_ideal_ab_components(ab, s)
        curves = [to_np_points(c) for c in curves]
        if len(curves) == 0:
            raise RuntimeError("No components returned for ideal AB")
        # n=1 common case: use first component for descriptors
        return curves[0], curves
    # Fallback to compat Fourier block
    pts = ssc.evaluate_fourier_block(ab.fourier, s.tolist())
    P = to_np_points(pts)
    return P, [P]


def compute_geom(block, s):
    out = {"kappa": None, "L": np.nan, "E_bend": np.nan, "mode_E": np.array([])}
    if hasattr(ssc, "curvature_exact"):
        out["kappa"] = np.array(ssc.curvature_exact(block, s.tolist(), 1e-12), dtype=float)
    if hasattr(ssc, "length_exact"):
        out["L"] = float(ssc.length_exact(block, 4096))
    if hasattr(ssc, "bending_energy_exact"):
        out["E_bend"] = float(ssc.bending_energy_exact(block, 4096, 1e-12))
    if hasattr(ssc, "mode_energies"):
        out["mode_E"] = np.array(ssc.mode_energies(block), dtype=float)
    return out


def resolve_fremlin_4_1_dir():
    candidates = [
        r"C:\\workspace\\projects\\SSTcore\\resources\\Knots_FourierSeries",
        r"C:\\workspace\\projects\\SSTcore\\src\\Knots_FourierSeries",
        os.path.join("resources", "Knots_FourierSeries"),
        os.path.join("src", "Knots_FourierSeries"),
    ]
    for p in candidates:
        if os.path.isdir(p):
            return p
    return None


def list_fremlin_4_1_variants():
    d = resolve_fremlin_4_1_dir()
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


def load_fseries_main_block(path):
    blocks = ssc.parse_fseries_multi(path)
    idx = ssc.index_of_largest_block(blocks)
    if idx < 0:
        raise RuntimeError(f"No Fourier blocks in {path}")
    return blocks[idx], idx


def truncate_fourier_block(block, M):
    """Python-side truncation helper using bound FourierBlock fields."""
    fb = ssc.FourierBlock()
    fb.header = getattr(block, "header", "") + f" [truncated to {M}]"
    fb.a_x = list(block.a_x[:M]); fb.b_x = list(block.b_x[:M])
    fb.a_y = list(block.a_y[:M]); fb.b_y = list(block.b_y[:M])
    fb.a_z = list(block.a_z[:M]); fb.b_z = list(block.b_z[:M])
    return fb


class MplPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fig = plt.Figure(figsize=(12, 8), constrained_layout=True)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def redraw(self):
        self.canvas.draw_idle()


class IdealVsFremlinGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SST Geometry Comparator — Embedded ideal.txt vs Fremlin .fseries")
        self.resize(1500, 950)

        self._ab_index = []       # list[(ab_id, label)]
        self._fremlin_files = []  # list[path]

        self._build_ui()
        self._load_dropdown_data()

    def _build_ui(self):
        root = QVBoxLayout(self)

        # --- Controls row 1 ---
        row1 = QHBoxLayout()
        root.addLayout(row1)

        row1.addWidget(QLabel("AB Id (from embedded ideal.txt):"))
        self.combo_ab = QComboBox()
        self.combo_ab.setMinimumWidth(500)
        row1.addWidget(self.combo_ab, stretch=2)

        row1.addWidget(QLabel("Samples:"))
        self.combo_samples = QComboBox()
        for s in ["100", "500", "1800", "3600", "7200"]:
            self.combo_samples.addItem(s)
        self.combo_samples.setCurrentText("1800")
        row1.addWidget(self.combo_samples)

        row1.addWidget(QLabel("Fremlin variant:"))
        self.combo_variant = QComboBox()
        self.combo_variant.setMinimumWidth(320)
        row1.addWidget(self.combo_variant, stretch=1)

        self.btn_compare = QPushButton("Compare Selected")
        self.btn_compare.clicked.connect(self.on_compare_selected)
        row1.addWidget(self.btn_compare)

        self.btn_sweep = QPushButton("Sweep 4_1 Variants")
        self.btn_sweep.clicked.connect(self.on_sweep_variants)
        row1.addWidget(self.btn_sweep)

        # --- Controls row 2 ---
        row2 = QHBoxLayout()
        root.addLayout(row2)

        self.chk_rescale_overlay = QCheckBox("Rescale Fremlin overlay to ideal length")
        self.chk_rescale_overlay.setChecked(True)
        row2.addWidget(self.chk_rescale_overlay)

        self.chk_truncate_ideal = QCheckBox("Truncate ideal to Fremlin mode count (apples-to-apples)")
        self.chk_truncate_ideal.setChecked(False)
        row2.addWidget(self.chk_truncate_ideal)

        row2.addStretch(1)

        # --- Text output + plot ---
        bottom = QHBoxLayout()
        root.addLayout(bottom, stretch=1)

        self.text_out = QTextEdit()
        self.text_out.setReadOnly(True)
        self.text_out.setMinimumWidth(520)
        bottom.addWidget(self.text_out, stretch=0)

        self.mpl = MplPanel()
        bottom.addWidget(self.mpl, stretch=1)

    def _load_dropdown_data(self):
        self.text_out.clear()
        self.log("Loading embedded ideal AB index...")

        try:
            self._ab_index = embedded_ideal_ids_and_headers(IDEAL_EMBEDDED_NAME)
            self.combo_ab.clear()
            for ab_id, label in self._ab_index:
                self.combo_ab.addItem(label, userData=ab_id)

            # Default select
            for i in range(self.combo_ab.count()):
                if self.combo_ab.itemData(i) == DEFAULT_AB_ID:
                    self.combo_ab.setCurrentIndex(i)
                    break

            self.log(f"Loaded {len(self._ab_index)} AB ids from embedded {IDEAL_EMBEDDED_NAME}")
        except Exception as e:
            self.log("ERROR loading embedded ideal ids:")
            self.log(str(e))
            self.log(traceback.format_exc())

        self._fremlin_files = list_fremlin_4_1_variants()
        self.combo_variant.clear()
        if self._fremlin_files:
            for p in self._fremlin_files:
                self.combo_variant.addItem(os.path.basename(p), userData=p)
            self.log(f"Found {len(self._fremlin_files)} Fremlin 4_1 variants")
        else:
            self.combo_variant.addItem("(none found)", userData=None)
            self.log("No Fremlin 4_1 variants found in resources/src Knots_FourierSeries/4_1")

    def log(self, msg=""):
        self.text_out.append(str(msg))

    def current_ab_id(self):
        return self.combo_ab.currentData()

    def current_samples(self):
        try:
            return int(self.combo_samples.currentText())
        except Exception:
            return 1800

    def current_variant_path(self):
        return self.combo_variant.currentData()

    def _compare(self, ab_id, fremlin_path):
        N = self.current_samples()
        s = np.linspace(0.0, 2.0*np.pi, N, endpoint=False)

        # Embedded ideal AB
        ab = parse_ab_by_id_embedded(ab_id, IDEAL_EMBEDDED_NAME)
        ideal_block = ab.fourier

        P_ideal, ideal_components = evaluate_ab_curve(ab, s)
        P_ideal_c = center_points(P_ideal)

        # Fremlin
        fremlin_block, fre_idx = load_fseries_main_block(fremlin_path)
        P_fre = to_np_points(ssc.evaluate_fourier_block(fremlin_block, s.tolist()))
        P_fre_c = center_points(P_fre)

        # Optional apples-to-apples truncation of ideal block
        ideal_block_for_metrics = ideal_block
        if self.chk_truncate_ideal.isChecked():
            M = len(fremlin_block.a_x)
            ideal_block_for_metrics = truncate_fourier_block(ideal_block, M)

        G_ideal = compute_geom(ideal_block_for_metrics, s)
        G_fre = compute_geom(fremlin_block, s)

        # Scale diagnostics
        L_i = G_ideal["L"]
        L_f = G_fre["L"]
        alpha_f_to_i = np.nan
        if np.isfinite(L_i) and np.isfinite(L_f) and abs(L_f) > 1e-12:
            alpha_f_to_i = L_i / L_f

        E_f_rescaled = np.nan
        if np.isfinite(G_fre["E_bend"]) and np.isfinite(alpha_f_to_i):
            E_f_rescaled = G_fre["E_bend"] / alpha_f_to_i

        LE_i = (L_i * G_ideal["E_bend"]) if (np.isfinite(L_i) and np.isfinite(G_ideal["E_bend"])) else np.nan
        LE_f = (L_f * G_fre["E_bend"]) if (np.isfinite(L_f) and np.isfinite(G_fre["E_bend"])) else np.nan

        # Spectrum comparison
        mode_i = G_ideal["mode_E"]
        mode_f = G_fre["mode_E"]
        Mmin = min(len(mode_i), len(mode_f))
        spec_l2 = np.nan
        spec_rel = np.nan
        if Mmin > 0:
            spec_l2 = float(np.linalg.norm(mode_f[:Mmin] - mode_i[:Mmin]))
            spec_rel = spec_l2 / max(float(np.linalg.norm(mode_i[:Mmin])), 1e-12)

        # Print report
        self.log("=" * 100)
        self.log(f'AB compare: {ab_id}   vs   {os.path.basename(fremlin_path)}')
        self.log(format_ab_header(ab))
        self.log(f"ideal harmonics = {len(ideal_block.a_x)} ; Fremlin harmonics = {len(fremlin_block.a_x)} (block idx {fre_idx})")
        if self.chk_truncate_ideal.isChecked():
            self.log(f"NOTE: Ideal metrics truncated to first {len(fremlin_block.a_x)} modes")

        self.log("-" * 100)
        self.log(f"{'metric':<34} {'ideal':>18} {'fremlin':>18}")
        self.log("-" * 100)
        self.log(f"{'L_exact':<34} {L_i:>18.9f} {L_f:>18.9f}")
        self.log(f"{'E_bend':<34} {G_ideal['E_bend']:>18.9f} {G_fre['E_bend']:>18.9f}")
        if np.isfinite(alpha_f_to_i):
            self.log(f"{'alpha (Fremlin->ideal length scale)':<34} {alpha_f_to_i:>18.9f}")
        if np.isfinite(E_f_rescaled):
            self.log(f"{'Fremlin E_bend rescaled to ideal L':<34} {'':>18} {E_f_rescaled:>18.9f}")
        if np.isfinite(LE_i) and np.isfinite(LE_f):
            self.log(f"{'L * E_bend (scale invariant)':<34} {LE_i:>18.9f} {LE_f:>18.9f}")
        if np.isfinite(spec_l2):
            self.log(f"{'Spectrum L2 (first M modes)':<34} {spec_l2:>18.9e} {'rel=' + format(spec_rel, '.3e'):>18}")
            self.log(f"{'M=min(#modes)':<34} {Mmin:>18d}")

        # Plot
        self._plot_compare(
            ab, P_ideal_c, P_fre_c, G_ideal, G_fre, alpha_f_to_i,
            fremlin_label=os.path.basename(fremlin_path)
        )

        return {
            "ab": ab,
            "fremlin_file": fremlin_path,
            "L_i": L_i,
            "L_f": L_f,
            "E_i": G_ideal["E_bend"],
            "E_f": G_fre["E_bend"],
            "alpha": alpha_f_to_i,
            "E_f_rescaled": E_f_rescaled,
            "LE_i": LE_i,
            "LE_f": LE_f,
            "spec_l2": spec_l2,
            "spec_rel": spec_rel,
            "M": Mmin,
        }

    def _plot_compare(self, ab, P_ideal_c, P_fre_c, G_ideal, G_fre, alpha_f_to_i, fremlin_label):
        fig = self.mpl.fig
        fig.clear()

        ax1 = fig.add_subplot(221, projection="3d")
        ax2 = fig.add_subplot(222, projection="3d")
        ax3 = fig.add_subplot(223, projection="3d")
        ax4 = fig.add_subplot(224)

        # ideal colored by curvature
        if G_ideal["kappa"] is not None and len(G_ideal["kappa"]) == len(P_ideal_c):
            kappa = G_ideal["kappa"]
            norm = plt.Normalize(vmin=float(np.min(kappa)), vmax=float(np.max(kappa)))
            cols = cm.plasma(norm(kappa))
            for i in range(len(P_ideal_c)):
                j = (i + 1) % len(P_ideal_c)
                ax1.plot([P_ideal_c[i,0], P_ideal_c[j,0]],
                         [P_ideal_c[i,1], P_ideal_c[j,1]],
                         [P_ideal_c[i,2], P_ideal_c[j,2]],
                         color=cols[i], linewidth=1.3)
            sm = plt.cm.ScalarMappable(cmap=cm.plasma, norm=norm)
            sm.set_array([])
            fig.colorbar(sm, ax=ax1, shrink=0.7, pad=0.04)
        else:
            ax1.plot(P_ideal_c[:,0], P_ideal_c[:,1], P_ideal_c[:,2], linewidth=1.4)
        ax1.set_title(f'Embedded ideal ({getattr(ab, "id", "?")})')
        set_equal_3d(ax1, P_ideal_c)

        # fremlin colored by curvature
        if G_fre["kappa"] is not None and len(G_fre["kappa"]) == len(P_fre_c):
            kappa = G_fre["kappa"]
            norm = plt.Normalize(vmin=float(np.min(kappa)), vmax=float(np.max(kappa)))
            cols = cm.plasma(norm(kappa))
            for i in range(len(P_fre_c)):
                j = (i + 1) % len(P_fre_c)
                ax2.plot([P_fre_c[i,0], P_fre_c[j,0]],
                         [P_fre_c[i,1], P_fre_c[j,1]],
                         [P_fre_c[i,2], P_fre_c[j,2]],
                         color=cols[i], linewidth=1.3)
            sm = plt.cm.ScalarMappable(cmap=cm.plasma, norm=norm)
            sm.set_array([])
            fig.colorbar(sm, ax=ax2, shrink=0.7, pad=0.04)
        else:
            ax2.plot(P_fre_c[:,0], P_fre_c[:,1], P_fre_c[:,2], linewidth=1.4)
        ax2.set_title(f"Fremlin {fremlin_label}")
        set_equal_3d(ax2, P_fre_c)

        # overlay
        P_fre_overlay = P_fre_c
        overlay_title = "Centered overlay"
        if self.chk_rescale_overlay.isChecked() and np.isfinite(alpha_f_to_i):
            P_fre_overlay = rescale_points(P_fre_c, alpha_f_to_i)
            overlay_title = f"Overlay (Fremlin rescaled α={alpha_f_to_i:.3f})"

        ax3.plot(P_ideal_c[:,0], P_ideal_c[:,1], P_ideal_c[:,2], linewidth=1.6, label="Embedded ideal")
        ax3.plot(P_fre_overlay[:,0], P_fre_overlay[:,1], P_fre_overlay[:,2], linewidth=1.2, label="Fremlin")
        set_equal_3d(ax3, np.vstack([P_ideal_c, P_fre_overlay]))
        ax3.set_title(overlay_title)
        ax3.legend()

        # spectra
        mode_i = G_ideal["mode_E"]
        mode_f = G_fre["mode_E"]
        if len(mode_i) > 0:
            ax4.plot(np.arange(1, len(mode_i)+1), mode_i, linewidth=1.4, label="Embedded ideal")
        if len(mode_f) > 0:
            ax4.plot(np.arange(1, len(mode_f)+1), mode_f, linewidth=1.1, label="Fremlin")
        ax4.set_yscale("log")
        ax4.set_xlabel("Harmonic index j")
        ax4.set_ylabel(r"$E_j$")
        ax4.set_title("Mode spectra")
        ax4.grid(True, alpha=0.3)
        ax4.legend()

        fig.suptitle(f"{format_ab_header(ab)}", fontsize=11)
        self.mpl.redraw()

    def on_compare_selected(self):
        ab_id = self.current_ab_id()
        fremlin_path = self.current_variant_path()
        if not ab_id:
            QMessageBox.warning(self, "No AB Id", "Select an AB Id first.")
            return
        if not fremlin_path:
            QMessageBox.warning(self, "No Fremlin variant", "No Fremlin .fseries variant found.")
            return

        try:
            self._compare(ab_id, fremlin_path)
        except Exception as e:
            self.log("ERROR during compare:")
            self.log(str(e))
            self.log(traceback.format_exc())
            QMessageBox.critical(self, "Compare error", str(e))

    def on_sweep_variants(self):
        ab_id = self.current_ab_id()
        if not ab_id:
            QMessageBox.warning(self, "No AB Id", "Select an AB Id first.")
            return
        if not self._fremlin_files:
            QMessageBox.warning(self, "No variants", "No Fremlin 4_1 variants found.")
            return

        self.log("")
        self.log(f"Sweeping variants for AB {ab_id} ...")
        results = []

        try:
            for p in self._fremlin_files:
                try:
                    r = self._compare(ab_id, p)
                    results.append(r)
                except Exception as e:
                    self.log(f"[SKIP] {os.path.basename(p)}: {e}")

            # Rank by scale-corrected bending error first, then spectrum rel error
            def score(item):
                e_scaled = item.get("E_f_rescaled", np.nan)
                e_i = item.get("E_i", np.nan)
                spec_rel = item.get("spec_rel", np.nan)
                if np.isfinite(e_scaled) and np.isfinite(e_i):
                    dE = abs(e_scaled - e_i)
                else:
                    dE = np.inf
                if not np.isfinite(spec_rel):
                    spec_rel = np.inf
                return (dE, spec_rel)

            results_sorted = sorted(results, key=score)

            self.log("")
            self.log("=" * 100)
            self.log(f"Variant ranking for AB {ab_id} (best first)")
            self.log("=" * 100)
            self.log(f"{'variant':<24} {'alpha':>10} {'|ΔE_scaled|':>16} {'spec_rel':>14} {'modes':>8}")
            self.log("-" * 100)
            for r in results_sorted:
                v = os.path.basename(r["fremlin_file"])
                alpha = r.get("alpha", np.nan)
                e_i = r.get("E_i", np.nan)
                e_fs = r.get("E_f_rescaled", np.nan)
                dE = abs(e_fs - e_i) if (np.isfinite(e_i) and np.isfinite(e_fs)) else np.nan
                spec_rel = r.get("spec_rel", np.nan)
                M = r.get("M", 0)
                self.log(f"{v:<24} {alpha:>10.3f} {dE:>16.6f} {spec_rel:>14.3e} {M:>8d}")

        except Exception as e:
            self.log("ERROR during sweep:")
            self.log(str(e))
            self.log(traceback.format_exc())
            QMessageBox.critical(self, "Sweep error", str(e))


def main():
    app = QApplication(sys.argv)
    w = IdealVsFremlinGui()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()