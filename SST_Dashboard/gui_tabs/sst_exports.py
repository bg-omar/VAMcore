# sst_exports.py
# Gedeelde export-map: alle scripts die automatisch output schrijven gebruiken deze folder.
# Ideal.txt:zelfde acquisitie-logica als sst_knot_gui (katlas.org).
from pathlib import Path
from typing import Optional

# calculations/exports (boven gui_tabs)
_EXPORTS_DIR: Optional[Path] = None

# Na eerste ensure_ideal_txt() het pad naar Ideal.txt in exports
_IDEAL_TXT_PATH: Optional[Path] = None


def get_exports_dir() -> Path:
    """Return the shared exports directory (calculations/exports). Creates it if needed."""
    global _EXPORTS_DIR
    if _EXPORTS_DIR is None:
        _EXPORTS_DIR = Path(__file__).resolve().parent.parent / "exports"
        _EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return _EXPORTS_DIR


def _local_ideal_txt_sources() -> list:
    """Paden waar lokaal ideal.txt kan staan (SSTcore/resources of sstcore-package)."""
    sources = []
    try:
        import sstcore
        p = sstcore.get_ideal_txt_path()
        if p and p.exists():
            sources.append(p)
        d = sstcore.get_resources_dir()
        if d:
            for name in ("ideal.txt", "Ideal.txt"):
                q = d / name
                if q.exists() and q not in sources:
                    sources.append(q)
    except ImportError:
        pass
    base = Path(__file__).resolve().parent.parent  # SST_Dashboard
    sstcore_root = base.parent  # SSTcore
    for name in ("ideal.txt", "Ideal.txt"):
        q = sstcore_root / "resources" / name
        if q.exists() and q not in sources:
            sources.append(q)
    return sources


def ensure_ideal_txt(
    url: str = "https://katlas.org/images/d/d2/Ideal.txt.gz",
) -> Path:
    """
    Haal Ideal.txt in exports: eerst kopiëren uit lokale resources indien aanwezig,
    anders download van katlas (prepare_database).
    Returns pad naar Ideal.txt.
    """
    global _IDEAL_TXT_PATH
    if _IDEAL_TXT_PATH is not None and _IDEAL_TXT_PATH.exists():
        return _IDEAL_TXT_PATH
    d = get_exports_dir()
    txt_dest = d / "Ideal.txt"
    # Eerst: kopieer uit lokale SSTcore/resources of sstcore als dat bestand er is
    for src in _local_ideal_txt_sources():
        try:
            import shutil
            shutil.copy2(src, txt_dest)
            _IDEAL_TXT_PATH = txt_dest
            return _IDEAL_TXT_PATH
        except Exception:
            continue
    # Anders: download via prepare_database
    try:
        from gui_tabs.sst_knot_gui import prepare_database
    except ImportError:
        from sst_knot_gui import prepare_database
    gz_name = str(d / "Ideal.txt.gz")
    txt_name = str(txt_dest)
    path_str = prepare_database(url=url, gz_name=gz_name, txt_name=txt_name)
    _IDEAL_TXT_PATH = Path(path_str)
    return _IDEAL_TXT_PATH


def get_ideal_txt_path() -> Optional[Path]:
    """Pad naar Ideal.txt in exports (None als ensure_ideal_txt nog niet succesvol is uitgevoerd)."""
    if _IDEAL_TXT_PATH is not None and _IDEAL_TXT_PATH.exists():
        return _IDEAL_TXT_PATH
    return None


def load_ideal_text_cached() -> Optional[str]:
    """Zelfde cache-logica als sst_knot_gui: lees Ideal.txt uit exports (gecached)."""
    try:
        from gui_tabs.sst_knot_gui import load_ideal_text_cached as _load_cached
    except ImportError:
        from sst_knot_gui import load_ideal_text_cached as _load_cached
    path = get_ideal_txt_path()
    if path is None:
        path = ensure_ideal_txt()
    return _load_cached(str(path))
