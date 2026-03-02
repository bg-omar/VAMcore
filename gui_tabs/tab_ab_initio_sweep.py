# gui_tabs/tab_ab_initio_sweep.py
import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal

try:
    import swirl_string_core as sstcore
except ImportError:
    try:
        import sstbindings as sstcore
    except ImportError:
        pass

# =====================================================================
# Constanten & Formules
# =====================================================================
phi0 = (1 + math.sqrt(5)) / 2
alpha_fs = 0.0072973525693
ELECTRON_MASS_MEV = 0.51099895000

def twist_t_plus(n: int) -> float:
    return ((2.0 * n + 1.0) + math.sqrt(4.0 * n + 1.0)) / (2.0 * n)

def k_from_twist_alexander(n: int, phi_val: float = phi0) -> float:
    t_plus = twist_t_plus(n)
    return (2.0 * math.log(phi_val)) / math.log(t_plus)

KNOT_INVARIANTS = {
    # BOSONEN (chi = 1.0)
    "0:1:1":  {"name": "Z Boson (Unknot)",  "k": 1.0,                       "g": 0, "n": 1, "G": 2, "chi": 1.0},
    "4:1:1":  {"name": "Dark Matter (4_1)", "k": k_from_twist_alexander(1), "g": 1, "n": 1, "G": 1, "chi": 1.0},

    # LEPTONEN (chi = 2.0)
    "3:1:1":  {"name": "Electron",          "k": 3.0,                       "g": 1, "n": 1, "G": 0, "chi": 2.0},
    "5:1:1":  {"name": "Muon",              "k": 5.0,                       "g": 2, "n": 1, "G": 1, "chi": 2.0},
    "7:1:1":  {"name": "Tau",               "k": 7.0,                       "g": 3, "n": 1, "G": 2, "chi": 2.0},

    # QUARKS (chi = 2.0)
    "5:1:2":  {"name": "Up Quark",          "k": k_from_twist_alexander(2), "g": 1, "n": 1, "G": 1, "chi": 2.0},
    "6:1:1":  {"name": "Down Quark",        "k": k_from_twist_alexander(3), "g": 1, "n": 1, "G": 1, "chi": 2.0},
    "7:1:2":  {"name": "Strange Quark",     "k": k_from_twist_alexander(4), "g": 1, "n": 1, "G": 1, "chi": 2.0},
    "8:1:1":  {"name": "Charm Quark",       "k": k_from_twist_alexander(5), "g": 1, "n": 1, "G": 2, "chi": 2.0},
    "9:1:2":  {"name": "Bottom Quark",      "k": k_from_twist_alexander(6), "g": 1, "n": 1, "G": 2, "chi": 2.0},
    "10:1:1": {"name": "Top Quark",         "k": k_from_twist_alexander(7), "g": 1, "n": 1, "G": 2, "chi": 2.0} # Aangepast naar G=2 (zoals eerder bewezen!)
}

# =====================================================================
# Achtergrond Worker Thread
# =====================================================================
class SweepWorker(QThread):
    progress_update = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, resolution):
        super().__init__()
        self.resolution = resolution
        self.is_cancelled = False

    def run_chunked_relaxation(self, particle, total_iterations=1500, chunks=10):
        """Voert de C++ relaxatie uit in kleine stapjes om freezes te voorkomen."""
        iter_per_chunk = total_iterations // chunks
        for _ in range(chunks):
            if self.is_cancelled:
                return False
            # C++ engine aanroepen
            particle.relax(iterations=iter_per_chunk, timestep=0.005)
        return True

    def run(self):
        try:
            print("\n=== SST Invariant Master Mass (Background Thread) ===")
            print(f"[*] Initialisatie: IJking van de Ether-dichtheid via het Elektron (3_1)... (Res: {self.resolution})")

            # --- STAP 1: Kalibratie ---
            electron_props = KNOT_INVARIANTS["3:1:1"]
            e_particle = sstcore.ParticleEvaluator("3:1:1", resolution=self.resolution)

            # Kalibratie kost 1/6e van de totale tijd (1 kalibratie + 5 targets = 6 stappen)
            if not self.run_chunked_relaxation(e_particle, 1500, 10):
                print("[!] Sweep geannuleerd door gebruiker.")
                self.finished_signal.emit()
                return

            self.progress_update.emit(16) # ~1/6e klaar

            L_tot_electron = e_particle.get_dimless_ropelength()
            b_supp = electron_props['k'] ** -1.5
            g_supp = phi0 ** -electron_props['g']
            c_supp = electron_props['n'] ** (-1.0 / phi0)

            M0 = ELECTRON_MASS_MEV / (electron_props['chi'] * b_supp * g_supp * c_supp * L_tot_electron)
            print(f"[+] Kalibratie voltooid. Globale M0 = {M0:.6f} MeV per L_tot")

            # --- STAP 2: De Sweep ---
            targets = ["0:1:1", "4:1:1", "3:1:1", "5:1:2", "10:1:1"]
            step_size = 84 / len(targets) # De resterende 84% verdelen
            current_progress = 16

            for tgt in targets:
                if self.is_cancelled:
                    print("[!] Sweep geannuleerd.")
                    break

                props = KNOT_INVARIANTS[tgt]
                print(f"\n┌" + "─" * 66)
                print(f"│ 🔬 DEELTJE: {props['name']}  |  Topologie ID: {tgt}")
                print("├" + "─" * 66)

                particle = sstcore.ParticleEvaluator(tgt, resolution=self.resolution)

                # De zware C++ stap in chunks
                if not self.run_chunked_relaxation(particle, 1500, 10):
                    print("│ [!] Relaxatie afgebroken.")
                    break

                L_tot = particle.get_dimless_ropelength()

                try:
                    print(f"│ ⚡ E_core [J] = {particle.compute_core_energy_J():.6e}")
                    print(f"│ ⚡ M_abinitio_core [MeV] = {particle.get_mass_mev_ab_initio(False):.6f}")

                    cfg = sstcore.TailApproxConfig()
                    cfg.enabled = True
                    cfg.radial_samples = 6
                    cfg.azimuth_samples = 8
                    cfg.r_min_factor = 1.25
                    cfg.r_max_factor = 6.0
                    cfg.exclusion_ds_factor = 3.0
                    particle.set_tail_approx_config(cfg)

                    E_tail = particle.compute_tail_energy_J(True)
                    print(f"│ ⚡ E_tail_surrogate [J] = {E_tail:.6e}")
                    print(f"│ ⚡ M_abinitio_core+tail_surrogate [MeV] = {particle.get_mass_mev_ab_initio(True):.6f}")
                except AttributeError:
                    pass

                if hasattr(particle, "compute_relativistic_metrics"):
                    metrics = particle.compute_relativistic_metrics()
                    print(f"│ 🌀 Invariant Helicity (H): {metrics.helicity:.4e}")
                    print(f"│ ⏱️ Core Swirl-Clock (S_t): {metrics.core_time_dilation:.6f}")

                b_s = props['k'] ** -1.5
                g_s = phi0 ** -props['g']
                c_s = props['n'] ** (-1.0 / phi0)
                amp_factor = (4.0 / alpha_fs) ** props['G']

                mass_pred = M0 * props['chi'] * amp_factor * b_s * g_s * c_s * L_tot

                print(f"│ 📏 Ab Initio L_tot : {L_tot:.3f} (Sferisch samengeperst volume)")
                print(f"│ 🧮 Theorema Factors: k^-1.5 = {b_s:.4f} | phi^-g = {g_s:.4f}")
                print(f"│ 🌀 Symmetrie (chi) : {props['chi']:.1f} | Componenten (n) = {props['n']}")
                print(f"│ 🛡️ Shielding (G)   : {props['G']} (Amplificatie = {amp_factor:.1e}x)")
                print("├" + "─" * 66)
                print(f"│ 🎯 SST Voorspelling: {mass_pred:.3f} MeV/c^2")
                print("└" + "─" * 66)

                current_progress += step_size
                self.progress_update.emit(int(current_progress))

        except Exception as e:
            print(f"[!] Engine Error: {str(e)}")
        finally:
            self.progress_update.emit(100)
            self.finished_signal.emit()

# =====================================================================
# De GUI Klasse voor de Sweep
# =====================================================================
class TabAbInitioSweep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Resolution (Vertices):"))
        self.resolution_input = QLineEdit("2000")
        layout.addWidget(self.resolution_input)

        # Voortgangsbalk
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Actie Knop
        self.btn_run = QPushButton("Run Master Mass Calibration & Sweep")
        self.btn_run.setStyleSheet("background-color: #0055ff; color: white; font-weight: bold; padding: 10px;")
        self.btn_run.clicked.connect(self.toggle_sweep)
        layout.addWidget(self.btn_run)

        layout.addStretch()
        self.worker = None

    def toggle_sweep(self):
        if self.worker is not None and self.worker.isRunning():
            # Gebruiker wil annuleren
            self.worker.is_cancelled = True
            self.btn_run.setText("Cancelling... Please wait for C++ to yield")
            self.btn_run.setEnabled(False)
            self.btn_run.setStyleSheet("background-color: #555555; color: white; font-weight: bold; padding: 10px;")
        else:
            # Start een nieuwe run
            try:
                res = int(self.resolution_input.text())
            except ValueError:
                res = 2000

            self.progress_bar.setValue(0)
            self.btn_run.setText("Cancel Sweep")
            self.btn_run.setStyleSheet("background-color: #ff0000; color: white; font-weight: bold; padding: 10px;")

            # Start de achtergrond thread
            self.worker = SweepWorker(resolution=res)
            self.worker.progress_update.connect(self.update_progress)
            self.worker.finished_signal.connect(self.sweep_finished)
            self.worker.start()

    def update_progress(self, val):
        self.progress_bar.setValue(val)

    def sweep_finished(self):
        # Reset knop wanneer thread stopt
        self.btn_run.setText("Run Master Mass Calibration & Sweep")
        self.btn_run.setStyleSheet("background-color: #0055ff; color: white; font-weight: bold; padding: 10px;")
        self.btn_run.setEnabled(True)