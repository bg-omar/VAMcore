# ⚙️ VAMcore: Hybrid Benchmark Engine for the Vortex Æther Model

Welcome to **VAMcore**, the computational backbone for the Vortex Æther Model (VAM).  
This hybrid C++/Python engine is designed to benchmark field-based gravity, time dilation, and EM swirl-field dynamics using modern numerical methods and a large helping of theoretical audacity. This repository contains the core engine, simulation scripts, and visualizations to explore the swirling depths of æther dynamics.
We build the C++ VAM-Bindings first, and then we can import it into benchmark Python code. When using the C++  VAM-bindings to do hard calculations we can run / render Python simulations 10-100x faster.

---

## 💾 Features

- 🚀 **High-Performance Core (C++)**  
  Handles numerically stiff vortex dynamics, EM field evolution, and topological energy exchanges.

- 🐍 **Python Frontend**  
  For visualization, parameter sweeps, and interactive experiments using `matplotlib`, `numpy`, and `PyBind11` integration.

- 🧲 **EM Field Simulations**  
  Supports generation and animation of **rotating 3-phase bivort** electric and magnetic field structures.

- ⌛ **Time Dilation & Gravity Models**  
  Fast comparison of GR vs VAM predictions in strong field limits.

---

## 🧪 Sample Outputs

| Simulation | Output |
|-----------|--------|
| Time Dilation Field | ![Time Dilation](examples/time_dilation.png) |
| Æther Inflow Velocity | ![Inflow](examples/inflow_quiver.png) |
| Rotating EM Vortex | ![EM Vortices](examples/em_quiver.gif) |

---

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
conda create -n  VAM    python=3.12
conda activate  VAM  
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

### 📂 Project Structure
```bash
project-root/
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
│   ├── module_vam.cpp
│   ├── py_fluid_dynamics.cpp
│   ├── py_thermo_dynamics.cpp
│   ├── py_vorticity_dynamics.cpp
│   └── ...
├── extern/pybind11/         # <-- Git submodule or manually cloned
├── CMakeLists.txt
```


### 🔨 Build C++ Core
Before building, ensure you have CMake installed and your environment is set up correctly.
Download and install CMake https://cmake.org/download/
You can use the following commands to build the C++ core and generate the Python bindings using `
```bash
mkdir build
cd build
cmake ..
cmake --build . --config Debug  # or Release

```
This command compiles the C++ core and generates the Python bindings using `pybind11`.

### 📦 Test if python receives VAM Bindings `
```bash
python -c "import vambindings; print(vambindings)"
````
This should return `<module 'vambindings' from 'C:\\workspace\\projects\\vamcore\\build\\Debug\\vambindings.cp312-win_amd64.pyd'>`
This indicates that the Python bindings for VAMcore have been successfully built and installed.
If this command fails, ensure that `vambindings.cp312-win_amd64.pyd` is found in the same directory where you run python.
When it does not work, you can try to recompile the C++ bindings from within `./build/` with `cmake --build . --config Debug` again.

### 🐍 Import the VAM Bindings in Python
```
from vambindings import VortexKnotSystem, biot_savart_velocity, compute_kinetic_energy
```


### 🔨 Load the C++ module dynamically from the compiled path, because the VAM Bindings are not installed in the Python site-packages.
```python
import os
module_path = os.path.abspath("C:\\Users\\mr\\IdeaProjects\\VAM\\VAMpyBindings\\build\\Debug\\vambindings.cp312-win_amd64.pyd")
module_name = "vambindings"
```

### 📊 Run Benchmarks
```bash
python tests/test_potential_timefield.py
```
---


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

This document provides a summary of implemented functions in the VAM C++/Python library along with their corresponding physical and mathematical formulas.



---

## 🌀 Helicity

**Function**: `compute_helicity(velocity, vorticity)`

**Formula**:
$${H} = \int_{\mathbb{R}^3} \mathbf{v} \cdot \omega \, d^3\mathbf{r}$$

---

## ⚡ Kinetic Energy

**Function**: `compute_kinetic_energy(velocity, rho_ae)`

**Formula**:
$$E = \frac{1}{2} \rho_æ \int |\mathbf{v}|^2 \, d^3\mathbf{r}$$

---

## 🧩 Curvature

**Function**: `compute_curvature_torsion(positions)`

**Formula**:
$$\kappa(s) = \left\| \frac{d^2 \mathbf{X}}{ds^2} \right\|$$

---

## 🔁 Torsion

**Function**: `compute_curvature_torsion(positions)`

**Formula**:
$$\tau(s) = \frac{ \left( \frac{d \mathbf{X}}{ds} \times \frac{d^2 \mathbf{X}}{ds^2} \right) \cdot \frac{d^3 \mathbf{X}}{ds^3} }{ \left\| \frac{d \mathbf{X}}{ds} \times \frac{d^2 \mathbf{X}}{ds^2} \right\|^2 }$$

---

## 🌌 Gravitational Acceleration (Bernoulli Gradient)

**Function**: `pressure_gradient` and `compute_bernoulli_pressure`

**Formula**:
$$\mathbf{g}(\mathbf{r}) = -\frac{1}{\rho_æ} \nabla P(\mathbf{r}) = \nabla \left( \frac{1}{2} |\mathbf{v}|^2 \right)$$

---

## ⏳ Time Dilation from Tangential Velocity

**Function**: `compute_time_dilation_map(tangential_velocities, ce)`

**Formula**:
$$\text{Time Dilation} = 1 - \frac{v^2}{C_e^2}$$

---

## 🌀 Gravitational Potential from Vorticity

**Function**: `compute_gravitational_potential(positions, vorticity, aether_density)`

**Formula**:
$$\Phi(\mathbf{r}) = \text{scalar potential derived from vorticity field}$$

---

Generated by VAM Core — Vortex Æther Model Simulation Toolkit