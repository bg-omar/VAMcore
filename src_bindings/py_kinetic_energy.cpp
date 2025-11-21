//
// Created by mr on 3/23/2025.
//
// bindings/py_kinetic_energy.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/kinetic_energy.h"

namespace py = pybind11;

void bind_kinetic_energy(py::module_& m) {
        m.def("compute_kinetic_energy", &sst::KineticEnergy::compute,
		  py::arg("velocity"),
		  py::arg("rho_ae"),
		  R"pbdoc(
            Compute kinetic energy E = (1/2) * ρ * ∑ |v|^2.
        )pbdoc");
}