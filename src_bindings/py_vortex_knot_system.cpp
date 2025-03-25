//
// Created by mr on 3/22/2025.
//
// bindings/py_vortex_knot_system.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/vortex_knot_system.h"

namespace py = pybind11;

void bind_vortex_knot_system(py::module_& m) {
	py::class_<vam::VortexKnotSystem, std::shared_ptr<vam::VortexKnotSystem>>(m, "VortexKnotSystem")
			.def(py::init<>())
			.def("initialize_trefoil_knot", &vam::VortexKnotSystem::initialize_trefoil_knot,
				 py::arg("resolution") = 400,
				 R"pbdoc(
				Initialize a trefoil knot with given resolution (default = 400 points).
			)pbdoc")
			.def("evolve", &vam::VortexKnotSystem::evolve,
				 py::arg("dt"), py::arg("steps"),
				 R"pbdoc(
				Evolve vortex knot using Biot–Savart dynamics.
			)pbdoc")
			.def("get_positions", &vam::VortexKnotSystem::get_positions,
				 py::return_value_policy::reference,
				 R"pbdoc(
				Get current 3D positions of the knot.
			)pbdoc")
			.def("get_tangents", &vam::VortexKnotSystem::get_tangents,
				 py::return_value_policy::reference,
				 R"pbdoc(
				Get current tangent vectors of the knot.
			)pbdoc");
}
