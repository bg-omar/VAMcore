
import vambindings as vam
from vam import circulation_surface_integral, enstrophy
import numpy as np

# Load knot points
pts, kappa = vam.load_knot_from_fseries("example.fseries", 200)
grid_size = 32
spacing = 0.1
coords = np.linspace(-grid_size//2*spacing, grid_size//2*spacing, grid_size)
X, Y, Z = np.meshgrid(coords, coords, coords, indexing='ij')
grid_points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1).tolist()

# Velocity
vel = vam.BiotSavart.compute_velocity(pts, grid_points)

# Vorticity
shape = (grid_size, grid_size, grid_size)
vort = vam.BiotSavart.compute_vorticity(vel, shape, spacing)

# Extract interior
margin = 8
v_sub = vam.BiotSavart.extract_interior(vel, shape, margin)
w_sub = vam.BiotSavart.extract_interior(vort, shape, margin)

# r_sq array for invariants
coords_interior = coords[margin:-margin]
Xf, Yf, Zf = np.meshgrid(coords_interior, coords_interior, coords_interior, indexing='ij')
r_sq = (Xf**2 + Yf**2 + Zf**2).ravel().tolist()

# Invariants
Hc, Hm, amu = vam.BiotSavart.compute_invariants(v_sub, w_sub, r_sq)
print(Hc, Hm, amu)
