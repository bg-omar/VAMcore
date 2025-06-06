import pytest
pytest.skip("example script", allow_module_level=True)
from vambindings import VortexKnotSystem
import numpy as np
import matplotlib.pyplot as plt

# Dummy positions simulating loaded evolved knot (replace with real data from Python bindings)
def generate_sample_trefoil(resolution=400):
    s = np.linspace(0, 2 * np.pi, resolution)
    x = (2 + np.cos(3 * s)) * np.cos(2 * s)
    y = (2 + np.cos(3 * s)) * np.sin(2 * s)
    z = np.sin(3 * s)
    return np.stack([x, y, z], axis=-1)

knot = VortexKnotSystem()
knot.initialize_trefoil_knot()
knot.evolve(dt=0.01, steps=10)
positions = np.array(knot.get_positions())

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], lw=2, color='mediumblue')
ax.set_title("Trefoil Vortex Knot (Sample)")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.grid(True)
plt.tight_layout()
plt.show()