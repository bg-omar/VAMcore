# sst_dashboard.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QTabWidget, QGroupBox)
from PyQt5.QtCore import QObject, pyqtSignal

# Importeer de Tab-Klassen uit de modulaire map
from gui_tabs.tab_ab_initio import TabAbInitio
from gui_tabs.tab_hydrogen import TabHydrogen
from gui_tabs.tab_theory import TabTheory
from gui_tabs.tab_ab_initio_sweep import TabAbInitioSweep




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

        # Instantieer en voeg de modulaire tabs toe
        self.tabs.addTab(TabAbInitio(), "Ab Initio Mass")
        # Instantieer en voeg de modulaire tabs toe
        self.tabs.addTab(TabAbInitioSweep(), "Full Ab Initio Sweep")
        self.tabs.addTab(TabHydrogen(), "Hydrogen Spectrum")
        self.tabs.addTab(TabTheory(), "Theory & Equations")

        left_layout.addWidget(self.tabs)

        # Rechter paneel: Live Hacker Console
        right_panel = QGroupBox("Live Simulation Console")
        right_layout = QVBoxLayout(right_panel)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 10pt;"
        )
        right_layout.addWidget(self.console)

        main_layout.addWidget(left_panel, 45)
        main_layout.addWidget(right_panel, 55)

        # Activeer de console routing
        sys.stdout = OutputWrapper()
        sys.stdout.textWritten.connect(self.append_text)

        print("=== SSTcore Engine Boot Sequence Initiated ===")
        print("[*] Modular UI Loaded.")
        print("[*] Ready for computations.\n")

    def append_text(self, text):
        self.console.insertPlainText(text)
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = SSTDashboard()
    window.show()
    sys.exit(app.exec_())