//
// Created by mr on 7/28/2025.
//
#include <pybind11/pybind11.h>
#include "../src/vortex_ring.h"

namespace py = pybind11;
using namespace vam;

void bind_vortex_ring(py::module_& m) {
  m.def("lamb_oseen_velocity", &VortexRing::lamb_oseen_velocity);
  m.def("lamb_oseen_vorticity", &VortexRing::lamb_oseen_vorticity);
  m.def("hill_streamfunction", &VortexRing::hill_streamfunction);
  m.def("hill_vorticity", &VortexRing::hill_vorticity);
  m.def("hill_circulation", &VortexRing::hill_circulation);
  m.def("hill_velocity", &VortexRing::hill_velocity);
}
