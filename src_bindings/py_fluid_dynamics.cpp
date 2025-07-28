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


        m.def("compute_vorticity", &vam::FluidDynamics::compute_vorticity,
                  py::arg("grad"),
                  R"pbdoc(
        Compute vorticity vector ω = ∇ × v from the velocity gradient tensor.
    )pbdoc");

        m.def("swirl_clock_rate", &vam::FluidDynamics::swirl_clock_rate,
                  py::arg("dv_dx"),
                  py::arg("du_dy"),
                  R"pbdoc(
        Swirl clock rate 0.5 * (dv/dx - du/dy).
    )pbdoc");

        m.def("vorticity_from_curvature", &vam::FluidDynamics::vorticity_from_curvature,
                  py::arg("V"),
                  py::arg("R"),
                  R"pbdoc(
        Vorticity magnitude for curved flow V/R.
    )pbdoc");

        m.def("vortex_pressure_drop", &vam::FluidDynamics::vortex_pressure_drop,
                  py::arg("rho"),
                  py::arg("c"),
                  R"pbdoc(
        Pressure drop 0.5 * ρ * c^2 in a vortex core.
    )pbdoc");

        m.def("vortex_transverse_pressure_diff", &vam::FluidDynamics::vortex_transverse_pressure_diff,
                  py::arg("rho"),
                  py::arg("c"),
                  R"pbdoc(
        Transverse pressure difference 0.25 * ρ * c^2.
    )pbdoc");

        m.def("swirl_energy", &vam::FluidDynamics::swirl_energy,
                  py::arg("rho"),
                  py::arg("omega"),
                  R"pbdoc(
        Rotational kinetic energy density (1/2) * ρ * ω^2.
    )pbdoc");

        m.def("kairos_energy_trigger", &vam::FluidDynamics::kairos_energy_trigger,
                  py::arg("rho"),
                  py::arg("omega"),
                  py::arg("Ce"),
                  R"pbdoc(
        Trigger when swirl energy exceeds 0.5 * ρ * Ce^2.
    )pbdoc");

        m.def("compute_helicity", &vam::FluidDynamics::compute_helicity,
                  py::arg("velocity"),
                  py::arg("vorticity"),
                  py::arg("dV"),
                  R"pbdoc(
        Compute helicity ∑ (v · ω) dV over a discretized field.
    )pbdoc");

        m.def("potential_vorticity", &vam::FluidDynamics::potential_vorticity,
                  py::arg("fa"),
                  py::arg("zeta_r"),
                  py::arg("h"),
                  R"pbdoc(
        Potential vorticity (fa + ζ_r) / h.
    )pbdoc");
        m.def("is_incompressible", &vam::FluidDynamics::is_incompressible,
                  py::arg("dudx"),
                  py::arg("dvdy"),
                  py::arg("dwdz"),
                  R"pbdoc(
        Determine if flow is incompressible by checking that the
        divergence of the velocity field is approximately zero.
    )pbdoc");

		m.def("circulation_surface_integral", &vam::FluidDynamics::circulation_surface_integral,
			  py::arg("omega_field"), py::arg("dA_field"),
			  R"pbdoc(Circulation as surface integral of vorticity dot area vector.
	)pbdoc");

		m.def("enstrophy", &vam::FluidDynamics::enstrophy,
			  py::arg("omega_squared"), py::arg("ds_area"),
			  R"pbdoc(Enstrophy as sum of squared vorticity weighted by area.
	)pbdoc");
}

