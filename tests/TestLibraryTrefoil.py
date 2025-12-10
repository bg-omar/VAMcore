# Re-run after environment reset
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import sstbindings
print(sstbindings.vorticity_z_2D(3.0, 1.0))  # Example


import os
script_name = os.path.splitext(os.path.basename(__file__))[0]
from matplotlib.colors import TwoSlopeNorm
from sstbindings import VortexKnotSystem, biot_savart_velocity, compute_kinetic_energy

# Simulated data for demonstration
plotGridsize = 50
n_vectors = 9
rho_ae = 7.0e-7
rotation_axis = "z"
pole_axis = "y"
blend_factor = 0.5

# Initialize trefoil knot
knot = VortexKnotSystem()
knot.initialize_trefoil_knot()
positions = np.array(knot.get_positions())
tangents = np.array(knot.get_tangents())

# Mock grid and velocity field
xv = np.linspace(-plotGridsize, plotGridsize, n_vectors)
yv = np.linspace(-plotGridsize, plotGridsize, n_vectors)
zv = np.linspace(-plotGridsize, plotGridsize, n_vectors)
Xg, Yg, Zg = np.meshgrid(xv, yv, zv)
points = np.stack((Xg, Yg, Zg), axis=-1).reshape(-1, 3)

# Biot–Savart velocity field
V = np.array([biot_savart_velocity(p.tolist(), positions.tolist(), tangents.tolist()) for p in points])
Vmag = np.linalg.norm(V, axis=1)
Vnorm = V / Vmag[:, np.newaxis]

# Reshape for gradient calculations
Vgrid = V.reshape(n_vectors, n_vectors, n_vectors, 3)
vx, vy, vz = Vgrid[..., 0], Vgrid[..., 1], Vgrid[..., 2]

# Compute vorticity components
dvx_dy = np.gradient(vx, yv, axis=1)
dvx_dz = np.gradient(vx, zv, axis=2)
dvy_dx = np.gradient(vy, xv, axis=0)
dvy_dz = np.gradient(vy, zv, axis=2)
dvz_dx = np.gradient(vz, xv, axis=0)
dvz_dy = np.gradient(vz, yv, axis=1)

omega_x = dvz_dy - dvy_dz
omega_y = dvx_dz - dvz_dx
omega_z = dvy_dx - dvx_dy

# Select swirl axis
swirl = {'x': omega_x, 'y': omega_y, 'z': omega_z}[rotation_axis]

# Compute swirl coloring
swirl_flat = swirl.ravel()
norm_swirl = TwoSlopeNorm(vcenter=0.0)
swirl_colors = plt.cm.gray_r(norm_swirl(swirl_flat))

# Simulate tangent vectors for poles
tangents = np.tile(np.array([0, 0, 1]), (points.shape[0], 1))
B_magnitude = np.linalg.norm(tangents, axis=1)
Bx, By, Bz = tangents[:, 0] / B_magnitude, tangents[:, 1] / B_magnitude, tangents[:, 2] / B_magnitude

# Compute pole direction (simplified mock)
dBx_dz = np.gradient(Bx)
dBz_dx = np.gradient(Bz)
pole_direction = dBx_dz - dBz_dx
pole_normalized = (pole_direction - np.min(pole_direction)) / (np.max(pole_direction) - np.min(pole_direction))
pole_colors = plt.cm.Greys(pole_normalized)

# Blend swirl and pole colors
final_colors = blend_factor * swirl_colors + (1 - blend_factor) * pole_colors

# Plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.quiver(points[:, 0], points[:, 1], points[:, 2],
          Vnorm[:, 0], Vnorm[:, 1], Vnorm[:, 2],
          length=(plotGridsize/10), normalize=True, color=final_colors, alpha=0.75)

ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
        color='red', linewidth=2, label='Trefoil Vortex Filament')

ax.set_title("Swirl (Gray) + Poles (Greyscale) Coloring of Velocity Field")
ax.set_xlim(-plotGridsize, plotGridsize)
ax.set_ylim(-plotGridsize, plotGridsize)
ax.set_zlim(-plotGridsize, plotGridsize)
ax.set_xlabel('x (m)')
ax.set_ylabel('y (m)')
ax.set_zlabel('z (m)')
ax.set_box_aspect([1, 1, 1])
plt.tight_layout()
plt.show()