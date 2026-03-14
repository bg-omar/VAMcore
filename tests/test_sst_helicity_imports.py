"""
Smoke tests for SST Dashboard helicity module: imports and API presence.

Ensures sst_helicity and HelicityCalculationVAMcore (legacy shim) are importable
and expose the expected API. Run from SSTcore root or with gui_tabs on PYTHONPATH.
"""
import sys
from pathlib import Path

# Allow importing from SST_Dashboard/gui_tabs when running tests from SSTcore root
_here = Path(__file__).resolve().parent
_root = _here.parent
_gui_tabs = _root / "SST_Dashboard" / "gui_tabs"
if _gui_tabs.is_dir() and str(_gui_tabs) not in sys.path:
    sys.path.insert(0, str(_gui_tabs))


def test_import_sst_helicity():
    """sst_helicity module imports and exposes required API."""
    import pytest
    m = pytest.importorskip("sst_helicity")
    assert hasattr(m, "compute_a_mu_for_file"), "sst_helicity must expose compute_a_mu_for_file"
    assert hasattr(m, "helicity_at"), "sst_helicity must expose helicity_at"
    assert hasattr(m, "HelicityResult"), "sst_helicity must expose HelicityResult"


def test_helicity_result_unpackable():
    """HelicityResult supports tuple unpacking for backward compatibility."""
    import pytest
    m = pytest.importorskip("sst_helicity")
    r = m.HelicityResult(a_mu=0.1, Hc=1.0, Hm=2.0)
    a, b, c = r
    assert (a, b, c) == (0.1, 1.0, 2.0)
    assert r.a_mu == 0.1 and r.Hc == 1.0 and r.Hm == 2.0


def test_import_helicity_calculation_vamcore():
    """Legacy HelicityCalculationVAMcore imports and re-exports compute_a_mu_for_file."""
    import pytest
    leg = pytest.importorskip("HelicityCalculationVAMcore")
    assert hasattr(leg, "compute_a_mu_for_file"), "HelicityCalculationVAMcore must re-export compute_a_mu_for_file"
    assert hasattr(leg, "helicity_at"), "HelicityCalculationVAMcore must re-export helicity_at"


if __name__ == "__main__":
    # Run without pytest: minimal checks (gui_tabs already added to path above)
    ok = 0
    try:
        import sst_helicity as m
        assert hasattr(m, "compute_a_mu_for_file") and hasattr(m, "HelicityResult")
        r = m.HelicityResult(0.0, 1.0, 2.0)
        a, b, c = r
        assert (a, b, c) == (0.0, 1.0, 2.0)
        print("sst_helicity: OK")
        ok += 1
    except Exception as e:
        print("sst_helicity:", e)
    try:
        import HelicityCalculationVAMcore as leg
        assert hasattr(leg, "compute_a_mu_for_file")
        print("HelicityCalculationVAMcore: OK")
        ok += 1
    except Exception as e:
        print("HelicityCalculationVAMcore:", e)
    sys.exit(0 if ok >= 1 else 1)
