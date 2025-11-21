//
// Created by mr on 7/28/2025.
//
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/fluid_rotation.h"

namespace py = pybind11;
using namespace sst;

void bind_fluid_rotation(py::module_& m) {
  m.def("rossby_number", &FluidRotation::rossby_number);
  m.def("ekman_number", &FluidRotation::ekman_number);
  m.def("cylinder_mass", &FluidRotation::cylinder_mass);
  m.def("cylinder_inertia", &FluidRotation::cylinder_inertia);
  m.def("torque", &FluidRotation::torque);
}