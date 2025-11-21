import sys
import os
import inspect


# Set path if needed
sys.path.insert(0, os.path.abspath("."))
# ✅ Get the script filename dynamically
import os
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Load the module dynamically from the compiled path
module_path = os.path.abspath("sstbindings.cp311-win_amd64.pyd")
module_name = "sstcore"

import sstbindings

print(sstbindings.list_bindings())



print("=== Functions ===")
for name in dir(sstbindings):
    attr = getattr(sstbindings, name)
    if inspect.isfunction(attr):
        print(name)

print("=== Available Attributes in sstcore ===")
for attr in dir(sstbindings):
    if not attr.startswith("__"):
        print(attr)

# print("\n=== Help Summary ===")
# help(sstcore)