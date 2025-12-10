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

  // ===== Biot-Savart and Helicity Calculations =====
  m.def("compute_biot_savart_velocity_grid",
        [](py::object curve_like, py::object grid_like) {
          std::vector<Vec3> curve, grid;
          if (py::isinstance<py::array>(curve_like)) {
            curve = to_vec3(curve_like.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>());
          } else {
            curve = curve_like.cast<std::vector<Vec3>>();
          }
          if (py::isinstance<py::array>(grid_like)) {
            grid = to_vec3(grid_like.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>());
          } else {
            grid = grid_like.cast<std::vector<Vec3>>();
          }
          std::vector<Vec3> result = KnotDynamics::compute_biot_savart_velocity_grid(curve, grid);
          py::array_t<double> out({(py::ssize_t)result.size(), (py::ssize_t)3});
          auto o = out.mutable_unchecked<2>();
          for (size_t i = 0; i < result.size(); ++i) {
            o((py::ssize_t)i, 0) = result[i][0];
            o((py::ssize_t)i, 1) = result[i][1];
            o((py::ssize_t)i, 2) = result[i][2];
          }
          return out;
        },
        py::arg("curve"), py::arg("grid_points"),
        R"pbdoc(
Compute Biot-Savart velocity field from a closed curve at grid points.

Parameters
----------
curve : array_like, shape (N,3)
    Closed curve points.
grid_points : array_like, shape (G,3)
    Grid points where velocity is computed.

Returns
-------
array, shape (G,3)
    Velocity vectors at each grid point.
)pbdoc");

  m.def("compute_vorticity_grid",
        [](py::array_t<double, py::array::c_style | py::array::forcecast> velocity,
           std::array<int, 3> shape, double spacing) {
          std::vector<Vec3> vel = to_vec3(velocity);
          std::vector<Vec3> result = KnotDynamics::compute_vorticity_grid(vel, shape, spacing);
          py::array_t<double> out({(py::ssize_t)result.size(), (py::ssize_t)3});
          auto o = out.mutable_unchecked<2>();
          for (size_t i = 0; i < result.size(); ++i) {
            o((py::ssize_t)i, 0) = result[i][0];
            o((py::ssize_t)i, 1) = result[i][1];
            o((py::ssize_t)i, 2) = result[i][2];
          }
          return out;
        },
        py::arg("velocity"), py::arg("shape"), py::arg("spacing"),
        R"pbdoc(
Compute vorticity from velocity field on a regular grid.

Parameters
----------
velocity : array, shape (N,3)
    Velocity field on grid.
shape : tuple of 3 ints
    Grid shape (nx, ny, nz).
spacing : float
    Grid spacing.

Returns
-------
array, shape (N,3)
    Vorticity field.
)pbdoc");

  m.def("extract_interior_field",
        [](py::array_t<double, py::array::c_style | py::array::forcecast> field,
           std::array<int, 3> shape, int margin) {
          std::vector<Vec3> f = to_vec3(field);
          std::vector<Vec3> result = KnotDynamics::extract_interior_field(f, shape, margin);
          py::array_t<double> out({(py::ssize_t)result.size(), (py::ssize_t)3});
          auto o = out.mutable_unchecked<2>();
          for (size_t i = 0; i < result.size(); ++i) {
            o((py::ssize_t)i, 0) = result[i][0];
            o((py::ssize_t)i, 1) = result[i][1];
            o((py::ssize_t)i, 2) = result[i][2];
          }
          return out;
        },
        py::arg("field"), py::arg("shape"), py::arg("margin"),
        R"pbdoc(
Extract cubic interior field subset.

Parameters
----------
field : array, shape (N,3)
    Field on full grid.
shape : tuple of 3 ints
    Grid shape (nx, ny, nz).
margin : int
    Margin to exclude from each side.

Returns
-------
array, shape (M,3)
    Interior field subset.
)pbdoc");

  m.def("compute_helicity_invariants",
        [](py::array_t<double, py::array::c_style | py::array::forcecast> v_sub,
           py::array_t<double, py::array::c_style | py::array::forcecast> w_sub,
           py::array_t<double, py::array::c_style | py::array::forcecast> r_sq) {
          std::vector<Vec3> v = to_vec3(v_sub);
          std::vector<Vec3> w = to_vec3(w_sub);
          if (r_sq.ndim() != 1 || r_sq.shape(0) != (py::ssize_t)v.size()) {
            throw std::invalid_argument("r_sq must be 1D with same length as v_sub/w_sub");
          }
          std::vector<double> r_sq_vec;
          auto r_sq_raw = r_sq.unchecked<1>();
          for (py::ssize_t i = 0; i < r_sq.shape(0); ++i) {
            r_sq_vec.push_back(r_sq_raw(i));
          }
          auto [H_charge, H_mass, a_mu] = KnotDynamics::compute_helicity_invariants(v, w, r_sq_vec);
          return py::make_tuple(H_charge, H_mass, a_mu);
        },
        py::arg("v_sub"), py::arg("w_sub"), py::arg("r_sq"),
        R"pbdoc(
Compute helicity invariants (H_charge, H_mass, a_mu).

Parameters
----------
v_sub : array, shape (M,3)
    Interior velocity field.
w_sub : array, shape (M,3)
    Interior vorticity field.
r_sq : array, shape (M,)
    Squared distances from origin for interior points.

Returns
-------
tuple
    (H_charge, H_mass, a_mu)
)pbdoc");

  m.def("compute_helicity_from_fourier_block",
        [](const FourierBlock& block,
           int grid_size, double spacing, int interior_margin, int nsamples) {
          auto [H_charge, H_mass, a_mu] = KnotDynamics::compute_helicity_from_fourier_block(
              block, grid_size, spacing, interior_margin, nsamples);
          return py::make_tuple(H_charge, H_mass, a_mu);
        },
        py::arg("block"), py::arg("grid_size") = 32, py::arg("spacing") = 0.1,
        py::arg("interior_margin") = 8, py::arg("nsamples") = 1000,
        R"pbdoc(
Compute helicity invariants from a Fourier block (high-level convenience method).

This method performs the full workflow:
1. Evaluates Fourier block to get knot points
2. Computes velocity on grid
3. Computes vorticity
4. Extracts interior
5. Computes invariants

Parameters
----------
block : FourierBlock
    Fourier series coefficients.
grid_size : int
    Grid size (default: 32).
spacing : float
    Grid spacing (default: 0.1).
interior_margin : int
    Interior margin to exclude (default: 8).
nsamples : int
    Number of samples for knot evaluation (default: 1000).

Returns
-------
tuple
    (H_charge, H_mass, a_mu)
)pbdoc");

  // ===== FourierKnot Curvature =====
  m.def("compute_curvature",
        [](py::array_t<double, py::array::c_style | py::array::forcecast> pts, double eps) {
          std::vector<Vec3> points = to_vec3(pts);
          std::vector<double> result = FourierKnot::curvature(points, eps);
          py::array_t<double> out((py::ssize_t)result.size());
          auto o = out.mutable_unchecked<1>();
          for (size_t i = 0; i < result.size(); ++i) {
            o((py::ssize_t)i) = result[i];
          }
          return out;
        },
        py::arg("points"), py::arg("eps") = 1e-8,
        R"pbdoc(
Compute discrete curvature from points using central differences (periodic curve).

Parameters
----------
points : array, shape (N,3)
    Curve points.
eps : float
    Small epsilon for numerical stability (default: 1e-8).

Returns
-------
array, shape (N,)
    Curvature values at each point.
)pbdoc");

  // ===== Load All Knots =====
  py::class_<FourierKnot::LoadedKnot>(m, "LoadedKnot")
      .def_readonly("name", &FourierKnot::LoadedKnot::name)
      .def_readonly("points", &FourierKnot::LoadedKnot::points)
      .def_readonly("curvature", &FourierKnot::LoadedKnot::curvature)
      .def("get_points_array",
           [](const FourierKnot::LoadedKnot& knot) {
             py::array_t<double> out({(py::ssize_t)knot.points.size(), (py::ssize_t)3});
             auto o = out.mutable_unchecked<2>();
             for (size_t i = 0; i < knot.points.size(); ++i) {
               o((py::ssize_t)i, 0) = knot.points[i][0];
               o((py::ssize_t)i, 1) = knot.points[i][1];
               o((py::ssize_t)i, 2) = knot.points[i][2];
             }
             return out;
           },
           "Get points as NumPy array (N,3)")
      .def("get_curvature_array",
           [](const FourierKnot::LoadedKnot& knot) {
             py::array_t<double> out((py::ssize_t)knot.curvature.size());
             auto o = out.mutable_unchecked<1>();
             for (size_t i = 0; i < knot.curvature.size(); ++i) {
               o((py::ssize_t)i) = knot.curvature[i];
             }
             return out;
           },
           "Get curvature as NumPy array (N,)");

  m.def("load_all_knots",
        [](const std::vector<std::string>& paths, int nsamples) {
          std::vector<FourierKnot::LoadedKnot> knots = FourierKnot::load_all_knots(paths, nsamples);
          return knots;
        },
        py::arg("paths"), py::arg("nsamples") = 1000,
        R"pbdoc(
Load all knots from a list of .fseries file paths.

This method loads all knots, evaluates them, and computes curvature.
All calculations are done in C++ - Python only receives the results for display.

Parameters
----------
paths : list of str
    List of paths to .fseries files.
nsamples : int
    Number of samples for evaluation (default: 1000).

Returns
-------
list of LoadedKnot
    List of loaded knots, each containing:
    - name: filename without extension (with 'knot'/'Knot' removed)
    - points: evaluated 3D points (N,3) - use get_points_array() for NumPy
    - curvature: curvature values (N,) - use get_curvature_array() for NumPy
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
      .def("initialize_knot_from_name", &VortexKnotSystem::initialize_knot_from_name,
           py::arg("knot_id"), py::arg("resolution") = 1000,
           R"pbdoc(
        Initialize any knot from bundled .fseries file by identifier.
        
        Examples:
            - "3_1" for Electron/Positron knot
            - "4_1" for Dark Knot
            - "5_1" for Muon knot
            - "5_2" for Up Quark knot
            - "6_1" for Down Quark knot
            - "7_1" for Tau knot
        
        The method searches for knot.{knot_id}.fseries in standard locations.
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

