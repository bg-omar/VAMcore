//
// Created by mr on 8/15/2025.
//
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "heavy_knot.h"

namespace py = pybind11;
using namespace vam;

void bind_heavy_knot(py::module_& m) {
  py::class_<FourierResult>(m, "FourierResult")
      .def_readonly("positions", &FourierResult::positions)
      .def_readonly("tangents", &FourierResult::tangents);

  m.def("evaluate_fourier_series", &evaluate_fourier_series,
        "Evaluate a Fourier series for positions and tangents");

  m.def("writhe_gauss_curve", &writhe_gauss_curve,
        "Compute writhe via Gauss integral");

  m.def("estimate_crossing_number", &estimate_crossing_number,
        py::arg("r"), py::arg("directions") = 24, py::arg("seed") = 12345,
        "Estimate crossing number from projections");
}
