import numpy as np
import matplotlib.pyplot as plt
from swirl_string_core import VortexKnotSystem, biot_savart_velocity
# ✅ Get the script filename dynamically
import os
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Initialize knot system
knot = VortexKnotSystem()
knot.initialize_trefoil_knot()
positions = np.array(knot.get_positions())
tangents = np.array(knot.get_tangents())

# Parameters
grid_size = 50
x_vals = np.linspace(-4, 4, grid_size)
y_vals = np.linspace(-4, 4, grid_size)
z_val = 0.0
rho_ae = 7e-7
P_infinity = 0.0

velocity_magnitude = np.zeros((grid_size, grid_size))
pressure_field = np.zeros((grid_size, grid_size))

# Evaluate fields on z=0 slice
for i, x in enumerate(x_vals):
    for j, y in enumerate(y_vals):
        r = [x, y, z_val]
        v = biot_savart_velocity(r, positions.tolist(), tangents.tolist())
        v_mag = np.linalg.norm(v)
        velocity_magnitude[j, i] = v_mag
        pressure_field[j, i] = P_infinity - 0.5 * rho_ae * v_mag**2

# Plot velocity magnitude and pressure field
fig, axs = plt.subplots(1, 2, figsize=(14, 6))
c1 = axs[0].contourf(x_vals, y_vals, velocity_magnitude, levels=50, cmap='viridis')
axs[0].set_title('|v| (m/s) at z = 0')
axs[0].set_xlabel('x')
axs[0].set_ylabel('y')
fig.colorbar(c1, ax=axs[0])

c2 = axs[1].contourf(x_vals, y_vals, pressure_field, levels=50, cmap='coolwarm')
axs[1].set_title('Pressure (Pa) at z = 0')
axs[1].set_xlabel('x')
axs[1].set_ylabel('y')
fig.colorbar(c2, ax=axs[1])



filename = f"{script_name}.png"
plt.savefig(filename, dpi=150)  # Save image with high resolution
plt.tight_layout()


# Initialize knot system
knot = VortexKnotSystem()
knot.initialize_trefoil_knot()
positions = np.array(knot.get_positions())
tangents = np.array(knot.get_tangents())

rho_ae = 7e-7
P_infinity = 0.0
plotGridsize = 4

# Grid setup
grid_size_light = 25
x_vals = np.linspace(-4, 4, grid_size_light)
y_vals = np.linspace(-4, 4, grid_size_light)
z_slices_focus = [-1.0, -0.5, 0.0, 0.5, 1.0]
slice_data_focus = []

# Evaluate velocity and pressure for each slice
for z_val in z_slices_focus:
    velocity_slice = np.zeros((grid_size_light, grid_size_light))
    pressure_slice = np.zeros((grid_size_light, grid_size_light))
    for i, x in enumerate(x_vals):
        for j, y in enumerate(y_vals):
            r = [x, y, z_val]
            v = biot_savart_velocity(r, positions.tolist(), tangents.tolist())
            v_mag = np.linalg.norm(v)
            velocity_slice[j, i] = v_mag
            pressure_slice[j, i] = P_infinity - 0.5 * rho_ae * v_mag**2
    slice_data_focus.append({"z": z_val, "velocity": velocity_slice, "pressure": pressure_slice})

# Plot each z-slice
fig, axs = plt.subplots(len(z_slices_focus), 2, figsize=(8, 4 * len(z_slices_focus)))

for idx, slice_info in enumerate(slice_data_focus):
    z = slice_info["z"]
    vel = slice_info["velocity"]
    pres = slice_info["pressure"]

    ax_v = axs[idx, 0]
    c1 = ax_v.contourf(x_vals, y_vals, vel, levels=40, cmap='viridis')
    ax_v.set_xlim(-plotGridsize, plotGridsize)
    ax_v.set_ylim(-plotGridsize, plotGridsize)
    ax_v.set_title(f'|v| at z = {z:.2f}')
    ax_v.set_xlabel('x')
    ax_v.set_ylabel('y')

    ax_p = axs[idx, 1]
    c2 = ax_p.contourf(x_vals, y_vals, pres, levels=40, cmap='coolwarm')
    ax_p.set_xlim(-plotGridsize, plotGridsize)
    ax_p.set_ylim(-plotGridsize, plotGridsize)
    ax_p.set_title(f'P at z = {z:.2f}')
    ax_p.set_xlabel('x')
    ax_p.set_ylabel('y')

plotGridsize = 4
filename = f"{script_name}2.png"
plt.savefig(filename, dpi=150)  # Save image with high resolution
plt.tight_layout()

def compute_tangent(X):
    dX = np.gradient(X, axis=0)
    norms = np.linalg.norm(dX, axis=1, keepdims=True)
    return dX / norms

def evolve_vortex(X_init, T_init, dt=0.01, steps=10, Gamma=1.0):
    X_evolved = np.copy(X_init)
    for step in range(steps):
        V_induced = np.array([biot_savart_velocity(xi.tolist(), X_evolved.tolist(), T_init.tolist(), Gamma) for xi in X_evolved])
        X_evolved += dt * V_induced
    return X_evolved

# Initialize knot system
knot = VortexKnotSystem()
knot.initialize_trefoil_knot()
X = np.array(knot.get_positions())
T = np.array(knot.get_tangents())

# Evolve
X_evolved = evolve_vortex(X, T, dt=0.01, steps=10)
T_evolved = compute_tangent(X_evolved)

# Plot
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')
ax.plot(X[:, 0], X[:, 1], X[:, 2], color='gray', linewidth=1.5, label='Initial Trefoil')
ax.plot(X_evolved[:, 0], X_evolved[:, 1], X_evolved[:, 2], color='red', linewidth=2.5, label='Evolved Trefoil')
ax.set_title('Trefoil Vortex Evolution Under SST Dynamics')
ax.set_xlim(-plotGridsize, plotGridsize)
ax.set_ylim(-plotGridsize, plotGridsize)
ax.set_zlim(-plotGridsize, plotGridsize)
ax.set_box_aspect([1, 1, 1])
ax.set_xlabel('x (m)')
ax.set_ylabel('y (m)')
ax.set_zlabel('z (m)')
ax.legend()


filename = f"{script_name}3.png"
plt.savefig(filename, dpi=150)  # Save image with high resolution
plt.tight_layout()
plt.show()