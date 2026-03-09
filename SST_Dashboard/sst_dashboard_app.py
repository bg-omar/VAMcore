# sst_dashboard.py
import sys
from pathlib import Path

# Zorg dat SSTcore-root en build/Release op path staan (sstcore-package + nieuwste .pyd)
_here = Path(__file__).resolve().parent
_sstcore_root = _here.parent
_build_release = _sstcore_root / "build" / "Release"
if _build_release.is_dir() and str(_build_release) not in sys.path:
    sys.path.insert(0, str(_build_release))
if _sstcore_root.is_dir() and str(_sstcore_root) not in sys.path:
    sys.path.insert(0, str(_sstcore_root))

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QTabWidget, QGroupBox, QLabel)
from PyQt5.QtCore import QObject, pyqtSignal, QThread

# Importeer de Tab-Klassen uit de modulaire map
from gui_tabs.tab_knot_fseries_master import TabKnotFseriesMaster, KnotVisualizationPanel
from gui_tabs.tab_ab_initio import TabAbInitio
from gui_tabs.tab_hydrogen import TabHydrogen
from gui_tabs.tab_theory import TabTheory
from gui_tabs.tab_ab_initio_sweep import TabAbInitioSweep
from gui_tabs.tab_mass_sweep import TabMassSweep
from gui_tabs.tab_fseries_tools import TabFseriesTools
from gui_tabs.tab_tools import TabTools




# =====================================================================
# Ideal.txt binnenhaling (zelfde logica als sst_knot_gui: katlas.org)
# =====================================================================
class IdealTxtAcquisitionThread(QThread):
    """Haal Ideal.txt binnen in exports (prepare_database-logica) op de achtergrond."""
    idealAcquired = pyqtSignal(bool)  # True = success

    def run(self):
        ok = False
        try:
            from gui_tabs.sst_exports import ensure_ideal_txt
            path = ensure_ideal_txt()
            print(f"[+] Ideal.txt beschikbaar: {path}\n")
            ok = True
        except Exception as e:
            print(f"[!] Ideal.txt acquisitie mislukt: {e}\n")
        self.idealAcquired.emit(ok)


# =====================================================================
# Output Router (Stuurt terminal output naar de GUI Console)
# =====================================================================
class OutputWrapper(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass


# =====================================================================
# Hoofd GUI Applicatie
# =====================================================================
class SSTDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSTcore Physics Engine Dashboard")
        self.resize(1100, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Linker paneel: Tabbladen Menu
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.tabs = QTabWidget()

        # Rechter paneel eerst (visualisatiepaneel doorgeven aan Knot Fseries-tab)
        right_panel = QGroupBox("Live Simulation & Visualisatie")
        right_layout = QVBoxLayout(right_panel)
        right_tabs = QTabWidget()
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 10pt;"
        )
        right_tabs.addTab(self.console, "Console")
        self.knot_vis_panel = KnotVisualizationPanel()
        right_tabs.addTab(self.knot_vis_panel, "Visualisatie (3D)")
        try:
            from gui_tabs.example_compare_ideal_vs_fremlin_4_1 import IdealVsFremlinGui
            right_tabs.addTab(IdealVsFremlinGui(), "Ideal vs Fremlin")
        except Exception as e:
            right_tabs.addTab(QLabel(f"Ideal vs Fremlin niet geladen:\n{e}"), "Ideal vs Fremlin")
        right_layout.addWidget(right_tabs)
        self.right_tabs = right_tabs

        # Linker tabs: Knot Fseries werkt samen met rechter visualisatie-tab
        self.tabs.addTab(TabKnotFseriesMaster(global_vis=self.knot_vis_panel), "Knot Fseries (Master)")
        self.tabs.addTab(TabAbInitio(), "Ab Initio Mass")
        self.tabs.addTab(TabAbInitioSweep(), "Full Ab Initio Sweep")
        self.tabs.addTab(TabMassSweep(), "Mass Sweep (Embedded)")
        self.tabs.addTab(TabHydrogen(), "Hydrogen Spectrum")
        self.tabs.addTab(TabTheory(), "Theory & Equations")
        self.tabs.addTab(TabFseriesTools(), "Fseries Tools")
        self.tabs.addTab(TabTools(), "Tools / Launcher")
        left_layout.addWidget(self.tabs)

        main_layout.addWidget(left_panel, 45)
        main_layout.addWidget(right_panel, 55)

        # Activeer de console routing
        sys.stdout = OutputWrapper()
        sys.stdout.textWritten.connect(self.append_text)

        print("=== SSTcore Engine Boot Sequence Initiated ===")
        print("[*] Modular UI Loaded.")
        print("[*] Ideal.txt wordt op de achtergrond binnengehaald (zoals sst_knot_gui)...\n")
        self._ideal_thread = IdealTxtAcquisitionThread()
        self._ideal_thread.idealAcquired.connect(self._on_ideal_acquired)
        self._ideal_thread.start()
        print("[*] Ready for computations.\n")

    def _on_ideal_acquired(self, success):
        """Na binnenhalen Ideal.txt: alle tabbladen refreshen."""
        if success:
            print("[*] Tabbladen verversen na Ideal.txt-acquisitie...\n")
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if w and hasattr(w, "refresh_after_ideal_loaded"):
                try:
                    w.refresh_after_ideal_loaded()
                except Exception as e:
                    print(f"[!] Refresh tab {i} mislukt: {e}\n")
        for i in range(self.right_tabs.count()):
            w = self.right_tabs.widget(i)
            if w and hasattr(w, "refresh_after_ideal_loaded"):
                try:
                    w.refresh_after_ideal_loaded()
                except Exception as e:
                    print(f"[!] Refresh rechter tab {i} mislukt: {e}\n")

    def append_text(self, text):
        self.console.insertPlainText(text)
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = SSTDashboard()
    window.showMaximized()
    sys.exit(app.exec_())