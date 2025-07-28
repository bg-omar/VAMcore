//
// Created by mr on 7/28/2025.
//
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/potential_flow.h"

namespace py = pybind11;
using namespace vam;

void bind_potential_flow(py::module_& m) {
  m.def("laplacian_phi", &PotentialFlow::laplacian_phi);
  m.def("grad_phi", &PotentialFlow::grad_phi);
  m.def("bernoulli_pressure", &PotentialFlow::bernoulli_pressure);
}
