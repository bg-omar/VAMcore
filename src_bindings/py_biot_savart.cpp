//
// Created by mr on 3/22/2025.
//
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/biot_savart.h"

namespace py = pybind11;
using namespace vam;

void bind_biot_savart(py::module_& m) {
  py::class_<BiotSavart>(m, "BiotSavart")
      .def_static("compute_velocity", &BiotSavart::computeVelocity)
      .def_static("compute_vorticity", &BiotSavart::computeVorticity)
      .def_static("extract_interior", &BiotSavart::extractInterior)
      .def_static("compute_invariants", &BiotSavart::computeInvariants);
        m.def("biot_savart_velocity", &vam::BiotSavart::velocity,
		  py::arg("r"),
		  py::arg("filament_points"),
		  py::arg("tangent_vectors"),
		  py::arg("circulation") = 1.0,
		  "Compute velocity at point r due to a vortex filament.");
}
