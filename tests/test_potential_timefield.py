import pytest
pytest.skip("example script", allow_module_level=True)
import numpy as np
import vambindings

# Sample filament positions forming a small loop
positions = [
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [-1.0, 0.0, 0.0],
    [0.0, -1.0, 0.0],
    [1.0, 0.0, 0.0]
]

# Uniform vorticity vector field aligned with binormals
vorticity = [
    [0.0, 0.0, 1.0],
    [0.0, 0.0, 1.0],
    [0.0, 0.0, 1.0],
    [0.0, 0.0, 1.0],
    [0.0, 0.0, 1.0]
]

# Uniform tangents for time dilation (simplified)
tangents = [
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [-1.0, 0.0, 0.0],
    [0.0, -1.0, 0.0],
    [1.0, 0.0, 0.0]
]

# Core tangential velocity constant (from your constants list)
C_e = 1093845.63  # m/s

# === Run Tests ===

# Gravitational potential (relative field)
potential = vambindings.compute_gravitational_potential(positions, vorticity, epsilon=0.2)
print("Æther Gravitational Potential Field:")
for i, val in enumerate(potential):
    print(f"  Φ[{i}] = {val:.6e} (J/kg)")

# Time dilation factor map (1 - v²/Ce²)
dilation = vambindings.compute_time_dilation_map(tangents, C_e)
print("\nTime Dilation Factors (Relative to Absolute Æther Time):")
for i, factor in enumerate(dilation):
    print(f"  γ[{i}] = {factor:.12f}")
