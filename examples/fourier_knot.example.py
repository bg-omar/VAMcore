# fourier_knot.example.py
import numpy as np
from sstbindings import load_knot_from_fseries, evaluate_fourier_block, curvature_of_points

# Load (auto-selects largest block), evaluate at 1000 points, returns centered points + curvature
pts, kappa = load_knot_from_fseries("myKnot.fseries", 1000)

# Or evaluate from raw coefficient arrays (all same length N)
# coeffs is a dict of 6 arrays: a_x,b_x,a_y,b_y,a_z,b_z
# pts2 = evaluate_fourier_block(coeffs, np.linspace(0, 2*np.pi, 1000))

# You can also compute curvature for any Nx3 array of points:
# kappa2 = curvature_of_points(pts2)

print(pts.shape, kappa.shape)