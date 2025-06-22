import importlib.util
import sys
import os
import inspect
# ✅ Get the script filename dynamically
import os
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Load the module dynamically from the compiled path
module_path = os.path.abspath("../build/Debug/vambindings.cp311-win_amd64.pyd")
module_name = "vambindings"

spec = importlib.util.spec_from_file_location(module_name, module_path)
vambindings = importlib.util.module_from_spec(spec)
sys.modules[module_name] = vambindings
spec.loader.exec_module(vambindings)

# Generate Markdown documentation
lines = ["# VAM Python Bindings (Auto-Generated API)\n"]

for name in dir(vambindings):
    if name.startswith("__"):
        continue
    obj = getattr(vambindings, name)
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
output_path = "../vambindings_api.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(markdown_doc)

print(output_path)
