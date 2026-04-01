# Backward compatibility: re-export sstcore (or sstbindings) so that
# "import swirl_string_core" and "from swirl_string_core import ..." work.
# Prefer "import sstcore" or "import SSTcore" for new code.

try:
    import sstcore as _native
    from sstcore import *
    __all__ = getattr(_native, "__all__", None)
except ImportError:
    import sstbindings as _native
    from sstbindings import *
    __all__ = getattr(_native, "__all__", None)
