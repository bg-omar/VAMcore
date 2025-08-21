import sys
import os
import inspect


# Set path if needed
sys.path.insert(0, os.path.abspath("."))
# ✅ Get the script filename dynamically
import os
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Load the module dynamically from the compiled path
module_path = os.path.abspath("vambindings.cp312-win_amd64.pyd")
module_name = "vambindings"

import vambindings

print(vambindings.list_bindings())



print("=== Functions ===")
for name in dir(vambindings):
    attr = getattr(vambindings, name)
    if inspect.isfunction(attr):
        print(name)

print("=== Available Attributes in vambindings ===")
for attr in dir(vambindings):
    if not attr.startswith("__"):
        print(attr)

# print("\n=== Help Summary ===")
# help(vambindings)

