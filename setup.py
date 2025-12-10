# setup.py for Swirl_String_core pip package
from setuptools import setup, Extension, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
import os
import glob
import subprocess
import tempfile
import shutil

__version__ = "0.1.3"

# Custom build_ext to generate embedded files during build
class CustomBuildExt(build_ext):
    def build_extensions(self):
        # Generate embedded files before building extensions
        header_file, source_file = generate_embedded_knot_files()
        
        if source_file and os.path.exists(source_file) and header_file and os.path.exists(header_file):
            # Get absolute paths
            header_dir = os.path.dirname(os.path.abspath(header_file))
            abs_source = os.path.abspath(source_file)
            
            # Update include dirs and sources for all extensions
            for ext in self.extensions:
                # Header is now in src/, which is already in include_dirs, so no need to add
                # But verify src is in include_dirs
                base_dir = os.path.dirname(os.path.abspath(__file__))
                src_dir = os.path.join(base_dir, "src")
                ext_include_dirs = [os.path.abspath(d) for d in ext.include_dirs]
                if os.path.abspath(src_dir) not in ext_include_dirs:
                    ext.include_dirs.insert(0, src_dir)
                    print(f"Ensured src directory in includes: {src_dir}")
                
                # Add source file - use relative path for build system
                base_dir = os.path.dirname(os.path.abspath(__file__))
                rel_source = os.path.relpath(abs_source, base_dir)
                ext_sources = [os.path.abspath(s) if os.path.isabs(s) else os.path.abspath(os.path.join(base_dir, s)) for s in ext.sources]
                if abs_source not in ext_sources:
                    ext.sources.append(rel_source)
                    print(f"Added source file: {rel_source}")
        else:
            print("Warning: Embedded knot files not generated, building without embedded knots")
        
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

def generate_embedded_knot_files():
    """Generate embedded knot files C++ source during build."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    knot_fseries_dir = os.path.join(base_dir, "src", "knot_fseries")
    if not os.path.exists(knot_fseries_dir):
        return None, None
    
    # Put generated files in build/temp for source, but header in src for easier inclusion
    build_temp = os.path.join(base_dir, "build", "temp")
    os.makedirs(build_temp, exist_ok=True)
    
    # Put header in src directory so it's found by relative includes
    src_dir = os.path.join(base_dir, "src")
    header_file = os.path.join(src_dir, "knot_files_embedded.h")
    source_file = os.path.join(build_temp, "knot_files_embedded.cpp")
    
    # Find all .fseries files
    fseries_files = glob.glob(os.path.join(knot_fseries_dir, "*.fseries"))
    
    # Generate header file
    with open(header_file, 'w') as f:
        f.write("// Auto-generated header - do not edit manually\n")
        f.write("#ifndef KNOT_FILES_EMBEDDED_H\n")
        f.write("#define KNOT_FILES_EMBEDDED_H\n\n")
        f.write("#include <map>\n")
        f.write("#include <string>\n\n")
        f.write("namespace sst {\n")
        f.write("    std::map<std::string, std::string> get_embedded_knot_files();\n")
        f.write("}\n\n")
        f.write("#endif // KNOT_FILES_EMBEDDED_H\n")
    
    # Generate source file
    with open(source_file, 'w') as f:
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
        f.write("} // namespace sst\n")
    
    print(f"Generated embedded knot files: {len(fseries_files)} .fseries files embedded")
    return header_file, source_file

# Generate embedded files before building
header_file, source_file = generate_embedded_knot_files()

# Get all source files
src_files = [
    "src/biot_savart.cpp",
    "src/fluid_dynamics.cpp",
    "src/field_kernels.cpp",
    "src/frenet_helicity.cpp",
    "src/potential_timefield.cpp",
    "src/hyperbolic_volume.cpp",
    "src/knot_dynamics.cpp",
    "src/radiation_flow.cpp",
    "src/swirl_field.cpp",
    "src/thermo_dynamics.cpp",
    "src/time_evolution.cpp",
    "src/vortex_ring.cpp",
    "src/vorticity_dynamics.cpp",
    "src/sst_gravity.cpp",
]

# Generated embedded files will be added by CustomBuildExt during build
# Don't add here to avoid path issues during sdist

# Get all binding files
binding_files = glob.glob("src_bindings/py_*.cpp")

# Include directories
# For sdist builds, paths are relative to the extracted source directory
# The generated header directory will be added by CustomBuildExt
include_dirs = ["src", pybind11.get_include()]

# C++ standard - use 20 for better compatibility across platforms
# C++23 is not fully supported on all compilers (especially older GCC versions)
import sys
cxx_std = 20  # Use C++20 for maximum compatibility

# Main module: swirl_string_core
ext_modules = [
    Pybind11Extension(
        "swirl_string_core",
        sources=["src_bindings/module_sst.cpp"] + binding_files + src_files,
        include_dirs=include_dirs,
        cxx_std=cxx_std,
        define_macros=[('VERSION_INFO', __version__), ('KNOT_FILES_EMBEDDED_H', '1')],
        language='c++',
    ),
    # Backwards compatibility module
    Pybind11Extension(
        "sstbindings",
        sources=["src_bindings/module_sstbindings.cpp"] + binding_files + src_files,
        include_dirs=include_dirs,
        cxx_std=cxx_std,
        define_macros=[('VERSION_INFO', __version__), ('KNOT_FILES_EMBEDDED_H', '1')],
        language='c++',
    ),
]

# Get all .fseries files for package data (for fallback access)
fseries_files = []
for root, dirs, files in os.walk("src/knot_fseries"):
    for file in files:
        if file.endswith(('.fseries', '.short')):
            fseries_files.append(os.path.join(root, file))

# Read long description
long_description = ""
if os.path.exists("Readme.md"):
    with open("Readme.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="swirl-string-core",
    version=__version__,
    author="Omar Iskandarani",
    author_email="info@omariskandarani.com",
    description="Swirl String Theory Canonical Core - High-performance C++ library for knot dynamics, vortex systems, and fluid mechanics",
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
    cmdclass={"build_ext": CustomBuildExt},
    zip_safe=False,
    python_requires=">=3.7",
    packages=find_packages(),
    include_package_data=True,
    # Data files installed to share/swirl_string_core/knot_fseries/ for CMake compatibility
    # Also accessible via package_data for pip install
    data_files=[
        ('share/swirl_string_core/knot_fseries', fseries_files),
    ] if fseries_files else [],
    # Package data for pip installs (accessible via importlib.resources)
    package_data={
        '': ['src/knot_fseries/**/*.fseries', 'src/knot_fseries/**/*.short'],
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Operating System :: OS Independent",
    ],
    keywords="physics, fluid-dynamics, knot-theory, vortex, computational-physics, cpp",
)