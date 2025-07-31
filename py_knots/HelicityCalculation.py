import numpy as np
import glob, os

def parse_fseries_multi(filename):
    knots = []
    header = None
    arrays = {k: [] for k in ('a_x','b_x','a_y','b_y','a_z','b_z')}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line.startswith('%'):
                if arrays['a_x']:
                    knots.append((header, {k: np.array(v) for k,v in arrays.items()}))
                    for v in arrays.values(): v.clear()
                header = line.lstrip('%').strip()
                continue
            if not line and arrays['a_x']:
                knots.append((header, {k: np.array(v) for k,v in arrays.items()}))
                for v in arrays.values(): v.clear()
                header = None
                continue
            parts = line.split()
            if len(parts)==6:
                for key,val in zip(arrays, map(float, parts)):
                    arrays[key].append(val)
    if arrays['a_x']:
        knots.append((header, {k: np.array(v) for k,v in arrays.items()}))
    return knots

def eval_fourier_block(coeffs, s):
    x = np.zeros_like(s)
    y = np.zeros_like(s)
    z = np.zeros_like(s)
    for j in range(len(coeffs['a_x'])):
        n = j + 1
        x += coeffs['a_x'][j] * np.cos(n * s) + coeffs['b_x'][j] * np.sin(n * s)
        y += coeffs['a_y'][j] * np.cos(n * s) + coeffs['b_y'][j] * np.sin(n * s)
        z += coeffs['a_z'][j] * np.cos(n * s) + coeffs['b_z'][j] * np.sin(n * s)
    return x, y, z

def compute_biot_savart_velocity(x, y, z, grid_points):
    N = len(x)
    velocity = np.zeros_like(grid_points)
    for i in range(N):
        r0 = np.array([x[i], y[i], z[i]])
        r1 = np.array([x[(i+1)%N], y[(i+1)%N], z[(i+1)%N]])
        dl = r1 - r0
        r_mid = 0.5 * (r0 + r1)
        R = grid_points - r_mid
        norm = np.linalg.norm(R, axis=1)**3 + 1e-12
        cross = np.cross(dl, R)
        velocity += cross / norm[:, np.newaxis]
    return velocity * (1 / (4 * np.pi))

def compute_vorticity_full_grid(velocity, shape, spacing):
    vx = velocity[:, 0].reshape(shape)
    vy = velocity[:, 1].reshape(shape)
    vz = velocity[:, 2].reshape(shape)
    curl_x = (np.roll(vz, -1, axis=1) - np.roll(vz, 1, axis=1))/(2*spacing) - (np.roll(vy, -1, axis=2) - np.roll(vy, 1, axis=2))/(2*spacing)
    curl_y = (np.roll(vx, -1, axis=2) - np.roll(vx, 1, axis=2))/(2*spacing) - (np.roll(vz, -1, axis=0) - np.roll(vz, 1, axis=0))/(2*spacing)
    curl_z = (np.roll(vy, -1, axis=0) - np.roll(vy, 1, axis=0))/(2*spacing) - (np.roll(vx, -1, axis=1) - np.roll(vx, 1, axis=1))/(2*spacing)
    return np.stack([curl_x, curl_y, curl_z], axis=-1).reshape(-1, 3)

def extract_interior_field(field, shape, interior):
    return field.reshape(*shape, 3)[interior, :, :][:, interior, :][:, :, interior].reshape(-1, 3)

# Setup grid
grid_size = 32
spacing = 0.1
interior = slice(8, -8)
grid_range = spacing * (np.arange(grid_size) - grid_size // 2)
interior_vals = grid_range[interior]
X, Y, Z = np.meshgrid(grid_range, grid_range, grid_range, indexing='ij')
grid_points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=-1)
Xf, Yf, Zf = np.meshgrid(interior_vals, interior_vals, interior_vals, indexing='ij')
r_sq = (Xf**2 + Yf**2 + Zf**2).ravel()
grid_shape = (grid_size, grid_size, grid_size)

# Find all .fseries files
paths = sorted(glob.glob("*.fseries"))

print("\\n=== VAM Muon Anomaly via Helicity ===")
for path in paths:
    blocks = parse_fseries_multi(path)
    if not blocks:
        print(f"{path}: [no valid blocks]")
        continue
    header, coeffs = max(blocks, key=lambda b: b[1]['a_x'].size)
    x, y, z = eval_fourier_block(coeffs, np.linspace(0, 2*np.pi, 1000))
    velocity = compute_biot_savart_velocity(x, y, z, grid_points)
    vorticity = compute_vorticity_full_grid(velocity, grid_shape, spacing)
    v_sub = extract_interior_field(velocity, grid_shape, interior)
    w_sub = extract_interior_field(vorticity, grid_shape, interior)
    H_charge = np.sum(np.einsum('ij,ij->i', v_sub, w_sub))
    H_mass = np.sum(np.linalg.norm(w_sub, axis=1)**2 * r_sq)
    a_mu = 0.5 * (H_charge / H_mass - 1)
    print(f"{os.path.basename(path)}:  a_mu^VAM = {a_mu:.8f}  [Hc={H_charge:.2f}, Hm={H_mass:.2f}]")

