import os
import sys
import math
import time
from datetime import datetime

try:
    import sstcore
except ImportError:
    import sstbindings as sstcore

# =====================================================================
# 1. STANDARD MODEL REFERENCE DATABASE
# =====================================================================
PDG_DATABASE = {
    "Electron (e-)": 0.510998,
    "Muon (mu)": 105.658,
    "Tau (tau)": 1776.86,
    "Up Quark (Constituent)": 336.0,
    "Down Quark (Constituent)": 340.0,
    "Strange Quark (Constituent)": 486.0,
    "Charm Quark (c)": 1270.0,
    "Bottom Quark (b)": 4180.0,
    "Top Quark (t)": 171200.0,
    "W Boson (W)": 80379.0,
    "Z Boson (Z)": 91187.6,
    "Higgs Boson (H)": 125100.0,
    "Pion (pi0)": 134.97,
    "Proton (p+)": 938.272
}

phi0 = (1 + math.sqrt(5)) / 2
alpha_fs = 0.0072973525693

def twist_t_plus(n: int) -> float:
    return ((2.0 * n + 1.0) + math.sqrt(4.0 * n + 1.0)) / (2.0 * n)

def k_from_twist_alexander(n: int) -> float:
    t_plus = twist_t_plus(n)
    return (2.0 * math.log(phi0)) / math.log(t_plus)

# =====================================================================
# 2. TOPOLOGICAL AUTOMATION
# =====================================================================
def auto_determine_physics(knot_id: str, n_components: int):
    """Returns (chi_spin, stretch_lambda) based on topology."""
    if n_components >= 2:
        return 1.0, math.sqrt(10.0) # Links: Bosonic (chi=1) and stretched (lambda=~3.16)

    amphichiral_knots = ["0:1:1", "4:1:1", "6:3:1", "8:3:1", "8:9:1"]
    if knot_id in amphichiral_knots:
        return 1.0, math.sqrt(10.0) # Amphichiral: Bosonic and stretched

    return 2.0, 1.0 # Default Chiral Knot: Fermionic (chi=2), unstretched (lambda=1)

def find_top_pdg_matches(calculated_mass_mev, top_n=3):
    matches = []
    for name, pdg_mass in PDG_DATABASE.items():
        ratio = calculated_mass_mev / pdg_mass
        diff = abs(ratio - 1.0) if ratio > 1.0 else abs((1.0/ratio) - 1.0)
        matches.append((diff, name, pdg_mass, ratio))
    matches.sort(key=lambda x: x[0])
    return matches[:top_n]

def scan_topology(knot_id, M0, k_val, g_val, n_components):
    chi_val, lambda_val = auto_determine_physics(knot_id, n_components)
    particle_type = "Fermion" if chi_val == 2.0 else "Boson"

    print(f"\n[>] Analyzing {knot_id} (k={k_val:.3f}, g={g_val}, n={n_components}) -> {particle_type} (chi={chi_val}, lambda={lambda_val:.2f})")

    try:
        particle = sstcore.ParticleEvaluator(knot_id, resolution=2000)
        particle.relax(iterations=1500, timestep=0.005)
        # C++ Engine inherently scales dimless_L by 1 / lambda^2
        L_tot = particle.get_dimless_ropelength(stretch_lambda=lambda_val)
    except Exception as e:
        print(f"    [!] Simulation Error: {e}")
        return

    print(f"    [+] Effective Ab Initio L_tot: {L_tot:.3f}")

    braid_suppression = k_val ** -1.5
    genus_suppression = phi0 ** -g_val
    component_suppression = n_components ** (-1.0 / phi0)

    for G in [0, 1, 2, 3]:
        amplification = (4.0 / alpha_fs) ** G
        mass_mev = M0 * chi_val * amplification * braid_suppression * genus_suppression * component_suppression * L_tot

        top_matches = find_top_pdg_matches(mass_mev, top_n=3)
        best_diff = top_matches[0][0]

        if best_diff < 0.6: # Print if within 60% error margin
            print(f"        -> G={G}: {mass_mev:12.3f} MeV")
            for rank, (diff, name, pdg, ratio) in enumerate(top_matches):
                if diff < 0.8:
                    print(f"             #{rank+1}: {name:25} (Ratio: {ratio:.3f})")

# =====================================================================
# 3. EXECUTION
# =====================================================================
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

def _main_search_particles():
    print("\n=== SST PARTICLE SEARCH ENGINE (INVARIANT AB INITIO) ===")

    ELECTRON_MASS_MEV = 0.51099895
    print("\n[*] Calibrating global Ether density via the Electron (3_1)...")
    e_particle = sstcore.ParticleEvaluator("3:1:1", resolution=2000)
    e_particle.relax(iterations=1500, timestep=0.005)
    L_tot_electron = e_particle.get_dimless_ropelength(stretch_lambda=1.0)

    M0 = ELECTRON_MASS_MEV / (2.0 * (3.0**-1.5) * (phi0**-1) * (1.0**(-1.0/phi0)) * L_tot_electron)
    print(f"[+] Calibration complete. Global M0 = {M0:.6f} MeV per L_tot")

    test_knots = [
        # Exotic limits
        ("0:1:2", 1.0, 0, 2),                           # Unlink (2-components)
        ("6:2:3", 6.0, 2, 3),                           # Borromean Rings (3-components)

        # Force Carriers
        ("0:1:1", 1.0, 0, 1),                           # Unknot
        ("2:2:1", 2.0, 1, 2),                           # Hopf Link
        ("4:1:1", k_from_twist_alexander(1), 1, 1),     # Figure-Eight

        # Fermion Roster
        ("3:1:1", 3.0, 1, 1),                           # Trefoil
        ("5:1:1", 5.0, 2, 1),                           # Torus 5_1
        ("5:1:2", k_from_twist_alexander(2), 1, 1),     # Twist 5_2
        ("6:1:1", k_from_twist_alexander(3), 1, 1),     # Twist 6_1
        ("7:1:1", 7.0, 3, 1),                           # Torus 7_1
        ("7:1:2", k_from_twist_alexander(4), 1, 1),     # Twist 7_2
        ("10:1:1", k_from_twist_alexander(7), 1, 1),    # Twist 10_1
    ]

    print("\n[*] Commencing systematic topological sweep...")
    for knot_id, k_val, g_val, n_val in test_knots:
        scan_topology(knot_id, M0, k_val, g_val, n_components=n_val)

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", f"search_particles_{datetime.now():%Y%m%d_%H%M%S}.txt")
    with open(out_path, "w", encoding="utf-8") as out_file:
        old_stdout = sys.stdout
        sys.stdout = Tee(old_stdout, out_file)
        try:
            _main_search_particles()
        finally:
            sys.stdout = old_stdout
    print(f"\n[+] Results also saved to {out_path}")