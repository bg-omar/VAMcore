// src_bindings/py_knot_pd.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <stdexcept>
#include "../src/knot_pd.h"

namespace py = pybind11;
using sst::Vec3;
using sst::PD;

// Accept a NumPy (N,3) array (C-contiguous or force-castable) and return std::vector<Vec3>
static std::vector<Vec3> to_vec3(
    py::array_t<double, py::array::c_style | py::array::forcecast> arr)
{
  if (arr.ndim() != 2 || arr.shape(1) != 3)
    throw std::invalid_argument("pd_from_curve: expected array with shape (N,3)");

  const py::ssize_t N = arr.shape(0);
  std::vector<Vec3> out(static_cast<std::size_t>(N));

  auto buf = arr.unchecked<2>();
  for (py::ssize_t i = 0; i < N; ++i) {
    out[static_cast<std::size_t>(i)] = { buf(i,0), buf(i,1), buf(i,2) };
  }
  return out;
}

void bind_knot_pd(py::module_& m){
  m.def("pd_from_curve",
        [](py::object P3_like, int tries, unsigned int seed){
          std::vector<Vec3> P3;
          if (py::isinstance<py::array>(P3_like)) {
            auto arr = P3_like.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
            P3 = to_vec3(arr);
          } else {
            // sequence of triples -> std::vector<std::array<double,3>>
            P3 = P3_like.cast<std::vector<Vec3>>();
          }
          PD pd = sst::pd_from_curve(P3, tries, seed);
          return pd; // -> List[List[int]]
        },
        py::arg("P3"), py::arg("tries")=40, py::arg("seed")=12345,
        R"pbdoc(
Compute a PD code from a closed 3D polygonal curve.

Parameters
----------
P3 : array_like, shape (N,3)
    Vertex list of the closed curve (segment i → i+1 mod N).
tries : int
    Random projection trials.
seed : int
    RNG seed.

Returns
-------
list[list[int]]
    PD tuples (a,b,c,d).
)pbdoc");
}