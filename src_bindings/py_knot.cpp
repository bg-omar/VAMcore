// src_bindings/py_knot.cpp - Unified knot bindings
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "../src/knot_dynamics.h"

namespace py = pybind11;
using sst::FourierBlock;
using sst::FourierKnot;
using sst::Vec3;
using sst::KnotDynamics;
using sst::VortexKnotSystem;

static void _check_1d_same_len(const py::array &a, const py::array &b, const char* name){
  if(a.ndim()!=1 || b.ndim()!=1 || a.shape(0)!=b.shape(0))
    throw std::invalid_argument(std::string("fourier_knot_eval: ") + name + " must be 1D and same length");
}

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

void bind_knot(py::module_& m) {
  // ===== Fourier Knot =====
  py::class_<FourierBlock>(m, "FourierBlock")
      .def(py::init<>())
      .def_readwrite("header", &FourierBlock::header)
      .def_readwrite("a_x", &FourierBlock::a_x)
      .def_readwrite("b_x", &FourierBlock::b_x)
      .def_readwrite("a_y", &FourierBlock::a_y)
      .def_readwrite("b_y", &FourierBlock::b_y)
      .def_readwrite("a_z", &FourierBlock::a_z)
      .def_readwrite("b_z", &FourierBlock::b_z);

  py::class_<FourierKnot>(m, "fourier_knot")
      .def(py::init<>())
      .def("loadBlocks", &FourierKnot::loadBlocks)
      .def("selectMaxHarmonics", &FourierKnot::selectMaxHarmonics)
      .def("reconstruct", &FourierKnot::reconstruct)
      .def_readwrite("points", &FourierKnot::points)
      .def_readwrite("blocks", &FourierKnot::blocks)
      .def_readwrite("activeBlock", &FourierKnot::activeBlock);

  m.def("parse_fseries_multi", &FourierKnot::parse_fseries_multi,
        py::arg("path"), "Parse a .fseries file into Fourier blocks.");

  m.def("index_of_largest_block", &FourierKnot::index_of_largest_block,
        py::arg("blocks"), "Return index of block with most harmonics.");

  m.def("evaluate_fourier_block", &FourierKnot::evaluate,
        py::arg("block"), py::arg("s"),
        "Evaluate r(s) for the given Fourier block.");

  // Numpy-friendly alias: fourier_knot_eval(a_x,b_x,a_y,b_y,a_z,b_z, s) -> (x,y,z)
  m.def("fourier_knot_eval",
        [](py::array_t<double, py::array::c_style | py::array::forcecast> a_x,
           py::array_t<double, py::array::c_style | py::array::forcecast> b_x,
           py::array_t<double, py::array::c_style | py::array::forcecast> a_y,
           py::array_t<double, py::array::c_style | py::array::forcecast> b_y,
           py::array_t<double, py::array::c_style | py::array::forcecast> a_z,
           py::array_t<double, py::array::c_style | py::array::forcecast> b_z,
           py::array_t<double, py::array::c_style | py::array::forcecast> s)
        {
          _check_1d_same_len(a_x, b_x, "a_x/b_x");
          _check_1d_same_len(a_y, b_y, "a_y/b_y");
          _check_1d_same_len(a_z, b_z, "a_z/b_z");
          if(s.ndim()!=1) throw std::invalid_argument("fourier_knot_eval: s must be 1D");

          FourierBlock blk;
          auto ax=a_x.unchecked<1>(), bx=b_x.unchecked<1>();
          auto ay=a_y.unchecked<1>(), by=b_y.unchecked<1>();
          auto az=a_z.unchecked<1>(), bz=b_z.unchecked<1>();
          const py::ssize_t M = ax.shape(0);
          blk.a_x.resize(M); blk.b_x.resize(M);
          blk.a_y.resize(M); blk.b_y.resize(M);
          blk.a_z.resize(M); blk.b_z.resize(M);
          for(py::ssize_t i=0;i<M;++i){
            blk.a_x[i]=ax(i); blk.b_x[i]=bx(i);
            blk.a_y[i]=ay(i); blk.b_y[i]=by(i);
            blk.a_z[i]=az(i); blk.b_z[i]=bz(i);
          }

          std::vector<double> S; S.reserve(static_cast<size_t>(s.shape(0)));
          auto sraw=s.unchecked<1>();
          for(py::ssize_t i=0;i<s.shape(0);++i) S.push_back(sraw(i));

          std::vector<Vec3> P = sst::FourierKnot::evaluate(blk, S);

          py::array_t<double> x(s.shape(0)), y(s.shape(0)), z(s.shape(0));
          auto xr=x.mutable_unchecked<1>();
          auto yr=y.mutable_unchecked<1>();
          auto zr=z.mutable_unchecked<1>();
          for(py::ssize_t i=0;i<s.shape(0);++i){
            xr(i)=P[(size_t)i][0];
            yr(i)=P[(size_t)i][1];
            zr(i)=P[(size_t)i][2];
          }
          return py::make_tuple(std::move(x), std::move(y), std::move(z));
        },
        py::arg("a_x"), py::arg("b_x"), py::arg("a_y"), py::arg("b_y"),
        py::arg("a_z"), py::arg("b_z"), py::arg("s"),
        "NumPy-friendly Fourier evaluation returning (x,y,z)");

  // ===== Knot Dynamics (merged from knot_dynamics, heavy_knot, knot_pd) =====
  py::class_<KnotDynamics::FourierResult>(m, "FourierResult")
      .def_readonly("positions", &KnotDynamics::FourierResult::positions)
      .def_readonly("tangents", &KnotDynamics::FourierResult::tangents);

  m.def("compute_writhe", &sst::KnotDynamics::compute_writhe, R"pbdoc(
        Compute the writhe of a closed filament (topological self-linking).
    )pbdoc");

  m.def("compute_linking_number", &sst::KnotDynamics::compute_linking_number, R"pbdoc(
        Compute the Gauss linking number between two closed loops.
    )pbdoc");

  m.def("compute_twist", &sst::KnotDynamics::compute_twist, R"pbdoc(
        Compute twist from Frenet frames along a filament.
    )pbdoc");

  m.def("compute_centerline_helicity", &sst::KnotDynamics::compute_centerline_helicity, R"pbdoc(
        Compute the centerline helicity as the sum of writhe and twist.
    )pbdoc");

  m.def("detect_reconnection_candidates", &sst::KnotDynamics::detect_reconnection_candidates, R"pbdoc(
        Detect pairs of points on the filament that approach closely enough to be candidates for reconnection.
    )pbdoc");

  m.def("evaluate_fourier_series", &KnotDynamics::evaluate_fourier_series,
        "Evaluate a Fourier series for positions and tangents");

  m.def("writhe_gauss_curve", &KnotDynamics::writhe_gauss_curve,
        "Compute writhe via Gauss integral");

  m.def("estimate_crossing_number", &KnotDynamics::estimate_crossing_number,
        py::arg("r"), py::arg("directions") = 24, py::arg("seed") = 12345,
        "Estimate crossing number from projections");

  m.def("pd_from_curve",
        [](py::object P3_like, int tries, unsigned int seed, double min_angle_deg, double depth_tol){
          std::vector<Vec3> P3;
          if (py::isinstance<py::array>(P3_like)) {
            auto arr = P3_like.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
            P3 = to_vec3(arr);
          } else {
            P3 = P3_like.cast<std::vector<Vec3>>();
          }
          KnotDynamics::PD pd = KnotDynamics::pd_from_curve(P3, tries, seed, min_angle_deg, depth_tol);
          return pd;
        },
        py::arg("P3"), py::arg("tries")=40, py::arg("seed")=12345, py::arg("min_angle_deg")=1.0, py::arg("depth_tol")=1e-6,
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
min_angle_deg : float
    Minimum crossing angle in degrees.
depth_tol : float
    Depth tolerance for crossing detection.

Returns
-------
list[list[int]]
    PD tuples (a,b,c,d).
)pbdoc");

  // ===== Vortex Knot System =====
  py::class_<VortexKnotSystem, std::shared_ptr<VortexKnotSystem>>(m, "VortexKnotSystem")
      .def(py::init<double>(), py::arg("circulation") = 1.0,
           R"pbdoc(
        Initialize a VortexKnotSystem with optional circulation parameter.
        
        Args:
            circulation (float): Circulation strength (default = 1.0).
    )pbdoc")
      .def("initialize_trefoil_knot", &VortexKnotSystem::initialize_trefoil_knot,
           py::arg("resolution") = 400,
           R"pbdoc(
        Initialize a trefoil knot with given resolution (default = 400 points).
    )pbdoc")
      .def("initialize_figure8_knot", &VortexKnotSystem::initialize_figure8_knot,
           py::arg("resolution") = 400,
           R"pbdoc(
        Initialize a figure-eight knot with given resolution (default = 400 points).
    )pbdoc")
      .def("evolve", &VortexKnotSystem::evolve,
           py::arg("dt"), py::arg("steps"),
           R"pbdoc(
        Evolve vortex knot using Biot–Savart dynamics.
    )pbdoc")
      .def("get_positions", &VortexKnotSystem::get_positions,
           py::return_value_policy::reference,
           R"pbdoc(
        Get current 3D positions of the knot.
    )pbdoc")
      .def("get_tangents", &VortexKnotSystem::get_tangents,
           py::return_value_policy::reference,
           R"pbdoc(
        Get current tangent vectors of the knot.
    )pbdoc");
}

