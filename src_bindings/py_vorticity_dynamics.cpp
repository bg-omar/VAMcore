// py_vorticity_dynamics.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/vorticity_dynamics.h"

namespace py = pybind11;

void bind_vorticity_dynamics(py::module_& m) {
	m.def("vorticity_z_2D", &sst::VorticityDynamics::vorticity_z_2D,
		  py::arg("dv_dx"), py::arg("du_dy"),
		  "Compute 2D vorticity: dv/dx - du/dy");

	m.def("local_circulation_density", &sst::VorticityDynamics::local_circulation_density,
		  py::arg("dv_dx"), py::arg("du_dy"),
		  "Local circulation density (vorticity) via Stokes' theorem");

	m.def("solid_body_rotation_vorticity", &sst::VorticityDynamics::solid_body_rotation_vorticity,
		  py::arg("omega"), "Vorticity of solid body rotation: 2 * omega");

	m.def("couette_vorticity", &sst::VorticityDynamics::couette_vorticity,
		  py::arg("alpha"), "Vorticity of Couette flow: -alpha");

	m.def("crocco_relation", &sst::VorticityDynamics::crocco_relation,
		  py::arg("vorticity"), py::arg("rho"), py::arg("pressure_gradient"),
		  "Velocity-curl product equals pressure gradient divided by density (Crocco's theorem)");

	m.def("compute_vorticity", &sst::VorticityDynamics::compute_vorticity2D,
		  "Compute 2D vorticity field", py::arg("u"), py::arg("v"), py::arg("nx"), py::arg("ny"), py::arg("dx"), py::arg("dy"),
			"Vorticity tools for 2D flows");

	// Relative vorticity methods (from Relative_Vorticity)
	m.def("rotating_frame_rhs", &sst::VorticityDynamics::rotating_frame_rhs,
		  py::arg("velocity"), py::arg("vorticity"), py::arg("grad_phi"), py::arg("grad_p"), py::arg("omega"), py::arg("rho"),
		  "Compute rotating frame momentum RHS");

	m.def("crocco_gradient", &sst::VorticityDynamics::crocco_gradient,
		  py::arg("velocity"), py::arg("vorticity"), py::arg("grad_phi"), py::arg("grad_p"), py::arg("rho"),
		  "Compute ∇H from Crocco's theorem");

	// Vorticity transport methods (from VorticityTransport)
	m.def("baroclinic_term", &sst::VorticityDynamics::baroclinic_term,
		  py::arg("grad_rho"), py::arg("grad_p"), py::arg("rho"),
		  "Baroclinic torque term");

	m.def("compute_vorticity_rhs", &sst::VorticityDynamics::compute_vorticity_rhs,
		  py::arg("omega"), py::arg("grad_u"), py::arg("div_u"), py::arg("grad_rho"), py::arg("grad_p"), py::arg("rho"),
		  "Vorticity transport RHS");
}