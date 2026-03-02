import numpy as np
from dataclasses import dataclass
from math import pi
from typing import Dict, List, Tuple


# ============================================================
# SST canonical constants (SI)
# ============================================================

@dataclass(frozen=True)
class SSTConstants:
    v_swirl: float = 1.09384563e6          # m/s  = \mathbf{v}_{\!\boldsymbol{\circlearrowleft}}
    r_c: float = 1.40897017e-15            # m
    rho_f: float = 7.0e-7                  # kg/m^3


def circulation_from_sst(c: SSTConstants) -> float:
    """
    Gamma = 2*pi*r_c*v_swirl   [m^2/s]
    """
    return 2.0 * pi * c.r_c * c.v_swirl


def core_internal_energy_per_length(c: SSTConstants) -> float:
    """
    Exact Rankine core internal kinetic energy per unit length:
        E_core/L = rho_f * Gamma^2 / (16*pi)   [J/m]
    """
    Gamma = circulation_from_sst(c)
    return c.rho_f * Gamma * Gamma / (16.0 * pi)


# ============================================================
# Trefoil T_{2,3} torus-knot centerline parameterization
# X(phi) = ((R + r cos(3phi)) cos(2phi), (R + r cos(3phi)) sin(2phi), r sin(3phi))
# phi in [0, 2pi)
# ============================================================

def trefoil_t23(phi: np.ndarray, R: float, r: float) -> np.ndarray:
    c2, s2 = np.cos(2.0 * phi), np.sin(2.0 * phi)
    c3, s3 = np.cos(3.0 * phi), np.sin(3.0 * phi)

    A = R + r * c3
    x = A * c2
    y = A * s2
    z = r * s3
    return np.column_stack((x, y, z))


def trefoil_t23_dphi(phi: np.ndarray, R: float, r: float) -> np.ndarray:
    """
    dX/dphi analytically
    """
    c2, s2 = np.cos(2.0 * phi), np.sin(2.0 * phi)
    c3, s3 = np.cos(3.0 * phi), np.sin(3.0 * phi)

    A = R + r * c3
    dA = -3.0 * r * s3

    dx = dA * c2 - 2.0 * A * s2
    dy = dA * s2 + 2.0 * A * c2
    dz = 3.0 * r * c3
    return np.column_stack((dx, dy, dz))


def trefoil_t23_ddphi(phi: np.ndarray, R: float, r: float) -> np.ndarray:
    """
    d^2X/dphi^2 analytically, useful for curvature checks
    """
    c2, s2 = np.cos(2.0 * phi), np.sin(2.0 * phi)
    c3, s3 = np.cos(3.0 * phi), np.sin(3.0 * phi)

    A = R + r * c3
    dA = -3.0 * r * s3
    ddA = -9.0 * r * c3

    ddx = ddA * c2 - 4.0 * dA * s2 - 4.0 * A * c2
    ddy = ddA * s2 + 4.0 * dA * c2 - 4.0 * A * s2
    ddz = -9.0 * r * s3
    return np.column_stack((ddx, ddy, ddz))


# ============================================================
# Geometry utilities
# ============================================================

def arc_length_and_samples(R: float, r: float, N: int) -> Dict[str, np.ndarray]:
    """
    Uniform sampling in phi, then compute:
      X_i, dX/dphi_i, ds_i, tangent_i (unit), phi_i
    using periodic trapezoidal rule.
    """
    if N < 32:
        raise ValueError("N too small; use at least N>=32 for meaningful geometry.")

    phi = np.linspace(0.0, 2.0 * pi, N, endpoint=False)
    X = trefoil_t23(phi, R, r)
    Xp = trefoil_t23_dphi(phi, R, r)

    speed_phi = np.linalg.norm(Xp, axis=1)   # ds/dphi
    dphi = 2.0 * pi / N
    ds = speed_phi * dphi
    L = np.sum(ds)

    # unit tangent t = dX/ds = (dX/dphi)/(ds/dphi)
    t_hat = Xp / speed_phi[:, None]

    return {
        "phi": phi,
        "X": X,
        "Xp": Xp,
        "speed_phi": speed_phi,
        "ds": ds,
        "L": np.array([L]),
        "t_hat": t_hat,
    }


def curvature_stats(R: float, r: float, N: int = 4096) -> Dict[str, float]:
    """
    Curvature kappa = |X' x X''| / |X'|^3  (derivatives w.r.t phi)
    """
    phi = np.linspace(0.0, 2.0 * pi, N, endpoint=False)
    Xp = trefoil_t23_dphi(phi, R, r)
    Xpp = trefoil_t23_ddphi(phi, R, r)
    num = np.linalg.norm(np.cross(Xp, Xpp), axis=1)
    den = np.linalg.norm(Xp, axis=1) ** 3
    kappa = num / den
    return {
        "kappa_min": float(np.min(kappa)),
        "kappa_max": float(np.max(kappa)),
        "kappa_mean": float(np.mean(kappa)),
    }


def min_nonlocal_distance(X: np.ndarray, skip_neighbors: int = 3) -> float:
    """
    Approximate minimum nonlocal separation by brute force over samples,
    ignoring near-neighbor points along the discretized curve.
    O(N^2) -> okay for moderate N (<= few thousand).
    """
    N = X.shape[0]
    dmin = np.inf
    for i in range(N):
        # vectorized distances from point i to all j
        d = np.linalg.norm(X - X[i], axis=1)
        # ignore self and nearby neighbors (periodic)
        for k in range(-skip_neighbors, skip_neighbors + 1):
            d[(i + k) % N] = np.inf
        local_min = np.min(d)
        if local_min < dmin:
            dmin = local_min
    return float(dmin)


# ============================================================
# Regularized nonlocal energy integral
# ============================================================
def nonlocal_energy_regularized(
    rho_f: float,
    Gamma: float,
    X: np.ndarray,
    t_hat: np.ndarray,
    ds: np.ndarray,
    delta: float,
    exclude_diagonal: bool = True,
    exclude_neighbors: int = 0,
    debug: bool = False,
) -> float:
    r"""
    Discrete quadrature for the regularized nonlocal filament energy:
      E_nonlocal(delta) = (rho_f * Gamma^2 / (8*pi)) *
          \iint [t·t'/|X-X'|] Theta(|X-X'|-delta) ds ds'

    This version properly removes a LOCAL STRIP around the diagonal using cyclic
    index-distance masking, not just the exact diagonal i=j.

    Parameters
    ----------
    rho_f : float
        Fluid density [kg/m^3]
    Gamma : float
        Circulation [m^2/s]
    X : (N,3) ndarray
        Centerline sample points [m]
    t_hat : (N,3) ndarray
        Unit tangents
    ds : (N,) ndarray
        Arc-length weights [m]
    delta : float
        Euclidean desingularization cutoff [m]
    exclude_diagonal : bool
        Exclude i=j terms
    exclude_neighbors : int
        Exclude this many cyclic neighbors on EACH side of each point.
        Example: exclude_neighbors=2 excludes j=i-2,...,i+2 (periodic).
    debug : bool
        If True, prints masking diagnostics.

    Notes
    -----
    - The returned value is the *nonlocal numerical part only*.
    - For asymptotic total energy, add the local matching term separately.
    """
    N = X.shape[0]
    pref = rho_f * Gamma * Gamma / (8.0 * np.pi)

    block = 512 if N > 1024 else N
    total = 0.0

    total_pairs_considered = 0
    total_pairs_kept = 0
    total_pairs_removed_delta = 0
    total_pairs_removed_localband = 0
    total_pairs_removed_diag = 0

    # Precompute global indices for cyclic local-band mask logic
    all_j = np.arange(N)

    for i0 in range(0, N, block):
        i1 = min(i0 + block, N)
        Bi = i1 - i0

        Xi = X[i0:i1]                      # (Bi,3)
        ti = t_hat[i0:i1]                  # (Bi,3)
        dsi = ds[i0:i1]                    # (Bi,)
        i_idx = np.arange(i0, i1)          # (Bi,)

        # Pairwise geometry
        diff = Xi[:, None, :] - X[None, :, :]       # (Bi,N,3)
        dist = np.linalg.norm(diff, axis=2)         # (Bi,N)

        # Tangent dot products
        dot_tt = np.einsum("ik,jk->ij", ti, t_hat)  # (Bi,N)

        # Start from delta-based mask
        mask = dist > delta

        # Count delta removals before other masks
        total_pairs_considered += Bi * N
        total_pairs_removed_delta += int(np.count_nonzero(~mask))

        # Exclude exact diagonal if requested
        if exclude_diagonal:
            rows = np.arange(Bi)
            cols = i_idx
            diag_before = mask[rows, cols].copy()
            mask[rows, cols] = False
            # Count only newly removed entries
            total_pairs_removed_diag += int(np.count_nonzero(diag_before))

        # Exclude cyclic local neighbor band (near-diagonal strip)
        if exclude_neighbors > 0:
            # cyclic index distance d_cyc(i,j) = min(|i-j|, N-|i-j|)
            # Build (Bi,N) matrix of cyclic distances
            absdiff = np.abs(i_idx[:, None] - all_j[None, :])
            cyc_dist = np.minimum(absdiff, N - absdiff)
            localband = cyc_dist <= exclude_neighbors

            # Count newly removed entries due to localband
            newly_removed_localband = np.count_nonzero(mask & localband)
            total_pairs_removed_localband += int(newly_removed_localband)

            mask &= ~localband

        total_pairs_kept += int(np.count_nonzero(mask))

        # Kernel
        kernel = np.zeros_like(dist)
        kernel[mask] = dot_tt[mask] / dist[mask]

        # Weighted sum
        total += np.sum(kernel * dsi[:, None] * ds[None, :])

    if debug:
        print(
            "[debug nonlocal_energy_regularized] "
            f"N={N}, delta={delta:.3e}, exclude_neighbors={exclude_neighbors}, "
            f"pairs_total={total_pairs_considered}, kept={total_pairs_kept}, "
            f"removed_delta={total_pairs_removed_delta}, "
            f"removed_diag={total_pairs_removed_diag}, "
            f"removed_localband={total_pairs_removed_localband}"
        )

    return pref * total


# ============================================================
# Driver / convergence study
# ============================================================

def run_trefoil_energy_study(
        R: float,
        r: float,
        N_values: List[int],
        delta_values: List[float],
        constants: SSTConstants = SSTConstants(),
        skip_neighbor_report_N: int = 2048,
) -> Dict[str, object]:
    """
    Computes geometry + energy table.
    R, r are trefoil torus-embedding geometric scales [m].
    delta_values are regularization cutoffs [m], should satisfy r_c << delta << geometric scales.
    """
    c = constants
    Gamma = circulation_from_sst(c)
    ecore_per_len = core_internal_energy_per_length(c)

    # High-resolution geometry diagnostics
    geom_hi = arc_length_and_samples(R, r, max(max(N_values), skip_neighbor_report_N))
    L_hi = float(geom_hi["L"][0])
    curv = curvature_stats(R, r, N=max(4096, max(N_values)))
    dmin_nonlocal = min_nonlocal_distance(geom_hi["X"][:skip_neighbor_report_N], skip_neighbors=3) \
        if geom_hi["X"].shape[0] >= skip_neighbor_report_N else min_nonlocal_distance(geom_hi["X"], skip_neighbors=3)

    results = []
    for N in N_values:
        geom = arc_length_and_samples(R, r, N)
        X = geom["X"]
        t_hat = geom["t_hat"]
        ds = geom["ds"]
        L = float(geom["L"][0])

        E_core = ecore_per_len * L

        # Average arc-length spacing (for choosing local strip width)
        ds_avg = L / N

        for delta in delta_values:
            # Local-strip exclusion width in index space.
            # Use a conservative factor so the numerical nonlocal piece is truly nonlocal.
            # You can tune factor_local_strip = 1.0, 2.0, 3.0 during convergence tests.
            factor_local_strip = 2.0
            exclude_neighbors = max(1, int(np.ceil(factor_local_strip * delta / ds_avg)))

            E_nonlocal = nonlocal_energy_regularized(
                rho_f=c.rho_f,
                Gamma=Gamma,
                X=X,
                t_hat=t_hat,
                ds=ds,
                delta=delta,
                exclude_diagonal=True,
                exclude_neighbors=exclude_neighbors,
                debug=(N == N_values[-1]),  # prints only for largest N per delta
            )

            E_partial = E_core + E_nonlocal

            results.append({
                "N": N,
                "delta_m": delta,
                "L_m": L,
                "Gamma_m2_s": Gamma,
                "ds_avg_m": ds_avg,
                "exclude_neighbors": exclude_neighbors,
                "E_core_J": E_core,
                "E_nonlocal_reg_J": E_nonlocal,
                "E_partial_J": E_partial,
            })

    return {
        "constants": {
            "v_swirl_m_s": c.v_swirl,
            "r_c_m": c.r_c,
            "rho_f_kg_m3": c.rho_f,
            "Gamma_m2_s": Gamma,
            "Omega_c_s^-1": c.v_swirl / c.r_c,
            "E_core_per_length_J_m^-1": ecore_per_len,
        },
        "geometry_reference": {
            "R_m": R,
            "r_m": r,
            "L_ref_m": L_hi,
            "kappa_min_m^-1": curv["kappa_min"],
            "kappa_max_m^-1": curv["kappa_max"],
            "kappa_mean_m^-1": curv["kappa_mean"],
            "a_kappa_max": c.r_c * curv["kappa_max"],
            "approx_min_nonlocal_sep_m": dmin_nonlocal,
        },
        "table": results,
        "notes": [
            "E_partial_J = E_core_J + E_nonlocal_reg_J only.",
            "For asymptotic highest-precision total energy, add local matching correction E_local_match(delta, a) for Rankine core.",
            "Use convergence in N and delta; validate against circular ring limit.",
        ],
    }


def pretty_print_report(report: Dict[str, object]) -> None:
    c = report["constants"]
    g = report["geometry_reference"]
    table = report["table"]

    print("\n=== SST constants / derived quantities ===")
    print(f"v_swirl = {c['v_swirl_m_s']:.15e} m/s")
    print(f"r_c     = {c['r_c_m']:.15e} m")
    print(f"rho_f   = {c['rho_f_kg_m3']:.15e} kg/m^3")
    print(f"Gamma   = {c['Gamma_m2_s']:.18e} m^2/s")
    print(f"Omega_c = {c['Omega_c_s^-1']:.18e} s^-1")
    print(f"E_core/L= {c['E_core_per_length_J_m^-1']:.18e} J/m")

    print("\n=== Trefoil geometry diagnostics ===")
    print(f"R = {g['R_m']:.6e} m, r = {g['r_m']:.6e} m")
    print(f"L_ref               = {g['L_ref_m']:.18e} m")
    print(f"kappa_max           = {g['kappa_max_m^-1']:.18e} 1/m")
    print(f"a*kappa_max         = {g['a_kappa_max']:.18e} (thin-core should be << 1)")
    print(f"approx min nonlocal separation = {g['approx_min_nonlocal_sep_m']:.18e} m")

    print("\n=== Energy convergence table (partial: core + regularized nonlocal) ===")
    header = (
        f"{'N':>6} {'delta [m]':>14} {'ds_avg [m]':>14} {'m_loc':>8} {'L [m]':>14} "
        f"{'E_core [J]':>18} {'E_nonlocal_reg [J]':>22} {'E_partial [J]':>18}"
    )
    print(header)
    print("-" * len(header))
    for row in table:
        print(
            f"{row['N']:6d} "
            f"{row['delta_m']:14.6e} "
            f"{row['ds_avg_m']:14.6e} "
            f"{row['exclude_neighbors']:8d} "
            f"{row['L_m']:14.6e} "
            f"{row['E_core_J']:18.10e} "
            f"{row['E_nonlocal_reg_J']:22.10e} "
            f"{row['E_partial_J']:18.10e}"
        )

    print("\nNotes:")
    for note in report["notes"]:
        print(f" - {note}")


if __name__ == "__main__":
    # ------------------------------------------------------------
    # USER INPUTS (must be set to define the actual trefoil embedding)
    # ------------------------------------------------------------
    # IMPORTANT: energy is not determined by topology alone.
    # You must choose geometric scale R, r [meters].
    #
    # Example only:
    # Set a trefoil size much larger than r_c so thin-core asymptotics applies.
    R = 1.0e-9   # m  (example major radius)
    r = 3.0e-10  # m  (example minor radius)

    c = SSTConstants()
    a = c.r_c

    # Choose delta such that a << delta << geometric scales
    delta_values = [
        1.0e-13,
        3.0e-13,
        1.0e-12,
    ]

    N_values = [256, 512, 1024]

    report = run_trefoil_energy_study(
        R=R,
        r=r,
        N_values=N_values,
        delta_values=delta_values,
        constants=c,
    )
    pretty_print_report(report)