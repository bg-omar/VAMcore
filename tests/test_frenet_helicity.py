import vambindings
import numpy as np

# Example closed curve (circle in XY-plane)
theta = np.linspace(0, 2 * np.pi, 100)
X = [(np.cos(t), np.sin(t), 0.0) for t in theta]

# Compute Frenet frames
T, N, B = vambindings.compute_frenet_frames(X)

# Compute curvature and torsion
curvature, torsion = vambindings.compute_curvature_torsion(T, N)

# Print some values
print("Curvature (first 5):", curvature[:5])
print("Torsion (first 5):", torsion[:5])

# Use T as both velocity and vorticity for test helicity
helicity = vambindings.compute_helicity(T, T)
print("Helicity (T · T):", helicity)
