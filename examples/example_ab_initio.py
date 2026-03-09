import os
import sys
import math
from datetime import datetime

try:
    import sstcore
except ImportError:
    import sstbindings as sstcore

# Formules voor Alexander Root
phi0 = (1 + math.sqrt(5)) / 2
def twist_t_plus(n: int) -> float:
    return ((2.0 * n + 1.0) + math.sqrt(4.0 * n + 1.0)) / (2.0 * n)

def k_from_twist_alexander(n: int, phi_val: float = phi0) -> float:
    t_plus = twist_t_plus(n)
    return (2.0 * math.log(phi_val)) / math.log(t_plus)

# De Volledige Standaardmodel Catalogus
# Inclusief Bosonen (chi=1.0) en de Unknot (0_1)
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

# Constanten voor de Master Equation
alpha_fs = 0.0072973525693 # 1 / 137.036
ELECTRON_MASS_MEV = 0.51099895

def evaluate_particle(knot_id, M0_calibration):
    props = KNOT_INVARIANTS.get(knot_id)
    if not props: return None

    print(f"\n┌──────────────────────────────────────────────────────────────────")
    print(f"│ 🔬 DEELTJE: {props['name']}  |  Topologie ID: {knot_id}")
    print(f"├──────────────────────────────────────────────────────────────────")

    # 1. AB INITIO C++ FYSICA: Horn Torus Compressie
    particle = sstcore.ParticleEvaluator(knot_id, resolution=2000)
    particle.relax(iterations=1500, timestep=0.005)
    L_tot = particle.get_dimless_ropelength()

    try:
        print(f"│ ⚡ E_core [J] = {particle.compute_core_energy_J():.6e}")
        print(f"│ ⚡ M_abinitio_core [MeV] = {particle.get_mass_mev_ab_initio(False):.6f}")
        # Tail surrogate (fast approximation; no full 3D grid)
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
        print("│ NOTE: rebuild pybind module to access ab initio energy/mass methods")

    # 2. SST-59 THEOREMA: Master Equation Factoren
    amplification = (4.0 / alpha_fs) ** props['G']
    braid_suppression = props['k'] ** -1.5
    genus_suppression = phi0 ** -props['g']
    component_suppression = props['n'] ** (-1.0 / phi0)

    # De VOLLEDIGE Master Mass Equation (incl. spin chi en component n)
    mass_mev = M0_calibration * props['chi'] * amplification * braid_suppression * genus_suppression * component_suppression * L_tot

    print(f"│ 📏 Ab Initio L_tot : {L_tot:.3f} (Sferisch samengeperst volume)")
    print(f"│ 🧮 Theorema Factors: k^-1.5 = {braid_suppression:.4f} | phi^-g = {genus_suppression:.4f}")
    print(f"│ 🌀 Symmetrie (chi) : {props['chi']:.1f} | Componenten (n) = {props['n']}")
    print(f"│ 🛡️ Shielding (G)   : {props['G']} (Amplificatie = {amplification:.1e}x)")
    print(f"├──────────────────────────────────────────────────────────────────")
    print(f"│ 🎯 SST Voorspelling: {mass_mev:.3f} MeV/c^2")
    print(f"└──────────────────────────────────────────────────────────────────")

    return mass_mev

class Tee:
    """Write to both stdout and a file."""
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

def _main_example_ab_initio():
    print("\n=== SST Invariant Master Mass (Volledig Afgewerkt Model) ===")

    # STAP A: IJking van de Globale Ether-Dichtheid (M0)
    print("\n[*] Initialisatie: IJking van de Ether-dichtheid via het Elektron (3_1)...")
    electron_props = KNOT_INVARIANTS["3:1:1"]
    e_particle = sstcore.ParticleEvaluator("3:1:1", resolution=2000)
    e_particle.relax(iterations=1500, timestep=0.005)
    L_tot_electron = e_particle.get_dimless_ropelength()

    b_supp = electron_props['k'] ** -1.5
    g_supp = phi0 ** -electron_props['g']
    c_supp = electron_props['n'] ** (-1.0 / phi0)

    # Berekening M0 inclusief de elektron spin (chi=2.0)
    M0 = ELECTRON_MASS_MEV / (electron_props['chi'] * b_supp * g_supp * c_supp * L_tot_electron)
    print(f"[+] Kalibratie voltooid. Globale M0 = {M0:.6f} MeV per L_tot")

    # STAP B: Voorspel de nieuwe deeltjes (Z-Boson, Donkere Materie) en een paar ijkpunten
    targets = ["0:1:1", "4:1:1", "3:1:1", "5:1:2", "10:1:1"]

    for knot in targets:
        evaluate_particle(knot, M0)

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", f"example_ab_initio_{datetime.now():%Y%m%d_%H%M%S}.txt")
    with open(out_path, "w", encoding="utf-8") as out_file:
        old_stdout = sys.stdout
        sys.stdout = Tee(old_stdout, out_file)
        try:
            _main_example_ab_initio()
        finally:
            sys.stdout = old_stdout
    print(f"\n[+] Results also saved to {out_path}")