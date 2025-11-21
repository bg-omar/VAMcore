# Swirl String Theory (SST) Core Library Reference
**Version:** 2.0.0 (Auto-Compiled) | **Generated:** 2025-11-21

This document is **automatically compiled** from the C++ Source Code (`src_bindings/`).
Equations marked with [Canon] are rigorously verified against the SST Protocol.

---

## 1. SST Gravity & Metric Engineering

### `compute_beltrami_shear`
✅ **[SST Canon]**

**Description:** Calculates the Beltrami Shear Stress (Vacuum Tearing).

**Equation:**
$$
S = \left\| \vec{B} \times (\nabla \times \vec{B}) \right\|
$$

---
### `compute_gravitational_potential`
✅ **[SST Canon]**

**Description:** Computes the effective gravitational potential derived from the vorticity distribution.

**Equation:**
$$
\Phi_G(\vec{r}) = -G \int \frac{|\vec{\omega}(\vec{r}')|^2}{|\vec{r} - \vec{r}'|} d^3r'
$$

---
### `compute_gravity_dilation`
✅ **[SST Canon]**

**Description:** Computes the scalar Gravity Dilation Map (G_local) based on the local Magnetic Intensity and Driving Frequency.

**Equation:**
$$
G_{local} = G_0 \left[ 1 - \left( \frac{|\vec{B}| \cdot \log_{10}(\omega)}{\rho_{vac} \cdot v_{swirl}} \right)^2 \right]
$$

---
## 2. Fluid Dynamics & Vortex Solvers

### `biot_savart_velocity`
✅ **[SST Canon]**

**Description:** Computes the induced velocity (B-field) via Biot-Savart Law.

**Equation:**
$$
\vec{v}(\vec{r}) = \frac{\Gamma}{4\pi} \oint_C \frac{d\vec{l} \times (\vec{r} - \vec{r}')}{|\vec{r} - \vec{r}'|^3}
$$

---
## 3. Topological Metrics

### `compute_helicity`
✅ **[SST Canon]**

**Description:** Computes the Hydrodynamic Helicity integral.

**Equation:**
$$
\mathcal{H} = \int_V \vec{v} \cdot \vec{\omega} \, dV
$$

---
