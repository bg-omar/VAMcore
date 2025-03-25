//
// Created by mr on 3/22/2025.
//
// bindings/py_gravity_timefield.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "gravity_timefield.h"

namespace py = pybind11;

void bind_gravity_timefield(py::module_& m) {
	m.def("compute_gravitational_potential", &vam::compute_gravitational_potential,
		  py::arg("positions"), py::arg("vorticity"), py::arg("epsilon") = 0.1,
		  R"pbdoc(
            Compute Æther gravitational potential field from vorticity.
        )pbdoc");

	m.def("compute_time_dilation_map", &vam::compute_time_dilation_map,
		  py::arg("tangents"), py::arg("C_e"),
		  R"pbdoc(
            Compute local time dilation factor map from tangential velocities.
        )pbdoc");
}
