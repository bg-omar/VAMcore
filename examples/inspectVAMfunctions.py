import sys
import os
import inspect


# Set path if needed
sys.path.insert(0, os.path.abspath("."))

import vambindings

print("=== Functions ===")
for name in dir(vambindings):
    attr = getattr(vambindings, name)
    if inspect.isfunction(attr):
        print(name)

print("=== Available Attributes in vambindings ===")
for attr in dir(vambindings):
    if not attr.startswith("__"):
        print(attr)

print("\n=== Help Summary ===")
help(vambindings)

