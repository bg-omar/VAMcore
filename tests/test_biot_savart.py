import pytest
pytest.skip("example script", allow_module_level=True)
import sys
sys.path.append("../cmake-build-debug")
import sstbindings

# Point where we evaluate the velocity
r = [0.0, 0.0, 0.0]

# Vortex filament points (simple straight line)
X = [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]

# Tangent vectors (uniform for test)
T = [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]]

v = sstbindings.biot_savart_velocity(r, X, T)

print("Biot–Savart Velocity at r =", r, ":", v)