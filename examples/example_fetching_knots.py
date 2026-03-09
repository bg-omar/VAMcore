"""
Example: fetching knot data from resources/**/*.fseries and ideal.txt.

All paths are resolved at runtime (script-relative, package-relative, or env).
No absolute paths in source — works on any computer after clone/pip install.

  1. Locate resources via SSTcore.get_resources_dir() or fallbacks (examples/../resources, SSTCORE_RESOURCES).
  2. List and read .fseries files under Knots_FourierSeries/.
  3. Read ideal.txt (ideal knot database with <AB> blocks).

Run from repo root or examples/; set SSTCORE_RESOURCES to point at your resources directory if needed.
"""
import os
import re
import sys
from pathlib import Path

# Prefer locally built module and SSTcore package (for get_resources_dir, etc.)
_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))
_parent = _script_dir.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

try:
    import SSTcore
    HAS_SSTCORE = True
except ImportError:
    HAS_SSTCORE = False


def get_resources_root():
    """Return Path to resources directory, or None. Uses SSTcore if available."""
    if HAS_SSTCORE:
        root = SSTcore.get_resources_dir()
        if root is not None:
            return Path(root)
    # Fallbacks when running from examples/ or repo root
    for base in [_script_dir.parent, _script_dir]:
        r = base / "resources"
        if r.is_dir():
            return r.resolve()
    env = os.environ.get("SSTCORE_RESOURCES")
    if env and Path(env).is_dir():
        return Path(env).resolve()
    return None


def get_fseries_dir():
    """Return Path to Knots_FourierSeries (resources/Knots_FourierSeries), or None."""
    if HAS_SSTCORE:
        kfs = SSTcore.get_knots_fourier_series_dir()
        if kfs is not None:
            return Path(kfs)
    root = get_resources_root()
    if root is None:
        return None
    kfs = root / "Knots_FourierSeries"
    return kfs.resolve() if kfs.is_dir() else None


def get_ideal_txt():
    """Return Path to ideal.txt, or None."""
    if HAS_SSTCORE:
        p = SSTcore.get_ideal_txt_path()
        if p is not None:
            return Path(p)
    root = get_resources_root()
    if root is None:
        return None
    for name in ("ideal.txt", "Knots_FourierSeries/ideal.txt"):
        f = root / name.replace("/", os.sep)
        if f.is_file():
            return f.resolve()
    return None


def list_fseries_files():
    """Return list of Paths to all knot.*.fseries files under resources (recursive)."""
    kfs = get_fseries_dir()
    if kfs is None:
        return []
    out = []
    for root, _dirs, files in os.walk(kfs):
        for fn in files:
            if fn.lower().startswith("knot.") and fn.lower().endswith(".fseries"):
                out.append(Path(root) / fn)
    return sorted(out)


def parse_fseries_file(path):
    """
    Parse one .fseries file. Returns (comment_lines, rows).
    rows: list of lists of floats; each row has 3 (a_x,b_x for one mode) or 6 (a_x,b_x,a_y,b_y,a_z,b_z).
    """
    comments = []
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip()
            if not line:
                continue
            stripped = line.lstrip()
            if stripped.startswith("%"):
                comments.append(line)
                continue
            parts = line.split()
            if not parts:
                continue
            try:
                vals = [float(x) for x in parts]
                if len(vals) in (3, 6):
                    rows.append(vals)
            except ValueError:
                continue
    return comments, rows


def knot_id_from_fseries_path(path):
    """e.g. knot.4_1d.fseries -> 4_1d."""
    name = Path(path).name
    if name.lower().startswith("knot.") and name.lower().endswith(".fseries"):
        return name[5:-8]
    return name


def read_ideal_txt_raw(path):
    """Read ideal.txt as text; return full string."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_ideal_ab_blocks(text):
    """
    Simple regex-based parse of ideal.txt: find <AB ...> opening tags and extract Id, Conway, L, D, n.
    Returns list of dicts with keys: id, conway, L, D, n (optional).
    """
    blocks = []
    # Match <AB Id="..." Conway="..." L="..." D="..." with optional n="..."
    ab_pattern = re.compile(
        r'<AB\s+Id="([^"]*)"\s+Conway="([^"]*)"\s+L="([^"]*)"\s+D="([^"]*)"(?:\s+n="([^"]*)")?\s*>',
        re.IGNORECASE,
    )
    for match in ab_pattern.finditer(text):
        id_, conway, L, D, n = match.groups()
        try:
            L_f = float(L.strip())
        except (ValueError, TypeError):
            L_f = None
        try:
            D_f = float(D.strip())
        except (ValueError, TypeError):
            D_f = None
        blocks.append({
            "id": id_.strip(),
            "conway": conway.strip(),
            "L": L_f,
            "D": D_f,
            "n": n.strip() if n else None,
        })
    return blocks


def main():
    print("=" * 70)
    print("  FETCHING KNOT DATA: resources/**/*.fseries and ideal.txt")
    print("=" * 70)

    # --- 0. Preferred API: get by ID, no path ---
    if HAS_SSTCORE:
        print("\n[0] SSTcore API (no path — resources resolved for you):")
        fseries_content = SSTcore.get_knot_fseries("4_1")
        if fseries_content:
            lines = fseries_content.strip().splitlines()
            print(f"    get_knot_fseries('4_1') -> {len(lines)} lines, first line: {lines[0][:60]}...")
        else:
            print("    get_knot_fseries('4_1') -> None (resources not found or no match)")
        ab_block = SSTcore.get_ideal_ab("3:1:1")
        if ab_block:
            print(f"    get_ideal_ab('3:1:1') -> <AB> block ({len(ab_block)} chars), starts: {ab_block[:55]}...")
        else:
            print("    get_ideal_ab('3:1:1') -> None (ideal.txt not found or Id not found)")
        # All ideal sources and link/HT/ideal_12
        p_ideal = SSTcore.get_ideal_file_path("ideal")
        print(f"    get_ideal_file_path('ideal') -> {p_ideal}")
        link_block = SSTcore.get_ideal_link("L2a1")
        if link_block:
            print(f"    get_ideal_link('L2a1') -> <TL> block ({len(link_block)} chars)")
        else:
            print("    get_ideal_link('L2a1') -> None")
        ht_block = SSTcore.get_ideal_ht("K11a1", source="ideal_11a")
        if ht_block:
            print(f"    get_ideal_ht('K11a1', source='ideal_11a') -> <HT> block ({len(ht_block)} chars)")
        else:
            print("    get_ideal_ht('K11a1') -> None (ideal_11a.txt optional)")
        ids_12 = SSTcore.list_ideal_12_ids()
        print(f"    list_ideal_12_ids() -> {len(ids_12)} 12-crossing files (e.g. {ids_12[:3]})")
        pts_12 = SSTcore.get_ideal_12_points("12a1") if ids_12 else None
        if pts_12:
            print(f"    get_ideal_12_points('12a1') -> {len(pts_12)} (x,y,z) points, first: {pts_12[0]}")
        else:
            print("    get_ideal_12_points('12a1') -> None")
        # All knot options for a fixed crossing (for overnight sweeps)
        opts_7 = SSTcore.list_all_knot_options(7)
        print(f"    list_all_knot_options(7) -> {len(opts_7)} options (e.g. {opts_7[0] if opts_7 else 'none'})")
        if opts_7:
            data = SSTcore.get_knot_data_for_option(opts_7[0])
            print(f"    get_knot_data_for_option(opts_7[0]) -> {type(data).__name__} ({len(data) if data else 0} chars/points)")

    # --- 1. Locate resources ---
    root = get_resources_root()
    if root is None:
        print("\n[!] No resources directory found.")
        print("    Set SSTCORE_RESOURCES or run from repo root with resources/ present.")
        return
    print(f"\n[1] Resources root: {root}")

    # --- 2. List .fseries files ---
    fseries_dir = get_fseries_dir()
    if not fseries_dir:
        print("[2] Knots_FourierSeries/ not found under resources.")
        fseries_paths = []
    else:
        print(f"    Knots_FourierSeries: {fseries_dir}")
        fseries_paths = list_fseries_files()
        print(f"    Found {len(fseries_paths)} .fseries files")
        if fseries_paths:
            print("    First 5:")
            for p in fseries_paths[:5]:
                print(f"      {p.relative_to(fseries_dir)}  ->  id = {knot_id_from_fseries_path(p)}")

    # --- 3. Read one .fseries file ---
    if fseries_paths:
        sample = fseries_paths[0]
        print(f"\n[3] Sample .fseries: {sample.name}")
        comments, rows = parse_fseries_file(sample)
        print(f"    Comment lines: {len(comments)}")
        print(f"    Data rows (3 or 6 floats): {len(rows)}")
        if comments:
            for c in comments[:3]:
                print(f"      {c[:70]}")
        if rows:
            print(f"    First row: {rows[0]}")

    # --- 4. ideal.txt ---
    ideal_path = get_ideal_txt()
    if ideal_path is None:
        print("\n[4] ideal.txt not found.")
    else:
        print(f"\n[4] ideal.txt: {ideal_path}")
        text = read_ideal_txt_raw(ideal_path)
        print(f"    File size: {len(text)} chars")
        blocks = parse_ideal_ab_blocks(text)
        print(f"    Parsed <AB> blocks (simple regex): {len(blocks)}")
        if blocks:
            print("    First 3 AB entries:")
            for b in blocks[:3]:
                print(f"      Id={b['id']}  Conway={b['conway']}  L={b['L']}  D={b['D']}  n={b['n']}")

    # --- 5. Optional: use swirl_string_core for ideal ---
    try:
        import swirl_string_core as ssc
        if ideal_path and hasattr(ssc, "parse_ideal_txt_multi"):
            blocks_cpp = ssc.parse_ideal_txt_multi(str(ideal_path))
            print(f"\n[5] swirl_string_core.parse_ideal_txt_multi: {len(blocks_cpp)} blocks")
            if blocks_cpp:
                first = blocks_cpp[0]
                print(f"    First: id={getattr(first,'id',first)}  L={getattr(first,'L',None)}  D={getattr(first,'D',None)}")
    except ImportError:
        print("\n[5] swirl_string_core not available (optional for full ideal parsing).")

    # --- 6. Knot counts by crossing (for overnight sweep planning) ---
    if HAS_SSTCORE:
        print("\n[6] Knot options by crossing (list_all_knot_options(n)):")
        for n in range(3, 13):
            opts = SSTcore.list_all_knot_options(n)
            print(f"    crossings={n}: {len(opts)} knots")
        print("    Sweep recipe: for opt in SSTcore.list_all_knot_options(n): data = SSTcore.get_knot_data_for_option(opt)")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
