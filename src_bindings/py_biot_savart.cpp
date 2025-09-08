// src_bindings/py_biot_savart.cpp  (your file, extended)
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "../src/biot_savart.h"

namespace py = pybind11;
using namespace vam;

static std::vector<Vec3> to_vec3_list(
    py::array_t<double, py::array::c_style | py::array::forcecast> arr)
{
  if(arr.ndim()!=2 || arr.shape(1)!=3)
    throw std::invalid_argument("Expected array with shape (N,3)");
  const py::ssize_t N = arr.shape(0);
  std::vector<Vec3> out((size_t)N);
  auto a = arr.unchecked<2>();
  for(py::ssize_t i=0;i<N;++i){
    out[(size_t)i] = { a(i,0), a(i,1), a(i,2) };
  }
  return out;
}

void bind_biot_savart(py::module_& m) {
  py::class_<BiotSavart>(m, "BiotSavart")
      .def_static("compute_velocity",   &BiotSavart::computeVelocity)
      .def_static("compute_vorticity",  &BiotSavart::computeVorticity)
      .def_static("extract_interior",   &BiotSavart::extractInterior)
      .def_static("compute_invariants", &BiotSavart::computeInvariants);

  m.def("biot_savart_velocity", &vam::BiotSavart::velocity,
        py::arg("r"), py::arg("filament_points"),
        py::arg("tangent_vectors"), py::arg("circulation") = 1.0,
        "Velocity at a single point r due to a filament.");

  // Convenience: grid-based velocity  (polyline (N,3), grid (G,3)) -> (G,3)
  m.def("biot_savart_velocity_grid",
        [](py::array_t<double, py::array::c_style | py::array::forcecast> polyline,
           py::array_t<double, py::array::c_style | py::array::forcecast> grid)
        {
          auto wire = to_vec3_list(polyline);
          auto pts  = to_vec3_list(grid);
          std::vector<Vec3> V = BiotSavart::computeVelocity(wire, pts);

          // pack to NumPy (G,3)
          const py::ssize_t G = (py::ssize_t)V.size();
          py::array_t<double> out({G,(py::ssize_t)3});
          auto o = out.mutable_unchecked<2>();
          for(py::ssize_t i=0;i<G;++i){
            o(i,0)=V[(size_t)i][0];
            o(i,1)=V[(size_t)i][1];
            o(i,2)=V[(size_t)i][2];
          }
          return out;
        },
        py::arg("polyline"), py::arg("grid"),
        "Biot–Savart velocity at arbitrary grid points for a polyline");
}
