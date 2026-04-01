# ⚙️ SSTcore: Hybrid Benchmark Engine for the Swirl-String Theory

Welcome to **SSTcore**, the computational backbone for the Swirl-String Theory (SST).  
This hybrid C++/Python engine is designed to benchmark field-based gravity, time dilation, and EM swirl-field dynamics using modern numerical methods and a large helping of theoretical audacity. This repository contains the core engine, simulation scripts, and visualizations to explore the swirling depths of æther dynamics.
We build the C++ SST-Bindings first, and then we can import it into benchmark Python code. When using the C++  SST-bindings to do hard calculations we can run / render Python simulations 10-100x faster.

---

## 💾 Features

- 🚀 **High-Performance Core (C++)**  
  Handles numerically stiff vortex dynamics, EM field evolution, and topological energy exchanges.

- 🐍 **Python Frontend**  
  For visualization, parameter sweeps, and interactive experiments using `matplotlib`, `numpy`, and `PyBind11` integration.

- 📦 **npm Package**  
  Available for Node.js and browser (WebAssembly) via `npm install sstcore`. Perfect for Angular and other JavaScript/TypeScript applications.

- 🧲 **EM Field Simulations**  
  Supports generation and animation of **rotating 3-phase bivort** electric and magnetic field structures.

- ⌛ **Time Dilation & Gravity Models**  
  Fast comparison of GR vs SST predictions in strong field limits.

---



### Installation Options

#### Python Package

```bash
pip install sstcore
```

**Resources na pip install (via import)**  
Na `pip install` kun je het resources-pad (o.a. `Knots_FourierSeries`, `ideal.txt`) zo aanroepen:

```python
import sstcore

# Basis resources-map (ideal.txt, Knots_FourierSeries, …)
resources_dir = sstcore.get_resources_dir()

# Alleen Knots_FourierSeries-map
kfs_dir = sstcore.get_knots_fourier_series_dir()

# Pad naar ideal.txt
ideal_path = sstcore.get_ideal_txt_path()
```

Optioneel: stel `SSTCORE_RESOURCES` in om een vaste map te forceren.

### SSTCORE Installation Guide (Windows)

This precompiled `sstbindings.cp311-win_amd64.pyd`  file is a pybind11 module
compiled for Python 3.11 on 64-bit Windows.

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


## 📦 Build & Run
I advise to make use of IDE like CLion, PyCharm or Visual Studio for building and running the project. When using CLion, you can follow these steps:
You must install Visual Studio 2022 with C++ support, and then you can use CLion to build the project.

### ⚙️ Repair MSVC with the Visual Studio Installer
Open the Visual Studio Installer and do the following:
- Find Visual Studio 2022 Community
- Click Modify

### Make sure the following are selected:
✔ Individual components:
✅ MSVC v14.3x - x64/x86 build tools
✅ Windows 10 SDK (or 11)
✅ C++ CMake tools for Windows
✅ C++ ATL/MFC support (optional)
✅ C++ Standard Library (STL)
After this, reboot CLion and retry the build.

### 🔧 Use Clang Toolchain (if MSVC is broken)
You can switch CLion to use Clang (LLVM):
Install LLVM from: https://github.com/llvm/llvm-project/releases
Point CLion to `clang++.exe` in your toolchain settings
You can still use `pybind11` + `C++23` this way and avoid MSVC issues altogether.

### 🐍 Install Python Dependencies
Make sure you have Python 3.11+ installed, then create a virtual environment and install the required packages.
This might be the time to take a look at Conda, which is a package manager that can help you manage Python environments and dependencies more easily.
```bash
conda create -n  SSTcore12    python=3.12
conda activate  SSTcore12 
```

We now have to at least `pip install pybind11` and  `pip install numpy` to run the Python bindings.
I recommend to use a `requirements.txt` file to manage the dependencies of the project, it will reflect my environment.
```bash
pip install -r requirements.txt
```
To keep file up to date: `pip freeze > requirements.txt`

### 🛠️ Get pyBind11 inside the project
```bash
mkdir extern
mkdir extern/pybind11
git clone https://github.com/pybind/pybind11.git extern/pybind11
````

### 🔨 Build C++ Core
Before building, ensure you have CMake installed and your environment is set up correctly.
Download and install CMake https://cmake.org/download/

First initialize the CMake project, this results in a new directory `cmake-build-debug-mingw` or  similar in the project.
You can now use the following commands (from project root) to build the C++ core and generate the Python bindings: 
```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release # or Debug

```
This command compiles the C++ core and generates the Python bindings using `pybind11`.

pip install PyQtWebEngine PyQt5 pyinstaller numpy
#### npm Package (Node.js / Browser)

```bash
npm install sstcore
```

See [README_NPM.md](README_NPM.md) for detailed usage instructions.

### 📦 Test if python receives SST Bindings `
```bash
python -c "import sstbindings; print(sstcore)"
````
This should return `<module 'sstcore' from 'C:\\workspace\\projects\\sstcore\\build\\Debug\\sstbindings.cp312-win_amd64.pyd'>`
This indicates that the Python bindings for SSTcore have been successfully built and installed.
If this command fails, ensure that `sstbindings.cp311-win_amd64.pyd` is found in the same directory where you run python.
When it does not work, you can delete the `cmake-build` and `build` folder and try to recompile the C++ bindings from within `./build/` with `cmake ..` followed by  `cmake --build . --config Debug` again.

### 🐍 Import the SST Bindings in Python
```
from sstbindings import VortexKnotSystem, biot_savart_velocity, compute_kinetic_energy
```


### 🔨 Load the C++ module dynamically from the compiled path, because the SST Bindings are not installed in the Python site-packages.
```python
import os
module_path = os.path.abspath("C:\\workspace\\projects\\sstcore\\build\\Debug\\sstbindings.cp312-win_amd64.pyd")
module_name = "sstcore"
```

### 📊 Run Benchmarks
```bash
python tests/test_potential_timefield.py
```
---

### 📂 Project Structure
```bash
project-root/
├── build/
│   └── ...
├── examples/
│   ├── example_fluid_rotation.py
│   ├── example_potential_flow.py
│   ├── example_vortex_ring.py
│   └── ...
├── src/
│   ├── fluid_dynamics.cpp
│   ├── thermo_dynamics.cpp
│   ├── vorticity_dynamics.cpp
│   └── ...
├── src_bindings/
│   ├── module_sst.cpp
│   ├── py_fluid_dynamics.cpp
│   ├── py_thermo_dynamics.cpp
│   ├── py_vorticity_dynamics.cpp
│   └── ...
├── extern/pybind11/         # <-- Git submodule or manually cloned -- git clone https://github.com/pybind/pybind11.git extern/pybind11
├── CMakeLists.txt
```


## 🧠 Author   

**ORCID**: [0009-0006-1686-3961](https://orcid.org/0009-0006-1686-3961)  
Conceived, written, and fearlessly pushed into the void by a person undeterred by the collapse of academic consensus.

---

## 📖 Documentation
- Theory Overview
- Swirl Core Model
- Benchmarked Results

---

## 🧃 Warning
This software may cause:
- Vortex-based worldview shifts
- Sudden rejection of spacetime curvature
- Hallucinations of swirling field lines in your breakfast cereal
---

## 💬 Contact
Open an issue or whisper into the æther.
This code is listening. Always.
---

### 1. Installeer PyTorch en de specifieke Intel Extension for PyTorch (IPEX) voor Windows XPU
```bash
conda create -n SSTcore11 intelpython3_full python=3.11 -c https://software.repos.intel.com/python/conda -c conda-forge --override-channels
conda activate SSTcore11
conda config --add channels conda-forge
conda config --set channel_priority flexible
conda install scikit-learn-intelex xgboost numpy scipy numexpr -c https://software.repos.intel.com/python/conda/ -c conda-forge
```
### 2. Installeer de Coqui TTS bibliotheek (die XTTSv2 bevat) & Zorg ervoor dat de nieuwste versie van torchaudio's backend (soundfile) beschikbaar is. Toevoeging voor de GPU-acceleratie van Neurale Netwerken (XTTS)
```bash
python -m pip install torch==2.1.0.post3 torchvision==0.16.0.post3 torchaudio==2.1.0.post3 intel-extension-for-pytorch==2.1.10+xpu --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/
python -m pip install TTS soundfile
```
### 3. Other setup steps for Python dependencies (if needed)
```bash
conda create -n SSTcore11 intelpython3_full python=3.11 -c https://software.repos.intel.com/python/conda -c conda-forge --override-channels
conda activate SSTcore11

conda install conda -c https://software.repos.intel.com/python/conda/
conda install conda -c conda-forge
conda install conda -c main
conda config --add channels conda-forge
conda config --set channel_priority flexible

conda install scikit-learn -c https://software.repos.intel.com/python/conda/
conda install scikit-learn-intelex -c https://software.repos.intel.com/python/conda/
conda install xgboost -c https://software.repos.intel.com/python/conda/
conda install numpy -c https://software.repos.intel.com/python/conda/ -c conda-forge
conda install scipy -c https://software.repos.intel.com/python/conda/ -c conda-forge
conda install numexpr -c https://software.repos.intel.com/python/conda/ -c conda-forge
```

```bash
# 1. Verwijder de gecorrumpeerde en verouderde installatie
pip uninstall -y torch torchvision torchaudio intel-extension-for-pytorch

# 2. Installeer de vereiste C-bibliotheek voor asynchrone I/O
conda install libuv -c conda-forge -y

# 3. Installeer de nieuwe PyTorch 2.5.1 XPU stack, geoptimaliseerd voor Intel Arc
python -m pip install torch==2.5.1+cxx11.abi torchvision==0.20.1+cxx11.abi torchaudio==2.5.1+cxx11.abi intel-extension-for-pytorch==2.5.10+xpu --index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/
```

 1. Isoleer de Intel GPU hardwarematig voor de SYCL/UR runtime
 1. Installeer de Intel-geoptimaliseerde PyTorch stack voor Python 3.12
 2. Activeer Level Zero optimalisaties voor PyTorch XPU
 2. Isoleer de Intel Arc A770 van de NVIDIA GTX 1060 voor de SYCL runtime
 3. Activeer Level Zero optimalisaties voor asynchrone executie
```bash
python -m pip install torch==2.5.1+cxx11.abi torchvision==0.20.1+cxx11.abi torchaudio==2.5.1+cxx11.abi intel-extension-for-pytorch==2.5.10+xpu --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/
conda install libuv -c conda-forge -y

set ONEAPI_DEVICE_SELECTOR=level_zero:gpu
set SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1
set ZES_ENABLE_SYSMAN=1
set ONEAPI_DEVICE_SELECTOR=level_zero:gpu
set SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1
set ZES_ENABLE_SYSMAN=1

python verify_sst_hardware.py
```