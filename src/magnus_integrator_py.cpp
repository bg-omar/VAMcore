// src/magnus_integrator_py.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "magnus_integrator.h"

namespace py = pybind11;

void bind_magnus_integrator(py::module_& m) {
  py::class_<MagnusBernoulliIntegrator>(m, "MagnusBernoulliIntegrator")
      .def(py::init<double, double, double, double>(),
           py::arg("rho_f"),
           py::arg("v_swirl"),
           py::arg("r_c"),
           py::arg("Gamma"),
           "Initializes the Magnus-Bernoulli Integrator with foundational SST constants.")

      .def("compute_magnus_force", &MagnusBernoulliIntegrator::compute_magnus_force,
           py::arg("tangent"),
           py::arg("normal"),
           py::arg("curvature_radius"),
           py::arg("v_knot"),
           py::arg("v_bg"),
           "Computes the transverse Magnus-Curvature force on a vortex segment.")

      .def("compute_swirl_coulomb_accel", &MagnusBernoulliIntegrator::compute_swirl_coulomb_accel,
           py::arg("eval_pos"),
           py::arg("source_pos"),
           "Computes the exact continuous Swirl-Coulomb radial acceleration.");
}
