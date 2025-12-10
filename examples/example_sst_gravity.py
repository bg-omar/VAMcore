import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

# --- Import your compiled library ---
# Ensure swirl_string_core.so (or .pyd) is in the same folder or python path
import swirl_string_core
from swirl_string_core import VortexKnotSystem, biot_savart_velocity
# If you bound the new class as 'SSTGravity' inside swirl_string_core:
from swirl_string_core import SSTGravity

# --- 1. Simulation Setup (SST Canon Constants) ---
# Canonical Swirl Velocity (c_l) ~ 10^6 m/s
v_swirl = 1.09384563e6
# Resonant Frequency for this geometry (Hypothetical 10.9 MHz)
omega_drive = 10.9e6
# Saturation Field (Tesla) - Lower this to see stronger effects in visualizer
B_saturation = 5.0

plotGridsize = 3.0
n_vectors = 5

# --- 2. Initialize Geometry (Trefoil Knot) ---
print("Initializing Vortex Geometry...")
knot = VortexKnotSystem()
knot.initialize_trefoil_knot()
positions = np.array(knot.get_positions())
tangents = np.array(knot.get_tangents())

# --- 3. Compute Vector Fields (B and Curl B) ---
print("Computing Magnetic Field (B)...")
xv = np.linspace(-plotGridsize, plotGridsize, n_vectors)
yv = np.linspace(-plotGridsize, plotGridsize, n_vectors)
zv = np.linspace(-plotGridsize, plotGridsize, n_vectors)
Xg, Yg, Zg = np.meshgrid(xv, yv, zv, indexing='ij')

# Flat list of points for C++ computation
points = np.stack((Xg, Yg, Zg), axis=-1).reshape(-1, 3)

# Calculate B (Velocity) using standard Biot-Savart
# (In a full VAM pipeline, utilize biot_savart_velocity_grid for speed)
V_flat = np.array([biot_savart_velocity(p.tolist(), positions.tolist(), tangents.tolist()) for p in points])
V_grid = V_flat.reshape(n_vectors, n_vectors, n_vectors, 3)

# Calculate Curl (Vorticity) necessary for Beltrami Shear
# We use numpy gradient here, but VAMcore likely has a kernel for this too
print("Computing Curl (Vorticity)...")
vx, vy, vz = V_grid[..., 0], V_grid[..., 1], V_grid[..., 2]

dVz_dy = np.gradient(vz, yv, axis=1)
dVy_dz = np.gradient(vy, zv, axis=2)
dVx_dz = np.gradient(vx, zv, axis=2)
dVz_dx = np.gradient(vz, xv, axis=0)
dVy_dx = np.gradient(vy, xv, axis=0)
dVx_dy = np.gradient(vx, yv, axis=1)

# Curl = (dw/dy - dv/dz, du/dz - dw/dx, dv/dx - du/dy)
Wx = dVz_dy - dVy_dz
Wy = dVx_dz - dVz_dx
Wz = dVy_dx - dVx_dy

Curl_flat = np.stack((Wx, Wy, Wz), axis=-1).reshape(-1, 3)

# --- 4. SST C++ Kernel Execution ---
print("Running SST Gravity Kernels (C++)...")

# A. Compute Beltrami Shear: S = || B x Curl(B) ||
# High shear = High Vacuum Stress (Potential for metric tearing)
shear_map = SSTGravity.compute_beltrami_shear(V_flat, Curl_flat)

# B. Compute Gravity Dilation: G_local
# 1.0 = Normal Gravity, 0.0 = Weightless
g_map = SSTGravity.compute_gravity_dilation(
    V_flat,
    omega_drive,
    v_swirl,
    B_saturation
)

# --- 5. Visualization ---
print("Rendering...")
fig = plt.figure(figsize=(14, 7))

# Normalize vectors for plotting arrows
V_mag = np.linalg.norm(V_flat, axis=1)
V_norm = V_flat / (V_mag[:, np.newaxis] + 1e-9)

# -- Plot 1: Gravity Modification Zones --
ax1 = fig.add_subplot(121, projection='3d')

# Color Strategy:
# Blue = Normal Gravity (G ~ 1.0)
# Red = Gravity Shielding (G < 1.0)
p1 = ax1.quiver(points[:, 0], points[:, 1], points[:, 2],
                V_norm[:, 0], V_norm[:, 1], V_norm[:, 2],
                length=0.4, normalize=True,
                cmap='coolwarm_r',  # Reversed so Red is Low G
                array=g_map,        # Color by G_local
                linewidth=1.5, alpha=0.8)

ax1.plot(positions[:, 0], positions[:, 1], positions[:, 2], 'k-', lw=3, label='Trefoil Coil')
ax1.set_title(f"SST Gravity Dilation ($G_{{local}}$)\nFreq: {omega_drive/1e6} MHz")
ax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('Z')
fig.colorbar(p1, ax=ax1, label="Local Gravity (1.0 = Standard)", shrink=0.6)

# -- Plot 2: Beltrami Topological Shear --
ax2 = fig.add_subplot(122, projection='3d')

# Color Strategy:
# Dark = Force-Free (Beltrami state)
# Bright/Yellow = High Shear (Vacuum Stress)
p2 = ax2.quiver(points[:, 0], points[:, 1], points[:, 2],
                V_norm[:, 0], V_norm[:, 1], V_norm[:, 2],
                length=0.4, normalize=True,
                cmap='inferno',
                array=shear_map,    # Color by Shear
                linewidth=1.5, alpha=0.8)

ax2.plot(positions[:, 0], positions[:, 1], positions[:, 2], 'g-', lw=3, label='Trefoil Coil')
ax2.set_title("Beltrami Shear Stress ($|\\vec{B} \\times \\nabla \\times \\vec{B}|$)\nVacuum Tearing Zones")
ax2.set_xlabel('X'); ax2.set_ylabel('Y'); ax2.set_zlabel('Z')
fig.colorbar(p2, ax=ax2, label="Topological Shear Intensity", shrink=0.6)

plt.tight_layout()
plt.show()