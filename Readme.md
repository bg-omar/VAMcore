# ⚙️ VAMcore: Hybrid Benchmark Engine for the Vortex Æther Model

Welcome to **VAMcore**, the computational backbone for the Vortex Æther Model (VAM).  
This hybrid C++/Python engine is designed to benchmark field-based gravity, time dilation, and EM swirl-field dynamics using modern numerical methods and a large helping of theoretical audacity.

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

### ⚙️ Set Python environmet variables first
```bash
set PYTHONPATH=build\Debug
```

### 🔨 Build C++ Core
```bash
cmake --build build --target vambindings
```

### 🐍 Simulate VAM
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
