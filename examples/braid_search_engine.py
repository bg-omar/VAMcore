import math
import os
import sys
from datetime import datetime

import numpy as np

try:
    import sstcore
except ImportError:
    import sstbindings as sstcore

class SSTFoundation:
    """
    Derives all Swirl-String Theory continuous fluid parameters dynamically
    from fundamental CODATA 2018 quantum constants (Zero Free Parameters).
    """
    def __init__(self):
        # 1. Standard CODATA 2018 Constants
        self.c = 299792458.0              # Speed of light [m/s]
        self.h_bar = 1.054571817e-34      # Reduced Planck constant [J s]
        self.m_e = 9.1093837015e-31       # Electron mass [kg]
        self.alpha = 0.0072973525693      # Fine-structure constant

        # 2. Derive SST Geometric Scales
        self.r_e = (self.alpha * self.h_bar) / (self.m_e * self.c)  # Classical electron radius
        self.r_c = self.r_e / 2.0                                   # Vortex core radius

        # 3. Derive SST Kinematic Scales
        self.omega_c = (self.m_e * self.c**2) / self.h_bar          # Compton angular frequency
        self.omega_swirl = self.alpha * self.omega_c                # Shielded characteristic vorticity
        self.v_swirl = (self.alpha * self.c) / 2.0                  # Characteristic core swirl speed

        # 4. Derive the Macroscopic Continuum Fluid Density (rho_f)
        # Using the exact volumetric energy integral from the SST Canon
        self.V_eff = (self.r_e**3) / 3.0
        self.rho_f = (2.0 * self.m_e * self.c**2) / ((self.omega_swirl**2) * self.V_eff)

    def boot_sequence(self):
        print("\n=== SST CONTINUUM FOUNDATION (ZERO-PARAMETER BOOT) ===")
        print("[*] Loading CODATA 2018 Quantum Constants...")
        print(f"    m_e   = {self.m_e} kg")
        print(f"    c     = {self.c} m/s")
        print(f"    h_bar = {self.h_bar} J s")
        print(f"    alpha = {self.alpha}")
        print("\n[*] Deriving Fluid Continuum Parameters...")
        print(f"    [+] Core Radius (r_c)    = {self.r_c:.7e} m")
        print(f"    [+] Swirl Speed (v_swirl)= {self.v_swirl:.2f} m/s")
        print(f"    [+] Fluid Density (rho_f)= {self.rho_f:.7e} kg/m^3")
        print("========================================================\n")

# =====================================================================
# 1. BRAID TO 3D GENERATOR
# =====================================================================
class BraidTo3D:
    @staticmethod
    def generate_filaments(braid_word, num_strands=None, resolution_per_cross=60):
        if num_strands is None:
            num_strands = max([abs(c) for c in braid_word]) + 1 if braid_word else 1

        strands = [[(float(i), 0.0, 0.0)] for i in range(num_strands)]
        current_pos = {i: i for i in range(num_strands)}
        pos_to_strand = {i: i for i in range(num_strands)}

        z_current = 0.0
        dz = 2.0

        for crossing in braid_word:
            pos_idx = abs(crossing) - 1
            sign = 1 if crossing > 0 else -1

            s1 = pos_to_strand[pos_idx]
            s2 = pos_to_strand[pos_idx + 1]

            for step in range(1, resolution_per_cross + 1):
                t = step / float(resolution_per_cross)
                z = z_current + t * dz

                x1 = pos_idx + t
                y1 = sign * 0.5 * np.sin(t * np.pi)
                strands[s1].append((x1, y1, z))

                x2 = pos_idx + 1 - t
                y2 = -sign * 0.5 * np.sin(t * np.pi)
                strands[s2].append((x2, y2, z))

                for p in range(num_strands):
                    if p != pos_idx and p != pos_idx + 1:
                        s_other = pos_to_strand[p]
                        strands[s_other].append((float(p), 0.0, z))

            current_pos[s1] = pos_idx + 1
            current_pos[s2] = pos_idx
            pos_to_strand[pos_idx] = s2
            pos_to_strand[pos_idx + 1] = s1
            z_current += dz

        visited_strands = set()
        closed_components = []
        R_OUT = 3.0

        for start_s in range(num_strands):
            if start_s in visited_strands:
                continue

            current_s = start_s
            component_points = []

            while True:
                visited_strands.add(current_s)
                component_points.extend(strands[current_s])
                end_x = float(current_pos[current_s])

                # Close the loop
                component_points.append((end_x, 0.0, z_current + 1.0))
                component_points.append((end_x, R_OUT, z_current + 1.0))
                component_points.append((end_x, R_OUT, -1.0))
                component_points.append((end_x, 0.0, -1.0))
                component_points.append((end_x, 0.0, 0.0))

                next_s = end_x
                if next_s == start_s:
                    break
                current_s = int(next_s)

            closed_components.append(component_points)

        return closed_components

# =====================================================================
# 2. PHYSICS & MASS EVALUATION
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

def twist_t_plus(n_cross: float) -> float:
    n = max(1.0, n_cross / 2.0)
    return ((2.0 * n + 1.0) + math.sqrt(4.0 * n + 1.0)) / (2.0 * n)

def k_from_crossings(crossings: float) -> float:
    if crossings <= 0: return 1.0
    t_plus = twist_t_plus(crossings)
    return (2.0 * math.log(phi0)) / math.log(t_plus)

def evaluate_braid_particle(name, braid_word, rho_0, amphichiral=False):
    print(f"\n[>] Simulating {name} | Braid: {braid_word}")

    crossings = len(braid_word)
    strands_needed = max([abs(c) for c in braid_word]) + 1 if braid_word else 2

    # 1. Generate Geometry
    raw_filaments = BraidTo3D.generate_filaments(braid_word, num_strands=strands_needed)
    n_comp = len(raw_filaments)

    # 2. Determine Physics Limits
    is_boson = (n_comp >= 2) or amphichiral
    chi_val = 1.0 if is_boson else 2.0
    lambda_val = math.sqrt(10.0) if is_boson else 1.0
    k_val = k_from_crossings(crossings)
    g_val = max(1, crossings // 3)

    # 3. Hamiltonian Collapse
    particle = sstcore.ParticleEvaluator(raw_filaments)
    particle.relax(iterations=1200, timestep=0.005)
    L_tot = particle.get_dimless_ropelength(stretch_lambda=lambda_val)

    print(f"    [+] Topology: {n_comp} component(s), Crossings: {crossings}, Type: {'Boson' if is_boson else 'Fermion'}")
    print(f"    [+] Effective L_tot: {L_tot:.3f}")

    # 4. Mass Functional
    braid_supp = k_val ** -1.5
    genus_supp = phi0 ** -g_val
    comp_supp = n_comp ** (-1.0 / phi0)

    for G in [0, 1, 2]:
        amplification = (4.0 / alpha_fs) ** G
        mass_mev = rho_0 * chi_val * amplification * braid_supp * genus_supp * comp_supp * L_tot

        # Find best match
        best_match, best_diff, best_ratio = "None", float('inf'), 0.0
        for pdg_name, pdg_mass in PDG_DATABASE.items():
            ratio = mass_mev / pdg_mass
            diff = abs(ratio - 1.0) if ratio > 1.0 else abs((1.0/ratio) - 1.0)
            if diff < best_diff and diff < 0.6:
                best_diff, best_match, best_ratio = diff, pdg_name, ratio

        if best_match != "None":
            print(f"        -> G={G}: {mass_mev:10.2f} MeV | Match: {best_match:20} (Ratio: {best_ratio:.3f})")

# =====================================================================
# 3. HYBRID BRAID DICTIONARY & AUTOMATED FETCHING
# =====================================================================
# =====================================================================
# 3. CANON-COMPLIANT MASTER DICTIONARY
# Format: "Name": ("SnapPy_Target/Array", exact_b_val, exact_g_val)
# =====================================================================
SST_EXACT_DICTIONARY = {
    # =====================================================================
    # --- 2-COMPONENT LINKS (Bosons / Mesons / Neutrino Architectures) ---
    # =====================================================================
    "Link 2^2_1 (Hopf Link)": ("2^2_1", 2.0, 0, 2),
    "Link 4^2_1 (Solomon's Knot)": ("4^2_1", 2.0, 1, 2),
    "Link 5^2_1 (Whitehead Link)": ("5^2_1", 3.0, 1, 2),
    "Link 6^2_1": ("6^2_1", 3.0, 1, 2),
    "Link 6^2_2": ("6^2_2", 3.0, 1, 2),
    "Link 8^2_1": ("8^2_1", 3.0, 2, 2),

    # =====================================================================
    # --- 3-COMPONENT LINKS (Fermions / Baryons / Triskelions) ---
    # =====================================================================
    "Link 6^3_1": ("6^3_1", 3.0, 0, 3),
    "Link 6^3_2 (Borromean Rings / Baryon)": ("6^3_2", 3.0, 1, 3),
    "Link 6^3_3": ("6^3_3", 3.0, 1, 3),

    # --- Bosons & Links (Hardcoded Arrays) ---
    "Unknot (1-comp)": ([1], 1.0, 0),
    "Unlink (2-comp)": ([1, -1], 1.0, 0),
    "Hopf Link (2^2_1)": ([1, 1], 2.0, 1),

    # --- 3 to 5 Crossings (Light Fermions) ---
    "Trefoil (3_1)": ("3_1", 3.0, 1), # Torus: b=3
    "Figure-Eight (4_1 / Amphichiral)": ("4_1", 1.0, 1), # Amphichiral: b=1
    "Torus 5_1": ("5_1", 5.0, 2), # Torus: b=5, g=2
    "Twist 5_2": ("5_2", k_from_crossings(5), 1), # Twist: g=1

    # --- 6 to 7 Crossings (Mid-Spectrum) ---
    "Twist 6_1": ("6_1", k_from_crossings(6), 1),
    "Knot 6_2": ("6_2", k_from_crossings(6), 1),
    "Knot 6_3 (Amphichiral)": ("6_3", 1.0, 1),
    "Torus 7_1": ("7_1", 7.0, 3), # Torus: b=7, g=3
    "Twist 7_2": ("7_2", k_from_crossings(7), 1),

    # --- 8 Crossings (Complete Family) ---
    "Twist 8_1": ("8_1", k_from_crossings(8), 1),
    "Knot 8_2": ("8_2", k_from_crossings(8), 2),
    "Knot 8_3 (Amphichiral)": ("8_3", 1.0, 1),
    "Knot 8_4": ("8_4", k_from_crossings(8), 1),
    "Knot 8_5": ("8_5", k_from_crossings(8), 2),
    "Knot 8_6": ("8_6", k_from_crossings(8), 2),
    "Knot 8_7": ("8_7", k_from_crossings(8), 2),
    "Knot 8_8": ("8_8", k_from_crossings(8), 2),
    "Knot 8_9 (Amphichiral)": ("8_9", 1.0, 1),
    "Knot 8_10": ("8_10", k_from_crossings(8), 2),
    "Knot 8_11": ("8_11", k_from_crossings(8), 1),
    "Knot 8_12 (Amphichiral)": ("8_12", 1.0, 2),
    "Knot 8_13": ("8_13", k_from_crossings(8), 1),
    "Knot 8_14": ("8_14", k_from_crossings(8), 2),
    "Knot 8_15": ("8_15", k_from_crossings(8), 2),
    "Knot 8_16": ("8_16", k_from_crossings(8), 2),
    "Knot 8_17 (Amphichiral / Non-Alternating)": ("8_17", 1.0, 1),
    "Knot 8_18 (Amphichiral)": ("8_18", 1.0, 1),
    "Torus 8_19 (T_3,4)": ("8_19", 8.0, 3), # Torus T(3,4): b=8, g=3
    "Knot 8_20": ("8_20", k_from_crossings(8), 1),
    "Knot 8_21": ("8_21", k_from_crossings(8), 2),

    # --- 9 to 10 Crossings (Heavy Fermions) ---
    "Torus 9_1": ("9_1", 9.0, 4), # Torus T(2,9): b=9, g=4
    "Twist 9_2": ("9_2", k_from_crossings(9), 1),
    "Twist 10_1": ("10_1", k_from_crossings(10), 1),
    "Torus 10_124 (T_3,5)": ("10_124", 10.0, 4), # Torus T(3,5): b=10, g=4

    # --- Ultra-High Crossing Candidates (Exotic States) ---
    "Knot 12a_1202": ("12a1202", k_from_crossings(12), 3),
    "Knot 15a_331": ("15a331", k_from_crossings(15), 4)
}

SST_APPENDIX_A_DICTIONARY = {

    # =====================================================================
    # --- 2-COMPONENT LINKS (Bosons / Mesons / Neutrino Architectures) ---
    # =====================================================================
    "Link 2^2_1 (Hopf Link)": ("2^2_1", 2.0, 0, 2),
    "Link 4^2_1 (Solomon's Knot)": ("4^2_1", 2.0, 1, 2),
    "Link 5^2_1 (Whitehead Link)": ("5^2_1", 3.0, 1, 2),
    "Link 6^2_1": ("6^2_1", 3.0, 1, 2),
    "Link 6^2_2": ("6^2_2", 3.0, 1, 2),
    "Link 8^2_1": ("8^2_1", 3.0, 2, 2),

    # =====================================================================
    # --- 3-COMPONENT LINKS (Fermions / Baryons / Triskelions) ---
    # =====================================================================
    "Link 6^3_1": ("6^3_1", 3.0, 0, 3),
    "Link 6^3_2 (Borromean Rings / Baryon)": ("6^3_2", 3.0, 1, 3),
    "Link 6^3_3": ("6^3_3", 3.0, 1, 3),

    # --- Bosons & Neutrinos (Links and Unknots) ---
    "Unknot (Boson)": ([1], 1.0, 0, 1),
    "Hopf Link (Neutrino/Boson)": ([1, 1], 2.0, 1, 2),

    # --- Lepton Ladder (Torus Knots T(2, q) -> b=2) ---
    "Trefoil (Electron / 3_1)": ("3_1", 2.0, 1, 1),
    "Torus 5_1 (Muon)": ("5_1", 2.0, 2, 1),
    "Torus 7_1 (Tau)": ("7_1", 2.0, 3, 1),
    "Torus 9_1": ("9_1", 2.0, 4, 1),

    # --- Quark Sector (Chiral Hyperbolics) ---
    "Twist 5_2": ("5_2", 3.0, 1, 1),
    "Twist 6_1": ("6_1", 3.0, 1, 1),
    "Knot 6_2": ("6_2", 3.0, 1, 1),
    "Twist 7_2": ("7_2", 3.0, 1, 1),
    "Knot 8_2": ("8_2", 3.0, 2, 1),

    # --- Dark Sector (Amphichiral) ---
    "Figure-Eight (4_1 / Dark)": ("4_1", 3.0, 1, 1),
    "Knot 6_3 (Dark)": ("6_3", 3.0, 1, 1),
    "Knot 8_3 (Dark)": ("8_3", 3.0, 1, 1),
    "Knot 8_9 (Dark)": ("8_9", 3.0, 1, 1),
    "Knot 8_12 (Dark)": ("8_12", 3.0, 2, 1),
    "Knot 8_17 (Dark / I2)": ("8_17", 3.0, 1, 1),

    # --- Heavy/Exotic States ---
    "Torus 8_19 (T(3,4))": ("8_19", 3.0, 3, 1),
    "Torus 10_124 (T(3,5))": ("10_124", 3.0, 4, 1),

    # --- Heavy Quark Sector (Higher-Order Twist Knots) ---
    "Twist 8_1": ("8_1", 3.0, 1, 1),
    "Twist 9_2": ("9_2", 3.0, 1, 1),
    "Twist 10_1": ("10_1", 3.0, 1, 1),
}

def fetch_braid_word(target):
    """Returns the direct array, or dynamically fetches it via SnapPy."""
    if isinstance(target, list):
        return target

    try:
        import snappy
        k = snappy.Link(target)
        return k.braid_word()
    except ImportError:
        print(f"[!] SnapPy is missing. Cannot fetch '{target}'. Run: pip install snappy")
        return None
    except Exception as e:
        print(f"[!] SnapPy evaluation failed for '{target}': {e}")
        return None

def evaluate_exact_particle(name, braid_target, exact_b, exact_g, exact_n, rho_0):
    print(f"[>] Simulating {name}")

    # 1. Fetch and generate Braid
    braid_word = fetch_braid_word(braid_target)
    if not braid_word: return

    strands_needed = max([abs(c) for c in braid_word]) + 1 if braid_word else 2
    raw_filaments = BraidTo3D.generate_filaments(braid_word, num_strands=strands_needed)

    # 2. Strict Physics Constraints
    is_amphichiral = "Dark" in name

    # EVEN components (2) = Bosons (Mesons). ODD components (1, 3) = Fermions (Leptons, Baryons).
    is_boson = (exact_n % 2 == 0) or is_amphichiral

    chi_val = 1.0 if is_boson else 2.0
    lambda_val = math.sqrt(10.0) if is_boson else 1.0

    # 3. Hamiltonian Collapse
    particle = sstcore.ParticleEvaluator(raw_filaments)
    particle.relax(iterations=1200, timestep=0.005)
    L_tot = particle.get_dimless_ropelength(stretch_lambda=lambda_val)

    print(f"    [+] Invariants -> b: {exact_b}, g: {exact_g}, n: {exact_n}, chi: {chi_val}")
    print(f"    [+] Effective L_tot: {L_tot:.3f}")

    # 4. Canonical Mass Functional: IM(K) * Lambda_0 * L_tot
    # Enforcing the exact topological parameters from Appendix A
    IM_K = (exact_b ** -1.5) * (phi0 ** -exact_g) * (exact_n ** (-1.0 / phi0))

    for G in [0, 1, 2]:
        amplification = (4.0 / alpha_fs) ** G
        mass_mev = rho_0 * chi_val * amplification * IM_K * L_tot

        # Matcher logic
        best_match, best_diff, best_ratio = "None", float('inf'), 0.0
        for pdg_name, pdg_mass in PDG_DATABASE.items():
            ratio = mass_mev / pdg_mass
            diff = abs(ratio - 1.0) if ratio > 1.0 else abs((1.0/ratio) - 1.0)
            if diff < best_diff and diff < 0.6:
                best_diff, best_match, best_ratio = diff, pdg_name, ratio

        if best_match != "None":
            print(f"        -> G={G}: {mass_mev:10.2f} MeV | Match: {best_match:20} (Ratio: {best_ratio:.3f})")

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

# =====================================================================
# 4. EXECUTION
# =====================================================================
def _main_braid_search():
    # 1. Boot the foundation from fundamental constants
    foundation = SSTFoundation()
    foundation.boot_sequence()

    print("=== SST AB INITIO GEOMETRY + CALIBRATED KERNEL BRAID SEARCH ENGINE ===")

    ELECTRON_MASS_MEV = 0.51099895
    print("\n[*] Calibrating kernel mass scale (rho_0) via the exact Braid Trefoil [1, 1, 1]...")

    try:
        e_filaments = BraidTo3D.generate_filaments([1, 1, 1], num_strands=2)
        e_particle = sstcore.ParticleEvaluator(e_filaments)
        e_particle.relax(iterations=1500, timestep=0.005)
        L_tot_e = e_particle.get_dimless_ropelength(stretch_lambda=1.0)

        # Exact invariants for the Electron (3_1): b=2.0, g=1, n=1, chi=2.0, G=0
        IM_K_e = (2.0 ** -1.5) * (phi0 ** -1.0) * (1.0 ** (-1.0 / phi0))
        rho_0 = ELECTRON_MASS_MEV / (2.0 * IM_K_e * L_tot_e)

        print(f"[+] Calibration complete. rho_0 = {rho_0:.6f} MeV / L_tot  (kernel scale, not rho_core / rho_f)\n")
    except Exception as e:
        print(f"[!] Critical Calibration Failure: {e}")
        import sys
        sys.exit(1)

    print("[*] Commencing automated spectrum evaluation...")

    # UNPACKING FIX: Now correctly expecting 4 values from the dictionary
    for knot_name, (target, exact_b, exact_g, exact_n) in SST_APPENDIX_A_DICTIONARY.items():
        word = fetch_braid_word(target)
        if not word:
            continue

        if isinstance(target, str):
            print(f"\n[+] SnapPy generated Braid Word for {knot_name}: {word}")

        evaluate_exact_particle(knot_name, target, exact_b, exact_g, exact_n, rho_0)

    print("\n[+] Deep Braid sweep completed successfully.")

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", f"braid_search_engine_{datetime.now():%Y%m%d_%H%M%S}.txt")
    with open(out_path, "w", encoding="utf-8") as out_file:
        old_stdout = sys.stdout
        sys.stdout = Tee(old_stdout, out_file)
        try:
            _main_braid_search()
        finally:
            sys.stdout = old_stdout
    print(f"\n[+] Results also saved to {out_path}")