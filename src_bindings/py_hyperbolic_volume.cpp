//
// Created by mr on 8/21/2025.
//
// ./src/hyperbolic_volume.cpp
// ./src_bindings/py_hyperbolic_volume.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/hyperbolic_volume.h"

namespace py = pybind11;

void bind_hyperbolic_volume(py::module_& m){
#ifdef SST_ENABLE_HYPVOL
  // Native C++ path (you must implement sst::hyperbolic_volume_from_pd)
  m.def("hyperbolic_volume_from_pd",
        &sst::hyperbolic_volume_from_pd,
        py::arg("pd"),
        R"pbdoc(Hyperbolic volume from PD (native).)pbdoc");
#else
  // Fallback: delegate to the pure-Python engine at runtime
  m.def("hyperbolic_volume_from_pd",
        [](const std::vector<std::array<int,4>>& pd)->double{
          py::gil_scoped_acquire gil;
          py::object mod = py::module_::import("sst_hypvol_no_deps");
          py::object fn  = mod.attr("hyperbolic_volume_from_pd");
          py::object out = fn(py::cast(pd), py::arg("verbose")=false);
          return out.cast<double>();
        },
        py::arg("pd"),
        R"pbdoc(Hyperbolic volume from PD (delegates to Python if no native solver is built).)pbdoc");
#endif
}