import numpy as np
import os
script_name = os.path.splitext(os.path.basename(__file__))[0]
# Load the module dynamically from the compiled path
module_path = os.path.abspath("../build/Debug/swirl_string_core.cp312-win_amd64.pyd")
module_name = "sstcore"
import sys
sys.path.insert(0, os.path.abspath("."))
import swirl_string_core
from swirl_string_core import circulation_surface_integral, enstrophy, BiotSavart, parse_fseries_multi, index_of_largest_block, evaluate_fourier_block

# Load knot points from .fseries file
blocks = parse_fseries_multi("example.fseries")
block_idx = index_of_largest_block(blocks)
block = blocks[block_idx]
s_vals = np.linspace(0, 2*np.pi, 200, endpoint=False).tolist()
pts_vec = evaluate_fourier_block(block, s_vals)
pts = np.array([[p[0], p[1], p[2]] for p in pts_vec])
grid_size = 32
spacing = 0.1
coords = np.linspace(-grid_size//2*spacing, grid_size//2*spacing, grid_size)
X, Y, Z = np.meshgrid(coords, coords, coords, indexing='ij')
grid_points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1).tolist()

# Velocity
vel = BiotSavart.compute_velocity(pts.tolist(), grid_points)

# Vorticity
shape = (grid_size, grid_size, grid_size)
vort = BiotSavart.compute_vorticity(vel, shape, spacing)

# Extract interior
margin = 8
v_sub = BiotSavart.extract_interior(vel, shape, margin)
w_sub = BiotSavart.extract_interior(vort, shape, margin)

# r_sq array for invariants
coords_interior = coords[margin:-margin]
Xf, Yf, Zf = np.meshgrid(coords_interior, coords_interior, coords_interior, indexing='ij')
r_sq = (Xf**2 + Yf**2 + Zf**2).ravel().tolist()

# Invariants
Hc, Hm, amu = BiotSavart.compute_invariants(v_sub, w_sub, r_sq)
print(Hc, Hm, amu)