import importlib.util
import sys
import os
import inspect
# ✅ Get the script filename dynamically
import sys
import os
import inspect


# Set path if needed
sys.path.insert(0, os.path.abspath("."))
# ✅ Get the script filename dynamically
import os
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Load the module dynamically from the compiled path
module_path = os.path.abspath("swirl_string_core.cp312-win_amd64.pyd")
module_name = "swirl_string_core"

import swirl_string_core



# Generate Markdown documentation
lines = ["# SST Python Bindings (Auto-Generated API)\n"]

for name in dir(swirl_string_core):
    if name.startswith("__"):
        continue
    obj = getattr(swirl_string_core, name)
    if inspect.isclass(obj):
        lines.append(f"## Class: `{name}`\n")
        doc = inspect.getdoc(obj)
        if doc:
            lines.append(f"{doc}\n")
        for method_name in dir(obj):
            if method_name.startswith("_"):
                continue
            method = getattr(obj, method_name)
            if inspect.isfunction(method) or inspect.ismethod(method):
                lines.append(f"### Method: `{method_name}`\n")
                method_doc = inspect.getdoc(method)
                if method_doc:
                    lines.append(f"{method_doc}\n")
    elif inspect.isfunction(obj):
        lines.append(f"## Function: `{name}`\n")
        doc = inspect.getdoc(obj)
        if doc:
            lines.append(f"{doc}\n")

markdown_doc = "\n".join(lines)

# Save to file and return path
output_path = "../sstcore_api.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(markdown_doc)

print(output_path)