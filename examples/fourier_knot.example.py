# fourier_knot.example.py
import numpy as np
from swirl_string_core import parse_fseries_multi, index_of_largest_block, evaluate_fourier_block

# Load (auto-selects largest block), evaluate at 1000 points
blocks = parse_fseries_multi("myKnot.fseries")
block_idx = index_of_largest_block(blocks)
block = blocks[block_idx]
s_vals = np.linspace(0, 2*np.pi, 1000, endpoint=False).tolist()
pts_vec = evaluate_fourier_block(block, s_vals)
pts = np.array([[p[0], p[1], p[2]] for p in pts_vec])

# Or evaluate from raw coefficient arrays (all same length N)
# Create a FourierBlock manually with a_x, b_x, a_y, b_y, a_z, b_z arrays
# block = FourierBlock()
# block.a_x = [...]; block.b_x = [...]; etc.
# pts2 = evaluate_fourier_block(block, np.linspace(0, 2*np.pi, 1000).tolist())

# Note: curvature_of_points is not currently bound; use Python implementation if needed
# def curvature_of_points(pts):
#     diffs = np.diff(pts, axis=0)
#     d2 = np.diff(diffs, axis=0)
#     cross = np.cross(diffs[:-1], d2)
#     kappa = np.linalg.norm(cross, axis=1) / (np.linalg.norm(diffs[:-1], axis=1)**3 + 1e-9)
#     return kappa

print(pts.shape)