#!/usr/bin/env python3
"""
Explore connected sums like 5_2#5_2#6_1 and 5_2#6_1#6_1 using:
  (A) KnotInfo (scrape) for invariants (sigma, tau, s, unknotting number if listed)
  (B) SnapPy/Spherogram for diagram-level experiments with crossing changes

What this script can do well
----------------------------
1) Pull KnotInfo values for: signature (σ), Ozsváth–Szabó tau (τ), Rasmussen s (s),
   unknotting number u (if shown on KnotInfo), plus a few extra fields if desired.
2) Build connected sums (as spherogram links).
3) Brute-force search for *upper bounds* on unknotting number of a given diagram by
   trying all crossing-change sets up to k (k=1..3, adjustable), simplifying, and
   testing if it becomes the unknot using strong-but-still-heuristic checks.

Important honesty note
----------------------
Determining "is this exactly the unknot?" from a diagram is subtle.
This script uses a combination of:
  - simplification attempts
  - Alexander polynomial == 1
  - Jones polynomial == 1
  - SnapPy exterior recognition heuristics (when available)

This is usually reliable for small examples, but it is still not a proof assistant.
If you need a proof-grade result, you typically combine:
  - a certified unknot recognizer (e.g., Regina / normal surface algorithms)
  - or published invariants/bounds.

Usage
-----
python investigate_knots.py --knot 5_2 --knot 5_2 --knot 6_1 --max-k 3
python investigate_knots.py --knot 5_2 --knot 6_1 --knot 6_1 --max-k 3
"""

import argparse
import itertools
import copy
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# --- Web scraping (KnotInfo) ---
import requests
from bs4 import BeautifulSoup

# --- SnapPy / Spherogram ---
try:
    import snappy  # noqa: F401
    from spherogram import Link
except Exception as e:
    print("ERROR: Could not import SnapPy/Spherogram.", file=sys.stderr)
    print("Install with something like:", file=sys.stderr)
    print("  pip install snappy spherogram", file=sys.stderr)
    raise


KNOTINFO_BASE = "https://knotinfo.math.indiana.edu"


@dataclass
class KnotInfoRecord:
    name: str
    url: str
    fields: Dict[str, str]


def knotinfo_url(rolfsen_name: str) -> str:
    """
    KnotInfo has multiple tables; the 'knot' table covers Rolfsen knots like 5_2, 6_1.
    This URL pattern works for many standard knots:
      https://knotinfo.math.indiana.edu/knot/knot.php?name=5_2
    """
    return f"{KNOTINFO_BASE}/knot/knot.php?name={rolfsen_name}"


def fetch_knotinfo_fields(
    rolfsen_name: str,
    desired_labels: Optional[List[str]] = None,
    timeout: int = 20,
) -> KnotInfoRecord:
    """
    Scrape KnotInfo page and extract row labels + values from the main table.

    desired_labels: if provided, try to return only those (case-insensitive contains match).
    Example desired_labels:
      ["Signature", "Ozsvath-Szabo tau", "Rasmussen s", "Unknotting Number"]
    """
    url = knotinfo_url(rolfsen_name)
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # KnotInfo pages typically have tables with rows: <tr><th>Label</th><td>Value</td></tr>
    # We'll extract all label/value pairs we can find.
    fields: Dict[str, str] = {}

    for tr in soup.find_all("tr"):
        th = tr.find("th")
        td = tr.find("td")
        if not th or not td:
            continue
        label = " ".join(th.get_text(" ", strip=True).split())
        value = " ".join(td.get_text(" ", strip=True).split())
        if label and value:
            fields[label] = value

    if desired_labels:
        wanted: Dict[str, str] = {}
        for want in desired_labels:
            want_low = want.lower()
            for label, value in fields.items():
                if want_low in label.lower():
                    wanted[label] = value
        fields = wanted

    return KnotInfoRecord(name=rolfsen_name, url=url, fields=fields)


def pretty_print_knotinfo(rec: KnotInfoRecord) -> None:
    print(f"\nKnotInfo: {rec.name}")
    print(f"URL: {rec.url}")
    if not rec.fields:
        print("  (No fields parsed — KnotInfo layout may have changed.)")
        return
    for k, v in rec.fields.items():
        print(f"  - {k}: {v}")


# --- Spherogram / SnapPy experiments ---

def parse_knot(name: str) -> Link:
    """
    Build a spherogram Link from a Rolfsen name like '5_2' or '6_1'.
    """
    return Link(name)


def connected_sum(links: List[Link]) -> Link:
    """
    Connected sum for knots: iteratively connected_sum.
    For links this may not do what you want, but for knots (1 component) it's fine.
    """
    if not links:
        raise ValueError("Need at least one Link.")
    out = links[0]
    for L in links[1:]:
        out = out.connected_sum(L)
    return out


def simplify_link(L: Link, rounds: int = 30) -> Link:
    """
    Try to simplify a link diagram in-place and return it.
    """
    # spherogram simplify can be a bit stochastic; call multiple times.
    for _ in range(rounds):
        try:
            L.simplify("global")
        except Exception:
            try:
                L.simplify()
            except Exception:
                break
    return L


def crossing_indices(L: Link) -> List[int]:
    """
    Return crossing indices 0..n-1 for the current diagram.
    """
    return list(range(len(L.crossings)))


def flip_crossings(L: Link, idxs: List[int]) -> Link:
    """
    Return a NEW Link with crossings at idxs switched.
    """
    # Make a fresh copy so we don't mutate the original. Try PD_code first
    # (often more reliable for connected sums), then DT_code, then deepcopy.
    L2 = None
    last_err = None
    for make_copy in [
        lambda: Link(L.PD_code()),
        lambda: Link(L.DT_code()),
        lambda: copy.deepcopy(L),
    ]:
        try:
            L2 = make_copy()
            break
        except Exception as e:
            last_err = e
    if L2 is None:
        raise RuntimeError(f"Could not copy link for crossing flip: {last_err}") from last_err

    for i in idxs:
        if i < len(L2.crossings):
            L2.crossings[i].switch()
    return L2


def alexander_is_trivial(L: Link) -> bool:
    """
    Alexander polynomial == 1 (up to units) is necessary for unknot, not sufficient.
    """
    try:
        poly = L.alexander_polynomial()
        # Normalize to string and look for "1" only
        s = str(poly).replace(" ", "")
        return s in {"1", "-1"}
    except Exception:
        return False


def jones_is_trivial(L: Link) -> bool:
    """
    Jones polynomial == 1 for the unknot (with a common convention).
    This is also not a complete invariant.
    """
    try:
        poly = L.jones_polynomial()
        s = str(poly).replace(" ", "")
        return s in {"1", "-1"}
    except Exception:
        return False


def exterior_looks_like_unknot(L: Link) -> bool:
    """
    Try SnapPy recognition: unknot complement is a solid torus.
    SnapPy can sometimes detect this via simplification + fundamental group / fillings.
    This is heuristic (depends on SnapPy version).
    """
    try:
        M = L.exterior()
        # Solid torus has H1 = Z. Many knot complements also have H1=Z, so not enough.
        # But combined with non-hyperbolicity checks, it's a useful filter.
        H = M.homology()
        if str(H) != "Z":
            return False

        # Unknot complement is not hyperbolic; SnapPy often raises or returns False here.
        try:
            if M.solution_type() == "all tetrahedra positively oriented":
                # likely hyperbolic => not unknot
                return False
        except Exception:
            pass

        # If SnapPy can recognize it directly, use that.
        try:
            name = M.identify()
            if name:
                # Some versions may return something like "Solid torus" or a census name.
                if "solid" in str(name).lower() and "torus" in str(name).lower():
                    return True
        except Exception:
            pass

        # Final heuristic: if after aggressive simplification, diagram has 0 crossings
        # (handled elsewhere) or both polynomials trivial, accept.
        return alexander_is_trivial(L) and jones_is_trivial(L)
    except Exception:
        return False


def is_very_likely_unknot(L: Link) -> bool:
    """
    Combine checks.
    """
    simplify_link(L, rounds=50)
    if len(L.crossings) == 0:
        return True
    # Strong-ish heuristic combo
    if alexander_is_trivial(L) and jones_is_trivial(L) and exterior_looks_like_unknot(L):
        return True
    return False


def search_unknotting_upper_bound(
    L: Link,
    max_k: int = 3,
    early_stop: bool = True,
) -> Tuple[Optional[int], Optional[List[int]]]:
    """
    Try all crossing-change sets up to size max_k and return the smallest k found
    such that the diagram becomes (very likely) the unknot.

    Returns: (k, crossing_indices) or (None, None) if not found.
    """
    simplify_link(L, rounds=50)
    n = len(L.crossings)
    idxs = crossing_indices(L)

    if is_very_likely_unknot(L):
        return 0, []

    for k in range(1, max_k + 1):
        for subset in itertools.combinations(idxs, k):
            try:
                L2 = flip_crossings(L, list(subset))
                if is_very_likely_unknot(L2):
                    return k, list(subset)
            except Exception:
                continue
        if early_stop:
            # if you want exhaustive across all k up to max_k, set early_stop=False
            pass
    return None, None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--knot",
        action="append",
        help="Rolfsen knot name, e.g. 5_2 or 6_1. Repeat for connected sum factors.",
    )
    ap.add_argument("--max-k", type=int, default=3, help="Max number of crossing changes to try.")
    ap.add_argument("--no-knotinfo", action="store_true", help="Skip KnotInfo scraping.")
    args = ap.parse_args()

    if not args.knot:
        args.knot = ["5_2", "5_2", "6_1"]
    factors = args.knot
    print("Factors:", " # ".join(factors))

    # --- KnotInfo invariants for each factor ---
    if not args.no_knotinfo:
        desired = ["Signature", "tau", "Rasmussen", "Unknotting"]
        knotinfo_unavailable = False
        for name in factors:
            if knotinfo_unavailable:
                continue
            try:
                rec = fetch_knotinfo_fields(name, desired_labels=desired)
                pretty_print_knotinfo(rec)
            except Exception as e:
                err_str = str(e).lower()
                if "max retries" in err_str or "resolve" in err_str or "connection" in err_str:
                    if not knotinfo_unavailable:
                        print("KnotInfo unavailable (e.g. offline), skipping.", file=sys.stderr)
                        knotinfo_unavailable = True
                else:
                    print(f"\nKnotInfo fetch failed for {name}: {e}", file=sys.stderr)

    # --- Build connected sum diagram ---
    links = [parse_knot(k) for k in factors]
    Ksum = connected_sum(links)
    simplify_link(Ksum, rounds=80)

    print("\nConnected sum diagram:")
    print(f"  crossings (after simplify): {len(Ksum.crossings)}")
    try:
        print(f"  Alexander: {Ksum.alexander_polynomial()}")
    except Exception:
        print("  Alexander: (failed)")
    try:
        print(f"  Jones: {Ksum.jones_polynomial()}")
    except Exception:
        print("  Jones: (failed)")

    # --- Try to find a small unknotting sequence (upper bound) ---
    k, subset = search_unknotting_upper_bound(Ksum, max_k=args.max_k)
    if k is None:
        print(f"\nNo unknotting found up to k={args.max_k} crossing changes (with heuristics).")
    else:
        print(f"\nFound heuristic unknotting with k={k} crossing change(s).")
        print(f"Crossing indices to switch: {subset}")

        # Verify / show invariants after switching
        K2 = flip_crossings(Ksum, subset)
        simplify_link(K2, rounds=120)
        print("\nAfter switching:")
        print(f"  crossings: {len(K2.crossings)}")
        try:
            print(f"  Alexander: {K2.alexander_polynomial()}")
        except Exception:
            pass
        try:
            print(f"  Jones: {K2.jones_polynomial()}")
        except Exception:
            pass
        try:
            M = K2.exterior()
            print(f"  exterior homology: {M.homology()}")
            try:
                print(f"  solution_type: {M.solution_type()}")
            except Exception:
                pass
        except Exception:
            pass


if __name__ == "__main__":
    main()