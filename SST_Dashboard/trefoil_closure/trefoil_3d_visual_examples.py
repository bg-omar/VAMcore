
#!/usr/bin/env python3
"""
Trefoil 3D visual examples for SST / ideal trefoil inspection.

Generates multiple 3D visualizations of the ideal trefoil:
1. centerline
2. tangent quivers
3. Frenet-like frame quivers (T, N, B)
4. curvature-colored centerline
5. ribbon / tube-like surface around the curve

Usage:
    python trefoil_3d_visual_examples.py

Outputs are written to:
    ./trefoil_3d_examples
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib import cm
from matplotlib.colors import Normalize


OUTPUT_DIR = Path("./trefoil_3d_examples")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IDEAL_TREFOIL_COEFFS = [
    (1, 0.374139, 0.000000, 0.000000, 0.000000, 0.373928, 0.000000),
    (2, 0.824246, 0.750260, 0.000352, 0.750450, -0.823952, -0.001991),
    (3, 0.000257, -0.000932, 0.352397, -0.000770, 0.000726, -0.386764),
    (4, 0.011652, -0.010656, 0.000743, 0.010739, 0.011613, -0.000230),
    (5, 0.010504, 0.110306, 0.000199, 0.110745, -0.010366, -0.000235),
    (6, 0.000015, -0.000006, -0.047465, -0.000050, -0.000001, 0.004595),
    (7, -0.000292, 0.002417, -0.000008, -0.002529, -0.000255, -0.000009),
    (8, 0.016487, -0.021784, 0.000041, -0.021922, -0.016421, -0.000044),
    (9, -0.000029, -0.000018, 0.011178, 0.000049, 0.000041, 0.008414),
    (10, -0.000216, -0.000290, -0.000018, 0.000311, -0.000197, -0.000044),
    (11, -0.011727, 0.002184, 0.000007, 0.002202, 0.011682, 0.000020),
    (12, 0.000026, 0.000019, -0.001308, -0.000004, -0.000019, -0.007039),
    (13, 0.000325, 0.000055, -0.000009, -0.000059, 0.000289, 0.000024),
    (14, 0.005213, 0.003201, 0.000001, 0.003210, -0.005188, 0.000010),
    (15, -0.000015, -0.000016, -0.001917, -0.000017, 0.000001, 0.003121),
    (16, -0.000136, 0.000062, 0.000019, -0.000075, -0.000112, -0.000007),
    (17, -0.000995, -0.003463, -0.000001, -0.003474, 0.000988, -0.000015),
    (18, 0.000003, 0.000008, 0.002178, 0.000019, 0.000008, -0.000615),
    (19, 0.000033, -0.000094, -0.000016, 0.000113, 0.000028, -0.000004),
    (20, -0.000999, 0.002013, -0.000000, 0.002019, 0.000998, 0.000000),
    (21, 0.000004, 0.000001, -0.001270, -0.000013, -0.000012, -0.000626),
    (22, 0.000034, 0.000060, 0.000009, -0.000072, 0.000026, 0.000010),
    (23, 0.001383, -0.000539, 0.000002, -0.000540, -0.001382, 0.000004),
    (24, -0.000005, -0.000011, 0.000344, 0.000009, 0.000007, 0.000890),
    (25, -0.000057, -0.000025, 0.000001, 0.000019, -0.000048, -0.000008),
    (26, -0.000931, -0.000356, -0.000000, -0.000357, 0.000931, -0.000005),
    (27, 0.000006, 0.000009, 0.000228, -0.000002, -0.000000, -0.000597),
    (28, 0.000040, -0.000007, -0.000004, 0.000019, 0.000036, 0.000004),
    (29, 0.000308, 0.000611, 0.000001, 0.000611, -0.000307, 0.000007),
    (30, 0.000002, 0.000001, -0.000391, -0.000006, 0.000001, 0.000195),
]

def eval_curve(t_arr: np.ndarray) -> np.ndarray:
    X = np.zeros((len(t_arr), 3), dtype=float)
    for (k, Ax, Ay, Az, Bx, By, Bz) in IDEAL_TREFOIL_COEFFS:
        phase = 2.0 * np.pi * k * t_arr
        X[:, 0] += Ax * np.cos(phase) + Bx * np.sin(phase)
        X[:, 1] += Ay * np.cos(phase) + By * np.sin(phase)
        X[:, 2] += Az * np.cos(phase) + Bz * np.sin(phase)
    return X

def eval_curve_d1(t_arr: np.ndarray) -> np.ndarray:
    dX = np.zeros((len(t_arr), 3), dtype=float)
    for (k, Ax, Ay, Az, Bx, By, Bz) in IDEAL_TREFOIL_COEFFS:
        phase = 2.0 * np.pi * k * t_arr
        w = 2.0 * np.pi * k
        dX[:, 0] += w * (-Ax * np.sin(phase) + Bx * np.cos(phase))
        dX[:, 1] += w * (-Ay * np.sin(phase) + By * np.cos(phase))
        dX[:, 2] += w * (-Az * np.sin(phase) + Bz * np.cos(phase))
    return dX

def eval_curve_d2(t_arr: np.ndarray) -> np.ndarray:
    ddX = np.zeros((len(t_arr), 3), dtype=float)
    for (k, Ax, Ay, Az, Bx, By, Bz) in IDEAL_TREFOIL_COEFFS:
        phase = 2.0 * np.pi * k * t_arr
        w2 = (2.0 * np.pi * k) ** 2
        ddX[:, 0] += -w2 * (Ax * np.cos(phase) + Bx * np.sin(phase))
        ddX[:, 1] += -w2 * (Ay * np.cos(phase) + By * np.sin(phase))
        ddX[:, 2] += -w2 * (Az * np.cos(phase) + Bz * np.sin(phase))
    return ddX

def unit(v: np.ndarray, eps: float = 1e-15) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.clip(n, eps, None)

def compute_geometry(n_pts: int = 2400):
    t = np.linspace(0.0, 1.0, n_pts, endpoint=False)
    x = eval_curve(t)
    d1 = eval_curve_d1(t)
    d2 = eval_curve_d2(t)
    T = unit(d1)
    cross = np.cross(d1, d2)
    kappa = np.linalg.norm(cross, axis=1) / np.clip(np.linalg.norm(d1, axis=1) ** 3, 1e-15, None)
    dt = 1.0 / n_pts
    dT_dt = (np.roll(T, -1, axis=0) - np.roll(T, 1, axis=0)) / (2 * dt)
    speed = np.linalg.norm(d1, axis=1)
    dT_ds = dT_dt / np.clip(speed[:, None], 1e-15, None)
    N = unit(dT_ds)
    B = unit(np.cross(T, N))
    N = unit(np.cross(B, T))
    return x, T, N, B, kappa

def set_equal_axes(ax, pts: np.ndarray):
    mins = pts.min(axis=0)
    maxs = pts.max(axis=0)
    center = 0.5 * (mins + maxs)
    radius = 0.55 * np.max(maxs - mins)
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)

def save_centerline(pts: np.ndarray):
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], lw=1.7)
    ax.set_title("Ideal trefoil - 3D centerline")
    set_equal_axes(ax, pts)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "01_centerline.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

def save_tangent_quivers(pts: np.ndarray, T: np.ndarray, step: int = 80, scale: float = 0.18):
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], lw=1.1, alpha=0.75)
    P = pts[::step]
    Q = T[::step] * scale
    ax.quiver(P[:, 0], P[:, 1], P[:, 2], Q[:, 0], Q[:, 1], Q[:, 2], length=1.0, normalize=False)
    ax.set_title("Ideal trefoil - tangent quivers")
    set_equal_axes(ax, pts)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "02_tangent_quivers.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

def save_frenet_quivers(pts: np.ndarray, T: np.ndarray, N: np.ndarray, B: np.ndarray, step: int = 120, scale: float = 0.16):
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], lw=1.0, alpha=0.65)
    P = pts[::step]
    Tq = T[::step] * scale
    Nq = N[::step] * scale
    Bq = B[::step] * scale
    ax.quiver(P[:, 0], P[:, 1], P[:, 2], Tq[:, 0], Tq[:, 1], Tq[:, 2], length=1.0, normalize=False)
    ax.quiver(P[:, 0], P[:, 1], P[:, 2], Nq[:, 0], Nq[:, 1], Nq[:, 2], length=1.0, normalize=False)
    ax.quiver(P[:, 0], P[:, 1], P[:, 2], Bq[:, 0], Bq[:, 1], Bq[:, 2], length=1.0, normalize=False)
    ax.set_title("Ideal trefoil - Frenet-like frame quivers (T, N, B)")
    set_equal_axes(ax, pts)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "03_frenet_quivers.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

def save_curvature_colormap(pts: np.ndarray, kappa: np.ndarray):
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")
    segments = np.stack([pts, np.roll(pts, -1, axis=0)], axis=1)
    lc = Line3DCollection(segments, cmap="viridis", linewidth=2.5)
    lc.set_array(kappa)
    ax.add_collection3d(lc)
    ax.scatter(pts[::50, 0], pts[::50, 1], pts[::50, 2], c=kappa[::50], cmap="viridis", s=10)
    cbar = fig.colorbar(cm.ScalarMappable(norm=Normalize(vmin=kappa.min(), vmax=kappa.max()), cmap="viridis"),
                        ax=ax, shrink=0.7, pad=0.08)
    cbar.set_label("curvature")
    ax.set_title("Ideal trefoil - curvature-colored centerline")
    set_equal_axes(ax, pts)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "04_curvature_colormap.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

def save_ribbon(pts: np.ndarray, N: np.ndarray, half_width: float = 0.05):
    left = pts + half_width * N
    right = pts - half_width * N
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], lw=0.8, alpha=0.45)
    ax.plot(left[:, 0], left[:, 1], left[:, 2], lw=0.6, alpha=0.7)
    ax.plot(right[:, 0], right[:, 1], right[:, 2], lw=0.6, alpha=0.7)
    for i in range(0, len(pts), 12):
        quad_x = [left[i, 0], right[i, 0], right[(i+1) % len(pts), 0], left[(i+1) % len(pts), 0]]
        quad_y = [left[i, 1], right[i, 1], right[(i+1) % len(pts), 1], left[(i+1) % len(pts), 1]]
        quad_z = [left[i, 2], right[i, 2], right[(i+1) % len(pts), 2], left[(i+1) % len(pts), 2]]
        ax.plot_trisurf(quad_x, quad_y, quad_z, linewidth=0.15, alpha=0.18, shade=True)
    ax.set_title("Ideal trefoil - ribbon approximation")
    set_equal_axes(ax, pts)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "05_ribbon.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

def save_tube_surface(pts: np.ndarray, N: np.ndarray, B: np.ndarray, tube_radius: float = 0.04, n_theta: int = 18):
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta, endpoint=False)
    cos_t = np.cos(theta)[None, :, None]
    sin_t = np.sin(theta)[None, :, None]
    circle_offsets = tube_radius * (cos_t * N[:, None, :] + sin_t * B[:, None, :])
    tube = pts[:, None, :] + circle_offsets
    X = tube[:, :, 0]
    Y = tube[:, :, 1]
    Z = tube[:, :, 2]
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, Z, rstride=12, cstride=1, linewidth=0.12, antialiased=True, alpha=0.35)
    ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], lw=0.7, alpha=0.7)
    ax.set_title("Ideal trefoil - tube surface")
    set_equal_axes(ax, pts)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "06_tube_surface.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

def main():
    pts, T, N, B, kappa = compute_geometry(2400)
    save_centerline(pts)
    save_tangent_quivers(pts, T)
    save_frenet_quivers(pts, T, N, B)
    save_curvature_colormap(pts, kappa)
    save_ribbon(pts, N)
    save_tube_surface(pts, N, B)
    print(f"Saved examples to: {OUTPUT_DIR.resolve()}")
    for p in sorted(OUTPUT_DIR.glob("*.png")):
        print(f"  - {p.name}")

if __name__ == "__main__":
    main()
