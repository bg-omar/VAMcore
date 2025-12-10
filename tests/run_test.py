import pytest
pytest.skip("example script", allow_module_level=True)
import sys
import os

# (VAM) C:\workspace\projects\vamcore>set PYTHONPATH=build\Debug
#
# (VAM) C:\workspace\projects\vamcore>python -c "import sstbindings; print(swirl_string_core)"
# <module 'swirl_string_core' from 'C:\\workspace\\projects\\vamcore\\build\\Debug\\sstbindings.cp311-win_amd64.pyd'>
#

# Adjust path if needed
build_dir = os.path.join(os.path.dirname(__file__), "../build/Debug")
sys.path.insert(0, build_dir)

import sstbindings
import numpy as np

X = [[1.0, 0.0, 0.0],
     [0.0, 1.0, 0.0],
     [-1.0, 0.0, 0.0],
     [0.0, -1.0, 0.0],
     [1.0, 0.0, 0.0]]

T, N, B = sstbindings.compute_frenet_frames(X)
kappa, tau = sstbindings.compute_curvature_torsion(T, N)
print("Curvature:", kappa)
print("Torsion:", tau)

print("Helicity:", sstbindings.compute_helicity(T, T))  # test w = v = T