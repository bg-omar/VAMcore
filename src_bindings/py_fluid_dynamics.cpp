//
// Created by mr on 3/22/2025.
//
// bindings/py_fluid_dynamics.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/fluid_dynamics.h"

namespace py = pybind11;

void bind_fluid_dynamics(py::module_& m) {
        m.def("compute_pressure_field", &sst::FluidDynamics::compute_pressure_field,
		  py::arg("velocity_magnitude"),
		  py::arg("rho_ae"),
		  py::arg("P_infinity"),
		  R"pbdoc(
        Compute Bernoulli pressure field from velocity magnitude:
            P = P_infinity - 0.5 * rho_ae * |v|^2
    )pbdoc");

        m.def("compute_velocity_magnitude", &sst::FluidDynamics::compute_velocity_magnitude,
		  py::arg("velocity"),
		  R"pbdoc(
        Compute magnitude |v| from vector velocity field.
    )pbdoc");

        m.def("evolve_positions_euler", &sst::FluidDynamics::evolve_positions_euler,
		  py::arg("positions"),
		  py::arg("velocity"),
		  py::arg("dt"),
		  R"pbdoc(
        Euler-step update of particle positions from velocity vectors.
    )pbdoc");


        m.def("compute_vorticity", &sst::FluidDynamics::compute_vorticity,
                  py::arg("grad"),
                  R"pbdoc(
        Compute vorticity vector ω = ∇ × v from the velocity gradient tensor.
    )pbdoc");

        m.def("swirl_clock_rate", &sst::FluidDynamics::swirl_clock_rate,
                  py::arg("dv_dx"),
                  py::arg("du_dy"),
                  R"pbdoc(
        Swirl clock rate 0.5 * (dv/dx - du/dy).
    )pbdoc");

        m.def("vorticity_from_curvature", &sst::FluidDynamics::vorticity_from_curvature,
                  py::arg("V"),
                  py::arg("R"),
                  R"pbdoc(
        Vorticity magnitude for curved flow V/R.
    )pbdoc");

        m.def("vortex_pressure_drop", &sst::FluidDynamics::vortex_pressure_drop,
                  py::arg("rho"),
                  py::arg("c"),
                  R"pbdoc(
        Pressure drop 0.5 * ρ * c^2 in a vortex core.
    )pbdoc");

        m.def("vortex_transverse_pressure_diff", &sst::FluidDynamics::vortex_transverse_pressure_diff,
                  py::arg("rho"),
                  py::arg("c"),
                  R"pbdoc(
        Transverse pressure difference 0.25 * ρ * c^2.
    )pbdoc");

        m.def("swirl_energy", &sst::FluidDynamics::swirl_energy,
                  py::arg("rho"),
                  py::arg("omega"),
                  R"pbdoc(
        Rotational kinetic energy density (1/2) * ρ * ω^2.
    )pbdoc");

        m.def("kairos_energy_trigger", &sst::FluidDynamics::kairos_energy_trigger,
                  py::arg("rho"),
                  py::arg("omega"),
                  py::arg("Ce"),
                  R"pbdoc(
        Trigger when swirl energy exceeds 0.5 * ρ * Ce^2.
    )pbdoc");

        m.def("compute_helicity", &sst::FluidDynamics::compute_helicity,
                  py::arg("velocity"),
                  py::arg("vorticity"),
                  py::arg("dV"),
                  R"pbdoc(
        Compute helicity ∑ (v · ω) dV over a discretized field.
    )pbdoc");

        m.def("potential_vorticity", &sst::FluidDynamics::potential_vorticity,
                  py::arg("fa"),
                  py::arg("zeta_r"),
                  py::arg("h"),
                  R"pbdoc(
        Potential vorticity (fa + ζ_r) / h.
    )pbdoc");
        m.def("is_incompressible", &sst::FluidDynamics::is_incompressible,
                  py::arg("dudx"),
                  py::arg("dvdy"),
                  py::arg("dwdz"),
                  R"pbdoc(
        Determine if flow is incompressible by checking that the
        divergence of the velocity field is approximately zero.
    )pbdoc");

		m.def("circulation_surface_integral", &sst::FluidDynamics::circulation_surface_integral,
			  py::arg("omega_field"), py::arg("dA_field"),
			  R"pbdoc(Circulation as surface integral of vorticity dot area vector.
	)pbdoc");

		m.def("enstrophy", &sst::FluidDynamics::enstrophy,
			  py::arg("omega_squared"), py::arg("ds_area"),
			  R"pbdoc(Enstrophy as sum of squared vorticity weighted by area.
	)pbdoc");

		// Pressure field methods (from PressureField)
		m.def("compute_bernoulli_pressure", &sst::FluidDynamics::compute_bernoulli_pressure,
			  py::arg("velocity_magnitude"), py::arg("rho") = 7.0e-7, py::arg("p_inf") = 0.0,
			  R"pbdoc(Compute Bernoulli pressure field from velocity magnitude.
	)pbdoc");

		m.def("pressure_gradient", &sst::FluidDynamics::pressure_gradient,
			  py::arg("pressure_field"), py::arg("dx") = 1.0, py::arg("dy") = 1.0,
			  R"pbdoc(Compute spatial pressure gradient vector field.
	)pbdoc");

		// Potential flow methods (from PotentialFlow)
		m.def("laplacian_phi", &sst::FluidDynamics::laplacian_phi,
			  py::arg("d2phidx2"), py::arg("d2phidy2"), py::arg("d2phidz2"),
			  R"pbdoc(Compute Laplacian of potential function.
	)pbdoc");

		m.def("grad_phi", &sst::FluidDynamics::grad_phi,
			  py::arg("phi_grad"),
			  R"pbdoc(Compute gradient of potential function.
	)pbdoc");

		m.def("bernoulli_pressure_potential", &sst::FluidDynamics::bernoulli_pressure_potential,
			  py::arg("velocity_squared"), py::arg("V"),
			  R"pbdoc(Compute Bernoulli pressure from potential flow.
	)pbdoc");

		// Kinetic energy methods (from KineticEnergy)
		m.def("compute_kinetic_energy", &sst::FluidDynamics::compute_kinetic_energy,
			  py::arg("velocity"), py::arg("rho_ae"),
			  R"pbdoc(Compute kinetic energy E = (1/2) * ρ * ∑ |v|^2.
	)pbdoc");

		// Fluid rotation methods (from FluidRotation)
		m.def("rossby_number", &sst::FluidDynamics::rossby_number,
			  py::arg("U"), py::arg("omega"), py::arg("d"),
			  R"pbdoc(Rossby number: Ro = U / (2Ωd).
	)pbdoc");

		m.def("ekman_number", &sst::FluidDynamics::ekman_number,
			  py::arg("nu"), py::arg("omega"), py::arg("H"),
			  R"pbdoc(Ekman number: Ek = ν / (Ω H²).
	)pbdoc");

		m.def("cylinder_mass", &sst::FluidDynamics::cylinder_mass,
			  py::arg("rho"), py::arg("R"), py::arg("H"),
			  R"pbdoc(Cylinder mass: m = ρ π R² H.
	)pbdoc");

		m.def("cylinder_inertia", &sst::FluidDynamics::cylinder_inertia,
			  py::arg("mass"), py::arg("R"),
			  R"pbdoc(Moment of inertia: I = (1/2) m R².
	)pbdoc");

		m.def("torque", &sst::FluidDynamics::torque,
			  py::arg("inertia"), py::arg("alpha"),
			  R"pbdoc(Torque: τ = I α.
	)pbdoc");
}