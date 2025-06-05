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

### 🛠️ Get pyBind11 inside the project
```bash
mkdir extern
mkdir extern/pybind11
git clone https://github.com/pybind/pybind11.git extern/pybind11
````

### ⚙️ Set Python environmet variables first
```bash
set PYTHONPATH=build\Debug
```

### 🔨 Build C++ Core
```bash
"C:\Program Files\JetBrains\CLion\bin\cmake\win\x64\bin\cmake.exe" --build C:\workspace\projects\vamcore\cmake-build-debug --target vambindings -j 18
```

```bash
cmake -S . -B cmake-build-debug -Dpybind11_DIR=extern/pybind11/share/cmake/pybind11
```

### 🐍 Install Python Dependencies
```bash
python -c "import vambindings; print(vambindings)"
````
This should return `<module 'vambindings' from 'C:\\workspace\\projects\\vamcore\\build\\Debug\\vambindings.cp311-win_amd64.pyd'>`
This indicates that the Python bindings for VAMcore have been successfully built and installed.

### 🔨 Load the C++ module dynamically from the compiled path
```python
import os
module_path = os.path.abspath("build/Debug/vambindings.cp311-win_amd64.pyd")
module_name = "vambindings"
```

### 📊 Run Benchmarks
```bash
python tests/test_potential_timefield.py
```
---

## 📖 Zenodo-Registered Releases
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15566101.svg)](https://doi.org/10.5281/zenodo.15566101)  
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15566319.svg)](https://doi.org/10.5281/zenodo.15566319)  
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15566336.svg)](https://doi.org/10.5281/zenodo.15566336)

All papers and associated code are archived on [Zenodo](https://zenodo.org/) for permanent accessibility and citation.

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
