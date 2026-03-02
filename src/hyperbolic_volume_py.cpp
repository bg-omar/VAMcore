// src/hyperbolic_volume_py.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "hyperbolic_volume.h"

namespace py = pybind11;

void bind_hyperbolic_volume(py::module_& m){
#ifdef SST_ENABLE_HYPVOL
  m.def("hyperbolic_volume_from_pd",
        &sst::hyperbolic_volume_from_pd,
        py::arg("pd"),
        R"pbdoc(Hyperbolic volume from PD (native).)pbdoc");
#else
  m.def("hyperbolic_volume_from_pd",
        [](const std::vector<std::array<int,4>>& pd)->double{
          py::gil_scoped_acquire gil;
          py::object mod = py::module_::import("sst_hypvol_no_deps");
          py::object fn  = mod.attr("hyperbolic_volume_from_pd");
          py::object out = fn(py::cast(pd), py::arg("verbose")=false);
          return out.cast<double>();
        },
        py::arg("pd"),
        R"pbdoc(Hyperbolic volume from PD (delegates to Python if no native solver).)pbdoc");
#endif
}
