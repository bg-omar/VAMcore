# setup.py for SSTcore pip package
from setuptools import setup, Extension, find_packages
from setuptools.command.build import build
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
import os
import glob
import subprocess
import tempfile
import shutil
import sys

__version__ = "0.2.1"
base_dir = os.path.dirname(os.path.abspath(__file__))


def _relative_path(path, base=base_dir):
    """Return path relative to base with forward slashes (setuptools data_files requirement). Never returns absolute paths."""
    p = os.path.normpath(os.path.abspath(path))
    b = os.path.normpath(os.path.abspath(base))
    try:
        rel = os.path.relpath(p, b)
    except ValueError:
        return None
    if os.path.isabs(rel):
        return None
    return rel.replace(os.sep, "/")

# Custom build_ext to generate embedded files during build
class CustomBuildExt(build_ext):
    def build_extensions(self):
        # Generate embedded files before building extensions (always generates at least stub)
        header_file, source_file = generate_embedded_knot_files()
        if not source_file or not os.path.exists(source_file):
            raise RuntimeError("generate_embedded_knot_files() did not produce source file")
        abs_source = os.path.abspath(source_file)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(base_dir, "src")
        rel_source = os.path.relpath(abs_source, base_dir)

        for ext in self.extensions:
            ext_include_dirs = [os.path.abspath(d) for d in ext.include_dirs]
            if os.path.abspath(src_dir) not in ext_include_dirs:
                ext.include_dirs.insert(0, src_dir)
            ext_sources = [os.path.abspath(s) if os.path.isabs(s) else os.path.abspath(os.path.join(base_dir, s)) for s in ext.sources]
            if abs_source not in ext_sources:
                ext.sources.append(rel_source)
        
        # Add compiler-specific flags for better compatibility (apply to all extensions)
        for ext in self.extensions:
            if sys.platform != "win32":
                # Linux/Unix: Use GCC/Clang flags
                if not hasattr(ext, 'extra_compile_args') or ext.extra_compile_args is None:
                    ext.extra_compile_args = []
                # Add flags if not already present
                if '-std=c++20' not in ext.extra_compile_args:
                    ext.extra_compile_args.extend(['-std=c++20', '-O3', '-fPIC'])
                # Suppress some warnings that might cause issues
                if '-Wno-deprecated-declarations' not in ext.extra_compile_args:
                    ext.extra_compile_args.append('-Wno-deprecated-declarations')
        
        # Now build extensions
        super().build_extensions()

# Custom build command to also build npm package
class CustomBuild(build):
    """Custom build command that also builds the npm package."""
    
    def run(self):
        # First, run the standard build
        super().run()
        
        # Then build npm package
        self.build_npm_package()
    
    def build_npm_package(self):
        """Build the npm package (Node.js native addon)."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        package_json = os.path.join(base_dir, "package.json")
        
        # Check if package.json exists
        if not os.path.exists(package_json):
            print("Warning: package.json not found, skipping npm build")
            return
        
        # Check if Node.js is available
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print("Warning: Node.js not available, skipping npm build")
                return
            print(f"Found Node.js: {result.stdout.strip()}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("Warning: Node.js not found, skipping npm build")
            return
        
        # Check if npm is available
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print("Warning: npm not available, skipping npm build")
                return
            print(f"Found npm: {result.stdout.strip()}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("Warning: npm not found, skipping npm build")
            return
        
        print("\n" + "="*60)
        print("Building npm package (Node.js native addon)...")
        print("="*60)
        
        # Install npm dependencies
        try:
            print("\n[1/3] Installing npm dependencies...")
            result = subprocess.run(
                ["npm", "install"],
                cwd=base_dir,
                check=False,
                capture_output=False
            )
            if result.returncode != 0:
                print("Warning: npm install failed, continuing anyway...")
        except Exception as e:
            print(f"Warning: npm install failed: {e}")
        
        # Generate embedded knot files for Node.js build (if not already done)
        try:
            print("\n[2/3] Generating embedded knot files for Node.js...")
            build_node_dir = os.path.join(base_dir, "build_node")
            generated_dir = os.path.join(build_node_dir, "generated")
            os.makedirs(generated_dir, exist_ok=True)
            
            # Run CMake to generate embedded files
            result = subprocess.run(
                ["cmake", "-B", "build_node", "-S", "."],
                cwd=base_dir,
                check=False,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ Embedded knot files generated")
            else:
                print("Warning: CMake configuration failed (this is okay if CMake is not available)")
        except Exception as e:
            print(f"Warning: Failed to generate embedded files: {e}")
        
        # Build Node.js native addon
        try:
            print("\n[3/3] Building Node.js native addon...")
            result = subprocess.run(
                ["npm", "run", "build:node"],
                cwd=base_dir,
                check=False,
                capture_output=False
            )
            if result.returncode == 0:
                print("✓ Node.js native addon built successfully")
            else:
                print("Warning: Node.js native addon build failed (this is okay, package will use WASM fallback)")
        except Exception as e:
            print(f"Warning: Failed to build Node.js addon: {e}")
        
        print("\n" + "="*60)
        print("npm package build completed")
        print("="*60 + "\n")

def generate_embedded_knot_files():
    """Generate embedded knot files C++ source during build. Always writes header and
    source so the linker has sst::get_embedded_knot_files(); uses empty map if no
    .fseries files are present."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, "src")
    build_temp = os.path.join(base_dir, "build", "temp")
    os.makedirs(build_temp, exist_ok=True)
    os.makedirs(src_dir, exist_ok=True)

    header_file = os.path.join(src_dir, "knot_files_embedded.h")
    source_file = os.path.join(build_temp, "knot_files_embedded.cpp")

    knot_fseries_dir = os.path.join(base_dir, "resources", "knot_fseries")
    fseries_files = (
        glob.glob(os.path.join(knot_fseries_dir, "*.fseries"))
        if os.path.exists(knot_fseries_dir)
        else []
    )
    
    # Generate header file (must match knot_dynamics.h: get_embedded_knot_files + get_embedded_ideal_files)
    with open(header_file, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated header - do not edit manually\n")
        f.write("#ifndef KNOT_FILES_EMBEDDED_H\n")
        f.write("#define KNOT_FILES_EMBEDDED_H\n\n")
        f.write("#include <map>\n")
        f.write("#include <string>\n\n")
        f.write("namespace sst {\n")
        f.write("    std::map<std::string, std::string> get_embedded_knot_files();\n")
        f.write("    std::map<std::string, std::string> get_embedded_ideal_files();\n")
        f.write("}\n\n")
        f.write("#endif // KNOT_FILES_EMBEDDED_H\n")
    
    # Generate source file (utf-8: .fseries files may contain Unicode e.g. Greek Σ)
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated file - do not edit manually\n")
        f.write("// This file contains embedded .fseries knot data\n\n")
        f.write('#include "knot_files_embedded.h"\n')
        f.write("#include <map>\n")
        f.write("#include <string>\n\n")
        f.write("namespace sst {\n\n")
        f.write("std::map<std::string, std::string> get_embedded_knot_files() {\n")
        f.write("    std::map<std::string, std::string> files;\n\n")
        
        for fseries_file in fseries_files:
            filename = os.path.basename(fseries_file)
            # Extract knot ID (e.g., "3_1" from "knot.3_1.fseries")
            if filename.startswith("knot."):
                knot_id = filename[5:].split(".")[0]
            else:
                knot_id = filename.replace(".fseries", "")
            
            # Read file content
            with open(fseries_file, 'r', encoding='utf-8') as kf:
                file_content = kf.read()
            
            # Use raw string literal with custom delimiter
            delim = "KNOT_FILE_DELIM"
            # Escape any occurrences of the delimiter in content (unlikely but safe)
            file_content_escaped = file_content.replace(f"){delim}\"", f"){delim}\\\"")
            
            f.write(f'    files["{knot_id}"] = R"{delim}({file_content_escaped}){delim}";\n')
        
        f.write("\n    return files;\n")
        f.write("}\n\n")
        f.write("std::map<std::string, std::string> get_embedded_ideal_files() {\n")
        f.write("    std::map<std::string, std::string> files;\n")
        f.write("    return files;\n")
        f.write("}\n\n")
        f.write("} // namespace sst\n")
    
    print(f"Generated embedded knot files: {len(fseries_files)} .fseries files embedded")
    return header_file, source_file

# Generate embedded files before building
header_file, source_file = generate_embedded_knot_files()

# Get all source files (must match CMakeLists sstcore_lib)
src_files = [
    "src/ab_initio_mass.cpp",
    "src/biot_savart.cpp",
    "src/fluid_dynamics.cpp",
    "src/field_kernels.cpp",
    "src/frenet_helicity.cpp",
    "src/potential_timefield.cpp",
    "src/magnus_integrator.cpp",
    "src/hyperbolic_volume.cpp",
    "src/knot_dynamics.cpp",
    "src/radiation_flow.cpp",
    "src/swirl_field.cpp",
    "src/thermo_dynamics.cpp",
    "src/time_evolution.cpp",
    "src/vortex_ring.cpp",
    "src/vorticity_dynamics.cpp",
    "src/sst_gravity.cpp",
    "src/sst_extensions.cpp",
    "src/sst_integrator.cpp",
]

# Generated embedded files will be added by CustomBuildExt during build
# Don't add here to avoid path issues during sdist

# Get all binding files
binding_files = glob.glob("src/*_py.cpp")

# Include directories
# For sdist builds, paths are relative to the extracted source directory
# The generated header directory will be added by CustomBuildExt
include_dirs = ["src", pybind11.get_include()]

# C++ standard - use 20 for better compatibility across platforms
# C++23 is not fully supported on all compilers (especially older GCC versions)
import sys
cxx_std = 20  # Use C++20 for maximum compatibility

# Main module: sstcore
ext_modules = [
    Pybind11Extension(
        "sstcore",
        sources=["src/module_sst.cpp"] + binding_files + src_files,
        include_dirs=include_dirs,
        cxx_std=cxx_std,
        define_macros=[('VERSION_INFO', __version__), ('KNOT_FILES_EMBEDDED_H', '1')],
        language='c++',
    ),
    # Backwards compatibility module
    Pybind11Extension(
        "sstbindings",
        sources=["src/module_sstbindings.cpp"] + binding_files + src_files,
        include_dirs=include_dirs,
        cxx_std=cxx_std,
        define_macros=[('VERSION_INFO', __version__), ('KNOT_FILES_EMBEDDED_H', '1')],
        language='c++',
    ),
]

# Get all .fseries files for package data (for fallback access)
# Use relative paths with / so setuptools never sees absolute paths
fseries_files = []
for root, dirs, files in os.walk("resources/knot_fseries"):
    for file in files:
        if file.endswith(('.fseries', '.short')):
            full = os.path.join(base_dir, root, file)
            rel = _relative_path(full)
            if rel:
                fseries_files.append(rel)

# Do not install resources/ via data_files: on Windows, setuptools/wheel rejects
# data_files when it resolves paths (raises "setup script specifies an absolute path").
# Keep resource_data_files empty so the wheel builds. Use the project's resources/
# directory at runtime if needed (e.g. via path relative to package or env).
resource_data_files = []

# Read long description
long_description = ""
if os.path.exists("Readme.md"):
    with open("Readme.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="sstcore",
    version=__version__,
    author="Omar Iskandarani",
    author_email="info@omariskandarani.com",
    description="SSTcore - Swirl String Theory Canonical Core. High-performance C++ library for knot dynamics, vortex systems, and fluid mechanics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="CC BY-NC 4.0",
    url="https://github.com/Swirl-String-Theory/SSTcore",
    project_urls={
        "Bug Tracker": "https://github.com/Swirl-String-Theory/SSTcore/issues",
        "Documentation": "https://github.com/Swirl-String-Theory/SSTcore#readme",
        "Source Code": "https://github.com/Swirl-String-Theory/SSTcore",
    },
    ext_modules=ext_modules,
    cmdclass={
        "build": CustomBuild,
        "build_ext": CustomBuildExt
    },
    zip_safe=False,
    python_requires=">=3.9",
    packages=find_packages() + ["SSTcore"],
    package_dir={"SSTcore": "."},
    py_modules=["swirl_string_core"],  # backward compat: import swirl_string_core -> same as sstcore
    include_package_data=True,
    # Data files installed to share/sstcore/knot_fseries/ for CMake compatibility
    # Also accessible via package_data for pip install
    data_files=(
        ([('share/sstcore/knot_fseries', fseries_files)] if fseries_files else [])
        + resource_data_files
    ),
    # Package data for pip installs (accessible via importlib.resources)
    package_data={
        '': [
            'resources/knot_fseries/**/*.fseries',
            'resources/knot_fseries/**/*.short',
            'resources/Knots_FourierSeries/**/*.fseries',
            'resources/Knots_FourierSeries/**/*.short',
            'resources/ideal.txt',
            'resources/ideal_11a.txt',
            'resources/ideal_11n.txt',
            'resources/idealLinks.txt',
            'resources/idealLinks_10a.txt',
            'resources/idealLinks_10n.txt',
        ],
    },
    install_requires=[
        "pybind11>=2.6.0",
        "numpy>=1.19.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: Other/Proprietary License",  # CC BY-NC 4.0 (non-commercial)
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Operating System :: OS Independent",
    ],
    keywords="physics, fluid-dynamics, knot-theory, vortex, computational-physics, cpp",
)