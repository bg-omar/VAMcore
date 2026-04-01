
# SSTCORE Installation Guide (Windows)

These precompiled `sstbindings.cp311-win_amd64.pyd` and `sstbindings.cp312-win_amd64.pyd` files are pybind11 modules
compiled for Python 3.11 and 3.12 on 64-bit Windows.

## ✅ Installation Steps

1. Determine your Python version:
   ```bash
   python --version
   ```

2. Copy the matching `.pyd` file into your Python project directory.
   Example:
   ```
   your_project/
   ├── sstbindings.cp311-win_amd64.pyd
   └── your_script.py
   ```

3. In your script:
   ```python
   import sstbindings
   ```

4. Use the exposed functions/classes such as:
   ```python
   vortex = sstbindings.VortexKnotSystem()
   vortex.initialize_trefoil_knot()
   ```

If you encounter an ImportError:
- Make sure the `.pyd` file matches your Python version and architecture (64-bit)
- Recompile using CMake and pybind11 if necessary for other OS

-- Swirl_String_core Team