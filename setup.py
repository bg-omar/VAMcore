# setup.py
from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import os

__version__ = "0.1.0"

ext_modules = [
    Pybind11Extension(
        "sstcore",
        [
            "src_bindings/py_sst_gravity.cpp",
            # "src_bindings/main.cpp" # Uncomment if entry point is separate
        ],
        include_dirs=["src"],
        cxx_std=17,
        # Define macros if needed for SST Canon versions
        define_macros = [('VERSION_INFO', __version__)],
    ),
]

setup(
    name="sstcore",
    version=__version__,
    author="SST Architect",
    description="Swirl String Theory Canonical Core",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
)