# examples/showcase_ideal_txt_figure8.py
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

try:
    import sstcore as ssc
except ImportError:
    try:
        import sstbindings as ssc
    except ImportError as e:
        print("ERROR: Could not import sstcore or sstbindings.")
        print("Build the pybind module first.")
        raise e


def candidate_ideal_paths():
    """Search ideal.txt in dev/build/install locations (portable: no absolute paths)."""
    here = os.path.abspath(os.path.dirname(__file__))
    root = os.path.abspath(os.path.join(here, ".."))
    candidates = []
    # Env override (works on any machine)
    if os.environ.get("IDEAL_TXT_PATH"):
        candidates.append(os.environ.get("IDEAL_TXT_PATH"))
    r = os.environ.get("SSTCORE_RESOURCES")
    if r:
        candidates.append(os.path.join(r.rstrip(os.sep), "ideal.txt"))
    # Source tree (repo root = parent of examples/)
    candidates.extend([
        os.path.join(root, "resources", "ideal.txt"),
        os.path.join(root, "resources", "Knots_FourierSeries", "ideal.txt"),
        os.path.join(root, "src", "Knots_FourierSeries", "ideal.txt"),
        os.path.join("resources", "ideal.txt"),
        os.path.join("resources", "Knots_FourierSeries", "ideal.txt"),
        os.path.join("src", "Knots_FourierSeries", "ideal.txt"),
        os.path.join(root, "build", "share", "sstcore", "resources", "ideal.txt"),
        os.path.join(root, "build", "share", "sstcore", "resources", "Knots_FourierSeries", "ideal.txt"),
    ])
    # Pip/install
    for sub in ("share/sstcore/resources/ideal.txt", "share/sstcore/resources/Knots_FourierSeries/ideal.txt"):
        candidates.append(os.path.join(sys.prefix, sub.replace("/", os.sep)))
    return candidates


def resolve_ideal_path():
    for p in candidate_ideal_paths():
        if p and os.path.exists(p):
            return p
    raise FileNotFoundError(
        "Could not locate ideal.txt.\nTried:\n  - " + "\n  - ".join(candidate_ideal_paths())
    )


def to_numpy_points(points_like):
    """Convert pybind-returned vector<array<double,3>> OR ndarray to np.ndarray."""
    arr = np.array(points_like, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 3:
        raise ValueError(f"Expected (N,3) points, got shape {arr.shape}")
    return arr


def set_equal_3d(ax, P):
    mins = P.min(axis=0)
    maxs = P.max(axis=0)
    mid = 0.5 * (mins + maxs)
    r = 0.5 * np.max(maxs - mins)
    r = max(r, 1e-6)
    ax.set_xlim(mid[0] - r, mid[0] + r)
    ax.set_ylim(mid[1] - r, mid[1] + r)
    ax.set_zlim(mid[2] - r, mid[2] + r)


def find_ab_block(blocks, target_id="4:1:1", fallback_conway="2 2"):
    # Fast path: API helper
    if hasattr(ssc, "index_of_ideal_id"):
        idx = ssc.index_of_ideal_id(blocks, target_id)
        if isinstance(idx, (int, np.integer)) and idx >= 0:
            return blocks[idx]

    # Manual fallback
    for b in blocks:
        if getattr(b, "id", "") == target_id:
            return b
    for b in blocks:
        if getattr(b, "conway", "").strip() == fallback_conway:
            return b

    raise RuntimeError(f"Could not find AB block id={target_id} or Conway={fallback_conway}")


def main():
    ideal_path = resolve_ideal_path()
    print("=" * 72)
    print("SST / Swirl String Core - ideal.txt Figure-8 Showcase")
    print("=" * 72)
    print("ideal.txt:", ideal_path)

    # Parse ideal.txt AB blocks
    blocks = ssc.parse_ideal_txt_multi(ideal_path)
    print(f"Parsed AB blocks: {len(blocks)}")

    # Figure-eight knot in ideal.txt examples is typically AB Id = 4:1:1, Conway = "2 2"
    ab = find_ab_block(blocks, target_id="4:1:1", fallback_conway="2 2")

    print("\nSelected AB block:")
    print(f"  id      = {getattr(ab, 'id', '<missing>')}")
    print(f"  Conway  = {getattr(ab, 'conway', '<missing>')}")
    print(f"  L(list) = {getattr(ab, 'L', float('nan'))}")
    print(f"  D(list) = {getattr(ab, 'D', float('nan'))}")

    fb = ab.fourier

    # Sample parameters
    N_curve = 2400
    s = np.linspace(0.0, 2.0 * np.pi, N_curve, endpoint=False)

    # Reconstruct curve from Fourier block
    P = to_numpy_points(ssc.evaluate_fourier_block(fb, s.tolist()))

    # Exact/spectral descriptors
    kappa = np.array(ssc.curvature_exact(fb, s.tolist(), 1e-12), dtype=float)
    L_exact = float(ssc.length_exact(fb, 4096))
    E_bend = float(ssc.bending_energy_exact(fb, 4096, 1e-12))
    mode_E = np.array(ssc.mode_energies(fb), dtype=float)

    # Bundled descriptors if available
    D = None
    if hasattr(ssc, "describe_fourier_block"):
        D = ssc.describe_fourier_block(fb, 2048, 4)

    print("\nComputed descriptors:")
    print(f"  L_exact               = {L_exact:.9f}")
    print(f"  Bending energy        = {E_bend:.9f}")
    if D is not None:
        print(f"  Writhe (sampled proxy)= {float(D.writhe):.9f}")
        print(f"  Min self-distance     = {float(D.min_self_distance):.9f}")
    print(f"  Modes                 = {len(mode_E)}")
    print(f"  First 12 mode energies:")
    for i, e in enumerate(mode_E[:12], start=1):
        print(f"    j={i:2d}: {e:.9e}")

    # Compare listed length if available
    L_listed = getattr(ab, "L", None)
    if L_listed is not None:
        try:
            rel_err = abs(L_exact - float(L_listed)) / max(abs(float(L_listed)), 1e-12)
            print(f"\nLength check vs ideal.txt:")
            print(f"  L_listed = {float(L_listed):.9f}")
            print(f"  rel_err  = {rel_err:.3e}")
        except Exception:
            pass

    # ---------------- Plotting ----------------
    fig = plt.figure(figsize=(15, 6))

    # 3D knot plot, colored by curvature
    ax = fig.add_subplot(121, projection="3d")

    norm = plt.Normalize(vmin=float(np.min(kappa)), vmax=float(np.max(kappa)))
    colors = cm.plasma(norm(kappa))

    for i in range(len(P)):
        j = (i + 1) % len(P)
        ax.plot([P[i, 0], P[j, 0]],
                [P[i, 1], P[j, 1]],
                [P[i, 2], P[j, 2]],
                color=colors[i], linewidth=1.5)

    ax.set_title("ideal.txt Figure-8 (AB 4:1:1)\nCurvature-colored Fourier reconstruction")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    set_equal_3d(ax, P)

    sm = plt.cm.ScalarMappable(cmap=cm.plasma, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.75, pad=0.08)
    cbar.set_label("Curvature", rotation=270, labelpad=15)

    # Mode spectrum
    ax2 = fig.add_subplot(122)
    j = np.arange(1, len(mode_E) + 1)
    ax2.plot(j, mode_E, linewidth=1.5)
    ax2.set_yscale("log")
    ax2.set_xlabel("Harmonic index j")
    ax2.set_ylabel(r"$E_j = \|A_j\|^2 + \|B_j\|^2$")
    ax2.set_title("Fourier mode energy spectrum (ideal.txt AB 4:1:1)")
    ax2.grid(True, alpha=0.3)

    # Annotation block
    txt = [
        f"id = {getattr(ab, 'id', '?')}",
        f"Conway = {getattr(ab, 'conway', '?')}",
        f"L_exact = {L_exact:.6f}",
        f"L_listed = {float(getattr(ab, 'L', np.nan)):.6f}",
        f"E_bend = {E_bend:.6f}",
    ]
    if D is not None:
        txt.append(f"Writhe ≈ {float(D.writhe):.6f}")
        txt.append(f"min self-dist ≈ {float(D.min_self_distance):.6f}")
    ax2.text(
        0.02, 0.98, "\n".join(txt),
        transform=ax2.transAxes,
        va="top", ha="left",
        fontsize=9,
        bbox=dict(boxstyle="round", alpha=0.1)
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()