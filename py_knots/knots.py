import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Needed for 3D plotting
import spherogram
import matplotlib
matplotlib.use('TkAgg')  # Ensure it uses Tkinter backend
import glob, os
import os
script_name = os.path.splitext(os.path.basename(__file__))[0]



def parse_fseries_multi(filename):
    """Parse a .fseries file, yielding (header, coeffs) for each block."""
    knots = []
    current_header = None
    a_x, b_x, a_y, b_y, a_z, b_z = [], [], [], [], [], []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('%'):
                if a_x:  # save previous block
                    knots.append((current_header, (
                        np.array(a_x), np.array(b_x),
                        np.array(a_y), np.array(b_y),
                        np.array(a_z), np.array(b_z)
                    )))
                    a_x, b_x, a_y, b_y, a_z, b_z = [], [], [], [], [], []
                current_header = line[1:].strip() or None  # drop leading '%'
                continue
            if not line:
                if a_x:  # end of block, save
                    knots.append((current_header, (
                        np.array(a_x), np.array(b_x),
                        np.array(a_y), np.array(b_y),
                        np.array(a_z), np.array(b_z)
                    )))
                    a_x, b_x, a_y, b_y, a_z, b_z = [], [], [], [], [], []
                current_header = None
                continue
            parts = line.split()
            if len(parts) == 3:  # skip xyz lines
                continue
            if len(parts) == 6:
                ax, bx, ay, by, az, bz = map(float, parts)
                a_x.append(ax)
                b_x.append(bx)
                a_y.append(ay)
                b_y.append(by)
                a_z.append(az)
                b_z.append(bz)
    if a_x:  # last block
        knots.append((current_header, (
            np.array(a_x), np.array(b_x),
            np.array(a_y), np.array(b_y),
            np.array(a_z), np.array(b_z)
        )))
    return knots

def eval_fourier(a_x, b_x, a_y, b_y, a_z, b_z, s):
    x = np.zeros_like(s)
    y = np.zeros_like(s)
    z = np.zeros_like(s)
    N = len(a_x)
    for j in range(N):
        n = j + 1
        x += a_x[j]*np.cos(n*s) + b_x[j]*np.sin(n*s)
        y += a_y[j]*np.cos(n*s) + b_y[j]*np.sin(n*s)
        z += a_z[j]*np.cos(n*s) + b_z[j]*np.sin(n*s)
    return x, y, z

def plot_knots_grid_auto(paths):
    # 1) find all files
    n = len(paths)
    if n==0:
        print(f"No .fseries in {folder}/"); return

    # 2) grid size
    cols = int(np.ceil(np.sqrt(n)))
    rows = int(np.ceil(n/cols))

    # 3) sample parameter
    s = np.linspace(0,2*np.pi,1000)

    # 4) collect all points to compute global limits
    all_pts = []
    knots_pts = []
    labels = []
    for p in paths:
        blocks = parse_fseries_multi(p)
        if not blocks:
            continue
        # pick block with most harmonics (size of a_x)
        _, coeffs = max(blocks, key=lambda b: b[1][0].size)

        x, y, z = eval_fourier(coeffs[0], coeffs[1], coeffs[2],
                               coeffs[3], coeffs[4], coeffs[5], s)
        knots_pts.append((x, y, z))
        labels.append(os.path.basename(p))
        all_pts.append(np.vstack((x, y, z)).T)  # ← you also forgot this!

    all_pts = np.vstack(all_pts)
    L = np.max(np.abs(all_pts))*1.1

    # 5) plot
    fig = plt.figure(figsize=(4*cols,4*rows))
    for i, ((x, y, z), lbl) in enumerate(zip(knots_pts, labels)):
            ax = fig.add_subplot(rows, cols, i+1, projection='3d')
            ax.plot(x, y, z, color='slateblue', lw=1.5)
            ax.set_title(lbl, fontsize=10)
            ax.set_xlim(-L,L); ax.set_ylim(-L,L); ax.set_zlim(-L,L)
            ax.axis('off')
    plt.tight_layout()
    plt.show()




if __name__ == "__main__":
    # automatically grab all .fseries in the fseries/ folder
    folder = "fseries"
    filenames = sorted(glob.glob(os.path.join(folder, "*.fseries")))
    if not filenames:
            print(f"No .fseries files found in '{folder}/'")
    else:
        plot_knots_grid_auto(filenames)
