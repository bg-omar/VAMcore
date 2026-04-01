# gui_tabs/tab_knot_fseries_master.py
# Eerste tab: Knot Fseries Master – Qt-versie met Ideal/knots uit SSTcore (knot_dynamics_py).
# Gebruikt swirl_string_core/sstbindings voor embedded Ideal.txt en .fseries in resources.
# Bevat 3D-visualisatie van geselecteerde knoop (.fseries of Ideal AB Id).
import os
import re
from pathlib import Path
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QTextEdit, QSpinBox, QDoubleSpinBox,
    QGroupBox, QComboBox, QTabWidget, QScrollArea, QFrame,
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# Single C++ backend: used for helicity, canonicalize, and embedded ideal/knots
using_cxx_backend = False
sstcore = None
try:
    import swirl_string_core as sstcore
    using_cxx_backend = True
except ImportError:
    try:
        import sstbindings as sstcore
        using_cxx_backend = True
    except ImportError:
        sstcore = None

# Python helicity fallback: prefer canonical module, then legacy shim
try:
    import sst_helicity as helicity_mod
except ImportError:
    try:
        import HelicityCalculationVAMcore as helicity_mod
    except ImportError:
        helicity_mod = None

# Matplotlib 3D voor knoop-render (Qt backend)
try:
    import matplotlib
    matplotlib.use("Qt5Agg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    HAS_MPL = True
except Exception:
    HAS_MPL = False

try:
    from sst_exports import get_exports_dir
except ImportError:
    get_exports_dir = None


def _exports_dir() -> Path:
    """Alle outputs gaan naar calculations/exports."""
    if get_exports_dir:
        d = get_exports_dir()
        d.mkdir(parents=True, exist_ok=True)
        return d
    d = Path(__file__).resolve().parent.parent / "exports"
    d.mkdir(parents=True, exist_ok=True)
    return d

try:
    import generate_knot_fseries as _genknot
    HAVE_GENKNOT = True
except Exception:
    _genknot = None
    HAVE_GENKNOT = False

try:
    import SST_Fseries_GUI_Full as _sst_full
    HAVE_SSTFULL = True
except Exception:
    _sst_full = None
    HAVE_SSTFULL = False

try:
    from fseries_compat import parse_fseries_multi as _parse_fseries_multi_py, eval_fourier_block as _eval_fourier_block_py
except ImportError:
    _parse_fseries_multi_py = _eval_fourier_block_py = None

EMBEDDED_IDEAL_NAME = "ideal.txt"
VIS_POINTS = 500  # aantal punten voor 3D-curve


def _set_equal_3d(ax, pts_list):
    """Zet 3D-assen gelijke schaal rond alle punten in pts_list (lijst van (N,3) arrays)."""
    if not pts_list:
        return
    P = np.vstack([np.asarray(p) for p in pts_list])
    mins = P.min(axis=0)
    maxs = P.max(axis=0)
    mid = 0.5 * (mins + maxs)
    r = max(0.5 * np.max(maxs - mins), 1e-6)
    ax.set_xlim(mid[0] - r, mid[0] + r)
    ax.set_ylim(mid[1] - r, mid[1] + r)
    ax.set_zlim(mid[2] - r, mid[2] + r)


class KnotVisualizationPanel(QWidget):
    """Herbruikbaar 3D-canvas voor knoopcurves; kan als tab naast de console."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        if HAS_MPL:
            self._fig = Figure(figsize=(5, 4), dpi=100)
            self._ax3d = self._fig.add_subplot(111, projection="3d")
            self._ax3d.set_xlabel("X")
            self._ax3d.set_ylabel("Y")
            self._ax3d.set_zlabel("Z")
            self._canvas = FigureCanvas(self._fig)
            self._canvas.setMinimumSize(350, 280)
            layout.addWidget(self._canvas)
        else:
            self._fig = self._ax3d = self._canvas = None
            layout.addWidget(QLabel("Matplotlib niet beschikbaar."))

    def plot_curve(self, r, title=""):
        """Teken één curve r (N,3)."""
        if not HAS_MPL or self._ax3d is None:
            return
        self._ax3d.clear()
        self._ax3d.set_xlabel("X")
        self._ax3d.set_ylabel("Y")
        self._ax3d.set_zlabel("Z")
        r = np.asarray(r)
        if r.ndim == 2 and r.shape[1] == 3:
            self._ax3d.plot(r[:, 0], r[:, 1], r[:, 2], linewidth=1.0)
            _set_equal_3d(self._ax3d, [r])
        if title:
            self._ax3d.set_title(title)
        self._canvas.draw()

    def plot_curves(self, pts_list, title=""):
        """Teken meerdere curves (lijst van (N,3))."""
        if not HAS_MPL or self._ax3d is None:
            return
        self._ax3d.clear()
        self._ax3d.set_xlabel("X")
        self._ax3d.set_ylabel("Y")
        self._ax3d.set_zlabel("Z")
        for arr in pts_list:
            arr = np.asarray(arr)
            if arr.ndim == 2 and arr.shape[1] == 3:
                self._ax3d.plot(arr[:, 0], arr[:, 1], arr[:, 2], linewidth=1.0)
        if pts_list:
            _set_equal_3d(self._ax3d, pts_list)
        if title:
            self._ax3d.set_title(title)
        self._canvas.draw()

    def clear(self):
        if HAS_MPL and self._ax3d is not None:
            self._ax3d.clear()
            self._ax3d.set_xlabel("X")
            self._ax3d.set_ylabel("Y")
            self._ax3d.set_zlabel("Z")
            self._canvas.draw()


def _find_sstcore_resources():
    """Probeer SSTcore/resources (Knots_FourierSeries, ideal.txt) te vinden.
    Eerst via pip-install (sstcore.get_resources_dir()), anders dev-paden."""
    try:
        import sstcore
        p = sstcore.get_resources_dir()
        if p is not None and p.is_dir():
            return p
    except ImportError:
        pass
    base = Path(__file__).resolve().parent.parent
    if os.environ.get("SSTCORE_RESOURCES"):
        p = Path(os.environ["SSTCORE_RESOURCES"])
        if p.is_dir():
            return p
    for candidate in [
        base.parent.parent.parent.parent / "SSTcore" / "resources",
        base.parent.parent.parent / "SSTcore" / "resources",
        Path(__file__).resolve().parent.parent.parent.parent / "SSTcore" / "resources",
    ]:
        if candidate.is_dir():
            return candidate
    return None


def _get_ideal_ab_ids_from_core(embedded_name=EMBEDDED_IDEAL_NAME):
    """AB IDs uit SSTcore embedded Ideal (parse_embedded_ideal_txt / load_embedded_ideal_text)."""
    ids = []
    if sstcore is None:
        return ids
    if hasattr(sstcore, "parse_embedded_ideal_txt"):
        try:
            blocks = sstcore.parse_embedded_ideal_txt(embedded_name)
            for b in blocks:
                aid = getattr(b, "id", None)
                if aid:
                    ids.append(aid)
            if ids:
                return sorted(ids)
        except Exception:
            pass
    if hasattr(sstcore, "load_embedded_ideal_text") and hasattr(sstcore, "parse_ideal_txt_from_string"):
        try:
            txt = sstcore.load_embedded_ideal_text(embedded_name)
            blocks = sstcore.parse_ideal_txt_from_string(txt)
            for b in blocks:
                aid = getattr(b, "id", None)
                if aid:
                    ids.append(aid)
            if ids:
                return sorted(ids)
        except Exception:
            pass
    return ids


def _canonicalize_file_j0_sixcols(path: Path) -> bool:
    """Eerste numerieke rij 3→6 nullen indien nodig. Returns True if modified."""
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return False
    num_idx, parsed = [], []
    for i, line in enumerate(txt):
        s = line.strip()
        if not s or s.startswith("%"):
            continue
        parts = s.split()
        try:
            vals = [float(x) for x in parts]
        except Exception:
            continue
        if len(vals) in (3, 6):
            num_idx.append(i)
            parsed.append(vals)
    if not num_idx or len(parsed[0]) == 6:
        return False
    nxt = next((p for p in parsed[1:] if len(p) == 6), None)
    if nxt is None:
        return False
    txt[num_idx[0]] = "    0.000000    0.000000    0.000000    0.000000    0.000000    0.000000"
    path.write_text("\n".join(txt) + "\n", encoding="utf-8")
    return True


class HelicityWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, files, grid, spacing, interior, out_csv):
        super().__init__()
        self.files = files
        self.grid = grid
        self.spacing = spacing
        self.interior = interior
        self.out_csv = out_csv

    def run(self):
        if helicity_mod is None:
            self.progress.emit("[ERR] Helicity module (sst_helicity / HelicityCalculationVAMcore) not importable.\n")
            self.finished.emit()
            return
        try:
            rows = []
            for f in self.files:
                self.progress.emit(f"[*] {f.name}\n")
                res = sstcore.compute_helicity_from_fseries(str(f), grid_size=self.grid, spacing=self.spacing, interior_margin=self.interior, nsamples=1000) if using_cxx_backend and sstcore is not None and hasattr(sstcore, 'compute_helicity_from_fseries') else helicity_mod.compute_a_mu_for_file(
                    str(f), grid_size=self.grid, spacing=self.spacing, interior=self.interior
                )
                extra = {"L": "", "kappa_max": "", "kappa_mean": "", "bend_energy": "", "min_non_neighbor_dist": "", "reach_proxy": "", "nsamples": ""}
                if hasattr(res, "a_mu") and hasattr(res, "Hc") and hasattr(res, "Hm"):
                    a_mu, Hc, Hm = res.a_mu, res.Hc, res.Hm
                    for key in extra.keys():
                        if hasattr(res, key):
                            extra[key] = getattr(res, key)
                elif isinstance(res, dict):
                    a_mu, Hc, Hm = res.get("a_mu"), res.get("Hc"), res.get("Hm")
                    for key in extra.keys():
                        extra[key] = res.get(key, "")
                else:
                    a_mu, Hc, Hm = res[0], res[1], res[2]
                rows.append((f.name, self.grid, self.spacing, self.interior, a_mu, Hc, Hm,
                             extra["L"], extra["kappa_max"], extra["kappa_mean"], extra["bend_energy"],
                             extra["min_non_neighbor_dist"], extra["reach_proxy"], extra["nsamples"]))
            out = Path(self.out_csv)
            out.parent.mkdir(parents=True, exist_ok=True)
            import csv
            with out.open("w", newline="", encoding="utf-8") as fp:
                w = csv.writer(fp)
                w.writerow(["file", "grid", "spacing", "interior", "a_mu", "Hc", "Hm",
                            "L", "kappa_max", "kappa_mean", "bend_energy",
                            "min_non_neighbor_dist", "reach_proxy", "nsamples"])
                for r in rows:
                    w.writerow(list(r))
            self.progress.emit(f"[OK] wrote {out}\n")
        except Exception as e:
            self.progress.emit(f"[ERR] {e}\n")
        self.finished.emit()


class GenerateAllWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, outdir, jmax, nsamp, iters, insert_j0):
        super().__init__()
        self.outdir = outdir
        self.jmax = jmax
        self.nsamp = nsamp
        self.iters = iters
        self.insert_j0 = insert_j0

    def run(self):
        catalog = getattr(_genknot, "knopen_catalogus", None) if HAVE_GENKNOT else {}
        if not catalog:
            self.progress.emit("[ERR] Geen knopen_catalogus (generate_knot_fseries).\n")
            self.finished.emit()
            return
        for naam, ab_id in catalog.items():
            self.progress.emit(f"  [{naam}] {ab_id} ...\n")
            try:
                if HAVE_SSTFULL and _sst_full:
                    out_path, _, _ = _sst_full.generate_sst_pipeline(
                        ab_id=ab_id, knot_name=f"knot_{naam}",
                        max_j_out=self.jmax, iterations=self.iters, num_points=self.nsamp,
                        out_dir=self.outdir, insert_j0_row=self.insert_j0, canonicalize_out=self.insert_j0,
                        log_fn=lambda m: self.progress.emit(m + "\n"),
                    )
                    self.progress.emit(f"    -> {out_path}\n")
                elif HAVE_GENKNOT and _genknot:
                    _genknot.generate_sst_pipeline(
                        ab_id=ab_id, knot_name=f"knot_{naam}",
                        max_j_out=self.jmax, iterations=self.iters, num_points=self.nsamp,
                        out_dir=self.outdir,
                    )
                    self.progress.emit(f"    -> ok\n")
            except Exception as e:
                self.progress.emit(f"    [ERR] {e}\n")
        self.progress.emit("[OK] Batch voltooid.\n")
        self.finished.emit()


class TabKnotFseriesMaster(QWidget):
    """Eerste tab: Knot Fseries met Ideal/knots uit SSTcore (swirl_string_core/sstbindings)."""

    def __init__(self, global_vis=None):
        super().__init__()
        self._global_vis = global_vis  # optioneel paneel rechts (tab naast console)
        self._sstcore_resources = _find_sstcore_resources()
        self._root_dir = self._default_root()
        self._ideal_ids = _get_ideal_ab_ids_from_core(EMBEDDED_IDEAL_NAME)
        self._use_embedded = False  # True = lijst uit SSTcore get_embedded_knot_files()
        self._embedded_ids = []      # knot_id's wanneer _use_embedded
        self._build_ui()

    def _default_root(self):
        if self._sstcore_resources:
            kf = self._sstcore_resources / "Knots_FourierSeries"
            if kf.is_dir():
                return kf
        return _exports_dir()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- Bron: embedded library (SSTcore) of map op schijf ---
        grp_paths = QGroupBox("Bron knopen")
        path_layout = QVBoxLayout(grp_paths)
        row_bron = QHBoxLayout()
        row_bron.addWidget(QLabel("Bron:"))
        self.bron_combo = QComboBox()
        self.bron_combo.addItem("Embedded (SSTcore library)", "embedded")
        self.bron_combo.addItem("Map op schijf", "map")
        self.bron_combo.currentIndexChanged.connect(self._on_bron_changed)
        row_bron.addWidget(self.bron_combo, 1)
        path_layout.addLayout(row_bron)
        row = QHBoxLayout()
        row.addWidget(QLabel("Knot root (alleen bij Map):"))
        self.root_edit = QLineEdit(str(self._root_dir))
        row.addWidget(self.root_edit, 1)
        btn = QPushButton("Browse…")
        btn.clicked.connect(self._browse_root)
        row.addWidget(btn)
        path_layout.addLayout(row)
        if self._sstcore_resources:
            path_layout.addWidget(QLabel(f"SSTcore resources: {self._sstcore_resources}"))
        layout.addWidget(grp_paths)

        # --- Knotenlijst (uit library of uit map) + acties ---
        grp_files = QGroupBox("Knopen (uit library of map)")
        file_layout = QHBoxLayout(grp_files)
        self.listw = QListWidget()
        try:
            self.listw.setMinimumWidth(280)
        except Exception:
            pass
        file_layout.addWidget(self.listw, 2)

        right = QVBoxLayout()
        right.addWidget(QLabel("Acties"))
        btn_scan = QPushButton("Scan / Refresh")
        btn_scan.clicked.connect(self._refresh_list)
        right.addWidget(btn_scan)
        btn_can = QPushButton("Canonicalize selected (j0)")
        btn_can.clicked.connect(self._canonicalize_selected)
        right.addWidget(btn_can)
        right.addStretch(1)

        right.addWidget(QLabel("Helicity"))
        self.h_grid = QSpinBox()
        self.h_grid.setRange(8, 128)
        self.h_grid.setValue(48)
        right.addWidget(QLabel("grid"))
        right.addWidget(self.h_grid)
        self.h_spacing = QDoubleSpinBox()
        self.h_spacing.setValue(0.08)
        self.h_spacing.setDecimals(4)
        right.addWidget(QLabel("spacing"))
        right.addWidget(self.h_spacing)
        self.h_interior = QSpinBox()
        self.h_interior.setRange(1, 64)
        self.h_interior.setValue(12)
        right.addWidget(QLabel("interior"))
        right.addWidget(self.h_interior)
        default_csv = _exports_dir() / "SST_helicity_master.csv"
        self.csv_edit = QLineEdit(str(default_csv))
        right.addWidget(QLabel("CSV"))
        right.addWidget(self.csv_edit)
        btn_h_sel = QPushButton("Helicity: selected")
        btn_h_sel.clicked.connect(self._helicity_selected)
        right.addWidget(btn_h_sel)
        btn_h_all = QPushButton("Helicity: ALL")
        btn_h_all.clicked.connect(self._helicity_all)
        right.addWidget(btn_h_all)
        right.addStretch(1)

        file_layout.addLayout(right, 1)
        layout.addWidget(grp_files, 1)

        # --- 3D Visualisatie ---
        grp_vis = QGroupBox("Visualisatie (3D)")
        vis_layout = QVBoxLayout(grp_vis)
        if HAS_MPL:
            self._fig = Figure(figsize=(5, 4), dpi=100)
            self._ax3d = self._fig.add_subplot(111, projection="3d")
            self._ax3d.set_xlabel("X")
            self._ax3d.set_ylabel("Y")
            self._ax3d.set_zlabel("Z")
            self._canvas = FigureCanvas(self._fig)
            self._canvas.setMinimumSize(400, 320)
            vis_layout.addWidget(self._canvas)
            row_vis = QHBoxLayout()
            row_vis.addWidget(QLabel("Punten:"))
            self.vis_points = QSpinBox()
            self.vis_points.setRange(64, 2000)
            self.vis_points.setValue(VIS_POINTS)
            row_vis.addWidget(self.vis_points)
            self.btn_plot_ab = QPushButton("Plot AB Id (Ideal)")
            self.btn_plot_ab.clicked.connect(self._plot_ideal_ab)
            row_vis.addWidget(self.btn_plot_ab)
            row_vis.addStretch(1)
            vis_layout.addLayout(row_vis)
            self.listw.itemSelectionChanged.connect(self._on_selection_plot)
        else:
            vis_layout.addWidget(QLabel("Matplotlib niet beschikbaar – geen 3D-preview."))
        layout.addWidget(grp_vis, 1)

        # --- Ideal from SSTcore + Generate ---
        grp_ideal = QGroupBox("Ideal.txt uit SSTcore (embedded) – Generator")
        ideal_layout = QVBoxLayout(grp_ideal)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("AB Id:"))
        self.ab_combo = QComboBox()
        self.ab_combo.setEditable(True)
        for aid in self._ideal_ids[:80]:
            self.ab_combo.addItem(aid)
        if not self._ideal_ids:
            self.ab_combo.addItem("4:1:1")
        row2.addWidget(self.ab_combo, 1)
        row2.addWidget(QLabel("Knot name:"))
        self.knot_name_edit = QLineEdit("knot_4_1")
        row2.addWidget(self.knot_name_edit)
        ideal_layout.addLayout(row2)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Output dir (exports):"))
        self.gen_outdir_edit = QLineEdit(str(_exports_dir()))
        row3.addWidget(self.gen_outdir_edit, 1)
        btn_gen_out = QPushButton("Browse…")
        btn_gen_out.clicked.connect(self._browse_gen_outdir)
        row3.addWidget(btn_gen_out)
        ideal_layout.addLayout(row3)
        row4 = QHBoxLayout()
        btn_single = QPushButton("Generate single (Ideal→relax→fseries)")
        btn_single.clicked.connect(self._on_generate_single)
        row4.addWidget(btn_single)
        btn_batch = QPushButton("Generate all from catalog")
        btn_batch.clicked.connect(self._on_generate_all)
        row4.addWidget(btn_batch)
        ideal_layout.addLayout(row4)
        layout.addWidget(grp_ideal)

        # --- Log ---
        grp_log = QGroupBox("Log")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        grp_log_layout = QVBoxLayout(grp_log)
        grp_log_layout.addWidget(self.log)
        layout.addWidget(grp_log, 1)

        # Standaard: embedded als SSTcore dat ondersteunt
        if sstcore is not None and getattr(sstcore, "get_embedded_knot_files", None):
            self.bron_combo.setCurrentIndex(0)
        self._on_bron_changed()

    def _on_bron_changed(self):
        self._use_embedded = (self.bron_combo.currentData() == "embedded")
        self._refresh_list()

    def refresh_after_ideal_loaded(self):
        """Wordt aangeroepen nadat Ideal.txt is binnengehaald."""
        self._refresh_list()
        self._ideal_ids = _get_ideal_ab_ids_from_core(EMBEDDED_IDEAL_NAME)
        current = (self.ab_combo.currentText() or "").strip()
        self.ab_combo.clear()
        for aid in self._ideal_ids[:80]:
            self.ab_combo.addItem(aid)
        if not self._ideal_ids:
            self.ab_combo.addItem("4:1:1")
        idx = self.ab_combo.findText(current)
        if idx >= 0:
            self.ab_combo.setCurrentIndex(idx)

    def _browse_root(self):
        d = QFileDialog.getExistingDirectory(self, "Knot root", self.root_edit.text())
        if d:
            self._root_dir = Path(d)
            self.root_edit.setText(d)
            self._refresh_list()

    def _browse_gen_outdir(self):
        start = self.gen_outdir_edit.text().strip() or str(_exports_dir())
        d = QFileDialog.getExistingDirectory(self, "Output dir (exports)", start)
        if d:
            self.gen_outdir_edit.setText(d)

    def _refresh_list(self):
        self.listw.clear()
        self._embedded_ids = []
        if self._use_embedded and sstcore is not None and getattr(sstcore, "get_embedded_knot_files", None):
            try:
                files = sstcore.get_embedded_knot_files()
                ids = sorted(files.keys()) if isinstance(files, dict) else []
                self._embedded_ids = ids
                for kid in ids:
                    it = QListWidgetItem(kid)
                    it.setData(256, kid)
                    self.listw.addItem(it)
                self._append(f"[*] Geladen uit SSTcore: {len(ids)} knopen (embedded).\n")
            except Exception as e:
                self._append(f"[!] Embedded knopen laden mislukt: {e}\n")
            return
        self._root_dir = Path(self.root_edit.text()).expanduser().resolve()
        if not self._root_dir.exists():
            self._append("Root bestaat niet.\n")
            return
        count = 0
        for p in sorted(self._root_dir.rglob("*.fseries")):
            try:
                rel = p.relative_to(self._root_dir)
            except Exception:
                rel = p.name
            it = QListWidgetItem(str(rel))
            it.setData(256, str(p))
            self.listw.addItem(it)
            count += 1
        self._append(f"[*] Gevonden op schijf: {count} .fseries bestanden.\n")

    def _on_selection_plot(self):
        """Bij selectie van één item: render 3D-curve (uit library of uit bestand)."""
        if not HAS_MPL or not hasattr(self, "_ax3d"):
            return
        sel = self.listw.selectedItems()
        if len(sel) != 1:
            return
        data = sel[0].data(256)
        if self._use_embedded and data in self._embedded_ids:
            self._plot_embedded_knot(str(data))
            return
        path = Path(data)
        if path.suffix.lower() == ".fseries" or path.suffix == "":
            self._plot_fseries_curve(path)

    def _curve_from_embedded(self, knot_id: str, n_points: int):
        """Evalueer knoopcurve uit embedded SSTcore; retourneer (N,3) of None."""
        if sstcore is None or not getattr(sstcore, "load_embedded_knot_block", None) or not getattr(sstcore, "evaluate_fourier_block", None):
            return None
        try:
            block = sstcore.load_embedded_knot_block(knot_id)
            s = np.linspace(0.0, 2.0 * np.pi, n_points, endpoint=False)
            out = sstcore.evaluate_fourier_block(block, s.tolist() if hasattr(s, "tolist") else list(s))
            if isinstance(out, (list, tuple)) and len(out) == 3:
                x, y, z = out
                return np.column_stack([np.asarray(x), np.asarray(y), np.asarray(z)])
            arr = np.asarray(out)
            if arr.ndim == 2 and arr.shape[1] == 3:
                return arr
        except Exception:
            pass
        return None

    def _curve_from_fseries(self, path: Path, n_points: int):
        """Evalueer knoopcurve uit .fseries; retourneer (N,3) array of lijst daarvan."""
        s = np.linspace(0.0, 2.0 * np.pi, n_points, endpoint=False)
        if sstcore is not None and hasattr(sstcore, "parse_fseries_multi") and hasattr(sstcore, "evaluate_fourier_block"):
            try:
                blocks = sstcore.parse_fseries_multi(str(path))
                if not blocks:
                    return None
                idx = sstcore.index_of_largest_block(blocks) if hasattr(sstcore, "index_of_largest_block") else 0
                block = blocks[idx]
                out = sstcore.evaluate_fourier_block(block, s.tolist() if hasattr(s, "tolist") else list(s))
                if isinstance(out, (list, tuple)) and len(out) == 3:
                    x, y, z = out
                    return np.column_stack([np.asarray(x), np.asarray(y), np.asarray(z)])
                arr = np.asarray(out)
                if arr.ndim == 2 and arr.shape[1] == 3:
                    return arr
                return None
            except Exception:
                pass
        if _parse_fseries_multi_py is not None and _eval_fourier_block_py is not None:
            try:
                knots = _parse_fseries_multi_py(str(path))
                if not knots:
                    return None
                _, coeffs = max(knots, key=lambda k: len(k[1]["a_x"]))
                x, y, z = _eval_fourier_block_py(coeffs, s)
                return np.column_stack([x, y, z])
            except Exception:
                pass
        return None

    def _plot_embedded_knot(self, knot_id: str):
        """Teken embedded knoop (uit SSTcore library) in het 3D-canvas."""
        n = self.vis_points.value() if hasattr(self, "vis_points") else VIS_POINTS
        r = self._curve_from_embedded(knot_id, n)
        if r is None:
            self._append(f"[Vis] Kon embedded knoop {knot_id!r} niet laden.\n")
            return
        self._ax3d.clear()
        self._ax3d.set_xlabel("X")
        self._ax3d.set_ylabel("Y")
        self._ax3d.set_zlabel("Z")
        self._ax3d.plot(r[:, 0], r[:, 1], r[:, 2], linewidth=1.0)
        _set_equal_3d(self._ax3d, [r])
        self._ax3d.set_title(knot_id)
        self._canvas.draw()
        if self._global_vis:
            self._global_vis.plot_curve(r, title=knot_id)
        self._append(f"[Vis] Getekend (library): {knot_id} ({n} punten)\n")

    def _plot_fseries_curve(self, path: Path):
        """Teken geselecteerd .fseries-bestand in het 3D-canvas."""
        n = self.vis_points.value() if hasattr(self, "vis_points") else VIS_POINTS
        r = self._curve_from_fseries(path, n)
        if r is None:
            self._append(f"[Vis] Kon curve niet laden: {path.name}\n")
            return
        self._ax3d.clear()
        self._ax3d.set_xlabel("X")
        self._ax3d.set_ylabel("Y")
        self._ax3d.set_zlabel("Z")
        self._ax3d.plot(r[:, 0], r[:, 1], r[:, 2], linewidth=1.0)
        _set_equal_3d(self._ax3d, [r])
        self._ax3d.set_title(path.name)
        self._canvas.draw()
        if self._global_vis:
            self._global_vis.plot_curve(r, title=path.name)
        self._append(f"[Vis] Getekend: {path.name} ({n} punten)\n")

    def _plot_ideal_ab(self):
        """Teken Ideal AB Id (uit embedded ideal.txt) in het 3D-canvas."""
        if not HAS_MPL or sstcore is None:
            self._append("[Vis] Matplotlib of SSTcore niet beschikbaar.\n")
            return
        if not hasattr(sstcore, "parse_embedded_ideal_ab_by_id") or not hasattr(sstcore, "evaluate_ideal_ab_components"):
            self._append("[Vis] parse_embedded_ideal_ab_by_id / evaluate_ideal_ab_components niet in core.\n")
            return
        ab_id = (self.ab_combo.currentText() or "").strip()
        if not ab_id:
            self._append("[Vis] Vul AB Id in.\n")
            return
        n = self.vis_points.value() if hasattr(self, "vis_points") else VIS_POINTS
        s = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
        try:
            ab = sstcore.parse_embedded_ideal_ab_by_id(ab_id, EMBEDDED_IDEAL_NAME)
        except Exception as e:
            self._append(f"[Vis] Kon AB {ab_id!r} niet laden: {e}\n")
            return
        try:
            curves = sstcore.evaluate_ideal_ab_components(ab, s)
        except Exception as e:
            self._append(f"[Vis] Eval AB componenten mislukt: {e}\n")
            return
        self._ax3d.clear()
        self._ax3d.set_xlabel("X")
        self._ax3d.set_ylabel("Y")
        self._ax3d.set_zlabel("Z")
        pts_list = []
        for P in curves:
            arr = np.asarray(P)
            if arr.ndim == 2 and arr.shape[1] == 3:
                self._ax3d.plot(arr[:, 0], arr[:, 1], arr[:, 2], linewidth=1.0)
                pts_list.append(arr)
        if pts_list:
            _set_equal_3d(self._ax3d, pts_list)
        self._ax3d.set_title(f"Ideal {ab_id}")
        self._canvas.draw()
        if self._global_vis:
            self._global_vis.plot_curves(pts_list, title=f"Ideal {ab_id}")
        self._append(f"[Vis] Ideal getekend: {ab_id} ({n} punten)\n")

    def _append(self, msg: str):
        self.log.insertPlainText(msg)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def _selected_paths(self):
        """Alleen bestandspaden wanneer bron = Map; bij Embedded lege lijst."""
        if self._use_embedded:
            return []
        return [Path(self.listw.item(i).data(256)) for i in range(self.listw.count()) if self.listw.item(i).isSelected()]

    def _canonicalize_selected(self):
        if self._use_embedded:
            self._append("Canonicalize alleen bij bron ‘Map op schijf’.\n")
            return
        paths = self._selected_paths()
        if not paths:
            self._append("Selecteer eerst bestanden.\n")
            return
        n = sum(1 for p in paths if _canonicalize_file_j0_sixcols(p))
        self._append(f"[OK] canonicalized {n} bestanden.\n")
        self._refresh_list()

    def _helicity_selected(self):
        if self._use_embedded:
            self._append("Helicity alleen bij bron ‘Map op schijf’ (bestanden).\n")
            return
        paths = self._selected_paths()
        if not paths:
            self._append("Selecteer .fseries in de lijst.\n")
            return
        self._run_helicity(paths)

    def _helicity_all(self):
        if self._use_embedded:
            self._append("Helicity ALL alleen bij bron ‘Map op schijf’.\n")
            return
        paths = [Path(self.listw.item(i).data(256)) for i in range(self.listw.count())]
        if not paths:
            self._append("Geen bestanden in lijst. Scan eerst.\n")
            return
        self._run_helicity(paths)

    def _run_helicity(self, files):
        out_csv = (self.csv_edit.text() or "").strip() or str(_exports_dir() / "SST_helicity_master.csv")
        self._append(f"=== Helicity ({len(files)} bestanden) ===\n")
        self._h_worker = HelicityWorker(
            files, self.h_grid.value(), self.h_spacing.value(), self.h_interior.value(), out_csv
        )
        self._h_worker.progress.connect(self._append)
        self._h_worker.finished.connect(lambda: self._append("Klaar.\n"))
        self._h_worker.start()

    def _on_generate_single(self):
        ab_id = (self.ab_combo.currentText() or "").strip()
        name = (self.knot_name_edit.text() or "").strip()
        outdir = (self.gen_outdir_edit.text() or "").strip() or str(_exports_dir())
        if not name or not ab_id or not outdir:
            self._append("[ERR] Vul AB Id, naam en output dir in.\n")
            return
        self._append(f"Generate: {ab_id} -> {name}\n")
        try:
            if HAVE_SSTFULL and _sst_full:
                out_path, _, _ = _sst_full.generate_sst_pipeline(
                    ab_id=ab_id, knot_name=name, out_dir=outdir,
                    log_fn=self._append,
                )
                self._append(f"[OK] {out_path}\n")
            elif HAVE_GENKNOT and _genknot:
                _genknot.generate_sst_pipeline(ab_id=ab_id, knot_name=name, out_dir=outdir)
                self._append("[OK] Klaar.\n")
            else:
                self._append("[ERR] Geen generator (SST_Fseries_GUI_Full of generate_knot_fseries).\n")
        except Exception as e:
            self._append(f"[ERR] {e}\n")
        self._refresh_list()

    def _on_generate_all(self):
        outdir = (self.gen_outdir_edit.text() or "").strip() or str(_exports_dir())
        if not outdir:
            self._append("[ERR] Kies output dir.\n")
            return
        self._append("=== Generate all from catalog ===\n")
        self._gen_worker = GenerateAllWorker(
            outdir, 50, 300, 1500, True
        )
        self._gen_worker.progress.connect(self._append)
        self._gen_worker.finished.connect(lambda: self._append("Batch klaar.\n"))
        self._gen_worker.finished.connect(self._refresh_list)
        self._gen_worker.start()
