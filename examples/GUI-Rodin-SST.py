import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, TextBox
from mpl_toolkits.mplot3d import Axes3D
import os
import matplotlib
matplotlib.use('TkAgg') # Use TkAgg for interactive GUI

# --- Import Compiled SST Library ---
try:
    import sstbindings
    from sstbindings import SSTGravity, biot_savart_velocity
    HAS_SST = True
    print("SUCCESS: SST C++ Bindings loaded. Gravity Modification Kernels active.")
except ImportError:
    HAS_SST = False
    print("WARNING: 'sstbindings' not found. Falling back to slow Python math (Visualization only).")

# --- SST Canon Constants ---
V_SWIRL = 1.09384563e6  # m/s (Vacuum stiffness)
OMEGA_DEFAULT = 10.9e6  # Hz (Resonance)
B_SAT_DEFAULT = 5.0     # Tesla (Visual contrast scaling)

# --- Geometry Generator: Rodin "Starship" Coil ---
def generate_rodin_starship(R=1.0, r=1.0, num_turns=10, num_points=2000):
    """
    Generates the toroidal 'Starship' winding geometry.
    This topology creates maximum shear at the crossover nodes.
    """
    theta = np.linspace(0, num_turns * 2 * np.pi, num_points)
    # Rodin/Vortex Math winding ratio often approximates Golden Ratio or specific integers
    phi = (2 + 2/5) * theta

    x = (R + r * np.cos(phi)) * np.cos(theta)
    y = (R + r * np.cos(phi)) * np.sin(theta)
    z = r * np.sin(phi)

    # Calculate Tangents for Biot-Savart
    points = np.stack([x, y, z], axis=-1)
    tangents = np.diff(points, axis=0)
    # Pad last tangent to match shape
    tangents = np.vstack([tangents, tangents[-1]])

    return points, tangents

# --- Physics Kernel: Compute Fields ---
def compute_sst_fields(points, tangents, grid_N=15, bounds=2.0, omega=OMEGA_DEFAULT):
    """
    Computes B-Field, Vorticity (Curl), Beltrami Shear, and Gravity Map.
    """
    # 1. Setup Grid
    xs = np.linspace(-bounds, bounds, grid_N)
    ys = np.linspace(-bounds, bounds, grid_N)
    zs = np.linspace(-bounds, bounds, grid_N)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
    grid_points = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)

    print(f"Computing B-Field on {grid_N}x{grid_N}x{grid_N} grid...")

    # 2. Compute B-Field (Velocity)
    # Using C++ kernel if available, else loop
    if HAS_SST:
        # Assuming you exposed a grid-based biot_savart in bindings (optional)
        # If not, we map the single point function (still faster than pure python math)
        V_flat = np.array([biot_savart_velocity(p.tolist(), points.tolist(), tangents.tolist()) for p in grid_points])
    else:
        # Fallback placeholder (random noise to prevent crash if library missing)
        V_flat = np.random.rand(len(grid_points), 3) * 0.1

    V_grid = V_flat.reshape(grid_N, grid_N, grid_N, 3)

    # 3. Compute Curl (Vorticity)
    print("Computing Vorticity & Beltrami Shear...")
    vx, vy, vz = V_grid[..., 0], V_grid[..., 1], V_grid[..., 2]

    # Numerical Gradients
    dVz_dy = np.gradient(vz, ys, axis=1)
    dVy_dz = np.gradient(vy, zs, axis=2)
    dVx_dz = np.gradient(vx, zs, axis=2)
    dVz_dx = np.gradient(vz, xs, axis=0)
    dVy_dx = np.gradient(vy, xs, axis=0)
    dVx_dy = np.gradient(vx, ys, axis=1)

    Wx = dVz_dy - dVy_dz
    Wy = dVx_dz - dVz_dx
    Wz = dVy_dx - dVx_dy
    Curl_flat = np.stack((Wx, Wy, Wz), axis=-1).reshape(-1, 3)

    # 4. Compute SST Scalar Maps
    if HAS_SST:
        # FIX: Wrap the C++ output in np.array()
        shear_map = np.array(SSTGravity.compute_beltrami_shear(V_flat, Curl_flat))
        g_map = np.array(SSTGravity.compute_gravity_dilation(V_flat, omega, V_SWIRL, B_SAT_DEFAULT))
    else:
        shear_map = np.zeros(len(V_flat))
        g_map = np.ones(len(V_flat))

    return X, Y, Z, V_flat, shear_map, g_map
# --- GUI Application Class ---
class SSTGui:
    def __init__(self):
        self.params = {
            "R": 1.0, "r": 0.4, "turns": 12,
            "grid_N": 13, "omega": 10.9e6
        }

        self.fig = plt.figure(figsize=(14, 9))
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.subplots_adjust(left=0.25, right=0.95, bottom=0.1)

        # Initial Computation
        self.recompute()
        self.init_widgets()
        self.update_plot()

    def recompute(self):
        self.coil_pts, self.coil_tan = generate_rodin_starship(
            self.params["R"], self.params["r"], self.params["turns"]
        )
        (self.X, self.Y, self.Z, self.V,
         self.shear, self.g_map) = compute_sst_fields(
            self.coil_pts, self.coil_tan,
            self.params["grid_N"], omega=self.params["omega"]
        )

    def init_widgets(self):
        # View Toggles
        rax = plt.axes([0.02, 0.7, 0.15, 0.15])
        self.check = CheckButtons(rax,
                                  ('Show Gravity Map', 'Show Shear Map', 'Show Coil'),
                                  (True, False, True))
        self.check.on_clicked(self.update_plot)

        # Parameters
        self.boxes = {}
        y_off = 0.6
        for key in ["R", "r", "turns", "grid_N"]:
            ax_box = plt.axes([0.06, y_off, 0.05, 0.04])
            plt.text(0.01, y_off+0.01, key, transform=plt.gcf().transFigure)
            tb = TextBox(ax_box, '', initial=str(self.params[key]))
            tb.on_submit(self.make_callback(key))
            self.boxes[key] = tb
            y_off -= 0.06

    def make_callback(self, key):
        def callback(text):
            try:
                val = float(text)
                if key in ["turns", "grid_N"]: val = int(val)
                self.params[key] = val
                print(f"Parameter {key} updated to {val}. Recomputing...")
                self.recompute()
                self.update_plot()
            except ValueError:
                pass
        return callback

    def update_plot(self, label=None):
        self.ax.clear()
        status = self.check.get_status() # [Gravity, Shear, Coil]

        # 1. Plot Coil
        if status[2]:
            self.ax.plot(self.coil_pts[:,0], self.coil_pts[:,1], self.coil_pts[:,2],
                         c='k', lw=2, alpha=0.6, label="Rodin Winding")

        # 2. Plot Fields
        # Normalize Vectors
        V_mag = np.linalg.norm(self.V, axis=1)
        V_norm = self.V / (V_mag[:, np.newaxis] + 1e-9)

        flat_X = self.X.flatten()
        flat_Y = self.Y.flatten()
        flat_Z = self.Z.flatten()

        # Mode Selection: Gravity or Shear?
        if status[0]: # Gravity Map (Blue->Red)
            # Invert G so Red (high value) = Low Gravity (high effect)
            color_data = 1.0 - self.g_map
            cmap = 'coolwarm'
            title = "SST Gravity Dilation ($G_{local}$)"

            # Filter low-effect arrows to clean up view
            mask = color_data > 0.05

            q = self.ax.quiver(flat_X[mask], flat_Y[mask], flat_Z[mask],
                               V_norm[mask,0], V_norm[mask,1], V_norm[mask,2],
                               length=0.25, normalize=True, cmap=cmap, array=color_data[mask])

        elif status[1]: # Shear Map (Dark->Bright)
            color_data = self.shear
            cmap = 'inferno'
            title = "Beltrami Shear Stress (Vacuum Tearing)"

            mask = color_data > np.percentile(color_data, 50) # Show top 50% shear only

            q = self.ax.quiver(flat_X[mask], flat_Y[mask], flat_Z[mask],
                               V_norm[mask,0], V_norm[mask,1], V_norm[mask,2],
                               length=0.25, normalize=True, cmap=cmap, array=color_data[mask])
        else:
            title = "Rodin Coil Geometry"

        self.ax.set_title(title)
        self.ax.set_xlabel('X'); self.ax.set_ylabel('Y'); self.ax.set_zlabel('Z')
        self.ax.set_xlim(-2, 2); self.ax.set_ylim(-2, 2); self.ax.set_zlim(-2, 2)

        self.fig.canvas.draw_idle()

if __name__ == "__main__":
    app = SSTGui()
    plt.show()