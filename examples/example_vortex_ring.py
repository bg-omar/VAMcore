import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Set path if needed
sys.path.insert(0, os.path.abspath("."))
from swirl_string_core import (
    lamb_oseen_velocity,
    lamb_oseen_vorticity,
    hill_streamfunction,
    hill_vorticity,
    hill_circulation,
    hill_velocity
)

# Parameters
gamma = 1.0     # circulation
nu = 0.01       # viscosity
t = 1.0
R_vals = np.linspace(0.01, 3.0, 300)

# Lamb–Oseen
velocities = [lamb_oseen_velocity(gamma, R, nu, t) for R in R_vals]
vorticities = [lamb_oseen_vorticity(gamma, R, nu, t) for R in R_vals]

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
stream_val = hill_streamfunction(A, 0.5, 0.5, R)
omega_val = hill_vorticity(A, 0.5, 0.5, R)
circ = hill_circulation(A, R)
speed = hill_velocity(circ, R)

print("Hill's Streamfunction:", stream_val)
print("Hill's Vorticity:", omega_val)
print("Hill's Circulation:", circ)
print("Hill's Speed:", speed)