# sst_native_filament_hopf.py
# Minimal SST-native filament demo:
# - Two linked vortex rings (Hopf link)
# - Regularized Biot–Savart induced velocity
# - Diagnostics: linking number Lk (Gauss integral), helicity proxy H_link=2*Gamma^2*Lk
#
# Dependencies: numpy, matplotlib (optional for plotting)

import numpy as np

# -----------------------------
# Geometry: two linked rings
# -----------------------------
def make_ring(center, normal, R=1.0, N=200):
    """
    Create a discretized circular filament (closed polygon) with N points.
    center: (3,)
    normal: (3,) direction normal to the ring plane
    """
    center = np.asarray(center, dtype=float)
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)

    # choose orthonormal basis (e1,e2) in ring plane
    tmp = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(tmp, n)) > 0.9:
        tmp = np.array([0.0, 1.0, 0.0])
    e1 = tmp - np.dot(tmp, n) * n
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(n, e1)

    theta = np.linspace(0, 2*np.pi, N, endpoint=False)
    pts = center[None, :] + R * (np.cos(theta)[:, None]*e1[None, :] + np.sin(theta)[:, None]*e2[None, :])
    return pts

# -----------------------------
# Regularized Biot–Savart
# -----------------------------
def biot_savart_velocity(x, fil_pts, Gamma=1.0, a=0.05):
    """
    Velocity at point x induced by a closed polygon filament fil_pts (N,3),
    with circulation Gamma and core regularization a.
    Uses segment midpoint approximation.
    """
    pts = fil_pts
    pts_next = np.roll(pts, -1, axis=0)
    dl = pts_next - pts  # (N,3)
    mid = 0.5*(pts_next + pts)  # (N,3)

    r = x[None, :] - mid  # (N,3)
    r2 = np.sum(r*r, axis=1) + a*a
    r32 = r2**1.5

    cross = np.cross(dl, r)  # (N,3)
    v = (Gamma/(4*np.pi)) * np.sum(cross / r32[:, None], axis=0)
    return v

def induced_velocities(filA, filB, Gamma=1.0, a=0.05, self_induction=False):
    """
    Compute velocities on each filament point induced by the other filament.
    self_induction=False keeps it minimal and avoids near-singular self terms.
    """
    vA = np.zeros_like(filA)
    vB = np.zeros_like(filB)

    for i in range(filA.shape[0]):
        vA[i] = biot_savart_velocity(filA[i], filB, Gamma=Gamma, a=a)
        if self_induction:
            vA[i] += biot_savart_velocity(filA[i], filA, Gamma=Gamma, a=a)

    for i in range(filB.shape[0]):
        vB[i] = biot_savart_velocity(filB[i], filA, Gamma=Gamma, a=a)
        if self_induction:
            vB[i] += biot_savart_velocity(filB[i], filB, Gamma=Gamma, a=a)

    return vA, vB

# -----------------------------
# Linking number (Gauss integral) for two closed polygons
# -----------------------------
def linking_number_gauss(filA, filB):
    """
    Discrete Gauss linking integral:
      Lk = (1/(4π)) ∬ ( (drA × drB) · (rA - rB) / |rA - rB|^3 )
    Approximated by summing over segments (midpoint rule).
    """
    A0 = filA
    A1 = np.roll(filA, -1, axis=0)
    dA = A1 - A0
    mA = 0.5*(A1 + A0)

    B0 = filB
    B1 = np.roll(filB, -1, axis=0)
    dB = B1 - B0
    mB = 0.5*(B1 + B0)

    # pairwise segment contributions
    lk_sum = 0.0
    for i in range(mA.shape[0]):
        rA = mA[i]
        dAi = dA[i]
        R = rA[None, :] - mB  # (NB,3)
        R2 = np.sum(R*R, axis=1)
        R3 = R2**1.5

        num = np.einsum('ij,ij->i', np.cross(dAi[None, :], dB), R)  # (NB,)
        lk_sum += np.sum(num / R3)

    return lk_sum / (4*np.pi)

# -----------------------------
# Time integration (RK2)
# -----------------------------
def rk2_step(filA, filB, dt, Gamma=1.0, a=0.05):
    vA1, vB1 = induced_velocities(filA, filB, Gamma=Gamma, a=a, self_induction=False)
    A_mid = filA + 0.5*dt*vA1
    B_mid = filB + 0.5*dt*vB1
    vA2, vB2 = induced_velocities(A_mid, B_mid, Gamma=Gamma, a=a, self_induction=False)
    return filA + dt*vA2, filB + dt*vB2

# -----------------------------
# Main
# -----------------------------
def main():
    # Parameters (dimensionless demo units)
    Gamma = 1.0
    R = 1.0
    a = 0.05        # core regularization
    N = 200         # points per ring
    dt = 0.01
    steps = 400

    # Hopf link:
    # Ring A: in xy-plane centered at origin
    filA = make_ring(center=[0, 0, 0], normal=[0, 0, 1], R=R, N=N)
    # Ring B: in xz-plane centered at y=R/2 (shifted to link)
    filB = make_ring(center=[0, R*0.5, 0], normal=[0, 1, 0], R=R, N=N)

    # Diagnostics history
    Lk_hist = []
    Hlink_hist = []

    for k in range(steps+1):
        if k % 20 == 0:
            Lk = linking_number_gauss(filA, filB)
            Hlink = 2*(Gamma**2)*Lk
            Lk_hist.append((k*dt, Lk))
            Hlink_hist.append((k*dt, Hlink))
            print(f"t={k*dt:8.3f}  Lk={Lk:+.6f}  H_link={Hlink:+.6f}")

        # advance
        if k < steps:
            filA, filB = rk2_step(filA, filB, dt=dt, Gamma=Gamma, a=a)

    # Optional plot
    try:
        import matplotlib.pyplot as plt
        tL = np.array([x[0] for x in Lk_hist])
        vL = np.array([x[1] for x in Lk_hist])
        tH = np.array([x[0] for x in Hlink_hist])
        vH = np.array([x[1] for x in Hlink_hist])

        plt.figure()
        plt.plot(tL, vL)
        plt.xlabel("t")
        plt.ylabel("Linking number Lk")
        plt.title("Topology diagnostic (should stay ~constant)")
        plt.show()

        plt.figure()
        plt.plot(tH, vH)
        plt.xlabel("t")
        plt.ylabel("H_link = 2 Gamma^2 Lk")
        plt.title("Helicity proxy (linking contribution)")
        plt.show()
    except Exception as e:
        print("Plot skipped:", e)

if __name__ == "__main__":
    main()