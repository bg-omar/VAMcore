import numpy as np
from swirl_string_core import (
    evaluate_fourier_series,
    writhe_gauss_curve,
    estimate_crossing_number
)

# Sample Fourier coefficients: 5 harmonics, shape (5,6)
N = 5
t_vals = np.linspace(0, 2 * np.pi, 100, endpoint=False)
coeffs = np.zeros((N, 6))
coeffs[1, 0] = 1.0  # cos(t) x
coeffs[1, 2] = 1.0  # cos(t) y
coeffs[1, 4] = 1.0  # cos(t) z (helix)

# Evaluate series
result = evaluate_fourier_series(coeffs.tolist(), t_vals.tolist())
positions = np.array(result.positions)
tangents = np.array(result.tangents)

# Compute writhe
Wr = writhe_gauss_curve(positions.tolist(), tangents.tolist())
print("Writhe:", Wr)

# Estimate crossing number
cr = estimate_crossing_number(positions.tolist(), directions=32)
print("Estimated crossing number:", cr)