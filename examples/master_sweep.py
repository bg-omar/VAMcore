import os
import re
import sys
import csv
import math
import time
from datetime import datetime

try:
    import swirl_string_core as sstcore
except ImportError:
    import sstbindings as sstcore

# =====================================================================
# 1. CONSTANTS & PHYSICS FUNCTIONS
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
    # Approximate half-twists based on crossing number
    n = max(1.0, n_cross / 2.0)
    return ((2.0 * n + 1.0) + math.sqrt(4.0 * n + 1.0)) / (2.0 * n)

def k_from_crossings(crossings: float) -> float:
    if crossings <= 0: return 1.0
    t_plus = twist_t_plus(crossings)
    return (2.0 * math.log(phi0)) / math.log(t_plus)

def auto_determine_physics(knot_id: str, n_components: int):
    """Returns (chi_spin, stretch_lambda) based on topology."""
    if n_components >= 2:
        return 1.0, math.sqrt(10.0)

    amphichiral_knots = ["0:1:1", "4:1:1", "6:3:1", "8:3:1", "8:9:1", "8:12:1", "8:17:1", "8:18:1"]
    if knot_id in amphichiral_knots:
        return 1.0, math.sqrt(10.0)

    return 2.0, 1.0

def find_best_pdg_match(calculated_mass_mev):
    best_match = "None"
    best_ratio_diff = float('inf')
    best_ratio = 0.0
    for name, pdg_mass in PDG_DATABASE.items():
        ratio = calculated_mass_mev / pdg_mass
        diff = abs(ratio - 1.0) if ratio > 1.0 else abs((1.0/ratio) - 1.0)
        if diff < best_ratio_diff and diff < 0.6: # Only consider matches within 60% error
            best_ratio_diff = diff
            best_match = name
            best_ratio = ratio
    return best_match, best_ratio


def compute_mass_diagnostics(masses, matches, m_core):
    """Compute per-generation and best-match diagnostics vs ab initio core baseline.

    masses: list/tuple of length 4 of floats (MeV) for G = 0..3
    matches: list/tuple of length 4 of labels corresponding to masses
    m_core: float or None, ab initio core mass (MeV)
    """
    # Ensure we have indexes 0..3 safely
    masses = list(masses)
    matches = list(matches)

    delta_G = {}
    ratio_G = {}

    # ------------------------------------------------------------
    # NEW: apples-to-apples diagnostics vs ab initio core baseline
    # ------------------------------------------------------------
    if m_core is not None:
        denom = max(abs(m_core), 1e-30)
        for g in (0, 1, 2, 3):
            mg = masses[g]
            delta_G[g] = abs(mg - m_core) / denom
            ratio_G[g] = mg / denom
        # Backward-compatible legacy scalar (choose G1 as "human-scale" default)
        delta_kernel_abinitio = delta_G[1]
    else:
        for g in (0, 1, 2, 3):
            delta_G[g] = None
            ratio_G[g] = None
        delta_kernel_abinitio = None

    # ------------------------------------------------------------
    # NEW: Best kernel match summary across generations (for CSV readability)
    # ------------------------------------------------------------
    candidates = []
    for g in (0, 1, 2, 3):
        mg = masses[g]
        if m_core is not None:
            score = abs(mg - m_core)
        else:
            score = abs(mg)
        candidates.append((score, g, mg, matches[g]))

    if candidates:
        _, g_best, m_best, label_best = min(candidates, key=lambda t: t[0])
        Best_G = int(g_best)
        Best_Mass_MeV = float(m_best)
        Best_Match_Label = label_best
        if m_core is not None:
            denom = max(abs(m_core), 1e-30)
            Best_delta_vs_abinitio_core = abs(m_best - m_core) / denom
            Best_ratio_to_abinitio_core = m_best / denom
        else:
            Best_delta_vs_abinitio_core = None
            Best_ratio_to_abinitio_core = None
    else:
        Best_G = None
        Best_Mass_MeV = None
        Best_Match_Label = None
        Best_delta_vs_abinitio_core = None
        Best_ratio_to_abinitio_core = None

    return {
        "delta_G": delta_G,
        "ratio_G": ratio_G,
        "delta_kernel_vs_abinitio_core": delta_kernel_abinitio,
        "Best_G": Best_G,
        "Best_Mass_MeV": Best_Mass_MeV,
        "Best_Match_Label": Best_Match_Label,
        "Best_delta_vs_abinitio_core": Best_delta_vs_abinitio_core,
        "Best_ratio_to_abinitio_core": Best_ratio_to_abinitio_core,
    }

# =====================================================================
# 2. DATABASE PARSER
# =====================================================================
def parse_ideal_database(filepath: str):
    """Extracts all Knot IDs and component counts from the raw XML-like text."""
    if not os.path.exists(filepath):
        print(f"[!] Database file not found at: {filepath}")
        return []

    with open(filepath, 'r') as file:
        content = file.read()

    # Regex to find blocks: <AB Id="...
    ab_blocks = re.finditer(r'<AB Id="([^"]+)"', content)
    knots = []

    for match in ab_blocks:
        knot_id = match.group(1)
        # Extract crossing number from ID (e.g., "10:1:1" -> 10)
        try:
            crossings = int(knot_id.split(':')[0])
        except:
            crossings = 0

        # Find the end of this specific block to count components
        start_idx = match.end()
        end_idx = content.find('</AB>', start_idx)
        if end_idx == -1: end_idx = len(content)

        block_content = content[start_idx:end_idx]
        n_components = block_content.count('<Component')
        if n_components == 0:
            n_components = 1 # Default to 1 for standard knots

        knots.append({
            "id": knot_id,
            "crossings": crossings,
            "components": n_components
        })

    return knots

# =====================================================================
# 3. THE MASTER SWEEP
# =====================================================================
def run_master_sweep(db_path: str, output_csv: str):
    print("\n=== SST MASTER SWEEP PIPELINE ===")
    knots_to_process = parse_ideal_database(db_path)
    print(f"[*] Found {len(knots_to_process)} unique topologies in database.")

    if not knots_to_process:
        return

    ELECTRON_MASS_MEV = 0.51099895
    print("[*] Calibrating global Ether density via the Electron (3:1:1)...")
    try:
        e_particle = sstcore.ParticleEvaluator("3:1:1", resolution=1500)
        e_particle.relax(iterations=1500, timestep=0.005)
        L_tot_e = e_particle.get_dimless_ropelength(stretch_lambda=1.0)
        k_e = k_from_crossings(3)
        M0 = ELECTRON_MASS_MEV / (2.0 * (k_e**-1.5) * (phi0**-1) * (1.0**(-1.0/phi0)) * L_tot_e)
        print(f"[+] Calibration complete. M0 = {M0:.6f} MeV")
    except Exception as e:
        print(f"[!] Calibration failed: {e}. Aborting.")
        return

    print(f"[*] Commencing batch processing. Results will be saved to {output_csv}")

    with open(output_csv, mode='w', newline='') as csv_file:
        fieldnames = ['Knot_ID', 'Crossings', 'Components', 'Chi_Spin', 'Lambda', 'L_tot',
                      'M_abinitio_core_MeV', 'delta_kernel_vs_abinitio_core',
                      'Mass_G0_MeV', 'Match_G0', 'delta_G0_vs_abinitio_core', 'ratio_G0_to_abinitio_core',
                      'Mass_G1_MeV', 'Match_G1', 'delta_G1_vs_abinitio_core', 'ratio_G1_to_abinitio_core',
                      'Mass_G2_MeV', 'Match_G2', 'delta_G2_vs_abinitio_core', 'ratio_G2_to_abinitio_core',
                      'Mass_G3_MeV', 'Match_G3', 'delta_G3_vs_abinitio_core', 'ratio_G3_to_abinitio_core',
                      'Best_G', 'Best_Mass_MeV', 'Best_Match_Label', 'Best_delta_vs_abinitio_core', 'Best_ratio_to_abinitio_core']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for idx, knot in enumerate(knots_to_process):
            k_id = knot['id']
            n_comp = knot['components']
            crossings = knot['crossings']

            print(f"    [{idx+1}/{len(knots_to_process)}] Simulating {k_id}...", end='', flush=True)

            k_val = k_from_crossings(crossings)
            g_val = max(1, crossings // 3) # Baseline genus approximation for sweep
            chi_val, lambda_val = auto_determine_physics(k_id, n_comp)

            try:
                # Lower resolution slightly to 1000 for faster batch processing
                particle = sstcore.ParticleEvaluator(k_id, resolution=1000)
                particle.relax(iterations=1200, timestep=0.005)
                L_tot = particle.get_dimless_ropelength(stretch_lambda=lambda_val)
                try:
                    # Core-only ab initio baseline (no tail term yet)
                    M_abinitio_core = particle.get_mass_mev_ab_initio(False)
                except AttributeError:
                    M_abinitio_core = None
                print(f" DONE (L_tot: {L_tot:.2f})")
            except Exception as e:
                print(f" ERROR ({e})")
                continue

            braid_supp = k_val ** -1.5
            genus_supp = phi0 ** -g_val
            comp_supp = n_comp ** (-1.0 / phi0)

            masses = []
            matches = []
            for G in [0, 1, 2, 3]:
                amplification = (4.0 / alpha_fs) ** G
                mass = M0 * chi_val * amplification * braid_supp * genus_supp * comp_supp * L_tot
                match_name, _ = find_best_pdg_match(mass)
                masses.append(mass)
                matches.append(match_name)

            diagnostics = compute_mass_diagnostics(masses, matches, M_abinitio_core)
            delta_G = diagnostics["delta_G"]
            ratio_G = diagnostics["ratio_G"]
            # NOTE:
            # "kernel vs abinitio core" is not a final physical validation metric.
            # It is a scale diagnostic until E_tail (or a surrogate) is included.
            delta_kernel_abinitio = diagnostics["delta_kernel_vs_abinitio_core"]
            Best_G = diagnostics["Best_G"]
            Best_Mass_MeV = diagnostics["Best_Mass_MeV"]
            Best_Match_Label = diagnostics["Best_Match_Label"]
            Best_delta_vs_abinitio_core = diagnostics["Best_delta_vs_abinitio_core"]
            Best_ratio_to_abinitio_core = diagnostics["Best_ratio_to_abinitio_core"]

            writer.writerow({
                'Knot_ID': k_id,
                'Crossings': crossings,
                'Components': n_comp,
                'Chi_Spin': chi_val,
                'Lambda': lambda_val,
                'L_tot': round(L_tot, 3),
                'M_abinitio_core_MeV': round(M_abinitio_core, 3) if M_abinitio_core is not None else '',
                'delta_kernel_vs_abinitio_core': round(delta_kernel_abinitio, 6) if delta_kernel_abinitio is not None else '',
                'Mass_G0_MeV': round(masses[0], 3),
                'Match_G0': matches[0],
                'delta_G0_vs_abinitio_core': round(delta_G[0], 6) if delta_G[0] is not None else '',
                'ratio_G0_to_abinitio_core': round(ratio_G[0], 6) if ratio_G[0] is not None else '',
                'Mass_G1_MeV': round(masses[1], 3),
                'Match_G1': matches[1],
                'delta_G1_vs_abinitio_core': round(delta_G[1], 6) if delta_G[1] is not None else '',
                'ratio_G1_to_abinitio_core': round(ratio_G[1], 6) if ratio_G[1] is not None else '',
                'Mass_G2_MeV': round(masses[2], 3),
                'Match_G2': matches[2],
                'delta_G2_vs_abinitio_core': round(delta_G[2], 6) if delta_G[2] is not None else '',
                'ratio_G2_to_abinitio_core': round(ratio_G[2], 6) if ratio_G[2] is not None else '',
                'Mass_G3_MeV': round(masses[3], 3),
                'Match_G3': matches[3],
                'delta_G3_vs_abinitio_core': round(delta_G[3], 6) if delta_G[3] is not None else '',
                'ratio_G3_to_abinitio_core': round(ratio_G[3], 6) if ratio_G[3] is not None else '',
                'Best_G': Best_G,
                'Best_Mass_MeV': round(Best_Mass_MeV, 3) if Best_Mass_MeV is not None else '',
                'Best_Match_Label': Best_Match_Label or '',
                'Best_delta_vs_abinitio_core': round(Best_delta_vs_abinitio_core, 6) if Best_delta_vs_abinitio_core is not None else '',
                'Best_ratio_to_abinitio_core': round(Best_ratio_to_abinitio_core, 6) if Best_ratio_to_abinitio_core is not None else '',
            })

            # Flush periodically so data is saved even if stopped halfway
            if idx % 5 == 0:
                csv_file.flush()

    print("\n[+] Master Sweep Complete!")

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

if __name__ == "__main__":
    # Adjust this path if your ideal_database.txt is located elsewhere
    DATABASE_PATH = "ideal_database.txt"
    os.makedirs("output", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_FILE = os.path.join("output", f"sst_master_sweep_results_{ts}.csv")
    LOG_FILE = os.path.join("output", f"sst_master_sweep_log_{ts}.txt")

    with open(LOG_FILE, "w", encoding="utf-8") as log_file:
        old_stdout = sys.stdout
        sys.stdout = Tee(old_stdout, log_file)
        try:
            run_master_sweep(DATABASE_PATH, OUTPUT_FILE)
        finally:
            sys.stdout = old_stdout
    print(f"\n[+] Log saved to {LOG_FILE}")