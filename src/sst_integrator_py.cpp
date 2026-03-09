// src/sst_integrator_py.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_integrator.h"

namespace py = pybind11;

void bind_sst_integrator(py::module_& m) {
    m.def("compute_sst_mass",
          [](const std::vector<std::array<double, 3>>& points, double chi_spin) {
              double m_core = 0.0, m_fluid = 0.0;
              sst::compute_sst_mass(points, chi_spin, m_core, m_fluid);
              return py::make_tuple(m_core, m_fluid);
          },
          py::arg("points"),
          py::arg("chi_spin"),
          R"pbdoc(
Compute SST mass (core + fluid) for a closed polyline.

Uses Rosenhead–Moore regularized Neumann mutual inductance integral.
points: list of [x,y,z] (closed curve by convention).
chi_spin: spin factor (e.g. 2 for fermion).
Returns: (m_core_kg, m_fluid_kg).
)pbdoc");
}
