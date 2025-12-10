import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Fourier coefficients from the prompt
coeffs = np.array([
    [0.000000, 0.000000, 0.000000],
    [0.000000, -0.008900, -0.106450],
    [0.000000, 0.000000, 0.000000],
    [0.000000, -0.153498, -0.061067],
    [0.000000, 0.000000, 0.000000],
    [0.000000, -0.154080, -0.098726],
    [0.000000, 0.000000, 0.000000],
    [0.000000, 0.032799, 0.036572],
    [0.000000, 0.000000, 0.000000],
    [0.000000, -0.015252, 0.000187],
    [0.000000, 0.000000, 0.000000]
])

# Extract coefficients
N = len(coeffs)
a_x = coeffs[:, 0]
b_x = coeffs[:, 1]
a_y = coeffs[:, 2]
b_y = np.zeros(N)
a_z = np.zeros(N)
b_z = np.zeros(N)

# Manually input z coefficients from original data
b_z[2] = 0.144705
b_z[4] = 0.069024
b_z[6] = -0.073844
b_z[8] = 0.002462
b_z[10] = -0.007937

# Parametric variable
s = np.linspace(0, 2 * np.pi, 2000)
x = np.zeros_like(s)
y = np.zeros_like(s)
z = np.zeros_like(s)

# Compute the series
for j in range(1, N + 1):
    x += a_x[j - 1] * np.cos(j * s) + b_x[j - 1] * np.sin(j * s)
    y += a_y[j - 1] * np.cos(j * s) + b_y[j - 1] * np.sin(j * s)
    z += a_z[j - 1] * np.cos(j * s) + b_z[j - 1] * np.sin(j * s)

# Plot
fig = plt.figure(figsize=(12, 10), facecolor='black')
ax = fig.add_subplot(111, projection='3d', facecolor='black')
ax.plot(x, y, z, color='#00ffff', linewidth=2.5, alpha=0.9)

# Styling
ax.set_axis_off()
ax.grid(False)
plt.tight_layout()
plt.show()
