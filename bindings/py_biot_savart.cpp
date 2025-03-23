//
// Created by mr on 3/22/2025.
//
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/biot_savart.h"

namespace py = pybind11;

void bind_biot_savart(py::module_& m) {
	m.def("biot_savart_velocity", &vam::biot_savart_velocity,
		  py::arg("r"),
		  py::arg("filament_points"),
		  py::arg("tangent_vectors"),
		  py::arg("circulation") = 1.0,
		  "Compute velocity at point r due to a vortex filament.");
}
