import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import os
script_name = os.path.splitext(os.path.basename(__file__))[0]
# Load the module dynamically from the compiled path
module_path = os.path.abspath("../build/Debug/swirl_string_core.cp312-win_amd64.pyd")
module_name = "sstcore"
from swirl_string_core import VortexKnotSystem, biot_savart_velocity, compute_kinetic_energy

plotGridsize = 3
n_vectors = 15
rho_ae = 7.0e-7  # Æther density (kg/m³)
blend_factor = 1
rotation_axis = "z"
pole_axis = "y"


# Initialize trefoil knot
knot = VortexKnotSystem()
knot.initialize_trefoil_knot()
positions = np.array(knot.get_positions())
tangents = np.array(knot.get_tangents())

# Grid points
xv = np.linspace(-plotGridsize, plotGridsize, n_vectors)
yv = np.linspace(-plotGridsize, plotGridsize, n_vectors)
zv = np.linspace(-plotGridsize, plotGridsize, n_vectors)
Xg, Yg, Zg = np.meshgrid(xv, yv, zv)
points = np.stack((Xg, Yg, Zg), axis=-1).reshape(-1, 3)

# Biot–Savart velocity field
V = np.array([biot_savart_velocity(p.tolist(), positions.tolist(), tangents.tolist()) for p in points])
Vmag = np.linalg.norm(V, axis=1)
Vnorm = V / Vmag[:, np.newaxis]

# Compute kinetic energy from C++ binding
velocity_vectors = V.tolist()
kinetic_energy = compute_kinetic_energy(velocity_vectors, rho_ae)

# Color mapping
B_magnitude = np.linalg.norm(tangents, axis=1)
Bx, By, Bz = tangents[:, 0] / B_magnitude, tangents[:, 1] / B_magnitude, tangents[:, 2] / B_magnitude


if rotation_axis == "x":
    dBz_dy = np.gradient(Bz)
    dBy_dz = np.gradient(By)
    rotation_direction = dBz_dy - dBy_dz
elif rotation_axis == "y":
    dBx_dz = np.gradient(Bx)
    dBz_dx = np.gradient(Bz)
    rotation_direction = dBx_dz - dBz_dx
elif rotation_axis == "z":
    dBy_dx = np.gradient(By)
    dBx_dy = np.gradient(Bx)
    rotation_direction = dBy_dx - dBx_dy

if pole_axis == "x":
    dBz_dy = np.gradient(Bz)
    dBy_dz = np.gradient(By)
    pole_direction = dBz_dy - dBy_dz
elif pole_axis == "y":
    dBx_dz = np.gradient(Bx)
    dBz_dx = np.gradient(Bz)
    pole_direction = dBx_dz - dBz_dx
elif pole_axis == "z":
    dBy_dx = np.gradient(By)
    dBx_dy = np.gradient(Bx)
    pole_direction = dBy_dx - dBx_dy

rotation_normalized = (rotation_direction - np.min(rotation_direction)) / (np.max(rotation_direction) - np.min(rotation_direction))
pole_normalized = (pole_direction - np.min(pole_direction)) / (np.max(pole_direction) - np.min(pole_direction))

rot_cmap = plt.get_cmap("seismic")
pole_cmap = plt.get_cmap("Greys")
rotate_colors = rot_cmap(rotation_normalized)
pole_colors = pole_cmap(pole_normalized)
final_colors = blend_factor * rotate_colors + (1 - blend_factor) * pole_colors

# Plotting
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')
ax.quiver(points[:, 0], points[:, 1], points[:, 2],
          Vnorm[:, 0], Vnorm[:, 1], Vnorm[:, 2],
          length=0.4, normalize=True, color=final_colors, alpha=0.5)

ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
        color='red', linewidth=2, label='Trefoil Vortex Filament')

ax.set_title(f'3D Trefoil Vortex & Induced Velocity Field\nKinetic Energy: {kinetic_energy:.3e} J')
ax.set_xlim(-plotGridsize, plotGridsize)
ax.set_ylim(-plotGridsize, plotGridsize)
ax.set_zlim(-plotGridsize, plotGridsize)
ax.set_box_aspect([1, 1, 1])
ax.set_xlabel('x (m)')
ax.set_ylabel('y (m)')
ax.set_zlabel('z (m)')
ax.legend()
plt.tight_layout()
plt.show()