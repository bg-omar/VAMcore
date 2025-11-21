import numpy as np
import os
script_name = os.path.splitext(os.path.basename(__file__))[0]
# Load the module dynamically from the compiled path
module_path = os.path.abspath("../build/Debug/sstbindings.cp311-win_amd64.pyd")
module_name = "sstcore"
import sys
sys.path.insert(0, os.path.abspath("."))
from sstbindings import circulation_surface_integral, enstrophy as sst


# Load knot points
pts, kappa = sst.load_knot_from_fseries("example.fseries", 200)
grid_size = 32
spacing = 0.1
coords = np.linspace(-grid_size//2*spacing, grid_size//2*spacing, grid_size)
X, Y, Z = np.meshgrid(coords, coords, coords, indexing='ij')
grid_points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1).tolist()

# Velocity
vel = sst.BiotSavart.compute_velocity(pts, grid_points)

# Vorticity
shape = (grid_size, grid_size, grid_size)
vort = sst.BiotSavart.compute_vorticity(vel, shape, spacing)

# Extract interior
margin = 8
v_sub = sst.BiotSavart.extract_interior(vel, shape, margin)
w_sub = sst.BiotSavart.extract_interior(vort, shape, margin)

# r_sq array for invariants
coords_interior = coords[margin:-margin]
Xf, Yf, Zf = np.meshgrid(coords_interior, coords_interior, coords_interior, indexing='ij')
r_sq = (Xf**2 + Yf**2 + Zf**2).ravel().tolist()

# Invariants
Hc, Hm, amu = sst.BiotSavart.compute_invariants(v_sub, w_sub, r_sq)
print(Hc, Hm, amu)