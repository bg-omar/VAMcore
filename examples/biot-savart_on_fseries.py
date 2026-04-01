import numpy as np
import math
import pandas as pd
from pathlib import Path

# --- SSTcore Bindings ---
try:
    from sstbindings import fourier_knot_eval, biot_savart_velocity_grid
    HAVE_SST = True
except ImportError:
    HAVE_SST = False
    print("[!] SSTcore library niet gevonden. Zorg dat de PyBind11 module is gecompileerd.")

# --- SST Canon Constanten ---
c = 299_792_458.0
r_c = 1.408_970_17e-15
v_swirl = 1.093_845_63e6
rho_core = 3.8934358266918687e18
rho_f = 7.0e-7

def compute_3d_mass_sstcore(coeffs, N_segments=5000, grid_size=64, padding_factor=4.0):
    if not HAVE_SST: return 0, 0

    # 1. Supersnelle C++ Fourier Evaluatie
    s = np.linspace(0, 2*math.pi, N_segments, endpoint=False)
    x, y, z = fourier_knot_eval(
        coeffs['a_x'], coeffs['b_x'],
        coeffs['a_y'], coeffs['b_y'],
        coeffs['a_z'], coeffs['b_z'],
        s.astype(float)
    )
    polyline = np.stack([x, y, z], axis=1)

    # (Hier schalen we polyline. Scaling code vergelijkbaar met eerdere scripts)
    # ... scaling naar D_raw = 2*r_c ...

    # 2. Setup 3D Evaluatie Grid
    box_min = np.min(polyline, axis=0) - padding_factor * r_c
    box_max = np.max(polyline, axis=0) + padding_factor * r_c

    spacing = (box_max[0] - box_min[0]) / grid_size
    grid_range_x = np.linspace(box_min[0], box_max[0], grid_size)
    grid_range_y = np.linspace(box_min[1], box_max[1], grid_size)
    grid_range_z = np.linspace(box_min[2], box_max[2], grid_size)

    X, Y, Z = np.meshgrid(grid_range_x, grid_range_y, grid_range_z, indexing='ij')
    grid_points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=-1)
    dV = spacing**3

    # 3. Supersnelle C++ Biot-Savart Integratie over ether-grid
    # Gegeven de circulatie Gamma berekent dit de vloeistofvelden
    velocity_grid = biot_savart_velocity_grid(polyline.astype(float), grid_points.astype(float))

    # Pas regularisatie en circulatie-schaal (Gamma) toe indien nodig,
    # afhankelijk van hoe uw C++ core exact werkt.
    v_squared = np.sum(velocity_grid**2, axis=1)

    # 4. Numerieke Integratie (E = 1/2 rho v^2 V)
    E_fluid = np.sum(0.5 * rho_f * v_squared * dV)
    M_fluid = E_fluid / (c**2)

    return M_fluid