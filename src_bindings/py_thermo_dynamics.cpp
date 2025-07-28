#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/thermo_dynamics.h"

namespace py = pybind11;

void bind_thermo_dynamics(py::module_& m) {
    m.def("potential_temperature", &vam::ThermoDynamics::potential_temperature,
          py::arg("T"), py::arg("p0"), py::arg("p"), py::arg("R"), py::arg("cp"),
"Compute potential temperature θ = T (p0/p)^k");

m.def("entropy_from_theta", &vam::ThermoDynamics::entropy_from_theta,
      py::arg("cp"), py::arg("theta"), py::arg("dtheta"),
"Entropy differential ds = cp * dθ / θ");

m.def("entropy_from_pv", &vam::ThermoDynamics::entropy_from_pv,
      py::arg("N"), py::arg("R"), py::arg("p"), py::arg("V"), py::arg("gamma"),
"Entropy from pressure and volume ds = NR/(γ-1) * (ln(p)+ln(V))");

m.def("enthalpy", &vam::ThermoDynamics::enthalpy,
      py::arg("internal_energy"), py::arg("p"), py::arg("V"),
"Enthalpy H = E + pV");
}
