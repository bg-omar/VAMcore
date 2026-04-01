// src/biot_savart_py.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <stdexcept>
#include <string>
#include "biot_savart.h"
#include "trefoil_closure_kernels.h"

namespace py = pybind11;
using namespace sst;

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

static void require_points_n3(py::ssize_t rows, py::ssize_t cols, const char* ctx) {
  if (cols != 3) {
    throw std::runtime_error(std::string(ctx) + ": points must have shape (N, 3)");
  }
  if (rows < 0) {
    throw std::runtime_error(std::string(ctx) + ": invalid point count");
  }
}

void bind_biot_savart(py::module_& m) {
  py::class_<BiotSavart>(m, "BiotSavart")
      .def_static(
          "compute_velocity",
          [](const std::vector<Vec3>& curve,
             const std::vector<Vec3>& grid_points,
             double circulation) {
            return BiotSavart::computeVelocity(curve, grid_points, circulation);
          },
          py::arg("curve"),
          py::arg("grid_points"),
          py::arg("circulation") = 1.0,
          "Compute the Biot–Savart velocity field from a closed curve at given grid points.\n"
          "Backward compatible with the historical 2-argument call; circulation defaults to 1.0.")
      .def_static("compute_vorticity",  &BiotSavart::computeVorticity)
      .def_static("extract_interior",   &BiotSavart::extractInterior)
      .def_static("compute_invariants", &BiotSavart::computeInvariants);

  m.def("biot_savart_velocity", &sst::BiotSavart::velocity,
        py::arg("r"), py::arg("filament_points"),
        py::arg("tangent_vectors"), py::arg("circulation") = 1.0,
        "Velocity at a single point r due to a filament.");

  // Convenience: grid-based velocity  (polyline (N,3), grid (G,3)) -> (G,3)
  m.def("biot_savart_velocity_grid",
        [](py::array_t<double, py::array::c_style | py::array::forcecast> polyline,
           py::array_t<double, py::array::c_style | py::array::forcecast> grid,
           double circulation)
        {
          auto wire = to_vec3_list(polyline);
          auto pts  = to_vec3_list(grid);
          std::vector<Vec3> V = BiotSavart::computeVelocity(wire, pts, circulation);

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
        py::arg("polyline"), py::arg("grid"), py::arg("circulation") = 1.0,
        "Biot–Savart velocity at arbitrary grid points for a polyline.\n"
        "Backward compatible with the historical 2-argument call; circulation defaults to 1.0.");

  // Drop-in aliases matching trefoil_closure/sst_core.pybind module (same names and semantics).
  m.def(
      "calculate_neumann_self_energy",
      [](py::array_t<double, py::array::c_style | py::array::forcecast> points, double rc) {
        auto r = points.unchecked<2>();
        require_points_n3(r.shape(0), r.shape(1), "calculate_neumann_self_energy");
        return sst::trefoil_neumann_self_energy(&r(0, 0), static_cast<std::size_t>(r.shape(0)), rc);
      },
      py::arg("points"),
      py::arg("rc"),
      "Calculate Neumann integral C_N(K) (trefoil_closure/sst_core compatibility).");

  m.def(
      "calculate_core_repulsion",
      [](py::array_t<double, py::array::c_style | py::array::forcecast> points, double rc) {
        auto r = points.unchecked<2>();
        require_points_n3(r.shape(0), r.shape(1), "calculate_core_repulsion");
        return sst::trefoil_core_repulsion(&r(0, 0), static_cast<std::size_t>(r.shape(0)), rc);
      },
      py::arg("points"),
      py::arg("rc"),
      "Hard-core volume repulsion (trefoil_closure/sst_core compatibility).");

  m.def(
      "calculate_length",
      [](py::array_t<double, py::array::c_style | py::array::forcecast> points) {
        auto r = points.unchecked<2>();
        require_points_n3(r.shape(0), r.shape(1), "calculate_length");
        return sst::trefoil_polyline_length(&r(0, 0), static_cast<std::size_t>(r.shape(0)));
      },
      py::arg("points"),
      "Closed polyline length L(K) (trefoil_closure/sst_core compatibility).");

  m.def(
      "calculate_writhe",
      [](py::array_t<double, py::array::c_style | py::array::forcecast> points, double rc) {
        auto r = points.unchecked<2>();
        require_points_n3(r.shape(0), r.shape(1), "calculate_writhe");
        return sst::trefoil_writhe_reg(&r(0, 0), static_cast<std::size_t>(r.shape(0)), rc);
      },
      py::arg("points"),
      py::arg("rc"),
      "Topological writhe H(K) with distance regularization rc (trefoil_closure/sst_core compatibility).");

  m.def(
      "calculate_curvature_penalty",
      [](py::array_t<double, py::array::c_style | py::array::forcecast> points) {
        auto r = points.unchecked<2>();
        require_points_n3(r.shape(0), r.shape(1), "calculate_curvature_penalty");
        return sst::trefoil_curvature_penalty_menger(&r(0, 0), static_cast<std::size_t>(r.shape(0)));
      },
      py::arg("points"),
      "Menger curvature penalty integral (trefoil_closure/sst_core compatibility).");

  m.def(
      "calculate_bs_cutoff_energy_scan",
      [](py::array_t<double, py::array::c_style | py::array::forcecast> points,
         py::array_t<double, py::array::c_style | py::array::forcecast> tangents,
         py::array_t<double, py::array::c_style | py::array::forcecast> ds_arr,
         py::array_t<double, py::array::c_style | py::array::forcecast> a_values) {
        auto pp = points.unchecked<2>();
        auto tt = tangents.unchecked<2>();
        auto ds = ds_arr.unchecked<1>();
        auto aa = a_values.unchecked<1>();
        const py::ssize_t n = pp.shape(0);
        const py::ssize_t m = aa.shape(0);
        if (tt.shape(0) != n || ds.shape(0) != n) {
          throw std::runtime_error("calculate_bs_cutoff_energy_scan: inconsistent N dimensions");
        }
        if (pp.shape(1) != 3 || tt.shape(1) != 3) {
          throw std::runtime_error("calculate_bs_cutoff_energy_scan: points/tangents must have shape (N, 3)");
        }
        std::vector<double> out = sst::bs_cutoff_energy_scan(
            &pp(0, 0), &tt(0, 0), &ds(0), static_cast<std::size_t>(n), &aa(0), static_cast<std::size_t>(m));
        py::array_t<double> numpy_out(m);
        auto e = numpy_out.mutable_unchecked<1>();
        for (py::ssize_t k = 0; k < m; ++k) {
          e(k) = out[static_cast<std::size_t>(k)];
        }
        return numpy_out;
      },
      py::arg("points"),
      py::arg("tangents"),
      py::arg("ds_arr"),
      py::arg("a_values"),
      "Accumulate a whole cutoff scan in one C++ pass (same kernel as trefoil_closure/sst_core.cpp).");

  m.def(
      "calculate_bs_cutoff_energy",
      [](py::array_t<double, py::array::c_style | py::array::forcecast> points,
         py::array_t<double, py::array::c_style | py::array::forcecast> tangents,
         py::array_t<double, py::array::c_style | py::array::forcecast> ds_arr,
         double a_cutoff) {
        auto pp = points.unchecked<2>();
        auto tt = tangents.unchecked<2>();
        auto ds = ds_arr.unchecked<1>();
        const py::ssize_t n = pp.shape(0);
        if (tt.shape(0) != n || ds.shape(0) != n) {
          throw std::runtime_error("calculate_bs_cutoff_energy: inconsistent N dimensions");
        }
        if (pp.shape(1) != 3 || tt.shape(1) != 3) {
          throw std::runtime_error("calculate_bs_cutoff_energy: points/tangents must have shape (N, 3)");
        }
        double aone = a_cutoff;
        std::vector<double> out = sst::bs_cutoff_energy_scan(
            &pp(0, 0), &tt(0, 0), &ds(0), static_cast<std::size_t>(n), &aone, 1);
        return out[0];
      },
      py::arg("points"),
      py::arg("tangents"),
      py::arg("ds_arr"),
      py::arg("a_cutoff"),
      "Single-cutoff Biot–Savart energy for closure scans.");
}
