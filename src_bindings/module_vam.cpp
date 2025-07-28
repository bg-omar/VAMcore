// bindings/py_vam.cpp
#include <pybind11/pybind11.h>

namespace py = pybind11;

// Forward declaration only!
void bind_biot_savart(py::module_& m);
void bind_fluid_dynamics(py::module_ &m);
void bind_fluid_rotation(py::module_ &m);
void bind_frenet_helicity(py::module_& m);
void bind_gravity_timefield(py::module_& m);
void bind_kinetic_energy(py::module_& m);
void bind_knot_dynamics(py::module_& m);
void bind_potential_flow(py::module_& m);
void bind_potential_timefield(py::module_& m);
void bind_pressure_field(py::module_& m);
void bind_radiation_flow(py::module_& m);
void bind_relative_vorticity(py::module_& m);
void bind_swirl_field(py::module_& m);
void bind_thermo_dynamics(py::module_& m);
void bind_time_evolution(py::module_& m);
void bind_vortex_knot_system(py::module_& m);
void bind_vortex_ring(py::module_& m);
void bind_vorticity_dynamics(py::module_& m);
void bind_vorticity_transport(py::module_& m);


PYBIND11_MODULE(vambindings, m) {
  m.doc() = "VAM Core Bindings";
  bind_biot_savart(m);
  bind_fluid_dynamics(m);
  bind_fluid_rotation(m);
  bind_frenet_helicity(m);
  bind_gravity_timefield(m);
  bind_kinetic_energy(m);
  bind_knot_dynamics(m);
  bind_potential_flow(m);
  bind_potential_timefield(m);
  bind_pressure_field(m);
  bind_radiation_flow(m);
  bind_relative_vorticity(m);
  bind_swirl_field(m);
  bind_thermo_dynamics(m);
  bind_time_evolution(m);
  bind_vortex_knot_system(m);
  bind_vortex_ring(m);
  bind_vorticity_dynamics(m);
  bind_vorticity_transport(m);
}
