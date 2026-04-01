import re
from importlib.metadata import version, PackageNotFoundError

input_path = "requirements.txt"
output_path = "requirements_clean.txt"

pkg_name_pattern = re.compile(
    r"""
    ^\s*
    (?:-e\s+)?           # optional -e
    (?:
        git\+[^#]+#egg=  # git+...#egg=
        |
        [^@=\s]+@        # name@file:// etc.
        |
    )
    (?P<name>[A-Za-z0-9_.\-]+)
    """,
    re.VERBOSE,
)

names = []

with open(input_path, "r", encoding="utf-8") as f:
    for line in f:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if "==" in stripped and not (" @ " in stripped or stripped.startswith("-e ")):
            # Already name==version, keep name part
            names.append(stripped.split("==", 1)[0])
            continue

        m = pkg_name_pattern.match(stripped)
        if m:
            names.append(m.group("name"))

names = sorted(set(names))

with open(output_path, "w", encoding="utf-8") as out:
    for name in names:
        try:
            ver = version(name)
            out.write(f"{name}=={ver}\n")
        except PackageNotFoundError:
            print(f"WARNING: {name} not found in current environment; skipping")