import sys
import os

# (VAM) C:\workspace\projects\vamcore>set PYTHONPATH=build\Debug
#
# (VAM) C:\workspace\projects\vamcore>python -c "import vambindings; print(vambindings)"
# <module 'vambindings' from 'C:\\workspace\\projects\\vamcore\\build\\Debug\\vambindings.cp311-win_amd64.pyd'>
#

# Adjust path if needed
build_dir = os.path.join(os.path.dirname(__file__), "../build/Debug")
sys.path.insert(0, build_dir)

import vambindings
import numpy as np

X = [[1.0, 0.0, 0.0],
     [0.0, 1.0, 0.0],
     [-1.0, 0.0, 0.0],
     [0.0, -1.0, 0.0],
     [1.0, 0.0, 0.0]]

T, N, B = vambindings.compute_frenet_frames(X)
kappa, tau = vambindings.compute_curvature_torsion(T, N)
print("Curvature:", kappa)
print("Torsion:", tau)
print("Helicity:", vambindings.compute_helicity(T, T))  # test w = v
