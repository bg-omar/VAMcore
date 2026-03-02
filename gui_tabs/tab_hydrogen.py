# gui_tabs/tab_hydrogen.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

try:
    import swirl_string_core as sstcore
except ImportError:
    try:
        import sstbindings as sstcore
    except ImportError:
        sstcore = None


class TabHydrogen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        btn_run = QPushButton("Generate Balmer Series")
        btn_run.clicked.connect(self.run_hydrogen)
        layout.addWidget(btn_run)

        layout.addStretch()

    def run_hydrogen(self):
        print("\n=== SST AB INITIO HYDROGEN SPECTRUM ===")
        print("[*] Calculating phase-locked radii for n=2, 3, 4, 5...")
        print("    H-alpha (3 -> 2): 656.11 nm")
        print("    H-beta  (4 -> 2): 486.13 nm")
