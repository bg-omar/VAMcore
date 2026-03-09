# SSTcore: companion package for sstcore (resources and helpers).
# The C++ extension is installed as sstcore / sstbindings.
# Resource location follows CMake install (share/sstcore/resources) or dev layout.
# Importing SSTcore also exposes the C extension API (same as sstcore / sstbindings / swirl_string_core).

from pathlib import Path
import os
import sys
import re
from typing import Optional, List, Tuple, Dict, Any

# Known ideal-style files in resources/ (knots: AB/HT, links: TL).
IDEAL_SOURCE_FILES = {
    "ideal": "ideal.txt",           # knots 3–10 crossings, <AB Id="n:m:k">
    "ideal_11a": "ideal_11a.txt",   # 11-crossing alternating, <HT Id="K11a1">
    "ideal_11n": "ideal_11n.txt",   # 11-crossing non-alternating, <HT Id="K11n1">
    "idealLinks": "idealLinks.txt", # links 2–9 crossings, <TL Id="L2a1">
    "idealLinks_10a": "idealLinks_10a.txt",
    "idealLinks_10n": "idealLinks_10n.txt",
}

__all__ = [
    "get_resources_dir",
    "get_knots_fourier_series_dir",
    "get_ideal_txt_path",
    "get_ideal_file_path",
    "get_ideal_12_data_dir",
    "get_knot_fseries",
    "get_ideal_ab",
    "get_ideal_ht",
    "get_ideal_link",
    "get_ideal_12_points",
    "list_ideal_12_ids",
    "list_ideal_ab_ids",
    "list_ideal_ht_ids",
    "list_ideal_link_ids",
    "list_all_knot_options",
    "list_all_link_options",
    "get_knot_data_for_option",
]

# Re-export C extension API so "import SSTcore" exposes the same as sstcore / sstbindings / swirl_string_core
try:
    import sstcore as _sst_native
    from sstcore import *  # noqa: F401, F403
    _native_all = getattr(_sst_native, "__all__", [])
    __all__ = list(__all__) + [x for x in _native_all if x not in __all__]
except ImportError:
    try:
        import sstbindings as _sst_native
        from sstbindings import *  # noqa: F401, F403
        _native_all = getattr(_sst_native, "__all__", [])
        __all__ = list(__all__) + [x for x in _native_all if x not in __all__]
    except ImportError:
        pass


def get_resources_dir() -> Optional[Path]:
    """
    Return the path to the SSTcore resources directory (ideal.txt, Knots_FourierSeries, etc.).
    Works after pip install and in development.

    - Uses SSTCORE_RESOURCES if set.
    - Else package-bundled resources/ (pip install with package_data).
    - Else share/sstcore/resources (CMake/data_files install).
    - Else resources/ next to the package (development).

    Returns None if no resources directory is found.
    """
    # 1. Explicit environment variable
    env = os.environ.get("SSTCORE_RESOURCES")
    if env:
        p = Path(env)
        if p.is_dir():
            return p.resolve()

    # 2. Package-bundled resources (pip install with package_data: ideal.txt, Knots_FourierSeries, etc.)
    _pkg_resources = Path(__file__).resolve().parent / "resources"
    if _pkg_resources.is_dir():
        return _pkg_resources

    # 3. Pip install: data_files go to prefix/share/sstcore/resources
    prefix = Path(sys.prefix)
    for candidate in [
        prefix / "share" / "sstcore" / "resources",
        prefix / "Lib" / "site-packages" / "share" / "sstcore" / "resources",  # Windows venv
    ]:
        if candidate.is_dir():
            return candidate.resolve()

    # 4. Development: resources/ next to this package (SSTcore repo root)
    this_file = Path(__file__).resolve()
    dev_resources = this_file.parent.parent / "resources"
    if dev_resources.is_dir():
        return dev_resources.resolve()

    return None


def get_knots_fourier_series_dir() -> Optional[Path]:
    """Return the path to Knots_FourierSeries (subdir of resources), or None."""
    root = get_resources_dir()
    if root is None:
        return None
    kfs = root / "Knots_FourierSeries"
    return kfs.resolve() if kfs.is_dir() else None


def get_ideal_txt_path() -> Optional[Path]:
    """Return the path to ideal.txt, or None. Prefers resources/ideal.txt then Knots_FourierSeries/ideal.txt."""
    p = get_ideal_file_path("ideal")
    if p is not None:
        return p
    root = get_resources_dir()
    if root is None:
        return None
    kfs = root / "Knots_FourierSeries" / "ideal.txt"
    return kfs.resolve() if kfs.is_file() else None


def get_ideal_file_path(source: str) -> Optional[Path]:
    """
    Return the path to a named ideal database file in resources. No path needed.

    source: one of "ideal", "ideal_11a", "ideal_11n", "idealLinks", "idealLinks_10a", "idealLinks_10n".
    Returns Path to that file, or None if not found.
    """
    root = get_resources_dir()
    if root is None:
        return None
    name = IDEAL_SOURCE_FILES.get(source) or source
    if "/" in name or "\\" in name:
        return None
    p = root / name
    return p.resolve() if p.is_file() else None


def get_ideal_12_data_dir() -> Optional[Path]:
    """Return the path to ideal_12_data/ (12-crossing point clouds), or None."""
    root = get_resources_dir()
    if root is None:
        return None
    d = root / "ideal_12_data"
    return d.resolve() if d.is_dir() else None


def get_knot_fseries(knot_id: str) -> Optional[str]:
    """
    Return the contents of a knot .fseries file by knot ID. No path needed — uses installed/dev resources.

    knot_id: e.g. "4_1", "4_1d", "8_5", "12a_1202". Tries exact knot.{knot_id}.fseries first,
    then any knot.{knot_id}*.fseries under Knots_FourierSeries (recursive).

    Returns file content as string, or None if not found.
    """
    kfs = get_knots_fourier_series_dir()
    if kfs is None:
        return None
    knot_id = knot_id.strip()
    base = knot_id.replace("-", "_")
    exact_name = f"knot.{base}.fseries"
    exact_path = None
    prefix_path = None
    for root, _dirs, files in os.walk(kfs):
        for fn in files:
            fn_lower = fn.lower()
            if fn_lower == exact_name.lower():
                exact_path = Path(root) / fn
                break
            if prefix_path is None and fn_lower.startswith(f"knot.{base}".lower()) and fn_lower.endswith(".fseries"):
                prefix_path = Path(root) / fn
        if exact_path is not None:
            break
    first_match_path = exact_path if exact_path is not None else prefix_path
    if first_match_path is None:
        return None
    try:
        return first_match_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _extract_xml_block(text: str, tag: str, id_value: str) -> Optional[str]:
    """Extract first <TAG Id="id_value" ...>...</TAG> from text. Id match exact or with :/_ normalized."""
    id_value = id_value.strip()
    pattern = re.compile(r'<' + tag + r'\s+Id="' + re.escape(id_value) + r'"\s[^>]*>', re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        alt = id_value.replace("_", ":")
        pattern = re.compile(r'<' + tag + r'\s+Id="[^"]*' + re.escape(alt) + r'[^"]*"\s[^>]*>', re.IGNORECASE)
        match = pattern.search(text)
    if not match:
        return None
    start = match.start()
    end_tag = text.find("</" + tag + ">", start)
    if end_tag == -1:
        return None
    return text[start : end_tag + len(tag) + 3]


def get_ideal_ab(ab_id: str, source: str = "ideal") -> Optional[str]:
    """
    Return the full <AB Id="..." ...>...</AB> block by AB Id. No path needed.

    ab_id: e.g. "3:1:1", "4:1:1", "0:1:1". source: "ideal" (default; only ideal*.txt have <AB>).
    Returns the block as string (including <AB> and </AB>), or None if not found.
    """
    path = get_ideal_file_path(source) if source != "ideal" else get_ideal_txt_path()
    if path is None:
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return _extract_xml_block(text, "AB", ab_id)


def get_ideal_ht(ht_id: str, source: str = "ideal_11a") -> Optional[str]:
    """
    Return the full <HT Id="...">...</HT> block for 11-crossing knots. No path needed.

    ht_id: e.g. "K11a1", "K11n1". source: "ideal_11a" (default) or "ideal_11n".
    """
    path = get_ideal_file_path(source)
    if path is None:
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return _extract_xml_block(text, "HT", ht_id)


def get_ideal_link(link_id: str, source: Optional[str] = None) -> Optional[str]:
    """
    Return the full <TL Id="...">...</TL> block for a link. No path needed.

    link_id: e.g. "L2a1", "L4a1". source: "idealLinks" (default if None), "idealLinks_10a", "idealLinks_10n", or None to try all.
    """
    if source is not None:
        path = get_ideal_file_path(source)
        if path is None:
            return None
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
        return _extract_xml_block(text, "TL", link_id)
    for src in ("idealLinks", "idealLinks_10a", "idealLinks_10n"):
        p = get_ideal_file_path(src)
        if p is None:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out = _extract_xml_block(text, "TL", link_id)
        if out is not None:
            return out
    return None


def get_ideal_12_points(knot_id: str) -> Optional[List[Tuple[float, float, float]]]:
    """
    Return the list of (x, y, z) points for a 12-crossing knot/link from ideal_12_data. No path needed.

    ideal_12_data files are plain text: one line per point, three floats per line (x y z).
    knot_id: e.g. "12a1", "12a1202", "12n73". Filename is ideal_12_data/{knot_id}.txt (12a_1202 -> 12a1202).
    """
    root = get_ideal_12_data_dir()
    if root is None:
        return None
    base = knot_id.replace("_", "").strip().lower()
    path = root / f"{base}.txt"
    if not path.is_file():
        return None
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    except OSError:
        return None
    points: List[Tuple[float, float, float]] = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 3:
            try:
                points.append((float(parts[0]), float(parts[1]), float(parts[2])))
            except ValueError:
                continue
    return points if points else None


def list_ideal_12_ids() -> List[str]:
    """List knot/link IDs available in ideal_12_data (stem of each .txt file). No path needed."""
    root = get_ideal_12_data_dir()
    if root is None:
        return []
    return sorted([p.stem for p in root.glob("*.txt")])


def list_ideal_ab_ids(crossings: Optional[int] = None) -> List[str]:
    """
    List all <AB> knot IDs from ideal.txt. No path needed.

    crossings: if set (3–10), return only IDs whose first number in Id equals this (e.g. 7 -> 7:1:1, 7:1:2, ...).
    Returns sorted list of AB Id strings (e.g. "3:1:1", "4:1:1").
    """
    path = get_ideal_txt_path()
    if path is None:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    # <AB Id="n:m:k" or Id="n:m:k"
    pattern = re.compile(r'<AB\s+Id="([^"]+)"', re.IGNORECASE)
    ids = []
    for m in pattern.finditer(text):
        ab_id = m.group(1).strip()
        if crossings is not None:
            parts = ab_id.split(":")
            if not parts or not parts[0].strip().isdigit():
                continue
            if int(parts[0]) != crossings:
                continue
        ids.append(ab_id)
    return sorted(set(ids))


def list_ideal_ht_ids(source: str = "ideal_11a") -> List[str]:
    """
    List all <HT> knot IDs from ideal_11a.txt or ideal_11n.txt (11-crossing). No path needed.

    source: "ideal_11a" or "ideal_11n".
    Returns sorted list of HT Id strings (e.g. "K11a1", "K11n1").
    """
    path = get_ideal_file_path(source)
    if path is None:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    pattern = re.compile(r'<HT\s+Id="([^"]+)"', re.IGNORECASE)
    ids = sorted(set(m.group(1).strip() for m in pattern.finditer(text)))
    return ids


def list_ideal_link_ids(
    crossings: Optional[int] = None,
    source: Optional[str] = None,
) -> List[Tuple[str, str]]:
    """
    List all <TL> link IDs from idealLinks*. No path needed.

    crossings: if set (2–10), return only links with that crossing number (from Id, e.g. L6a1 -> 6).
    source: "idealLinks", "idealLinks_10a", "idealLinks_10n", or None to search all three.
    Returns list of (link_id, source) tuples, e.g. ("L6a1", "idealLinks"), sorted by (id, source).
    """
    sources = [source] if source is not None else ["idealLinks", "idealLinks_10a", "idealLinks_10n"]
    out: List[Tuple[str, str]] = []
    seen: set = set()
    for src in sources:
        path = get_ideal_file_path(src)
        if path is None:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        pattern = re.compile(r'<TL\s+Id="([^"]+)"', re.IGNORECASE)
        for m in pattern.finditer(text):
            tl_id = m.group(1).strip()
            if crossings is not None:
                # L2a1 -> 2, L10a1 -> 10
                match = re.match(r"L(\d+)", tl_id, re.IGNORECASE)
                if not match or int(match.group(1)) != crossings:
                    continue
            key = (tl_id, src)
            if key not in seen:
                seen.add(key)
                out.append(key)
    return sorted(out)


def list_all_knot_options(crossings: int) -> List[Dict[str, Any]]:
    """
    List all knot options for a fixed crossing number, for overnight sweeps. No path needed.

    crossings: 3–12. Returns list of option dicts, each with:
      - "id": knot ID (AB Id, HT Id, or ideal_12 stem)
      - "kind": "ab" | "ht_11a" | "ht_11n" | "ideal_12"
      - "source": source name for get_ideal_ht (only for kind ht_11a/ht_11n)

    Use with get_knot_data_for_option(opt) to fetch data for each option.
    """
    if crossings < 3 or crossings > 12:
        return []
    options: List[Dict[str, Any]] = []
    if crossings <= 10:
        for ab_id in list_ideal_ab_ids(crossings):
            options.append({"id": ab_id, "kind": "ab", "source": "ideal"})
    elif crossings == 11:
        for ht_id in list_ideal_ht_ids("ideal_11a"):
            options.append({"id": ht_id, "kind": "ht_11a", "source": "ideal_11a"})
        for ht_id in list_ideal_ht_ids("ideal_11n"):
            options.append({"id": ht_id, "kind": "ht_11n", "source": "ideal_11n"})
    else:
        for knot_id in list_ideal_12_ids():
            options.append({"id": knot_id, "kind": "ideal_12", "source": "ideal_12_data"})
    return options


def list_all_link_options(crossings: int) -> List[Dict[str, Any]]:
    """
    List all link options for a fixed crossing number. No path needed.

    crossings: 2–10 (idealLinks has 2–9; 10 from idealLinks_10a / idealLinks_10n).
    Returns list of option dicts: "id", "kind": "link", "source" (idealLinks | idealLinks_10a | idealLinks_10n).
    """
    if crossings < 2 or crossings > 10:
        return []
    return [
        {"id": link_id, "kind": "link", "source": src}
        for link_id, src in list_ideal_link_ids(crossings=crossings)
    ]


def get_knot_data_for_option(opt: Dict[str, Any]) -> Optional[Any]:
    """
    Fetch knot data for one option from list_all_knot_options. No path needed.

    opt: dict with "id", "kind", and optionally "source".
    Returns: for "ab" the <AB>...</AB> string; for "ht_11a"/"ht_11n" the <HT>...</HT> string;
    for "ideal_12" the list of (x,y,z) points; for "link" the <TL>...</TL> string. None if not found.
    """
    kind = (opt.get("kind") or "").strip()
    kid = opt.get("id")
    if not kid:
        return None
    if kind == "ab":
        return get_ideal_ab(kid, source=opt.get("source") or "ideal")
    if kind in ("ht_11a", "ht_11n"):
        return get_ideal_ht(kid, source=opt.get("source") or "ideal_11a")
    if kind == "ideal_12":
        return get_ideal_12_points(kid)
    if kind == "link":
        return get_ideal_link(kid, source=opt.get("source"))
    return None
