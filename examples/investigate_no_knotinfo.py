#!/usr/bin/env python3
"""
Unknotting upper-bound search using SnapPy + Spherogram (your build)
- Crossing change implemented by flipping Crossing.sign
- No KnotInfo
- No DT copying
- Primary "unknot" success criterion: simplify down to 0 crossings

This is a practical explorer for small k (1..3).
If you need a proof, pair it with a certified unknot recognizer (e.g. Regina).
"""

import argparse
import itertools
from typing import List, Optional, Tuple

from spherogram import Link


def parse_rolfsen(name: str) -> Link:
    return Link(name)


def connected_sum(links: List[Link]) -> Link:
    out = links[0]
    for L in links[1:]:
        out = out.connected_sum(L)
    return out


def simplify_link(L: Link, rounds: int = 200) -> None:
    for _ in range(rounds):
        try:
            L.simplify("global")
        except Exception:
            try:
                L.simplify()
            except Exception:
                break


def toggle_crossing_by_sign(L: Link, i: int) -> None:
    """
    Crossing change by flipping the crossing sign.
    This matches your Crossing API dump: attr 'sign' is present and int-valued.
    """
    L.crossings[i].sign *= -1


def is_unknot_by_simplify(L: Link, rounds: int = 300) -> bool:
    """
    Heuristic: after aggressive simplification, 0 crossings -> unknot diagram.
    """
    simplify_link(L, rounds=rounds)
    return len(L.crossings) == 0


def search_unknotting_upper_bound(
        L: Link,
        max_k: int,
        verbose: bool = False,
) -> Tuple[Optional[int], Optional[List[int]]]:
    simplify_link(L, rounds=200)

    if is_unknot_by_simplify(L):
        return 0, []

    n = len(L.crossings)
    idxs = list(range(n))

    for k in range(1, max_k + 1):
        if verbose:
            # combinations count can be big; just print k and n
            print(f"Trying k={k} over subsets of {n} crossings ...")

        for subset in itertools.combinations(idxs, k):
            subset = list(subset)

            # toggle in-place
            for i in subset:
                toggle_crossing_by_sign(L, i)

            ok = is_unknot_by_simplify(L)

            # toggle back
            for i in subset:
                toggle_crossing_by_sign(L, i)

            if ok:
                return k, subset

    return None, None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--knot", action="append", required=True,
                    help="Rolfsen knot name like 5_2 or 6_1 (repeatable).")
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--seed-simplify-rounds", type=int, default=200,
                    help="Simplify rounds before search (default 200).")
    args = ap.parse_args()

    factors = args.knot
    print("Factors:", " # ".join(factors))

    L = connected_sum([parse_rolfsen(k) for k in factors])
    simplify_link(L, rounds=args.seed_simplify_rounds)

    print("\nInitial simplified diagram")
    print("  crossings:", len(L.crossings))
    print("  (Crossing change uses crossing.sign *= -1)")

    k, subset = search_unknotting_upper_bound(L, max_k=args.max_k, verbose=args.verbose)

    if k is None:
        print(f"\nNo unknot found up to k={args.max_k} using simplify-to-zero heuristic.")
        print("Try increasing simplify rounds or searching higher k, or try random diagram variants.")
        return

    print(f"\nFound candidate unknotting with k={k} crossing changes.")
    print("Crossing indices to switch:", subset)

    # Show result after applying
    for i in subset:
        toggle_crossing_by_sign(L, i)
    simplify_link(L, rounds=400)
    print("\nAfter switching + simplify")
    print("  crossings:", len(L.crossings))


if __name__ == "__main__":
    main()