//
// Created by mr on 3/22/2025.
//
// bindings/py_pressure_field.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/pressure_field.h"

namespace py = pybind11;

void bind_pressure_field(py::module_& m) {
        m.def("compute_bernoulli_pressure", &sst::PressureField::compute_bernoulli_pressure, R"pbdoc(
        Compute Bernoulli pressure field from velocity magnitude.
    )pbdoc");

        m.def("pressure_gradient", &sst::PressureField::pressure_gradient, R"pbdoc(
        Compute spatial pressure gradient vector field.
    )pbdoc");
}