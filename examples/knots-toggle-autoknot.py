import glob
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, Button
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use('TkAgg')

# --- Import C++ bindings (with fallback to Python) ---
USE_CPP = False
try:
    import swirl_string_core
    from swirl_string_core import load_all_knots
    USE_CPP = True
    print("[INFO] Using C++ bindings for calculations")
except ImportError:
    try:
        import swirl_string_core as swirl_string_core
        from swirl_string_core import load_all_knots
        USE_CPP = True
        print("[INFO] Using C++ bindings (swirl_string_core) for calculations")
    except ImportError:
        print("[INFO] C++ bindings not available, using Python fallback")
        USE_CPP = False

# --- Global states ---
effects_enabled = False
ignore_redraw = False

# --- Python fallback functions (used when C++ bindings unavailable) ---
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
    return np.stack((x, y, z), axis=1)

def compute_curvature(x, y, z):
    dx = np.gradient(x)
    dy = np.gradient(y)
    dz = np.gradient(z)
    d2x = np.gradient(dx)
    d2y = np.gradient(dy)
    d2z = np.gradient(dz)
    num = np.sqrt((dy*d2z - dz*d2y)**2 + (dz*d2x - dx*d2z)**2 + (dx*d2y - dy*d2x)**2)
    denom = (dx**2 + dy**2 + dz**2)**1.5 + 1e-8
    return num / denom

# --- Load and prepare knots ---
folder = './'
paths = sorted(glob.glob(os.path.join(folder, '*.fseries')))
labels = [os.path.splitext(os.path.basename(p))[0].replace('knot','').replace('Knot','') for p in paths]

if USE_CPP:
    # Load all knots from C++ - returns list of LoadedKnot objects
    # All calculations (parsing, evaluation, curvature) are done in C++
    loaded_knots = load_all_knots(paths, nsamples=1000)
    
    # Create mapping from cleaned filename to knot
    knot_dict = {}
    for knot in loaded_knots:
        knot_dict[knot.name] = knot
    
    # Convert to format expected by display code (maintain original order)
    knots = []
    labels = []
    for p in paths:
        base_name = os.path.splitext(os.path.basename(p))[0]
        clean_name = base_name.replace('knot', '').replace('Knot', '')
        
        if clean_name in knot_dict:
            knot = knot_dict[clean_name]
            # Get points and curvature as NumPy arrays
            pts = knot.get_points_array()
            curv = knot.get_curvature_array()
            knots.append((pts, curv))
            labels.append(knot.name)
        else:
            knots.append(None)
            labels.append(clean_name)
else:
    # Python fallback - original implementation
    s = np.linspace(0, 2*np.pi, 1000)
    knots = []
    for p in paths:
        blocks = parse_fseries_multi(p)
        if blocks:
            hdr, coeffs = max(blocks, key=lambda b: b[1]['a_x'].size)
            pts = eval_fourier_block(coeffs, s)
            curv = compute_curvature(pts[:,0], pts[:,1], pts[:,2])
            knots.append((pts, curv))
        else:
            knots.append(None)
    # Labels already set above from paths

selected = [k is not None for k in knots]

# --- UI Setup ---
fig = plt.figure(figsize=(14, 8))
rax1 = fig.add_axes([0.01, 0.05, 0.12, 0.9])
rax2 = fig.add_axes([0.14, 0.05, 0.12, 0.9])
mid = len(labels) // 2
check1 = CheckButtons(rax1, labels[:mid], selected[:mid])
check2 = CheckButtons(rax2, labels[mid:], selected[mid:])

# Buttons
select_ax = fig.add_axes([0.4, 0.02, 0.12, 0.05])
deselect_ax = fig.add_axes([0.55, 0.02, 0.12, 0.05])
effects_ax = fig.add_axes([0.7, 0.02, 0.12, 0.05])
select_btn = Button(select_ax, 'Select All')
deselect_btn = Button(deselect_ax, 'Deselect All')
effects_btn = Button(effects_ax, 'Toggle Effects')

axes = []

def redraw(_):
    global selected, axes, ignore_redraw
    if ignore_redraw:
        return

    new_status = list(check1.get_status()) + list(check2.get_status())
    if new_status.count(True) == 0:
        new_status[0] = True
        check1.set_active(0)
    selected = new_status

    for ax in axes:
        fig.delaxes(ax)
    axes.clear()

    active = [k for k, sel in zip(knots, selected) if sel]
    if not active:
        fig.canvas.draw_idle()
        return

    L = 0
    centered_active = []
    for pts, curv in active:
        centroid = pts.mean(axis=0)
        pts_centered = pts - centroid
        radius = np.max(np.linalg.norm(pts_centered, axis=1))
        L = max(L, radius)
        centered_active.append((pts_centered, curv))
    L *= 1.1

    cols = int(np.ceil(np.sqrt(len(active))))
    rows = int(np.ceil(len(active) / cols))

    from matplotlib import cm
    norm = plt.Normalize(0, 0.5)

    for idx, (pts, curv) in enumerate(active):
        ax = fig.add_subplot(rows, cols, idx+1, projection='3d')
        x, y, z = pts[:,0], pts[:,1], pts[:,2]
        if effects_enabled:
            for i in range(len(x) - 1):
                rgba = cm.plasma(norm(curv[i]))
                ax.plot(x[i:i+2], y[i:i+2], z[i:i+2], color=rgba, lw=2)
            for i in range(2, 0, -1):
                ax.plot(x, y, z, color=(1, 1, 1, 0.04*i), lw=1+i)
        else:
            ax.plot(x, y, z, color='slateblue', lw=1.5)
        ax.set_xlim(-L, L); ax.set_ylim(-L, L); ax.set_zlim(-L, L)
        ax.set_axis_off()
        axes.append(ax)

    plt.tight_layout(rect=(0.27, 0.08, 1, 1))
    fig.canvas.draw_idle()

def toggle_effects(event):
    global effects_enabled
    effects_enabled = not effects_enabled
    redraw(None)

def select_all(event):
    global ignore_redraw
    ignore_redraw = True
    for i, stat in enumerate(check1.get_status()):
        if not stat:
            check1.set_active(i)
    for i, stat in enumerate(check2.get_status()):
        if not stat:
            check2.set_active(i)
    ignore_redraw = False
    redraw(None)

def deselect_all(event):
    global ignore_redraw
    if selected.count(True) <= 1:
        print("[INFO] At least one knot must remain.")
        return
    ignore_redraw = True
    # Leave only the first selected
    toggled = 0
    for i, stat in enumerate(check1.get_status()):
        if stat and toggled > 0:
            check1.set_active(i)
        elif stat:
            toggled += 1
    for i, stat in enumerate(check2.get_status()):
        if stat:
            check2.set_active(i)
    ignore_redraw = False
    redraw(None)

check1.on_clicked(redraw)
check2.on_clicked(redraw)
select_btn.on_clicked(select_all)
deselect_btn.on_clicked(deselect_all)
effects_btn.on_clicked(toggle_effects)
redraw(None)
plt.show()