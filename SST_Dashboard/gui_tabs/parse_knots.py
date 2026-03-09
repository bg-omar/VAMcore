import numpy as np
import pandas as pd
import re
from pathlib import Path
from sst_exports import get_exports_dir

def parse_coeffs(filename):
    with open(filename, 'r') as f:
        text = f.read()
    # Remove lines starting with '%'
    lines = [l for l in text.split('\n') if not l.strip().startswith('%')]
    text_clean = ' '.join(lines)
    # Extract all floating point numbers
    floats = [float(x) for x in re.findall(r'-?\d+\.\d+(?:e[+-]?\d+)?', text_clean)]

    # Reshape into (N, 6)
    num_elements = len(floats)
    remainder = num_elements % 6
    if remainder != 0:
        # Just drop the trailing incomplete row if any, or pad.
        # But standard files should be exact multiples of 6.
        floats = floats[:-remainder]

    return np.array(floats).reshape(-1, 6)

def process_fseries(filename, out_filename, num_points=300):
    coeffs = parse_coeffs(filename)

    def r(t):
        j = np.arange(len(coeffs))
        t_col = t[:, None]
        j_row = j[None, :]

        cos_jt = np.cos(j_row * t_col)
        sin_jt = np.sin(j_row * t_col)

        ax, bx = coeffs[:, 0], coeffs[:, 1]
        ay, by = coeffs[:, 2], coeffs[:, 3]
        az, bz = coeffs[:, 4], coeffs[:, 5]

        x = np.sum(cos_jt * ax + sin_jt * bx, axis=1)
        y = np.sum(cos_jt * ay + sin_jt * by, axis=1)
        z = np.sum(cos_jt * az + sin_jt * bz, axis=1)
        return np.vstack((x, y, z)).T

    # Dense parameterization
    t_dense = np.linspace(0, 2*np.pi, 100000)
    pts = r(t_dense)

    # Arc-length integration
    dp = np.diff(pts, axis=0)
    ds = np.linalg.norm(dp, axis=1)
    s = np.zeros(len(t_dense))
    s[1:] = np.cumsum(ds)

    L = s[-1]

    # Equidistant points along arc-length
    s_target = np.linspace(0, L, num_points, endpoint=False)
    t_target = np.interp(s_target, s, t_dense)

    pts_uniform = r(t_target)

    df = pd.DataFrame(pts_uniform, columns=['x', 'y', 'z'])
    df.to_csv(out_filename, index=False)
    return L, len(coeffs)

_exports = get_exports_dir()
L_9_2, N_9_2 = process_fseries('knot.9_2.fseries', str(_exports / 'knot_9_2_normalized.csv'))
L_10_1, N_10_1 = process_fseries('knot.10_1.fseries', str(_exports / 'knot_10_1_normalized.csv'))
print(f"9_2: L={L_9_2:.4f}, j_max={N_9_2-1}")
print(f"10_1: L={L_10_1:.4f}, j_max={N_10_1-1}")

import numpy as np
import pandas as pd

def fourier_coeffs(coord, s, maxJ):
    a = np.zeros(maxJ)
    b = np.zeros(maxJ)
    N = len(coord)
    for j in range(1, maxJ + 1):
        a[j-1] = (2 / N) * np.sum(coord * np.cos(j * s))
        b[j-1] = (2 / N) * np.sum(coord * np.sin(j * s))
    return a, b

def process_to_fseries(input_csv, output_fseries, maxJ=50):
    df = pd.read_csv(input_csv)
    X, Y, Z = df['x'].values, df['y'].values, df['z'].values
    N = len(df)
    s = np.linspace(0, 2*np.pi, N, endpoint=False)

    ax, bx = fourier_coeffs(X, s, maxJ)
    ay, by = fourier_coeffs(Y, s, maxJ)
    az, bz = fourier_coeffs(Z, s, maxJ)

    with open(output_fseries, 'w') as f:
        f.write(f"% (Fourier projection from normalized {input_csv})\n")
        f.write("% lines  a_x(j) b_x(j)  a_y(j) b_y(j)  a_z(j) b_z(j)\n")
        # In original .fseries, j=0 is often 0 (constant offset).
        # Since the mean of the coordinates should be roughly 0, we start at j=1 mapped to index 0 of the arrays.
        for j in range(maxJ):
            f.write(f"{ax[j]: 9.6f} {bx[j]: 9.6f} {ay[j]: 9.6f} {by[j]: 9.6f} {az[j]: 9.6f} {bz[j]: 9.6f}\n")

process_to_fseries('knot_9_2_normalized.csv', 'knot_9_2_normalized.fseries', maxJ=50)
process_to_fseries('knot_10_1_normalized.csv', 'knot_10_1_normalized.fseries', maxJ=50)

print("Files generated: knot_9_2_normalized.fseries, knot_10_1_normalized.fseries")

import numpy as np

def extract_dhf_coefficients(input_file, output_file, harmonics=10, scale_factor=1.0):
    """
    Ingests N x 3 Cartesian coordinates and exports formatted DHF coefficients.
    scale_factor allows mapping to canonical physical dimensions (e.g., r_c) if required by downstream logic.
    """
    # Load discrete topological vertices
    coords = np.loadtxt(input_file)
    N = len(coords)

    # Enforce origin centralization (remove j=0 translation bias)
    coords -= np.mean(coords, axis=0)
    coords *= scale_factor

    x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]
    k_array = np.arange(N)

    with open(output_file, 'w') as f:
        f.write(f"% Computed DHF Coefficients for {input_file}\n")
        f.write("% lines: a_x(j)  b_x(j)  a_y(j)  b_y(j)  a_z(j)  b_z(j)\n")

        for j in range(1, harmonics + 1):
            # Phase angle calculation for harmonic j
            theta_jk = (2 * np.pi * j * k_array) / N
            cos_theta = np.cos(theta_jk)
            sin_theta = np.sin(theta_jk)

            # Discrete sums for orthogonal components
            a_x = (2.0 / N) * np.sum(x * cos_theta)
            b_x = (2.0 / N) * np.sum(x * sin_theta)

            a_y = (2.0 / N) * np.sum(y * cos_theta)
            b_y = (2.0 / N) * np.sum(y * sin_theta)

            a_z = (2.0 / N) * np.sum(z * cos_theta)
            b_z = (2.0 / N) * np.sum(z * sin_theta)

            # Formatted exactly to Fortran/C expectations (12.3f standard spacing)
            line = f"{a_x:12.3f}{b_x:12.3f}{a_y:12.3f}{b_y:12.3f}{a_z:12.3f}{b_z:12.3f}\n"
            f.write(line)

# Execution example:
# extract_dhf_coefficients('knot92_raw.txt', 'knot92_dhf.d4.1', harmonics=10)
import numpy as np
import pandas as pd
import os

def relax_knot_vectorized(filename, iterations=1000, alpha=0.005):
    # If file doesn't exist (kernel reset), we abort safely
    if not os.path.exists(filename):
        return None

    df = pd.read_csv(filename)
    pts = df[['x', 'y', 'z']].values
    N = len(pts)

    k_spring = 5.0
    q_repulse = 0.05

    for step in range(iterations):
        # Calculate current mean segment length
        lengths = np.linalg.norm(np.diff(np.vstack((pts, [pts[0]])), axis=0), axis=1)
        l0 = np.mean(lengths)

        pts_next = np.roll(pts, -1, axis=0)
        pts_prev = np.roll(pts, 1, axis=0)

        v_next = pts_next - pts
        d_next = np.linalg.norm(v_next, axis=1, keepdims=True)
        f_next = k_spring * (d_next - l0) * (v_next / (d_next + 1e-9))

        v_prev = pts_prev - pts
        d_prev = np.linalg.norm(v_prev, axis=1, keepdims=True)
        f_prev = k_spring * (d_prev - l0) * (v_prev / (d_prev + 1e-9))

        f_spring = f_next + f_prev

        diff = pts[:, np.newaxis, :] - pts[np.newaxis, :, :] # NxNx3
        dist = np.linalg.norm(diff, axis=2) # NxN

        mask = np.ones((N, N), dtype=bool)
        np.fill_diagonal(mask, False)
        for i in range(N):
            mask[i, (i+1)%N] = False
            mask[i, (i-1)%N] = False

        dist[~mask] = 1e9

        f_rep_mag = q_repulse / (dist**3 + 1e-9)
        f_rep_mag[~mask] = 0.0

        f_repulse = np.sum(diff * f_rep_mag[:, :, np.newaxis], axis=1)

        grad = -f_spring - f_repulse

        # Limit max gradient step to prevent explosions
        grad_norm = np.linalg.norm(grad, axis=1, keepdims=True)
        grad = np.where(grad_norm > 5.0, grad * (5.0 / grad_norm), grad)

        pts -= alpha * grad
        pts -= np.mean(pts, axis=0)

    # Final re-parameterization to equal arc length
    dp = np.diff(np.vstack((pts, [pts[0]])), axis=0)
    ds = np.linalg.norm(dp, axis=1)
    s = np.zeros(N+1)
    s[1:] = np.cumsum(ds)
    L = s[-1]

    s_target = np.linspace(0, L, N, endpoint=False)
    pts_uniform = np.zeros_like(pts)
    for dim in range(3):
        pts_uniform[:, dim] = np.interp(s_target, s, np.append(pts[:, dim], pts[0, dim]))

    return pts_uniform

# Execute
res_9_2 = relax_knot_vectorized('knot_9_2_normalized.csv', iterations=1000)
res_10_1 = relax_knot_vectorized('knot_10_1_normalized.csv', iterations=1000)

success = res_9_2 is not None and res_10_1 is not None
if success:
    pd.DataFrame(res_9_2, columns=['x','y','z']).to_csv('knot_9_2_relaxed.csv', index=False)
    pd.DataFrame(res_10_1, columns=['x','y','z']).to_csv('knot_10_1_relaxed.csv', index=False)
print(f"Relaxation success: {success}")


import numpy as np
from pyknotid.make import Knot

def generate_knot_dhf(alexander_notation, output_filename, harmonics=10):
    """
    Retrieves relaxed dimensionless coordinates for a given prime knot,
    computes the DHF coefficients, and formats them for Fortran ingestion.
    """
    # 1. Retrieve topological manifold (N x 3 array)
    try:
        k = Knot(alexander_notation)
        coords = k.points
    except Exception as e:
        print(f"Topology retrieval failed: {e}")
        return

    N = len(coords)

    # 2. Centralize topological center of mass to origin
    coords -= np.mean(coords, axis=0)

    x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]
    k_array = np.arange(N)

    # 3. Spectral extraction and formatted output
    with open(output_filename, 'w') as f:
        f.write(f"% Knot {alexander_notation} DHF \n")
        f.write("% lines: a_x(j)  b_x(j)  a_y(j)  b_y(j)  a_z(j)  b_z(j)\n")

        for j in range(1, harmonics + 1):
            theta_jk = (2 * np.pi * j * k_array) / N
            cos_theta = np.cos(theta_jk)
            sin_theta = np.sin(theta_jk)

            # Dimensionless L^2 projections
            a_x = (2.0 / N) * np.sum(x * cos_theta)
            b_x = (2.0 / N) * np.sum(x * sin_theta)

            a_y = (2.0 / N) * np.sum(y * cos_theta)
            b_y = (2.0 / N) * np.sum(y * sin_theta)

            a_z = (2.0 / N) * np.sum(z * cos_theta)
            b_z = (2.0 / N) * np.sum(z * sin_theta)

            # Formatted exactly to Fortran 12.3f standard spacing
            line = f"{a_x:12.3f}{b_x:12.3f}{a_y:12.3f}{b_y:12.3f}{a_z:12.3f}{b_z:12.3f}\n"
            f.write(line)

    print(f"Extraction complete: {output_filename}")

# Execute for required knots
generate_knot_dhf('9_2', 'knot92_dhf.d4.1', harmonics=10)
generate_knot_dhf('10_1', 'knot101_dhf.d4.1', harmonics=10)