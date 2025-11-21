//
// Created by mr on 3/22/2025.
//
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/time_evolution.h"

namespace py = pybind11;

void bind_time_evolution(py::module_& m) {
	py::class_<sst::TimeEvolution>(m, "TimeEvolution")
			.def(py::init<std::vector<sst::Vec3>, std::vector<sst::Vec3>, double>(),
				 py::arg("initial_positions"), py::arg("initial_tangents"), py::arg("gamma") = 1.0)
			.def("evolve", &sst::TimeEvolution::evolve,
				 py::arg("dt"), py::arg("steps"))
			.def("get_positions", &sst::TimeEvolution::get_positions,
				 py::return_value_policy::reference)
			.def("get_tangents", &sst::TimeEvolution::get_tangents,
				 py::return_value_policy::reference);

}