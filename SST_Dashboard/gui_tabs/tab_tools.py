# gui_tabs/tab_tools.py
# Merge van main.py SCRIPT_CANDIDATES + oude TOOLS; alles in Qt-stijl.
import sys
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
    QLineEdit, QFileDialog, QScrollArea, QFrame, QGroupBox,
)
from PyQt5.QtCore import Qt

# main.py: (label, modname, filename)
SCRIPT_CANDIDATES = [
    ("Master GUI (recommended)", "GUI_SST_Knot_fseries", "GUI_SST_Knot_fseries.py"),
    ("Full Fseries GUI (legacy)", "SST_Fseries_GUI_Full", "SST_Fseries_GUI_Full.py"),
    ("Knot Generator GUI (legacy)", "sst_knot_gui", "sst_knot_gui.py"),
    ("Helicity tool (CLI)", "HelicityCalculationVAMcore", "HelicityCalculationVAMcore.py"),
    ("Parse knots tool (CLI)", "parse_knots", "parse_knots.py"),
    ("Muon calc tool (CLI)", "SST_Muon_calculation", "SST-Muon_calculation.py"),
    ("Canon Pipeline (length, vol)", "Swirl_String_TheoryCanon_Pipeline", "Swirl_String_TheoryCanon_Pipeline.py"),
    ("Filament Hopf (Biot–Savart)", "sst_native_filament_hopf", "sst_native_filament_hopf.py"),
    ("Mass invariant SEMF (Canon)", "SST_ATOM_MASS_INVARIANT_SEMF_canonical_only", "SST_ATOM_MASS_INVARIANT_SEMF_canonical_only.py"),
    ("Generate .fseries (Ideal→relax)", "generate_knot_fseries", "generate_knot_fseries.py"),
    ("Ideal AB Showcase (embedded)", "example_showcase_embedded_ideal_ab_by_id", "example_showcase_embedded_ideal_ab_by_id.py"),
    ("Ideal vs Fremlin Comparator", "example_compare_ideal_vs_fremlin_4_1", "example_compare_ideal_vs_fremlin_4_1.py"),
    ("Master Sweep Pipeline", "master_sweep", "master_sweep.py"),
]

# Oude TOOLS-lijst (label, filename); wordt gemerged: alleen toevoegen als filename nog niet in SCRIPT_CANDIDATES
TOOLS_LEGACY = [
    ("Master Sweep", "master_sweep.py"),
    ("Compare Ideal vs Fremlin", "example_compare_ideal_vs_fremlin_4_1.py"),
    ("Showcase embedded Ideal AB", "example_showcase_embedded_ideal_ab_by_id.py"),
    ("Generator (CLI) generate_knot_fseries", "generate_knot_fseries.py"),
    ("Canon Pipeline", "Swirl_String_TheoryCanon_Pipeline.py"),
    ("Atom mass invariant SEMF", "SST_ATOM_MASS_INVARIANT_SEMF_canonical_only.py"),
    ("Filament Hopf demo", "sst_native_filament_hopf.py"),
    ("Parse knots", "parse_knots.py"),
]


def _merged_script_list():
    """SCRIPT_CANDIDATES + TOOLS_LEGACY entries waar filename nog niet voorkomt. Elk item = (label, modname, filename)."""
    seen = {f for (_, _, f) in SCRIPT_CANDIDATES}
    out = list(SCRIPT_CANDIDATES)
    for label, filename in TOOLS_LEGACY:
        if filename not in seen:
            modname = Path(filename).stem
            out.append((label, modname, filename))
            seen.add(filename)
    return out


# Qt-styling voor de Tools-tab
TOOLS_TAB_STYLE = """
    QGroupBox {
        font-weight: bold;
        border: 1px solid palette(mid);
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 8px;
        padding: 0 4px;
        background-color: palette(base);
    }
    QPushButton {
        min-height: 24px;
        padding: 6px 12px;
        border: 1px solid palette(mid);
        border-radius: 4px;
        background: palette(button);
    }
    QPushButton:hover {
        background: palette(light);
        border-color: palette(highlight);
    }
    QPushButton:pressed {
        background: palette(dark);
    }
    QLineEdit {
        min-height: 24px;
        padding: 4px 8px;
        border: 1px solid palette(mid);
        border-radius: 4px;
        background: palette(base);
    }
    QLineEdit:focus {
        border-color: palette(highlight);
    }
    QScrollArea {
        border: 1px solid palette(mid);
        border-radius: 4px;
        background: palette(base);
    }
    QLabel {
        color: palette(window-text);
    }
"""


def _script_exists(base_dir: Path, filename: str) -> bool:
    return (base_dir / filename).exists()


class TabTools(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(TOOLS_TAB_STYLE)
        self.base_dir = Path(__file__).resolve().parent  # gui_tabs: alle scripts hier
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # --- Base directory (Qt GroupBox) ---
        grp_base = QGroupBox("Base directory")
        row = QHBoxLayout(grp_base)
        row.addWidget(QLabel("Path:"))
        self.base_edit = QLineEdit(str(self.base_dir))
        self.base_edit.setPlaceholderText("Folder containing scripts (default: gui_tabs)")
        row.addWidget(self.base_edit, 1)
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self._browse)
        row.addWidget(btn_browse)
        layout.addWidget(grp_base)

        # --- Script launcher (Qt GroupBox + scroll) ---
        grp_scripts = QGroupBox("Run script (main.py + legacy TOOLS)")
        grp_layout = QVBoxLayout(grp_scripts)
        scroll = QScrollArea()
        try:
            scroll.setWidgetResizeMode(QScrollArea.ResizeToContents)  # PyQt5
        except AttributeError:
            scroll.setWidgetResizable(True)  # PyQt6
        scroll.setFrameShape(QFrame.NoFrame)
        try:
            _sb_off = Qt.ScrollBarAlwaysOff
        except AttributeError:
            _sb_off = Qt.ScrollBarPolicy.ScrollBarAlwaysOff  # PyQt6
        scroll.setHorizontalScrollBarPolicy(_sb_off)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 4, 0, 0)

        scripts = _merged_script_list()
        available = [
            (label, modname, filename)
            for label, modname, filename in scripts
            if _script_exists(self.base_dir, filename)
        ]
        if not available:
            inner_layout.addWidget(QLabel("No scripts found in base dir. Default is gui_tabs."))
        for label, modname, filename in available:
            b = QPushButton(f"Run: {label}")
            b.clicked.connect(lambda checked, l=label, m=modname, f=filename: self._run(l, m, f))
            inner_layout.addWidget(b)
        inner_layout.addStretch(1)
        scroll.setWidget(inner)
        grp_layout.addWidget(scroll, 1)
        layout.addWidget(grp_scripts, 1)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Choose base directory", self.base_edit.text())
        if d:
            self.base_edit.setText(d)
            self._refresh_buttons()

    def refresh_after_ideal_loaded(self):
        """Wordt aangeroepen nadat Ideal.txt is binnengehaald."""
        self._refresh_buttons()

    def _refresh_buttons(self):
        """Herlaad de lijst knoppen na wijziging van base dir."""
        base = Path(self.base_edit.text()).expanduser().resolve()
        grp_scripts = self.layout().itemAt(1).widget()
        scroll = grp_scripts.layout().itemAt(0).widget()
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 4, 0, 0)
        scripts = _merged_script_list()
        available = [
            (label, modname, filename)
            for label, modname, filename in scripts
            if _script_exists(base, filename)
        ]
        if not available:
            inner_layout.addWidget(QLabel("No scripts found in base dir."))
        for label, modname, filename in available:
            b = QPushButton(f"Run: {label}")
            b.clicked.connect(lambda checked, l=label, m=modname, f=filename: self._run(l, m, f))
            inner_layout.addWidget(b)
        inner_layout.addStretch(1)
        scroll.setWidget(inner)

    def _run(self, label: str, modname: str, filename: str):
        base = Path(self.base_edit.text()).expanduser().resolve()
        py = base / filename
        if not py.exists():
            print(f"[ERR] not found: {py}")
            return
        cmd = [sys.executable, str(py)]
        # cwd = calculations (parent van gui_tabs) zodat scripts relatief paden naar data vinden
        cwd = base.parent
        print(f"[launch] {label}  ->  {' '.join(cmd)}  (cwd={cwd})")
        subprocess.Popen(cmd, cwd=str(cwd))
