import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import glob

# --- Import your compiled library ---
try:
    import swirl_string_core
    from swirl_string_core import VortexKnotSystem, load_all_knots
except ImportError:
    try:
        import swirl_string_core
        from swirl_string_core import VortexKnotSystem, load_all_knots
    except ImportError:
        print("ERROR: Could not import swirl_string_core or swirl_string_core. Build the C++ module first.")
        exit(1)

# --- 0. List Available Knots ---
print("=" * 70)
print("Available Built-in Knots in Swirl String Core:")
print("=" * 70)

# Find all .fseries files to list available knots
knot_fseries_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'knot_fseries')
if not os.path.exists(knot_fseries_dir):
    knot_fseries_dir = os.path.join('src', 'knot_fseries')
if not os.path.exists(knot_fseries_dir):
    knot_fseries_dir = 'knot_fseries'

fseries_files = sorted(glob.glob(os.path.join(knot_fseries_dir, '*.fseries')))

# Knot descriptions
knot_descriptions = {
    '3_1': 'Electron / Positron (canon)',
    '4_1': 'Dark Knot (research)',
    '5_1': 'Muon (research)',
    '5_2': 'Up Quark (canon)',
    '6_1': 'Down Quark (canon)',
    '7_1': 'Tau (research)',
}

# Group by knot type
knot_groups = {}
for fpath in fseries_files:
    basename = os.path.basename(fpath)
    if basename.startswith('knot.'):
        knot_id = basename[5:].split('.')[0]
        if knot_id not in knot_groups:
            knot_groups[knot_id] = []

print("\n📐 All Built-in Knots:")
print()

# Special parametric knots
print("  1. Trefoil Knot (3₁)")
print("     - Method: initialize_trefoil_knot(resolution=400)")
print("     - Description: The simplest non-trivial knot")
print()
print("  2. Figure-8 Knot (4₁)")
print("     - Method: initialize_figure8_knot(resolution=400)")
print("     - Description: The simplest amphichiral knot")
print()

# All other knots from .fseries files
for i, (knot_id, _) in enumerate(sorted(knot_groups.items()), start=3):
    desc = knot_descriptions.get(knot_id, '')
    if desc:
        print(f"  {i}. Knot {knot_id} - {desc}")
    else:
        print(f"  {i}. Knot {knot_id}")
    print(f"     - Method: initialize_knot_from_name('{knot_id}', resolution=1000)")

print()
print(f"   Total: {len(knot_groups) + 2} built-in knot types available")
print("=" * 70)
print()

# --- 1. Initialize Knots (No .fseries files needed) ---
print("Initializing knots...")

# Create Trefoil Knot
print("  Creating trefoil knot...")
knot1 = VortexKnotSystem()
knot1.initialize_trefoil_knot(resolution=400)
positions1 = np.array(knot1.get_positions())
tangents1 = np.array(knot1.get_tangents())

# Create Figure-8 Knot
print("  Creating figure-8 knot...")
knot2 = VortexKnotSystem()
knot2.initialize_figure8_knot(resolution=400)
positions2 = np.array(knot2.get_positions())
tangents2 = np.array(knot2.get_tangents())

# --- 2. Compute Curvature for Visualization ---
def compute_curvature(positions):
    """Compute curvature from knot positions using finite differences."""
    n = len(positions)
    curvature = np.zeros(n)
    
    for i in range(n):
        # Periodic boundary conditions
        prev = positions[(i - 1) % n]
        curr = positions[i]
        next_pos = positions[(i + 1) % n]
        
        # First derivative (tangent)
        t1 = (next_pos - prev) / 2.0
        
        # Second derivative
        t2 = next_pos - 2*curr + prev
        
        # Curvature = |t' × t''| / |t'|^3
        cross = np.cross(t1, t2)
        kappa = np.linalg.norm(cross) / (np.linalg.norm(t1)**3 + 1e-8)
        curvature[i] = kappa
    
    return curvature

print("  Computing curvature...")
curvature1 = compute_curvature(positions1)
curvature2 = compute_curvature(positions2)

# --- 3. Visualization ---
print("Rendering...")
fig = plt.figure(figsize=(14, 6))

# Normalize curvature for color mapping
from matplotlib import cm
norm1 = plt.Normalize(vmin=0, vmax=np.max(curvature1))
norm2 = plt.Normalize(vmin=0, vmax=np.max(curvature2))

# --- Plot 1: Trefoil Knot ---
ax1 = fig.add_subplot(121, projection='3d')

# Color by curvature
colors1 = cm.plasma(norm1(curvature1))
for i in range(len(positions1) - 1):
    ax1.plot([positions1[i, 0], positions1[i+1, 0]],
             [positions1[i, 1], positions1[i+1, 1]],
             [positions1[i, 2], positions1[i+1, 2]],
             color=colors1[i], linewidth=2)

# Add tangent vectors at selected points
step = len(positions1) // 20
for i in range(0, len(positions1), step):
    p = positions1[i]
    t = tangents1[i]
    t_norm = t / (np.linalg.norm(t) + 1e-8)
    ax1.quiver(p[0], p[1], p[2],
               t_norm[0], t_norm[1], t_norm[2],
               length=0.3, color='white', alpha=0.6, arrow_length_ratio=0.3)

ax1.set_title("Trefoil Knot\n(3₁)")
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')

# Set equal aspect ratio
max_range1 = np.array([positions1[:, 0].max() - positions1[:, 0].min(),
                       positions1[:, 1].max() - positions1[:, 1].min(),
                       positions1[:, 2].max() - positions1[:, 2].min()]).max() / 2.0
mid1 = np.array([positions1[:, 0].mean(), positions1[:, 1].mean(), positions1[:, 2].mean()])
ax1.set_xlim(mid1[0] - max_range1, mid1[0] + max_range1)
ax1.set_ylim(mid1[1] - max_range1, mid1[1] + max_range1)
ax1.set_zlim(mid1[2] - max_range1, mid1[2] + max_range1)

# --- Plot 2: Figure-8 Knot ---
ax2 = fig.add_subplot(122, projection='3d')

# Color by curvature
colors2 = cm.plasma(norm2(curvature2))
for i in range(len(positions2) - 1):
    ax2.plot([positions2[i, 0], positions2[i+1, 0]],
             [positions2[i, 1], positions2[i+1, 1]],
             [positions2[i, 2], positions2[i+1, 2]],
             color=colors2[i], linewidth=2)

# Add tangent vectors at selected points
step = len(positions2) // 20
for i in range(0, len(positions2), step):
    p = positions2[i]
    t = tangents2[i]
    t_norm = t / (np.linalg.norm(t) + 1e-8)
    ax2.quiver(p[0], p[1], p[2],
               t_norm[0], t_norm[1], t_norm[2],
               length=0.3, color='white', alpha=0.6, arrow_length_ratio=0.3)

ax2.set_title("Figure-8 Knot\n(4₁)")
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z')

# Set equal aspect ratio
max_range2 = np.array([positions2[:, 0].max() - positions2[:, 0].min(),
                       positions2[:, 1].max() - positions2[:, 1].min(),
                       positions2[:, 2].max() - positions2[:, 2].min()]).max() / 2.0
mid2 = np.array([positions2[:, 0].mean(), positions2[:, 1].mean(), positions2[:, 2].mean()])
ax2.set_xlim(mid2[0] - max_range2, mid2[0] + max_range2)
ax2.set_ylim(mid2[1] - max_range2, mid2[1] + max_range2)
ax2.set_zlim(mid2[2] - max_range2, mid2[2] + max_range2)

# Add colorbar
sm1 = plt.cm.ScalarMappable(cmap=cm.plasma, norm=norm1)
sm1.set_array([])
cbar1 = fig.colorbar(sm1, ax=ax1, shrink=0.6, pad=0.1)
cbar1.set_label('Curvature', rotation=270, labelpad=15)

sm2 = plt.cm.ScalarMappable(cmap=cm.plasma, norm=norm2)
sm2.set_array([])
cbar2 = fig.colorbar(sm2, ax=ax2, shrink=0.6, pad=0.1)
cbar2.set_label('Curvature', rotation=270, labelpad=15)

plt.tight_layout()
print("Displaying plot...")
plt.show()