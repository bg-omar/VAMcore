import numpy as np
import matplotlib.pyplot as plt
import os
import sys

try:
    import sstcore
except ImportError:
    try:
        import swirl_string_core as sstcore  # backward compatibility
    except ImportError:
        import sstbindings as sstcore

# Parameters
gamma = 1.0     # circulation
nu = 0.01       # viscosity
t = 1.0
R_vals = np.linspace(0.01, 3.0, 300)

# Lamb–Oseen
velocities = [sstcore.lamb_oseen_velocity(gamma, R, nu, t) for R in R_vals]
vorticities = [sstcore.lamb_oseen_vorticity(gamma, R, nu, t) for R in R_vals]

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(R_vals, velocities)
plt.title("Lamb–Oseen Velocity")
plt.xlabel("Radius R")
plt.ylabel("Vθ")

plt.subplot(1, 2, 2)
plt.plot(R_vals, vorticities)
plt.title("Lamb–Oseen Vorticity")
plt.xlabel("Radius r")
plt.ylabel("ω")

plt.tight_layout()
plt.show()

# Hill's vortex
R = 1.0
A = 0.75
stream_val = sstcore.hill_streamfunction(A, 0.5, 0.5, R)
omega_val = sstcore.hill_vorticity(A, 0.5, 0.5, R)
circ = sstcore.hill_circulation(A, R)
speed = sstcore.hill_velocity(circ, R)

print("Hill's Streamfunction:", stream_val)
print("Hill's Vorticity:", omega_val)
print("Hill's Circulation:", circ)
print("Hill's Speed:", speed)