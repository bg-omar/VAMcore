import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

try:
    import sstcore as ssc
except ImportError:
    print("ERROR: Could not import sstcore. Build/install the pybind module first.")
    raise


def find_ideal_txt():
    candidates = [
        os.environ.get("IDEAL_TXT_PATH", ""),
        "ideal.txt",
        os.path.join(os.path.dirname(__file__), "ideal.txt"),
        os.path.join(os.path.dirname(__file__), "..", "resources", "ideal.txt"),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None


def equal_axes(ax, pts):
    pts = np.asarray(pts)
    mins = pts.min(axis=0)
    maxs = pts.max(axis=0)
    center = 0.5 * (mins + maxs)
    radius = 0.5 * np.max(maxs - mins)
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)


def main():
    print("=" * 72)
    print("Swirl String Core — ideal.txt Fourier + built-in knot showcase")
    print("=" * 72)

    ideal_path = find_ideal_txt()
    ideal_ab = None
    ideal_block = None

    if ideal_path:
        print(f"Loading ideal file: {ideal_path}")
        blocks = ssc.parse_ideal_txt_multi(ideal_path)
        print(f"Parsed {len(blocks)} ideal <AB> blocks")
        idx = ssc.index_of_ideal_id(blocks, "4:1:1")
        if idx < 0:
            print("AB Id='4:1:1' not found, using first block")
            idx = 0
        ideal_ab = blocks[idx]
        ideal_block = ideal_ab.fourier
        print(f"Selected AB {ideal_ab.id}, Conway={ideal_ab.conway}, L(listed)={ideal_ab.L:.6f}, D={ideal_ab.D:.6f}")

        desc = ssc.describe_fourier_block(ideal_block, nsamples=2048, exclude_window=4)
        print("\nDescriptors:")
        print(f"  L(computed)          = {desc.L:.6f}")
        print(f"  ΔL (computed-listed) = {desc.L - ideal_ab.L:+.6e}")
        print(f"  bending energy       = {desc.bending_energy:.6f}")
        print(f"  min self-distance    = {desc.min_self_distance:.6f}")
        print(f"  writhe (sampled)     = {desc.writhe:.6f}")
        modeE = np.array(desc.mode_energy_array())
        print("  first 8 mode energies:")
        for j, e in enumerate(modeE[:8], start=1):
            print(f"    E_{j:02d} = {e:.6e}")
    else:
        print("No ideal.txt found (set IDEAL_TXT_PATH to use ideal Fourier blocks).")

    print("\nCreating built-in trefoil + figure-8...")
    trefoil = ssc.VortexKnotSystem()
    trefoil.initialize_trefoil_knot(resolution=500)
    p3 = np.array(trefoil.get_positions())

    fig8 = ssc.VortexKnotSystem()
    fig8.initialize_figure8_knot(resolution=500)
    p4 = np.array(fig8.get_positions())
    k4_discrete = np.array(ssc.compute_curvature(p4, 1e-8))

    p4_ideal = None
    k4_ideal = None
    if ideal_block is not None:
        s = np.linspace(0.0, 2*np.pi, 1200, endpoint=False)
        p4_ideal = np.array(ssc.evaluate_fourier_block(ideal_block, s.tolist()))
        k4_ideal = np.array(ssc.compute_curvature_exact_fourier(ideal_block, s, 1e-12))

    from matplotlib import cm
    fig = plt.figure(figsize=(16, 10))

    ax1 = fig.add_subplot(221, projection="3d")
    ax1.plot(p3[:,0], p3[:,1], p3[:,2], lw=2)
    ax1.set_title("Built-in Trefoil (3₁)")
    equal_axes(ax1, p3)

    ax2 = fig.add_subplot(222, projection="3d")
    n2 = plt.Normalize(vmin=float(k4_discrete.min()), vmax=float(k4_discrete.max()))
    c2 = cm.plasma(n2(k4_discrete))
    for i in range(len(p4)):
        j = (i + 1) % len(p4)
        ax2.plot([p4[i,0], p4[j,0]], [p4[i,1], p4[j,1]], [p4[i,2], p4[j,2]], color=c2[i], lw=2)
    ax2.set_title("Built-in Figure-8 (4₁) — discrete curvature")
    equal_axes(ax2, p4)

    ax3 = fig.add_subplot(223, projection="3d")
    if p4_ideal is not None:
        n3 = plt.Normalize(vmin=float(k4_ideal.min()), vmax=float(k4_ideal.max()))
        c3 = cm.viridis(n3(k4_ideal))
        for i in range(len(p4_ideal)):
            j = (i + 1) % len(p4_ideal)
            ax3.plot([p4_ideal[i,0], p4_ideal[j,0]], [p4_ideal[i,1], p4_ideal[j,1]], [p4_ideal[i,2], p4_ideal[j,2]], color=c3[i], lw=1.5)
        ax3.set_title(f"ideal.txt Figure-8 ({ideal_ab.id}) — exact Fourier curvature")
        equal_axes(ax3, p4_ideal)
    else:
        ax3.set_title("ideal.txt Figure-8 (not loaded)")
        ax3.text(0.1, 0.5, 0.5, "No ideal.txt found", fontsize=11)

    ax4 = fig.add_subplot(224)
    if ideal_block is not None:
        modeE = np.array(ssc.compute_mode_energies_fourier(ideal_block))
        j = np.arange(1, len(modeE)+1)
        ax4.semilogy(j, modeE + 1e-30, marker='.', lw=1)
        ax4.set_xlabel("Mode j")
        ax4.set_ylabel(r"$E_j = ||A_j||^2 + ||B_j||^2$")
        ax4.set_title("Ideal Figure-8 geometric mode spectrum")
        ax4.grid(True, alpha=0.3)
    else:
        ax4.axis("off")
        ax4.text(0.05, 0.5, "Mode spectrum available when ideal.txt is loaded", fontsize=11)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()