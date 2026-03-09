"""
SSTcore: Particle Zoo Evaluator (Topology-First Scaffold)

Pre-registers knot assignments and topology, then tests mass predictions.
Model 1: Geometry-only (no masses) – structural content.
Model 2: Mass model (one calibration constant) – tests if phi is special after topology fixed.

Usage:
    python example_particle_zoo_eval.py

See docs: topology → prediction → comparison. Quark sector: use hadron tests, not raw masses.
"""

from dataclasses import dataclass
from typing import Optional, List
import math
import random
import statistics

try:
    import sstcore as sst
except ImportError:
    import sstbindings as sst


@dataclass
class ParticleState:
    name: str
    sector: str
    family: str
    knot_id: str
    C: int
    layer_index: Optional[int]
    obs_mass_mev: Optional[float]
    notes: str = ""


def energy_proxy(state: ParticleState, alpha=1.0, beta=0.0, gamma=0.0, L=0.0, H=0.0):
    # Placeholder until invariant/geometry tables are attached.
    return alpha * state.C + beta * L + gamma * H


def model_mass_mev(state: ParticleState, M0: float, base: float, alpha=1.0, beta=0.0, gamma=0.0, L=0.0, H=0.0):
    F = energy_proxy(state, alpha=alpha, beta=beta, gamma=gamma, L=L, H=H)
    return M0 * F * (base ** (-state.layer_index))


def rel_err(pred: float, obs: float) -> float:
    return abs(pred - obs) / obs


def build_default_zoo() -> List[ParticleState]:
    return [
        # Lepton scaffold (topology-first placeholders)
        ParticleState("tau", "lepton", "vortex-knot", "3_1", 3, 0, 1776.86, "reference"),
        ParticleState("mu",  "lepton", "vortex-knot", "3_1", 3, 6, 105.66, ""),
        ParticleState("e",   "lepton", "vortex-knot", "3_1", 3, 17, 0.5110, ""),

        # Quark placeholders (evaluate at hadron-combination level later)
        ParticleState("u?",  "quark", "twist-knot", "5_2", 5, None, None, "Prefer hadron-level tests"),
        ParticleState("d?",  "quark", "twist-knot", "6_1", 6, None, None, "Prefer hadron-level tests"),
    ]


def get_leptons(zoo: List[ParticleState]) -> List[ParticleState]:
    return [s for s in zoo if s.sector == "lepton" and s.obs_mass_mev is not None and s.layer_index is not None]


def calibrate_M0_from_reference(ref: ParticleState, base: float, alpha=1.0, beta=0.0, gamma=0.0, L=0.0, H=0.0) -> float:
    F_ref = energy_proxy(ref, alpha=alpha, beta=beta, gamma=gamma, L=L, H=H)
    if F_ref == 0:
        raise ValueError("Reference state has zero energy proxy.")
    # m_ref = M0 * F_ref * base^{-n_ref}
    return ref.obs_mass_mev / (F_ref * (base ** (-ref.layer_index)))


def evaluate_states(states: List[ParticleState], base: float, ref_name: str = "tau",
                    alpha=1.0, beta=0.0, gamma=0.0, L=0.0, H=0.0):
    ref = next(s for s in states if s.name == ref_name)
    M0 = calibrate_M0_from_reference(ref, base, alpha=alpha, beta=beta, gamma=gamma, L=L, H=H)
    rows = []
    for s in states:
        pred = model_mass_mev(s, M0=M0, base=base, alpha=alpha, beta=beta, gamma=gamma, L=L, H=H)
        err = rel_err(pred, s.obs_mass_mev)
        rows.append((s, pred, err))
    return M0, rows


def base_scan(states: List[ParticleState], b_min=1.55, b_max=1.70, n_steps=301,
              ref_name: str = "tau", alpha=1.0, beta=0.0, gamma=0.0, L=0.0, H=0.0):
    if n_steps < 2:
        raise ValueError("n_steps must be >= 2")

    best = None
    results = []

    for i in range(n_steps):
        b = b_min + (b_max - b_min) * (i / (n_steps - 1))
        M0, rows = evaluate_states(states, base=b, ref_name=ref_name, alpha=alpha, beta=beta, gamma=gamma, L=L, H=H)

        # Exclude calibration reference from score (predictive score on remaining leptons)
        scored = [(s, pred, err) for (s, pred, err) in rows if s.name != ref_name]
        mean_rel = sum(err for _, _, err in scored) / len(scored)
        max_rel = max(err for _, _, err in scored)
        rms_rel = math.sqrt(sum(err * err for _, _, err in scored) / len(scored))

        record = {
            "base": b,
            "M0": M0,
            "mean_rel": mean_rel,
            "max_rel": max_rel,
            "rms_rel": rms_rel,
            "rows": rows,
        }
        results.append(record)

        if best is None or record["mean_rel"] < best["mean_rel"]:
            best = record

    return best, results


def estimate_base_from_two_gaps(leptons: List[ParticleState]):
    tau = next(s for s in leptons if s.name == "tau")
    out = {}
    for s in leptons:
        if s.name == "tau":
            continue
        dn = s.layer_index - tau.layer_index
        ratio = tau.obs_mass_mev / s.obs_mass_mev
        b_eff = sst.GoldenNLSClosure.infer_effective_base(ratio, dn)
        out[s.name] = {"ratio": ratio, "delta_n": dn, "b_eff": b_eff}
    return out


def summarize_scan_result(scan_record, ref_name="tau"):
    b = scan_record["base"]
    M0 = scan_record["M0"]
    mean_rel = scan_record["mean_rel"]
    max_rel = scan_record["max_rel"]
    rms_rel = scan_record["rms_rel"]
    print(f"  best base = {b:.10f} | M0 = {M0:.6f} MeV")
    print(f"  mean rel err (excluding {ref_name}) = {mean_rel:.4%}")
    print(f"  rms  rel err (excluding {ref_name}) = {rms_rel:.4%}")
    print(f"  max  rel err (excluding {ref_name}) = {max_rel:.4%}")
    print("  name |       pred |        obs |  rel_err")
    for s, pred, err in scan_record["rows"]:
        print(f"  {s.name:>4} | {pred:10.4f} | {s.obs_mass_mev:10.4f} | {err:7.3%}")


def permutation_test_layer_assignment(leptons: List[ParticleState], base: float, trials: int = 10000,
                                      ref_name: str = "tau", seed: int = 12345,
                                      alpha=1.0, beta=0.0, gamma=0.0, L=0.0, H=0.0):
    """
    Shuffle the non-reference layer indices among the non-reference leptons.
    Score = mean relative error on non-reference leptons.
    """
    rng = random.Random(seed)
    ref = next(s for s in leptons if s.name == ref_name)
    nonref = [s for s in leptons if s.name != ref_name]

    original_layers = [s.layer_index for s in nonref]
    obs_score = evaluate_states(leptons, base=base, ref_name=ref_name, alpha=alpha, beta=beta, gamma=gamma, L=L, H=H)[1]
    obs_score = [err for (s, _, err) in obs_score if s.name != ref_name]
    obs_mean = sum(obs_score) / len(obs_score)

    perm_scores = []
    for _ in range(trials):
        perm = original_layers[:]
        rng.shuffle(perm)

        # Build temporary copy with shuffled layer assignments on non-reference states
        temp = []
        p_i = 0
        for s in leptons:
            if s.name == ref_name:
                temp.append(s)
            else:
                temp.append(ParticleState(
                    name=s.name,
                    sector=s.sector,
                    family=s.family,
                    knot_id=s.knot_id,
                    C=s.C,
                    layer_index=perm[p_i],
                    obs_mass_mev=s.obs_mass_mev,
                    notes=s.notes
                ))
                p_i += 1

        _, rows = evaluate_states(temp, base=base, ref_name=ref_name, alpha=alpha, beta=beta, gamma=gamma, L=L, H=H)
        errs = [err for (s, _, err) in rows if s.name != ref_name]
        perm_scores.append(sum(errs) / len(errs))

    # one-sided p-value: how often shuffled score <= observed score
    better_or_equal = sum(1 for s in perm_scores if s <= obs_mean)
    p_value = (better_or_equal + 1) / (trials + 1)

    return {
        "observed_mean_rel_err": obs_mean,
        "perm_mean": statistics.mean(perm_scores),
        "perm_median": statistics.median(perm_scores),
        "perm_min": min(perm_scores),
        "perm_max": max(perm_scores),
        "p_value_one_sided": p_value,
        "trials": trials,
    }


def main():
    print("--- SSTcore: Particle Zoo Evaluator (Topology-First Scaffold) ---\n")

    phi = (1 + math.sqrt(5)) / 2
    zoo = build_default_zoo()
    leptons = get_leptons(zoo)

    # Baseline phi evaluation
    print("Lepton-only test (M0 calibrated on tau, base=phi):")
    M0_phi, rows_phi = evaluate_states(leptons, base=phi, ref_name="tau", alpha=1.0)
    F_tau = energy_proxy(next(s for s in leptons if s.name == "tau"), alpha=1.0)
    print(f"  M0 = {M0_phi:.6f} MeV (with F_tau = {F_tau:.1f})")
    print("  name |       pred |        obs |  rel_err")
    for s, pred, err in rows_phi:
        print(f"  {s.name:>4} | {pred:10.4f} | {s.obs_mass_mev:10.4f} | {err:7.3%}")

    # Effective base implied by each gap if exponents are fixed
    print("\nEffective-base diagnostics from fixed layer indices (topology-first placeholders):")
    bdiag = estimate_base_from_two_gaps(leptons)
    for name, info in bdiag.items():
        print(
            f"  tau/{name:<2} ratio = {info['ratio']:.8f} | "
            f"delta_n = {info['delta_n']:>2d} | "
            f"b_eff = {info['b_eff']:.10f}"
        )
    print(f"  phi = {phi:.10f}")

    # Base scan
    print("\nBase scan (fit quality over b in [1.55, 1.70], tau-calibrated):")
    best, scan = base_scan(leptons, b_min=1.55, b_max=1.70, n_steps=301, ref_name='tau', alpha=1.0)
    summarize_scan_result(best, ref_name="tau")

    # Compare phi record directly
    phi_record = min(scan, key=lambda r: abs(r["base"] - phi))
    print("\nPhi scan-point summary:")
    summarize_scan_result(phi_record, ref_name="tau")

    # Permutation test on layer assignments (lepton scaffold only)
    print("\nPermutation test (shuffle non-reference lepton layer indices):")
    perm = permutation_test_layer_assignment(leptons, base=phi, trials=10000, ref_name="tau", seed=12345, alpha=1.0)
    print(f"  observed mean rel err = {perm['observed_mean_rel_err']:.4%}")
    print(f"  perm mean             = {perm['perm_mean']:.4%}")
    print(f"  perm median           = {perm['perm_median']:.4%}")
    print(f"  perm min / max        = {perm['perm_min']:.4%} / {perm['perm_max']:.4%}")
    print(f"  one-sided p-value     = {perm['p_value_one_sided']:.6f}  (trials={perm['trials']})")

    print("\nNote: quark entries are placeholders; evaluate at hadron-combination level, not direct quark masses.")
    print("Next: add permutation test, base scan, and pre-registered topology → prediction benchmarks.")


if __name__ == "__main__":
    main()
