//
// Created by mr on 3/22/2025.
//
// bindings/py_knot_dynamics.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/knot_dynamics.h"

namespace py = pybind11;

void bind_knot_dynamics(py::module_& m) {
	m.def("compute_writhe", &vam::compute_writhe, R"pbdoc(
        Compute the writhe of a closed filament (topological self-linking).
    )pbdoc");

	m.def("compute_linking_number", &vam::compute_linking_number, R"pbdoc(
        Compute the Gauss linking number between two closed loops.
    )pbdoc");

	m.def("compute_twist", &vam::compute_twist, R"pbdoc(
        Compute twist from Frenet frames along a filament.
    )pbdoc");

	m.def("compute_centerline_helicity", &vam::compute_centerline_helicity, R"pbdoc(
        Compute the centerline helicity as the sum of writhe and twist.
    )pbdoc");

	m.def("detect_reconnection_candidates", &vam::detect_reconnection_candidates, R"pbdoc(
        Detect pairs of points on the filament that approach closely enough to be candidates for reconnection.
    )pbdoc");
}