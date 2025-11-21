import datetime
import re
import os
import glob

# ==============================================================================
# 1. THE SST CANON (MANUAL OVERRIDES & EXPANSION)
# ==============================================================================
SST_CANON = {
    # --- GRAVITY & METRIC ---
    "compute_gravity_dilation": {
        "desc": "Computes the scalar Gravity Dilation Map (G_local). Limits to 0 as induced velocity approaches swirl velocity.",
        "latex": r"G_{local} = G_0 \left[ 1 - \left( \frac{|\vec{B}| \cdot \log_{10}(\omega)}{\rho_{vac} \cdot v_{swirl}} \right)^2 \right]"
    },
    "compute_beltrami_shear": {
        "desc": "Calculates the Beltrami Shear Stress (Vacuum Tearing). Measures deviation from Force-Free state.",
        "latex": r"S = \left\| \vec{B} \times (\nabla \times \vec{B}) \right\|"
    },
    "compute_gravitational_potential": {
        "desc": "Computes the effective gravitational potential derived from the vorticity distribution.",
        "latex": r"\Phi_G(\vec{r}) = -G \int \frac{|\vec{\omega}(\vec{r}')|^2}{|\vec{r} - \vec{r}'|} d^3r'"
    },
    "compute_time_dilation_map": {
        "desc": "Computes local time dilation based on the transverse velocity of the vortex filaments.",
        "latex": r"\Delta t' = \Delta t \sqrt{1 - \frac{v_t^2}{c_{eth}^2}}"
    },

    # --- FIELDS (BIOT-SAVART) ---
    "biot_savart_velocity": {
        "desc": "Computes the induced velocity (B-field) via Biot-Savart Law.",
        "latex": r"\vec{v}(\vec{r}) = \frac{\Gamma}{4\pi} \oint_C \frac{d\vec{l} \times (\vec{r} - \vec{r}')}{|\vec{r} - \vec{r}'|^3}"
    },
    "biot_savart_velocity_grid": {
        "desc": "Vectorized Biot-Savart solver for arbitrary 3D grids.",
        "latex": r"\vec{v}_{ij k} = \sum_{seg} \text{BiotSavart}(\vec{r}_{ijk}, \vec{l}_{seg})"
    },
    "biot_savart_wire_grid": {
        "desc": "Optimized kernel for polyline-to-grid field induction.",
        "latex": r"\vec{B}(\vec{x}) = \frac{\mu_0 I}{4\pi} \sum \frac{d\vec{l} \times \hat{r}}{r^2}"
    },
    "dipole_ring_field_grid": {
        "desc": "Superposition of magnetic dipoles arranged in a ring.",
        "latex": r"\vec{B}_{total} = \sum_{i=1}^N \frac{3(\vec{m}_i \cdot \hat{r})\hat{r} - \vec{m}_i}{r^3}"
    },

    # --- FLUID DYNAMICS ---
    "compute_pressure_field": {
        "desc": "Computes the macroscopic pressure field using the Bernoulli principle for incompressible flow.",
        "latex": r"P = P_{\infty} - \frac{1}{2} \rho_{ae} |\vec{v}|^2"
    },
    "compute_bernoulli_pressure": {
        "desc": "Alias for pressure field computation.",
        "latex": r"P + \frac{1}{2}\rho v^2 = \text{const}"
    },
    "swirl_energy": {
        "desc": "Rotational kinetic energy density of the vortex system.",
        "latex": r"E_k = \frac{1}{2} \rho \int_V |\vec{\omega}|^2 \, dV"
    },
    "enstrophy": {
        "desc": "Computes Enstrophy, a measure of the dissipation potential and turbulence intensity.",
        "latex": r"\mathcal{E} = \int_V |\vec{\omega}|^2 \, dV"
    },
    "swirl_clock_rate": {
        "desc": "The local tick-rate of the fluid element, derived from the 2D curl component.",
        "latex": r"\Omega_z = \frac{1}{2} \left( \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y} \right)"
    },
    "vorticity_from_curvature": {
        "desc": "Approximates vorticity for curved laminar flow based on path radius.",
        "latex": r"|\vec{\omega}| \approx \frac{v}{R_{curve}}"
    },
    "potential_vorticity": {
        "desc": "Computes Ertel Potential Vorticity, conserved in adiabatic flow.",
        "latex": r"PV = \frac{\vec{\omega} \cdot \nabla \theta}{\rho}"
    },

    # --- TOPOLOGY & KNOTS ---
    "compute_helicity": {
        "desc": "Computes Hydrodynamic Helicity (Knottedness).",
        "latex": r"\mathcal{H} = \int_V \vec{v} \cdot \vec{\omega} \, dV"
    },
    "compute_centerline_helicity": {
        "desc": "Total helicity decomposed into Writhe and Twist.",
        "latex": r"H = Wr + Tw"
    },
    "compute_writhe": {
        "desc": "The Writhe number (Gauss integral), measuring global coiling.",
        "latex": r"Wr = \frac{1}{4\pi} \iint \frac{(\vec{r}_1-\vec{r}_2) \cdot (d\vec{r}_1 \times d\vec{r}_2)}{|\vec{r}_1-\vec{r}_2|^3}"
    },
    "compute_linking_number": {
        "desc": "Gauss Linking Number between two closed loops.",
        "latex": r"Lk = \frac{1}{4\pi} \oint_{\gamma_1} \oint_{\gamma_2} \frac{\vec{r}_{12} \cdot (d\vec{r}_1 \times d\vec{r}_2)}{r_{12}^3}"
    },
    "evaluate_fourier_series": {
        "desc": "Reconstructs knot geometry from Fourier coefficients.",
        "latex": r"\vec{r}(t) = \sum [ \vec{a}_n \cos(nt) + \vec{b}_n \sin(nt) ]"
    },

    # --- THERMODYNAMICS ---
    "potential_temperature": {
        "desc": "Temperature a fluid parcel would attain if brought adiabatically to standard pressure.",
        "latex": r"\theta = T \left( \frac{P_0}{P} \right)^{R/c_p}"
    },
    "entropy_from_theta": {
        "desc": "Calculates entropy from potential temperature.",
        "latex": r"s = c_p \ln(\theta) + \text{const}"
    }
}
# ==============================================================================
# 2. ROBUST C++ PARSER
# ==============================================================================

def clean_docstring(doc):
    """Cleans whitespace/quotes from C++ string literals."""
    doc = doc.strip()
    # Remove surrounding quotes if standard string
    if doc.startswith('"') and doc.endswith('"'):
        doc = doc[1:-1]

    lines = doc.split('\n')
    cleaned = [line.strip() for line in lines if line.strip()]
    return ' '.join(cleaned)

def extract_def_blocks(content):
    """
     robustly extracts m.def("name", ...) blocks handling nested parentheses/lambdas.
    Yields (name, body_content) tuples.
    """
    # Find start indices of all m.def
    start_pattern = re.compile(r'm\.def\s*\(')

    for match in start_pattern.finditer(content):
        start_idx = match.end()

        # Parse forward handling nested parens and strings
        balance = 1
        current_idx = start_idx
        in_string = False
        escape = False

        while current_idx < len(content) and balance > 0:
            char = content[current_idx]

            if in_string:
                if char == '\\':
                    escape = not escape
                elif char == '"' and not escape:
                    in_string = False
                else:
                    escape = False
            else:
                if char == '"':
                    in_string = True
                elif char == '(':
                    balance += 1
                elif char == ')':
                    balance -= 1

            current_idx += 1

        if balance == 0:
            # Extracted the full arguments inside m.def(...)
            full_args = content[start_idx : current_idx-1]

            # Now extract the name (first argument)
            # It should be a string literal at the start
            name_match = re.match(r'\s*"(\w+)"\s*,(.*)', full_args, re.DOTALL)
            if name_match:
                yield name_match.group(1), name_match.group(2)

def extract_docstring_from_args(body):
    """
    Analyzes the arguments of m.def to find the documentation string.
    Prioritizes R"pbdoc(...)pbdoc", then falls back to the last string literal.
    """
    # 1. Check for Raw PBDOC
    pb_match = re.search(r'R"pbdoc\s*\((.*?)\)pbdoc"', body, re.DOTALL)
    if pb_match:
        return pb_match.group(1)

    # 2. Check for Standard String at the end
    # We look for a string literal that is NOT wrapped in py::arg("...")
    # Regex: find the last string literal in the text
    str_matches = list(re.finditer(r'"([^"]*)"', body))

    if str_matches:
        last_match = str_matches[-1]
        doc = last_match.group(1)
        start_pos = last_match.start()

        # Context check: Is this string preceded immediately by 'py::arg(' ?
        # We check the 20 chars before the string
        preceding_text = body[max(0, start_pos-20):start_pos]
        # Remove whitespace to check simple pattern
        preceding_clean = re.sub(r'\s+', '', preceding_text)

        if "py::arg(" in preceding_clean:
            return "See Description (Arg Name Detected)"

        return doc

    return "See Description"

def auto_latex(text_math):
    """Heuristic to convert C++ plain-text math into LaTeX."""
    l = text_math
    l = l.replace("rho_ae", r"\rho_{ae}")
    l = l.replace("rho", r"\rho")
    l = l.replace("omega", r"\omega")
    l = l.replace("mu0", r"\mu_0")
    l = l.replace("pi", r"\pi")
    l = l.replace("zeta_r", r"\zeta_r")
    l = l.replace("P_infinity", r"P_{\infty}")
    l = l.replace(" * ", " ")
    l = l.replace("0.5", r"\frac{1}{2}")
    l = l.replace("0.25", r"\frac{1}{4}")
    l = re.sub(r'\b([vwBg])\b', r'\\vec{\1}', l)
    l = l.replace("dv/dx", r"\frac{\partial v}{\partial x}")
    l = l.replace("du/dy", r"\frac{\partial u}{\partial y}")
    return l

def scan_bindings(src_dir="src_bindings"):
    found_funcs = {}
    cpp_files = glob.glob(os.path.join(src_dir, "*.cpp"))
    print(f"Scanning {len(cpp_files)} C++ binding files in '{src_dir}'...")

    for fpath in cpp_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

            for fname, body in extract_def_blocks(content):
                raw_doc = extract_docstring_from_args(body)
                desc = clean_docstring(raw_doc)

                # Heuristic for LaTeX extraction
                parts = desc.split(':')
                if len(parts) > 1:
                    desc_text = parts[0].strip()
                    math_txt = parts[1].strip()
                    latex = auto_latex(math_txt)
                else:
                    desc_text = desc
                    latex = auto_latex(desc) # Try to latex-ify the whole description

                found_funcs[fname] = {
                    "desc": desc_text,
                    "latex": latex,
                    "source": os.path.basename(fpath)
                }

    return found_funcs

# ==============================================================================
# 3. DOCUMENT GENERATOR
# ==============================================================================

def generate_markdown(filename="00-SST_Library_Reference.md"):
    auto_data = scan_bindings()
    final_registry = {}

    for fname, data in auto_data.items():
        final_registry[fname] = data

    for fname, data in SST_CANON.items():
        if fname in final_registry:
            final_registry[fname].update(data)
            final_registry[fname]['is_canon'] = True
        else:
            final_registry[fname] = data
            final_registry[fname]['is_canon'] = True
            final_registry[fname]['source'] = "SST Canon"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Swirl String Theory (SST) Core Library Reference\n")
        f.write(f"**Version:** 2.1.0 (Parser Upgrade) | **Generated:** {datetime.date.today()}\n\n")
        f.write("This document is **automatically compiled** from the C++ Source Code (`src_bindings/`).\n")
        f.write("It supports both `R\"pbdoc` and Standard String documentation.\n\n")

        f.write("---\n\n")

        def write_func(name, meta):
            f.write(f"### `{name}`\n")
            source = meta.get('source', 'Unknown')
            canon_badge = "✅ **[SST Canon]**" if meta.get('is_canon') else f"🛠️ *[Auto-Extracted from {source}]*"
            f.write(f"{canon_badge}\n\n")
            f.write(f"**Description:** {meta['desc']}\n\n")
            f.write(f"**Equation:**\n")
            f.write(f"$$\n{meta['latex']}\n$$\n\n")
            # NEW: Add diagrams for specific complex concepts
            if "knot" in name or "writhe" in name or "helicity" in name:
                f.write("![Topology Diagram](topology_concept.png)\n\n")
            f.write("---\n")

        sorted_names = sorted(final_registry.keys())

        f.write("## 1. SST Gravity & Metric Engineering\n\n")
        for name in sorted_names:
            if any(x in name for x in ['Gravity', 'dilation', 'shear', 'potential']) and 'flow' not in name:
                write_func(name, final_registry[name])

        f.write("## 2. Fluid Dynamics & Vortex Solvers\n\n")
        for name in sorted_names:
            if any(x in name for x in ['pressure', 'velocity', 'vorticity', 'fluid', 'swirl', 'biot']) and 'Gravity' not in name:
                write_func(name, final_registry[name])

        f.write("## 3. Topological Metrics\n\n")
        for name in sorted_names:
            if any(x in name for x in ['helicity', 'writhe', 'linking', 'knot', 'fourier']):
                write_func(name, final_registry[name])

    print(f"Successfully compiled {len(final_registry)} functions into {filename}")

if __name__ == "__main__":
    if not os.path.exists("src_bindings"):
        print("WARNING: 'src_bindings' folder not found. Running in Canon-Only mode.")
        scan_bindings = lambda: {}
    generate_markdown()