import re
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

try:
    import swirl_string_core as ssc
except ImportError:
    import sstbindings as ssc

# Optional Qt for GUI
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QComboBox, QPushButton, QMessageBox, QGroupBox, QFrame,
    )
    from PyQt5.QtCore import Qt
    HAS_QT = True
except ImportError:
    HAS_QT = False

# ----------------------------
# Config (change as needed)
# ----------------------------
DEFAULT_AB_ID = "4:1:1"       # e.g. figure-eight knot in ideal.txt
EMBEDDED_NAME = "ideal.txt"   # can also be "ideal_database.txt" etc.
DEFAULT_N_SAMPLES = 1800
SAMPLE_OPTIONS = [100, 256, 500, 1000, 1800, 3600, 7200]


def _to_np_points(arr_like):
    arr = np.array(arr_like, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 3:
        raise ValueError(f"Expected shape (N,3), got {arr.shape}")
    return arr


def _set_equal_3d(ax, pts_list):
    P = np.vstack(pts_list)
    mins = P.min(axis=0)
    maxs = P.max(axis=0)
    mid = 0.5 * (mins + maxs)
    r = max(0.5 * np.max(maxs - mins), 1e-6)
    ax.set_xlim(mid[0] - r, mid[0] + r)
    ax.set_ylim(mid[1] - r, mid[1] + r)
    ax.set_zlim(mid[2] - r, mid[2] + r)


def _rescale(P, alpha):
    """Rescale point array by factor alpha (in-place shape preserved)."""
    return P * float(alpha)


def _print_embedded_keys():
    if hasattr(ssc, "get_embedded_ideal_files"):
        files = ssc.get_embedded_ideal_files()
        print(f"Embedded ideal resources: {len(files)}")
        for k in sorted(files.keys())[:20]:
            print("  -", k)
        if len(files) > 20:
            print("  ...")
    else:
        print("No get_embedded_ideal_files() binding found (not fatal).")


def _get_all_ideal_ab_ids(embedded_name):
    """Return sorted list of AB IDs found in the given embedded ideal resource."""
    ids = []
    # Prefer core API: parse full file and collect ids
    if hasattr(ssc, "parse_embedded_ideal_txt"):
        try:
            blocks = ssc.parse_embedded_ideal_txt(embedded_name)
            for b in blocks:
                aid = getattr(b, "id", None)
                if aid:
                    ids.append(aid)
            if ids:
                return sorted(ids)
        except Exception:
            pass
    if hasattr(ssc, "load_embedded_ideal_text") and hasattr(ssc, "parse_ideal_txt_from_string"):
        try:
            txt = ssc.load_embedded_ideal_text(embedded_name)
            blocks = ssc.parse_ideal_txt_from_string(txt)
            for b in blocks:
                aid = getattr(b, "id", None)
                if aid:
                    ids.append(aid)
            if ids:
                return sorted(ids)
        except Exception:
            pass
    # Fallback: read from examples/ideal_database.txt (or same basename) and regex
    for name in (embedded_name, "ideal_database.txt", "ideal.txt"):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                ids = re.findall(r'<AB\s+Id="([^"]+)"', text)
                if ids:
                    return sorted(set(ids))
            except Exception:
                pass
    return ids


def _format_ab_header(ab):
    if hasattr(ssc, "format_ideal_ab_header"):
        return ssc.format_ideal_ab_header(ab)

    # Fallback formatter if helper not yet bound
    ab_id = getattr(ab, "id", "?")
    conway = getattr(ab, "conway", "?")
    L = getattr(ab, "L", float("nan"))
    D = getattr(ab, "D", float("nan"))
    n = getattr(ab, "n", 1)
    return f'AB Id="{ab_id}" Conway="{conway}" L="{L}" D="{D}" n="{n}"'


def _select_ab(ab_id, embedded_name):
    # Preferred: single-AB parse from embedded text (lazy)
    if hasattr(ssc, "parse_embedded_ideal_ab_by_id"):
        return ssc.parse_embedded_ideal_ab_by_id(ab_id, embedded_name)

    # Fallback: parse whole embedded file, then search
    if hasattr(ssc, "parse_embedded_ideal_txt"):
        blocks = ssc.parse_embedded_ideal_txt(embedded_name)
    elif hasattr(ssc, "load_embedded_ideal_text") and hasattr(ssc, "parse_ideal_txt_from_string"):
        txt = ssc.load_embedded_ideal_text(embedded_name)
        blocks = ssc.parse_ideal_txt_from_string(txt)
    else:
        raise RuntimeError(
            "Missing embedded ideal parser APIs.\n"
            "Expected one of:\n"
            "  - parse_embedded_ideal_ab_by_id\n"
            "  - parse_embedded_ideal_txt\n"
            "  - load_embedded_ideal_text + parse_ideal_txt_from_string"
        )

    # Search by id
    if hasattr(ssc, "index_of_ideal_id"):
        idx = ssc.index_of_ideal_id(blocks, ab_id)
        if idx >= 0:
            return blocks[idx]

    for b in blocks:
        if getattr(b, "id", None) == ab_id:
            return b

    raise RuntimeError(f"AB Id not found: {ab_id}")


def _eval_components(ab, s):
    # Preferred: native component-aware evaluator (supports I=0 offset)
    if hasattr(ssc, "evaluate_ideal_ab_components"):
        curves = ssc.evaluate_ideal_ab_components(ab, s)
        return [_to_np_points(c) for c in curves]

    # Fallback: evaluate first-component compatibility Fourier only (n=1 expected)
    if hasattr(ab, "fourier") and hasattr(ssc, "evaluate_fourier_block"):
        pts = ssc.evaluate_fourier_block(ab.fourier, s.tolist() if hasattr(s, "tolist") else s)
        return [_to_np_points(pts)]

    raise RuntimeError("No evaluator available for ideal AB components/fourier.")


def run_showcase(ab_id, embedded_name, n_samples):
    """Load the chosen AB, evaluate, and show the 3D + optional spectrum plot."""
    print(f"Selecting AB Id = {ab_id!r} from embedded resource {embedded_name!r} (samples={n_samples}) ...")
    ab = _select_ab(ab_id, embedded_name)

    if hasattr(ab, "components") and len(ab.components) > 0:
        print("first component harmonic count a_x =", len(ab.components[0].fourier.a_x))
    else:
        print("No components parsed")

    print("compat Fourier harmonic count a_x   =", len(ab.fourier.a_x))

    # Metadata print in requested style
    print("\n" + _format_ab_header(ab))

    # Component summary
    n_attr = getattr(ab, "n", None)
    comps = getattr(ab, "components", [])
    print(f"Parsed components: {len(comps)}" + (f" (n={n_attr})" if n_attr is not None else ""))

    if len(comps) > 0:
        for c in comps:
            ci = getattr(c, "component_index", "?")
            A0 = getattr(c, "A0", [0, 0, 0])
            B0 = getattr(c, "B0", [0, 0, 0])
            print(f"  Component I=\"{ci}\" A0={A0} B0={B0}")

    # Parameter samples
    s = np.linspace(0.0, 2.0 * np.pi, n_samples, endpoint=False)

    # Evaluate all components
    curves = _eval_components(ab, s)

    # ----------------------------
    # Plot setup
    # ----------------------------
    ncols = 2 if len(curves) == 1 else 1
    fig = plt.figure(figsize=(14, 6 if len(curves) == 1 else 8))

    if len(curves) == 1:
        ax3d = fig.add_subplot(121, projection="3d")
    else:
        ax3d = fig.add_subplot(111, projection="3d")

    # Plot all components
    comp_colors = plt.rcParams['axes.prop_cycle'].by_key().get('color', ['C0', 'C1', 'C2', 'C3'])
    plotted_pts = []

    for idx, P in enumerate(curves, start=1):
        plotted_pts.append(P)
        color = comp_colors[(idx - 1) % len(comp_colors)]

        # If single component and exact curvature available, color by curvature
        if len(curves) == 1 and hasattr(ssc, "curvature_exact") and hasattr(ab, "fourier"):
            try:
                kappa = np.array(ssc.curvature_exact(ab.fourier, s.tolist(), 1e-12), dtype=float)
                norm = plt.Normalize(vmin=float(kappa.min()), vmax=float(kappa.max()))
                colors = cm.plasma(norm(kappa))
                for i in range(len(P)):
                    j = (i + 1) % len(P)
                    ax3d.plot([P[i, 0], P[j, 0]],
                              [P[i, 1], P[j, 1]],
                              [P[i, 2], P[j, 2]],
                              color=colors[i], linewidth=1.5)
                sm = plt.cm.ScalarMappable(cmap=cm.plasma, norm=norm)
                sm.set_array([])
                cbar = fig.colorbar(sm, ax=ax3d, shrink=0.75, pad=0.08)
                cbar.set_label("Curvature", rotation=270, labelpad=15)
            except Exception as e:
                print("Curvature_exact unavailable for this object, using plain line plot:", e)
                ax3d.plot(P[:, 0], P[:, 1], P[:, 2], color=color, linewidth=1.6, label=f"Component {idx}")
        else:
            ax3d.plot(P[:, 0], P[:, 1], P[:, 2], color=color, linewidth=1.8, label=f"Component {idx}")

        # Mark a start point
        ax3d.scatter([P[0, 0]], [P[0, 1]], [P[0, 2]], color=color, s=24)

    _set_equal_3d(ax3d, plotted_pts)
    ax3d.set_xlabel("x")
    ax3d.set_ylabel("y")
    ax3d.set_zlabel("z")
    ax3d.set_title(_format_ab_header(ab))

    if len(curves) > 1:
        ax3d.legend(loc="upper right")

    # ----------------------------
    # Optional right panel for n=1 spectral diagnostics
    # ----------------------------
    if len(curves) == 1:
        ax2 = fig.add_subplot(122)
        txt_lines = [_format_ab_header(ab)]

        # Exact descriptors if available
        if hasattr(ssc, "length_exact") and hasattr(ssc, "bending_energy_exact") and hasattr(ab, "fourier"):
            try:
                L_exact = float(ssc.length_exact(ab.fourier, 4096))
                E_bend = float(ssc.bending_energy_exact(ab.fourier, 4096, 1e-12))
                txt_lines.append(f"L_exact = {L_exact:.6f}")
                txt_lines.append(f"E_bend  = {E_bend:.6f}")
            except Exception as e:
                txt_lines.append(f"(exact descriptor error: {e})")

        mode_E = None
        if hasattr(ssc, "mode_energies") and hasattr(ab, "fourier"):
            try:
                mode_E = np.array(ssc.mode_energies(ab.fourier), dtype=float)
            except Exception as e:
                txt_lines.append(f"(mode_energies error: {e})")

        if mode_E is not None and len(mode_E) > 0:
            j = np.arange(1, len(mode_E) + 1)
            ax2.plot(j, mode_E, linewidth=1.4)
            ax2.set_yscale("log")
            ax2.set_xlabel("Harmonic index j")
            ax2.set_ylabel(r"$E_j = \|A_j\|^2 + \|B_j\|^2$")
            ax2.set_title("Fourier mode energy spectrum")
            ax2.grid(True, alpha=0.3)
        else:
            ax2.axis("off")

        ax2.text(
            0.02, 0.98, "\n".join(txt_lines),
            transform=ax2.transAxes,
            va="top", ha="left",
            fontsize=9,
            bbox=dict(boxstyle="round", alpha=0.1)
        )

    plt.tight_layout()
    plt.show()


# ----------------------------
# Qt GUI
# ----------------------------
class IdealShowcaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ideal AB Showcase — AB ID & Samples")
        self.setMinimumWidth(360)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # AB ID dropdown (from ideal.txt / ideal_database.txt)
        id_group = QGroupBox("AB ID (from ideal database)")
        id_layout = QVBoxLayout(id_group)
        self.ab_id_combo = QComboBox()
        self.ab_id_combo.setMinimumHeight(28)
        self._embedded_name = EMBEDDED_NAME
        ids = _get_all_ideal_ab_ids(self._embedded_name)
        if not ids:
            # Try alternate embedded name
            self._embedded_name = "ideal_database.txt"
            ids = _get_all_ideal_ab_ids(self._embedded_name)
        if ids:
            self.ab_id_combo.addItems(ids)
            if DEFAULT_AB_ID in ids:
                self.ab_id_combo.setCurrentText(DEFAULT_AB_ID)
        else:
            self.ab_id_combo.addItem(DEFAULT_AB_ID)
            self.ab_id_combo.setEditable(True)
        id_layout.addWidget(self.ab_id_combo)
        layout.addWidget(id_group)

        # Samples dropdown
        samples_group = QGroupBox("Samples")
        samples_layout = QVBoxLayout(samples_group)
        self.samples_combo = QComboBox()
        self.samples_combo.addItems([str(n) for n in SAMPLE_OPTIONS])
        idx = next((i for i, n in enumerate(SAMPLE_OPTIONS) if n == DEFAULT_N_SAMPLES), 0)
        self.samples_combo.setCurrentIndex(idx)
        samples_layout.addWidget(self.samples_combo)
        layout.addWidget(samples_group)

        # Plot button
        self.plot_btn = QPushButton("Plot ideal curve")
        self.plot_btn.setStyleSheet(
            "background-color: #0055ff; color: white; font-weight: bold; padding: 10px;"
        )
        self.plot_btn.clicked.connect(self._on_plot)
        layout.addWidget(self.plot_btn)

        layout.addStretch()
        self.statusBar().showMessage("Choose AB ID and samples, then click Plot.")

    def _on_plot(self):
        ab_id = self.ab_id_combo.currentText().strip()
        try:
            n_samples = int(self.samples_combo.currentText().strip())
        except ValueError:
            n_samples = DEFAULT_N_SAMPLES
        try:
            self.statusBar().showMessage(f"Plotting {ab_id} with {n_samples} samples...")
            QApplication.processEvents()
            run_showcase(ab_id, self._embedded_name, n_samples)
            self.statusBar().showMessage(f"Plotted {ab_id}.")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Plot error",
                f"Failed to plot AB Id {ab_id!r}:\n{e}",
            )
            self.statusBar().showMessage("Plot failed.")


def main():
    """CLI entry: run with default AB ID and samples (no GUI)."""
    print("=" * 80)
    print("Embedded ideal.txt AB selector showcase")
    print("=" * 80)
    _print_embedded_keys()
    run_showcase(DEFAULT_AB_ID, EMBEDDED_NAME, DEFAULT_N_SAMPLES)


def main_gui():
    """Launch Qt GUI for AB ID and samples selection."""
    if not HAS_QT:
        print("PyQt5 not installed. Install with: pip install PyQt5")
        print("Falling back to CLI with defaults.")
        main()
        return
    app = QApplication([])
    win = IdealShowcaseWindow()
    win.show()
    app.exec_()


if __name__ == "__main__":
    main_gui()