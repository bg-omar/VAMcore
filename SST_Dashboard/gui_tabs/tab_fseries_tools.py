
# gui_tabs/tab_fseries_tools.py
import os
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QTextEdit, QSpinBox, QDoubleSpinBox,
)
from PyQt5.QtCore import QThread, pyqtSignal

# Prefer C++ SSTcore backend when available
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

# Python fallback: prefer canonical module, then legacy shim
try:
    import sst_helicity as helicity_mod
except ImportError:
    try:
        import HelicityCalculationVAMcore as helicity_mod
    except ImportError:
        helicity_mod = None

try:
    from sst_exports import get_exports_dir
except ImportError:
    get_exports_dir = None


def _exports_dir() -> Path:
    """Alle outputs naar calculations/exports."""
    if get_exports_dir:
        d = get_exports_dir()
        d.mkdir(parents=True, exist_ok=True)
        return d
    d = Path(__file__).resolve().parent.parent / "exports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _is_fseries(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() == ".fseries"


def _canonicalize_file_j0_sixcols(path: Path) -> bool:
    """
    Ensure the first numeric row is 6 zeros. If the first numeric row is 3 zeros and
    subsequent numeric rows have 6 cols, upgrade it to 6 zeros.
    Returns True if modified.
    """
    txt = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    # Find numeric rows
    num_idx = []
    parsed = []
    for i, line in enumerate(txt):
        s = line.strip()
        if not s or s.startswith("%"):
            continue
        parts = s.split()
        # numeric row must be all floats
        ok = True
        vals = []
        for t in parts:
            try:
                vals.append(float(t))
            except Exception:
                ok = False
                break
        if ok and len(vals) in (3, 6):
            num_idx.append(i)
            parsed.append(vals)

    if not num_idx:
        return False

    first = parsed[0]
    if len(first) == 6:
        return False

    # first has 3 cols; check next numeric row cols
    nxt = None
    for k in range(1, len(parsed)):
        if len(parsed[k]) in (3, 6):
            nxt = parsed[k]
            break
    if nxt is None or len(nxt) != 6:
        return False

    # Replace first numeric row with 6 zeros
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
            # HelicityCalculationVAMcore.compute_a_mu_for_file returns dict-like or tuple depending on version.
            rows = []
            for f in self.files:
                self.progress.emit(f"[*] Helicity: {f.name}\n")
                res = sstcore.compute_helicity_from_fseries(str(f), grid_size=self.grid, spacing=self.spacing, interior_margin=self.interior, nsamples=1000) if using_cxx_backend and sstcore is not None and hasattr(sstcore, 'compute_helicity_from_fseries') else helicity_mod.compute_a_mu_for_file(
                    str(f),
                    grid_size=self.grid,
                    spacing=self.spacing,
                    interior=self.interior,
                )
                # normalize
                # Normalize result from C++ object, dict, or tuple
                extra = {"L": "", "kappa_max": "", "kappa_mean": "", "bend_energy": "", "min_non_neighbor_dist": "", "reach_proxy": "", "nsamples": ""}
                if hasattr(res, "a_mu") and hasattr(res, "Hc") and hasattr(res, "Hm"):
                    a_mu = res.a_mu
                    Hc = res.Hc
                    Hm = res.Hm
                    for key in extra.keys():
                        if hasattr(res, key):
                            extra[key] = getattr(res, key)
                elif isinstance(res, dict):
                    a_mu = res.get("a_mu")
                    Hc = res.get("Hc")
                    Hm = res.get("Hm")
                    for key in extra.keys():
                        extra[key] = res.get(key, "")
                else:
                    # assume (a_mu, Hc, Hm) or similar
                    a_mu, Hc, Hm = res
                rows.append((f.name, self.grid, self.spacing, self.interior, a_mu, Hc, Hm,
                             extra["L"], extra["kappa_max"], extra["kappa_mean"], extra["bend_energy"],
                             extra["min_non_neighbor_dist"], extra["reach_proxy"], extra["nsamples"]))

            # write csv
            import csv
            out_csv = Path(self.out_csv)
            out_csv.parent.mkdir(parents=True, exist_ok=True)
            with out_csv.open("w", newline="", encoding="utf-8") as fp:
                w = csv.writer(fp)
                w.writerow(["file", "grid", "spacing", "interior", "a_mu", "Hc", "Hm",
                            "L", "kappa_max", "kappa_mean", "bend_energy",
                            "min_non_neighbor_dist", "reach_proxy", "nsamples"])
                for r in rows:
                    w.writerow(list(r))
            self.progress.emit(f"[OK] wrote {out_csv}\n")
        except Exception as e:
            self.progress.emit(f"[ERR] {e}\n")
        finally:
            self.finished.emit()


class TabFseriesTools(QWidget):
    def __init__(self):
        super().__init__()
        self.root_dir = Path.cwd()
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Root chooser
        row = QHBoxLayout()
        row.addWidget(QLabel("Fseries root:"))
        self.root_edit = QLineEdit(str(self.root_dir))
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self._browse_root)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self._refresh_list)
        row.addWidget(self.root_edit)
        row.addWidget(btn_browse)
        row.addWidget(btn_refresh)
        layout.addLayout(row)

        # File list + controls
        mid = QHBoxLayout()
        self.listw = QListWidget()
        mid.addWidget(self.listw, 2)

        controls = QVBoxLayout()

        # Canonicalize
        btn_can_sel = QPushButton("Canonicalize selected (3→6 zeros)")
        btn_can_sel.clicked.connect(self._canonicalize_selected)
        btn_can_all = QPushButton("Canonicalize ALL in root")
        btn_can_all.clicked.connect(self._canonicalize_all)
        controls.addWidget(btn_can_sel)
        controls.addWidget(btn_can_all)

        # Helicity params
        controls.addWidget(QLabel("Helicity params:"))
        hrow1 = QHBoxLayout()
        hrow1.addWidget(QLabel("grid"))
        self.grid_spin = QSpinBox(); self.grid_spin.setRange(8, 256); self.grid_spin.setValue(48)
        hrow1.addWidget(self.grid_spin)
        hrow1.addWidget(QLabel("interior"))
        self.int_spin = QSpinBox(); self.int_spin.setRange(1, 128); self.int_spin.setValue(12)
        hrow1.addWidget(self.int_spin)
        controls.addLayout(hrow1)

        hrow2 = QHBoxLayout()
        hrow2.addWidget(QLabel("spacing"))
        self.spacing_spin = QDoubleSpinBox(); self.spacing_spin.setDecimals(4); self.spacing_spin.setRange(1e-4, 10.0); self.spacing_spin.setSingleStep(0.01); self.spacing_spin.setValue(0.08)
        hrow2.addWidget(self.spacing_spin)
        controls.addLayout(hrow2)

        # Output CSV (altijd exports)
        outrow = QHBoxLayout()
        outrow.addWidget(QLabel("CSV (exports):"))
        default_csv = _exports_dir() / "SST_helicity_gui.csv"
        self.csv_edit = QLineEdit(str(default_csv))
        btn_csv = QPushButton("…")
        btn_csv.clicked.connect(self._choose_csv)
        outrow.addWidget(self.csv_edit)
        outrow.addWidget(btn_csv)
        controls.addLayout(outrow)

        btn_h_sel = QPushButton("Helicity: selected")
        btn_h_sel.clicked.connect(self._helicity_selected)
        btn_h_all = QPushButton("Helicity: ALL")
        btn_h_all.clicked.connect(self._helicity_all)
        controls.addWidget(btn_h_sel)
        controls.addWidget(btn_h_all)

        # Logs
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        controls.addWidget(QLabel("Log"))
        controls.addWidget(self.log, 1)

        mid.addLayout(controls, 3)
        layout.addLayout(mid)

    def _browse_root(self):
        d = QFileDialog.getExistingDirectory(self, "Choose root folder", str(self.root_dir))
        if d:
            self.root_dir = Path(d)
            self.root_edit.setText(str(self.root_dir))
            self.csv_edit.setText(str(_exports_dir() / "SST_helicity_gui.csv"))
            self._refresh_list()

    def _choose_csv(self):
        start = (self.csv_edit.text() or "").strip() or str(_exports_dir() / "SST_helicity_gui.csv")
        p, _ = QFileDialog.getSaveFileName(self, "Choose CSV output (exports)", start, "CSV (*.csv)")
        if p:
            self.csv_edit.setText(p)

    def _refresh_list(self):
        self.root_dir = Path(self.root_edit.text()).expanduser().resolve()
        self.listw.clear()
        if not self.root_dir.exists():
            return
        for p in sorted(self.root_dir.glob("*.fseries")):
            it = QListWidgetItem(p.name)
            it.setData(256, str(p))
            self.listw.addItem(it)

    def refresh_after_ideal_loaded(self):
        """Wordt aangeroepen nadat Ideal.txt is binnengehaald."""
        self._refresh_list()

    def _selected_paths(self):
        out = []
        for it in self.listw.selectedItems():
            out.append(Path(it.data(256)))
        return out

    def _append(self, msg: str):
        self.log.insertPlainText(msg)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def _canonicalize_selected(self):
        changed = 0
        for p in self._selected_paths():
            if (sstcore.canonicalize_fseries_file_inplace(str(p)).changed if using_cxx_backend and sstcore is not None and hasattr(sstcore, 'canonicalize_fseries_file_inplace') else _canonicalize_file_j0_sixcols(p)):
                changed += 1
        self._append(f"[OK] canonicalized {changed} selected files\n")
        self._refresh_list()

    def _canonicalize_all(self):
        changed = 0
        for p in self.root_dir.glob("*.fseries"):
            if (sstcore.canonicalize_fseries_file_inplace(str(p)).changed if using_cxx_backend and sstcore is not None and hasattr(sstcore, 'canonicalize_fseries_file_inplace') else _canonicalize_file_j0_sixcols(p)):
                changed += 1
        self._append(f"[OK] canonicalized {changed} files in root\n")
        self._refresh_list()

    def _helicity_selected(self):
        files = self._selected_paths()
        if not files:
            self._append("[WARN] no selection\n")
            return
        self._run_helicity(files)

    def _helicity_all(self):
        files = [Path(self.listw.item(i).data(256)) for i in range(self.listw.count())]
        self._run_helicity(files)

    def _run_helicity(self, files):
        grid = int(self.grid_spin.value())
        spacing = float(self.spacing_spin.value())
        interior = int(self.int_spin.value())
        out_csv = (self.csv_edit.text() or "").strip() or str(_exports_dir() / "SST_helicity_gui.csv")

        self._append(f"=== Helicity run === files={len(files)} grid={grid} spacing={spacing} interior={interior}\n")
        self._append("[i] using C++ helicity backend\n" if using_cxx_backend and sstcore is not None and hasattr(sstcore, "compute_helicity_from_fseries") else "[i] using Python helicity backend\n")
        self.worker = HelicityWorker(files, grid, spacing, interior, out_csv)
        self.worker.progress.connect(self._append)
        self.worker.finished.connect(lambda: self._append("[done]\n"))
        self.worker.start()
