//
// Created by mr on 7/28/2025.
//
#include <pybind11/pybind11.h>
#include "../src/radiation_flow.h"

namespace py = pybind11;
using namespace sst;

void bind_radiation_flow(py::module_& m) {
  m.def("radiation_force", &RadiationFlow::radiation_force);
  m.def("van_der_pol_dx", &RadiationFlow::dxdt);
  m.def("van_der_pol_dy", &RadiationFlow::dydt);
}