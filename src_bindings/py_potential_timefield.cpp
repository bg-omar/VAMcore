//
// Created by mr on 3/22/2025.
//
// bindings/py_potential_timefield.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/potential_timefield.h"

namespace py = pybind11;

void bind_potential_timefield(py::module_& m) {
        m.def("compute_gravitational_potential", &sst::PotentialTimeField::compute_gravitational_potential,
		  py::arg("positions"),
		  py::arg("vorticity"),
		  py::arg("epsilon") = 0.1,
		  R"pbdoc(
            Compute Ætheric gravitational potential field from vorticity gradients.
        )pbdoc");

        m.def("compute_time_dilation_map", &sst::PotentialTimeField::compute_time_dilation_map,
		  py::arg("tangents"),
		  py::arg("C_e"),
		  R"pbdoc(
            Compute time dilation factors from knot tangential velocities.
        )pbdoc");
}