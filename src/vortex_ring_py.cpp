// src/vortex_ring_py.cpp
#include <pybind11/pybind11.h>
#include "vortex_ring.h"

namespace py = pybind11;
using namespace sst;

void bind_vortex_ring(py::module_& m) {
  // Existing Classical Ring Bindings
  m.def("lamb_oseen_velocity", &VortexRing::lamb_oseen_velocity);
  m.def("lamb_oseen_vorticity", &VortexRing::lamb_oseen_vorticity);
  m.def("hill_streamfunction", &VortexRing::hill_streamfunction);
  m.def("hill_vorticity", &VortexRing::hill_vorticity);
  m.def("hill_circulation", &VortexRing::hill_circulation);
  m.def("hill_velocity", &VortexRing::hill_velocity);

  // Golden NLS Closure Bindings
  py::enum_<GoldenNLSClosure::DensityRegime>(m, "DensityRegime")
      .value("EFFECTIVE_FLUID", GoldenNLSClosure::DensityRegime::EFFECTIVE_FLUID)
      .value("CORE_DOMINATED", GoldenNLSClosure::DensityRegime::CORE_DOMINATED)
      .export_values();

  py::class_<GoldenNLSClosure>(m, "GoldenNLSClosure")
      .def(py::init<GoldenNLSClosure::DensityRegime>(), py::arg("regime") = GoldenNLSClosure::DensityRegime::CORE_DOMINATED)
      .def("set_regime", &GoldenNLSClosure::set_regime)
      .def("get_active_density", &GoldenNLSClosure::get_active_density)
      .def("calculate_loop_energy", &GoldenNLSClosure::calculate_loop_energy, py::arg("R"))
      .def("calculate_loop_mass", &GoldenNLSClosure::calculate_loop_mass, py::arg("R"))
      .def("calculate_screened_mass", &GoldenNLSClosure::calculate_screened_mass, py::arg("bare_mass"), py::arg("double_k"))
      .def("infer_geometric_ratio", &GoldenNLSClosure::infer_geometric_ratio,
           py::arg("target_mass") = 9.10938356e-31,
           py::arg("tolerance") = 1e-12,
           py::arg("max_iter") = 100)
      .def("infer_geometric_ratio_safe", &GoldenNLSClosure::infer_geometric_ratio_safe,
           py::arg("target_mass") = 9.10938356e-31,
           py::arg("x0") = 1.0,
           py::arg("x_min") = 1e-6,
           py::arg("x_max") = 10.0,
           py::arg("x_tol") = 1e-12,
           py::arg("f_tol") = 1e-12,
           py::arg("max_iter") = 100)
      .def("geometric_ratio_residual", &GoldenNLSClosure::geometric_ratio_residual,
           py::arg("x"),
           py::arg("target_mass") = 9.10938356e-31)
      .def_static("infer_effective_base", &GoldenNLSClosure::infer_effective_base,
           py::arg("ratio"), py::arg("exponent_n"))
      .def_static("predicted_ratio_from_base", &GoldenNLSClosure::predicted_ratio_from_base,
           py::arg("base"), py::arg("exponent_n"))
      .def_static("relative_error", &GoldenNLSClosure::relative_error,
           py::arg("predicted"), py::arg("observed"));
}