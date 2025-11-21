//
// Created by mr on 7/18/2025.
//
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/relative_vorticity.h"

namespace py = pybind11;
using namespace sst;

void bind_relative_vorticity(py::module_& m) {
	m.def("crocco_gradient", &Relative_Vorticity::crocco_gradient,
		  "Compute ∇H from Crocco's theorem");

	m.def("rotating_frame_rhs", &Relative_Vorticity::rotating_frame_rhs,
		  "Compute rotating frame momentum RHS");
}