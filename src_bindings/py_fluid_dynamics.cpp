//
// Created by mr on 3/22/2025.
//
// bindings/py_fluid_dynamics.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/fluid_dynamics.h"

namespace py = pybind11;

void bind_fluid_dynamics(py::module_& m) {
        m.def("compute_pressure_field", &vam::FluidDynamics::compute_pressure_field,
		  py::arg("velocity_magnitude"),
		  py::arg("rho_ae"),
		  py::arg("P_infinity"),
		  R"pbdoc(
        Compute Bernoulli pressure field from velocity magnitude:
            P = P_infinity - 0.5 * rho_ae * |v|^2
    )pbdoc");

        m.def("compute_velocity_magnitude", &vam::FluidDynamics::compute_velocity_magnitude,
		  py::arg("velocity"),
		  R"pbdoc(
        Compute magnitude |v| from vector velocity field.
    )pbdoc");

        m.def("evolve_positions_euler", &vam::FluidDynamics::evolve_positions_euler,
		  py::arg("positions"),
		  py::arg("velocity"),
		  py::arg("dt"),
		  R"pbdoc(
        Euler-step update of particle positions from velocity vectors.
    )pbdoc");
}
