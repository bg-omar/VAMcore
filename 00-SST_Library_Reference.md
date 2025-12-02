# Swirl String Theory (SST) Core Library Reference
**Version:** 2.1.0 (Parser Upgrade) | **Generated:** 2025-11-21

This document is **automatically compiled** from the C++ Source Code (`src_bindings/`).
It supports both `R"pbdoc` and Standard String documentation.

---

## 1. SST Gravity & Metric Engineering

### `biot_savart_vector_potential_grid`
🛠️ *[Auto-Extracted from py_field_kernels.cpp]*

**Description:** Computes Magnetic Vector Potential A on a grid.

**Equation:**
$$
Computes Magnetic Vector Potential A on a grid.
$$

---
### `compute_beltrami_shear`
✅ **[SST Canon]**

**Description:** Calculates the Beltrami Shear Stress (Vacuum Tearing). Measures deviation from Force-Free state.

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

**Description:** Computes the scalar Gravity Dilation Map (G_local). Limits to 0 as induced velocity approaches swirl velocity.

**Equation:**
$$
G_{local} = G_0 \left[ 1 - \left( \frac{|\vec{B}| \cdot \log_{10}(\omega)}{\rho_{vac} \cdot v_{swirl}} \right)^2 \right]
$$

---
### `compute_time_dilation_map`
✅ **[SST Canon]**

**Description:** Computes local time dilation based on the transverse velocity of the vortex filaments.

**Equation:**
$$
\Delta t' = \Delta t \sqrt{1 - \frac{v_t^2}{c_{eth}^2}}
$$

---
### `potential_temperature`
✅ **[SST Canon]**

**Description:** Temperature a fluid parcel would attain if brought adiabatically to standard pressure.

**Equation:**
$$
\theta = T \left( \frac{P_0}{P} \right)^{R/c_p}
$$

---
### `potential_vorticity`
✅ **[SST Canon]**

**Description:** Computes Ertel Potential Vorticity, conserved in adiabatic flow.

**Equation:**
$$
PV = \frac{\vec{\omega} \cdot \nabla \theta}{\rho}
$$

---
## 2. Fluid Dynamics & Vortex Solvers

### `bernoulli_pressure`
🛠️ *[Auto-Extracted from py_potential_flow.cpp]*

**Description:** See Description

**Equation:**
$$
See Description
$$

---
### `biot_savart_vector_potential_grid`
🛠️ *[Auto-Extracted from py_field_kernels.cpp]*

**Description:** Computes Magnetic Vector Potential A on a grid.

**Equation:**
$$
Computes Magnetic Vector Potential A on a grid.
$$

---
### `biot_savart_velocity`
✅ **[SST Canon]**

**Description:** Computes the induced velocity (B-field) via Biot-Savart Law.

**Equation:**
$$
\vec{v}(\vec{r}) = \frac{\Gamma}{4\pi} \oint_C \frac{d\vec{l} \times (\vec{r} - \vec{r}')}{|\vec{r} - \vec{r}'|^3}
$$

---
### `biot_savart_velocity_grid`
✅ **[SST Canon]**

**Description:** Vectorized Biot-Savart solver for arbitrary 3D grids.

**Equation:**
$$
\vec{v}_{ij k} = \sum_{seg} \text{BiotSavart}(\vec{r}_{ijk}, \vec{l}_{seg})
$$

---
### `biot_savart_wire_grid`
✅ **[SST Canon]**

**Description:** Optimized kernel for polyline-to-grid field induction.

**Equation:**
$$
\vec{B}(\vec{x}) = \frac{\mu_0 I}{4\pi} \sum \frac{d\vec{l} \times \hat{r}}{r^2}
$$

---
### `compute_bernoulli_pressure`
✅ **[SST Canon]**

**Description:** Alias for pressure field computation.

**Equation:**
$$
P + \frac{1}{2}\rho v^2 = \text{const}
$$

---
### `compute_pressure_field`
✅ **[SST Canon]**

**Description:** Computes the macroscopic pressure field using the Bernoulli principle for incompressible flow.

**Equation:**
$$
P = P_{\infty} - \frac{1}{2} \rho_{ae} |\vec{v}|^2
$$

---
### `compute_swirl_field`
🛠️ *[Auto-Extracted from py_swirl_field.cpp]*

**Description:** Compute 2D swirl force field at a given resolution and time.

**Equation:**
$$
Compute 2D swirl force field at a given resolution and time.
$$

---
### `compute_velocity_magnitude`
🛠️ *[Auto-Extracted from py_fluid_dynamics.cpp]*

**Description:** Compute magnitude |v| from vector velocity field.

**Equation:**
$$
Compute magnitude |\vec{v}| from vector velocity field.
$$

---
### `compute_vorticity`
🛠️ *[Auto-Extracted from py_vorticity_dynamics.cpp]*

**Description:** See Description (Arg Name Detected)

**Equation:**
$$
See Description (Arg Name Detected)
$$

---
### `compute_vorticity_rhs`
🛠️ *[Auto-Extracted from py_vorticity_transport.cpp]*

**Description:** Vorticity transport RHS

**Equation:**
$$
Vorticity transport RHS
$$

---
### `couette_vorticity`
🛠️ *[Auto-Extracted from py_vorticity_dynamics.cpp]*

**Description:** See Description (Arg Name Detected)

**Equation:**
$$
See Description (Arg Name Detected)
$$

---
### `hill_velocity`
🛠️ *[Auto-Extracted from py_vortex_ring.cpp]*

**Description:** See Description

**Equation:**
$$
See Description
$$

---
### `hill_vorticity`
🛠️ *[Auto-Extracted from py_vortex_ring.cpp]*

**Description:** See Description

**Equation:**
$$
See Description
$$

---
### `lamb_oseen_velocity`
🛠️ *[Auto-Extracted from py_vortex_ring.cpp]*

**Description:** See Description

**Equation:**
$$
See Description
$$

---
### `lamb_oseen_vorticity`
🛠️ *[Auto-Extracted from py_vortex_ring.cpp]*

**Description:** See Description

**Equation:**
$$
See Description
$$

---
### `potential_vorticity`
✅ **[SST Canon]**

**Description:** Computes Ertel Potential Vorticity, conserved in adiabatic flow.

**Equation:**
$$
PV = \frac{\vec{\omega} \cdot \nabla \theta}{\rho}
$$

---
### `pressure_gradient`
🛠️ *[Auto-Extracted from py_pressure_field.cpp]*

**Description:** Compute spatial pressure gradient vector field.

**Equation:**
$$
Compute spatial pressure gradient vector field.
$$

---
### `solid_body_rotation_vorticity`
🛠️ *[Auto-Extracted from py_vorticity_dynamics.cpp]*

**Description:** See Description (Arg Name Detected)

**Equation:**
$$
See Description (Arg Name Detected)
$$

---
### `swirl_clock_rate`
✅ **[SST Canon]**

**Description:** The local tick-rate of the fluid element, derived from the 2D curl component.

**Equation:**
$$
\Omega_z = \frac{1}{2} \left( \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y} \right)
$$

---
### `swirl_energy`
✅ **[SST Canon]**

**Description:** Rotational kinetic energy density of the vortex system.

**Equation:**
$$
E_k = \frac{1}{2} \rho \int_V |\vec{\omega}|^2 \, dV
$$

---
### `vortex_pressure_drop`
🛠️ *[Auto-Extracted from py_fluid_dynamics.cpp]*

**Description:** Pressure drop 0.5 * ρ * c^2 in a vortex core.

**Equation:**
$$
Pressure drop \frac{1}{2} ρ c^2 in a vortex core.
$$

---
### `vortex_transverse_pressure_diff`
🛠️ *[Auto-Extracted from py_fluid_dynamics.cpp]*

**Description:** Transverse pressure difference 0.25 * ρ * c^2.

**Equation:**
$$
Transverse pressure difference \frac{1}{4} ρ c^2.
$$

---
### `vorticity_from_curvature`
✅ **[SST Canon]**

**Description:** Approximates vorticity for curved laminar flow based on path radius.

**Equation:**
$$
|\vec{\omega}| \approx \frac{v}{R_{curve}}
$$

---
### `vorticity_z_2D`
🛠️ *[Auto-Extracted from py_vorticity_dynamics.cpp]*

**Description:** Compute 2D vorticity

**Equation:**
$$
\frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}
$$

---
## 3. Topological Metrics

### `compute_centerline_helicity`
✅ **[SST Canon]**

**Description:** Total helicity decomposed into Writhe and Twist.  
**Equation:**
$$
H = Wr + Tw
$$

---
### `compute_helicity`
✅ **[SST Canon]**

**Description:** Computes Hydrodynamic Helicity (Knottedness).
**Equation:**
$$
\mathcal{H} = \int_V \vec{v} \cdot \vec{\omega} \, dV
$$

![Topology Diagram](topology_concept.png)

---
### `compute_linking_number`
✅ **[SST Canon]**

**Description:** Gauss Linking Number between two closed loops.

**Equation:**
$$
Lk = \frac{1}{4\pi} \oint_{\gamma_1} \oint_{\gamma_2} \frac{\vec{r}_{12} \cdot (d\vec{r}_1 \times d\vec{r}_2)}{r_{12}^3}
$$

---
### `compute_writhe`
✅ **[SST Canon]**

**Description:** The Writhe number (Gauss integral), measuring global coiling.

**Equation:**
$$
Wr = \frac{1}{4\pi} \iint \frac{(\vec{r}_1-\vec{r}_2) \cdot (d\vec{r}_1 \times d\vec{r}_2)}{|\vec{r}_1-\vec{r}_2|^3}
$$

![Topology Diagram](topology_concept.png)

---
### `evaluate_fourier_block`
🛠️ *[Auto-Extracted from py_fourier_knot.cpp]*

**Description:** Evaluate r(s) for the given Fourier block.

**Equation:**
$$
Evaluate r(s) for the given Fourier block.
$$

---
### `evaluate_fourier_series`
✅ **[SST Canon]**

**Description:** Reconstructs knot geometry from Fourier coefficients.

**Equation:**
$$
\vec{r}(t) = \sum [ \vec{a}_n \cos(nt) + \vec{b}_n \sin(nt) ]
$$

---
### `evolve_vortex_knot`
🛠️ *[Auto-Extracted from py_frenet_helicity.cpp]*

**Description:** Evolve vortex knot filaments using Biot–Savart dynamics.

**Equation:**
$$
Evolve vortex knot filaments using Biot–Savart dynamics.
$$

![Topology Diagram](topology_concept.png)

---
### `fourier_knot_eval`
🛠️ *[Auto-Extracted from py_fourier_knot.cpp]*

**Description:** NumPy-friendly Fourier evaluation returning (x,y,z)

**Equation:**
$$
NumPy-friendly Fourier evaluation returning (x,y,z)
$$

![Topology Diagram](topology_concept.png)

---
### `writhe_gauss_curve`
🛠️ *[Auto-Extracted from py_heavy_knot.cpp]*

**Description:** Compute writhe via Gauss integral

**Equation:**
$$
Compute writhe via Gauss integral
$$

![Topology Diagram](topology_concept.png)

---