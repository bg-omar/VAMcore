# ./examples/knot_pd_and_volume_example.py
#!/usr/bin/env python3
"""
Example: build a simple 3D knot curve, extract a PD via swirl_string_core.pd_from_curve,
then compute (or attempt) the hyperbolic volume via swirl_string_core.hyperbolic_volume_from_pd.

Notes
  • If the native C++ hyperbolic solver is not built, the binding delegates to
    `sst_hypvol_no_deps.hyperbolic_volume_from_pd` automatically.
  • The demo curve below is a (2,3) torus knot (trefoil). Torus knots are NOT hyperbolic,
    so the volume solver may return 0 or raise; this is normal. Replace the curve or
    pass a PD of a known hyperbolic knot (e.g., figure-eight 4_1) to see a nonzero volume.
"""

import math
import argparse

try:
    import numpy as np
except Exception:
    np = None

try:
    # Provided by your PyBind11 module
    from swirl_string_core import pd_from_curve, hyperbolic_volume_from_pd
except Exception as e:
    raise SystemExit(
        "ERROR: Could not import 'sstcore'. Build & install the module first.\n"
        f"Details: {e}"
    )

def torus_knot_points(p=2, q=3, R=2.0, r=1.0, M=800):
    """
    (p,q)-torus knot sampling on a standard torus embedding.
    Returns ndarray (M,3).
    """
    if np is None:
        # numpy-free fallback
        pts = []
        for k in range(M):
            t = 2*math.pi*k/M
            x = (R + r*math.cos(q*t)) * math.cos(p*t)
            y = (R + r*math.cos(q*t)) * math.sin(p*t)
            z =  r*math.sin(q*t)
            pts.append((x,y,z))
        return pts
    t = np.linspace(0.0, 2.0*math.pi, M, endpoint=False)
    x = (R + r*np.cos(q*t)) * np.cos(p*t)
    y = (R + r*np.cos(q*t)) * np.sin(p*t)
    z =  r*np.sin(q*t)
    return np.stack([x,y,z], axis=1)

def main():
    ap = argparse.ArgumentParser(description="PD + hyperbolic volume demo using sstcore")
    ap.add_argument("--samples", type=int, default=800, help="number of points on the curve")
    ap.add_argument("--tries",   type=int, default=60,  help="random projection trials for PD")
    ap.add_argument("--seed",    type=int, default=12345, help="RNG seed for PD")
    args = ap.parse_args()

    # Build a demo curve (trefoil). Replace with your own (N,3) array for other knots.
    P3 = torus_knot_points(p=2, q=3, R=2.0, r=1.0, M=args.samples)

    # 1) Extract a PD from the 3D curve
    pd = pd_from_curve(P3, tries=args.tries, seed=args.seed)
    print(f"PD extracted: {len(pd)} crossings, {len(pd)*2} arc labels.")

    # 2) Attempt hyperbolic volume
    try:
        vol = hyperbolic_volume_from_pd(pd)
        print(f"Hyperbolic volume: {vol:.12f}")
    except Exception as e:
        print("Volume computation failed (likely non-hyperbolic knot or invalid PD).")
        print("Details:", e)

    # Tip: For a known hyperbolic knot, replace `pd` with a PD of 4_1 (figure-eight)
    # in this convention (positions 1 & 3 are over-arcs). Then rerun.

if __name__ == "__main__":
    main()