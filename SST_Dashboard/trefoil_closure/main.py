import os
import sys
import glob
from setuptools import setup, Extension

def needs_recompile(cpp_file="sst_core.cpp", module_name="sst_core"):
    """Controleert of de broncode nieuwer is dan de gecompileerde binary."""
    if not os.path.exists(cpp_file):
        return False

    # Zoek naar gecompileerde binaries (ondersteunt .pyd op Windows en .so op Linux/Mac)
    compiled_files = glob.glob(f"{module_name}.*")

    # Filter bestanden die geen binaries zijn (bijv. .cpp of .py) uit de lijst
    binaries = [f for f in compiled_files if f.endswith('.pyd') or f.endswith('.so')]

    if not binaries:
        return True  # Geen binary gevonden, moet compileren

    # Pak de laatst gewijzigde binary
    latest_binary = max(binaries, key=os.path.getmtime)

    # Als de C++ file recenter is gewijzigd dan de binary, recompileer
    return os.path.getmtime(cpp_file) > os.path.getmtime(latest_binary)

def build_sst_core():
    import pybind11
    print("Bouwen van sst_core C++ module via pybind11...")
    ext_modules = [
        Extension(
            "sst_core",
            ["sst_core.cpp"],
            include_dirs=[pybind11.get_include()],
            language="c++",
            extra_compile_args=["-O3", "-std=c++11"]
        ),
    ]
    sys.argv = ["setup.py", "build_ext", "--inplace"]
    setup(
        name="sst_core",
        ext_modules=ext_modules,
        script_args=["build_ext", "--inplace"],
    )

# --- Automatische Hot-Reload Logica ---
if needs_recompile():
    print("Wijziging in sst_core.cpp gedetecteerd (of nog niet gecompileerd).")
    build_sst_core()

import sst_core
print("sst_core module succesvol geladen.")

# --- SST Canonieke Constanten ---
v_swirl = 1.09384563e6
r_c = 1.40897017e-15
rho_core = 3.8934358266918687e18

Gamma = 2 * np.pi * r_c * v_swirl
alpha = (rho_core * Gamma**2) / (4 * np.pi)

# Torusknoop parameters
R_major = 100 * r_c
r_minor = 30 * r_c
p, q = 2, 3

# Dynamische schaalfactoren voor L(K) en H(K)
# beta heeft dimensie [Kracht], gamma heeft dimensie [Energie]
beta = alpha * np.log(R_major / r_c)
gamma = alpha * r_c

# --- Topologische Generator ---
def generate_torus_knot(p, q, R, r, N_points=2000):
    sigma = np.linspace(0, 2 * np.pi, N_points, endpoint=False)
    points = np.zeros((N_points, 3))
    points[:, 0] = (R + r * np.cos(q * sigma)) * np.cos(p * sigma)
    points[:, 1] = (R + r * np.cos(q * sigma)) * np.sin(p * sigma)
    points[:, 2] = -r * np.sin(q * sigma)
    return points

points_knot = generate_torus_knot(p, q, R_major, r_minor)

# --- Evaluatie van de Functionaal E_eff[K] ---
print(f"\n--- Evaluatie Functionaal E_eff[K] voor ({p},{q})-Torus Knoop ---")

# 1. Biot-Savart (C)
C_K = sst_core.calculate_biot_savart_integral(points_knot, r_c)
E_C = alpha * C_K

# 2. Lijntensie (L)
L_K = sst_core.calculate_length(points_knot)
E_L = beta * L_K

# 3. Heliciteit / Writhe (H)
Wr = sst_core.calculate_writhe(points_knot, r_c)
E_H = gamma * abs(Wr)

# Totale Effectieve Energie
E_total = E_C + E_L + E_H

print(f"Biot-Savart Term (alpha * C) : {E_C:.4e} J")
print(f"Lijntensie Term (beta * L)   : {E_L:.4e} J")
print(f"Heliciteit Term (gamma * |H|): {E_H:.4e} J  [Writhe = {Wr:.4f}]")
print(f"--------------------------------------------------")
print(f"Totale Effectieve Energie    : {E_total:.4e} J")