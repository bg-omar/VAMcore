# gui_tabs/tab_ab_initio.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton

try:
    import swirl_string_core as sstcore
except ImportError:
    try:
        import sstbindings as sstcore
    except ImportError:
        sstcore = None


class TabAbInitio(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Knoop Selectie
        layout.addWidget(QLabel("Select Particle Topology (SnapPy ID):"))
        self.knot_selector = QComboBox()
        self.knot_selector.addItems([
            "3:1:1 (Electron)", "0:1:1 (Z Boson)", "5:1:2 (Up Quark)",
            "10:1:1 (Top Quark)", "4:1:1 (Dark Sector 4_1)"
        ])
        layout.addWidget(self.knot_selector)

        # Resolutie Input
        layout.addWidget(QLabel("Resolution (Vertices):"))
        self.resolution_input = QLineEdit("2000")
        layout.addWidget(self.resolution_input)

        # Actie Knop
        btn_run = QPushButton("Run Ab Initio Relaxation")
        btn_run.setStyleSheet("background-color: #0055ff; color: white; font-weight: bold; padding: 10px;")
        btn_run.clicked.connect(self.run_ab_initio)
        layout.addWidget(btn_run)

        layout.addStretch()

    def run_ab_initio(self):
        if sstcore is None:
            print("[!] sstcore engine not available.")
            return
        knot_id = self.knot_selector.currentText().split(" ")[0]
        res = int(self.resolution_input.text())

        print(f"\n[>] Initializing ParticleEvaluator for {knot_id} (Res: {res})...")
        try:
            particle = sstcore.ParticleEvaluator(knot_id, resolution=res)
            print("[*] Relaxing Hamiltonian (1500 iterations)...")
            particle.relax(iterations=1500, timestep=0.005)

            ltot = particle.get_dimless_ropelength()
            print(f"[+] Relaxation Complete! L_tot = {ltot:.3f}")

            # Roep C++ Relativistic Metrics aan
            if hasattr(particle, "compute_relativistic_metrics"):
                metrics = particle.compute_relativistic_metrics()
                print(f"    -> Invariant Helicity (H): {metrics.helicity:.4e}")
                print(f"    -> Core Swirl-Clock (S_t): {metrics.core_time_dilation:.6f}")

        except Exception as e:
            print(f"[!] Engine Error: {str(e)}")
