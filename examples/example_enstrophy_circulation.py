
import numpy as np
import os
import sys

try:
    import sstcore
except ImportError:
    import sstbindings as sstcore


# Example field data
omega_field = np.array([[0.0, 0.0, 1.0]] * 100)
dA_field = np.array([[0.0, 0.0, 0.01]] * 100)
omega_squared = np.array([1.0] * 100)
ds_area = np.array([0.01] * 100)

Gamma = sstcore.circulation_surface_integral(omega_field.tolist(), dA_field.tolist())
E = sstcore.enstrophy(omega_squared.tolist(), ds_area.tolist())

print(f"Circulation: {Gamma}")
print(f"Enstrophy: {E}")