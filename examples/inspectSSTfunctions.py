import sys
import os
import inspect
from pathlib import Path

# Set path if needed
sys.path.insert(0, os.path.abspath("."))
# ✅ Get the script filename dynamically
import os
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Load the module dynamically from the compiled path
_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))
_parent = _script_dir.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

try:
    import sstcore
except ImportError:
    try:
        import swirl_string_core as sstcore  # backward compatibility
    except ImportError:
        import sstbindings as sstcore


print(sstcore.list_bindings())



print("=== Functions ===")
for name in dir(sstcore):
    attr = getattr(sstcore, name)
    if inspect.isfunction(attr):
        print(name)

print("=== Available Attributes in sstcore ===")
for attr in dir(sstcore):
    if not attr.startswith("__"):
        print(attr)

# print("\n=== Help Summary ===")
# help(sstcore)