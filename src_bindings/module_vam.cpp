// bindings/py_vam.cpp
#include <pybind11/pybind11.h>



namespace py = pybind11;

// Forward declaration only!
void bind_frenet_helicity(py::module_& m);
void bind_gravity_timefield(py::module_& m);
void bind_potential_timefield(py::module_& m);
void bind_biot_savart(py::module_& m);
void bind_knot_dynamics(py::module_& m);
void bind_pressure_field(py::module_& m);
void bind_time_evolution(py::module_& m);
void bind_fluid_dynamics(py::module_& m);  // Forward declare
void bind_vortex_knot_system(py::module_& m);
void bind_kinetic_energy(py::module_& m); // forward declaration
void bind_swirl_field(py::module_& m); // forward declaration

PYBIND11_MODULE(vambindings, m) {
	m.doc() = "VAM Core Bindings";

	bind_frenet_helicity(m);
	bind_potential_timefield(m);
	bind_gravity_timefield(m);
	bind_biot_savart(m);
	bind_knot_dynamics(m);
	bind_pressure_field(m);
	bind_time_evolution(m);
	bind_fluid_dynamics(m);  // Call here
	bind_vortex_knot_system(m);  // ✅ Include this
	bind_kinetic_energy(m);
	bind_swirl_field(m);
}
