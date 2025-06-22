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


		m.def("compute_vorticity", &vam::FluidDynamics::compute_vorticity);
		m.def("swirl_clock_rate", &vam::FluidDynamics::swirl_clock_rate);
		m.def("vorticity_from_curvature", &vam::FluidDynamics::vorticity_from_curvature);
		m.def("vortex_pressure_drop", &vam::FluidDynamics::vortex_pressure_drop);
		m.def("vortex_transverse_pressure_diff", &vam::FluidDynamics::vortex_transverse_pressure_diff);
		m.def("swirl_energy", &vam::FluidDynamics::swirl_energy);
		m.def("kairos_energy_trigger", &vam::FluidDynamics::kairos_energy_trigger);
		m.def("compute_helicity", &vam::FluidDynamics::compute_helicity);
		m.def("potential_vorticity", &vam::FluidDynamics::potential_vorticity);
	}

