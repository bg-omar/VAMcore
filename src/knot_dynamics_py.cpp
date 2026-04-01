// src/knot_dynamics_py.cpp - Unified knot bindings
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "knot_dynamics.h"

namespace py = pybind11;
using sst::FourierBlock;
using sst::FourierKnot;
using sst::Vec3;
using sst::KnotDynamics;
using sst::VortexKnotSystem;
using IdealABBlock = sst::FourierKnot::IdealABBlock;
using IdealABComponent = sst::FourierKnot::IdealABComponent;

static void _check_1d_same_len(const py::array &a, const py::array &b, const char* name){
  if(a.ndim()!=1 || b.ndim()!=1 || a.shape(0)!=b.shape(0))
    throw std::invalid_argument(std::string("fourier_knot_eval: ") + name + " must be 1D and same length");
}

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
  py::class_<FourierBlock>(m, "FourierBlock")
      .def(py::init<>())
      .def_readwrite("header", &FourierBlock::header)
      .def_readwrite("a_x", &FourierBlock::a_x)
      .def_readwrite("b_x", &FourierBlock::b_x)
      .def_readwrite("a_y", &FourierBlock::a_y)
      .def_readwrite("b_y", &FourierBlock::b_y)
      .def_readwrite("a_z", &FourierBlock::a_z)
      .def_readwrite("b_z", &FourierBlock::b_z);

  py::class_<IdealABComponent>(m, "IdealABComponent")
      .def(py::init<>())
      .def_readwrite("component_index", &IdealABComponent::component_index)
      .def_readwrite("A0", &IdealABComponent::A0)
      .def_readwrite("B0", &IdealABComponent::B0)
      .def_readwrite("fourier", &IdealABComponent::fourier);

  py::class_<IdealABBlock>(m, "IdealABBlock")
      .def(py::init<>())
      .def_readwrite("id", &IdealABBlock::id)
      .def_readwrite("conway", &IdealABBlock::conway)
      .def_readwrite("L", &IdealABBlock::L)
      .def_readwrite("D", &IdealABBlock::D)
      .def_readwrite("n", &IdealABBlock::n)
      .def_readwrite("components", &IdealABBlock::components)
      .def_readwrite("fourier", &IdealABBlock::fourier);

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

  m.def("parse_ideal_txt_multi", &FourierKnot::parse_ideal_txt_multi,
        py::arg("path"), "Parse an ideal.txt-style file into IdealABBlock entries.");

  m.def("parse_ideal_txt_from_string", &FourierKnot::parse_ideal_txt_from_string,
        py::arg("content"), "Parse ideal.txt-style content string into IdealABBlock entries.");

  m.def("index_of_ideal_id", &FourierKnot::index_of_ideal_id,
        py::arg("blocks"), py::arg("id"),
        "Return index of IdealABBlock with given id, or -1 if not found.");

  m.def("index_of_largest_block", &FourierKnot::index_of_largest_block,
        py::arg("blocks"), "Return index of block with most harmonics.");

  m.def("evaluate_fourier_block", &FourierKnot::evaluate,
        py::arg("block"), py::arg("s"),
        "Evaluate r(s) for the given Fourier block.");

  m.def("evaluate_with_derivatives",
        &FourierKnot::evaluate_with_derivatives,
        py::arg("block"), py::arg("s"),
        "Evaluate Fourier block and its first three derivatives at parameter s.");

  m.def("curvature_exact",
        &FourierKnot::curvature_exact,
        py::arg("block"), py::arg("s"), py::arg("eps") = 1e-12,
        "Compute exact curvature from Fourier coefficients at sample parameters.");

  m.def("length_exact",
        &FourierKnot::length_exact,
        py::arg("block"), py::arg("nsamples") = 4096,
        "Compute exact length of Fourier curve by sampling.");

  m.def("bending_energy_exact",
        &FourierKnot::bending_energy_exact,
        py::arg("block"), py::arg("nsamples") = 4096, py::arg("eps") = 1e-12,
        "Compute bending energy integral of Fourier curve.");

  m.def("mode_energies",
        &FourierKnot::mode_energies,
        py::arg("block"),
        "Compute per-mode energy from Fourier coefficients.");

  m.def("min_self_distance_sampled",
        &FourierKnot::min_self_distance_sampled,
        py::arg("points"), py::arg("exclude_window") = 4,
        "Compute minimum self-distance of a closed polygonal curve.");

  m.def("min_self_distance_exactish",
        &FourierKnot::min_self_distance_exactish,
        py::arg("block"), py::arg("nsamples") = 2048, py::arg("exclude_window") = 4,
        "Estimate minimum self-distance of Fourier curve via sampling.");

  py::class_<FourierKnot::GeometricDescriptors>(m, "GeometricDescriptors")
      .def_readonly("L", &FourierKnot::GeometricDescriptors::L)
      .def_readonly("bending_energy", &FourierKnot::GeometricDescriptors::bending_energy)
      .def_readonly("min_self_distance", &FourierKnot::GeometricDescriptors::min_self_distance)
      .def_readonly("writhe", &FourierKnot::GeometricDescriptors::writhe)
      .def_readonly("mode_energy", &FourierKnot::GeometricDescriptors::mode_energy);

  m.def("describe_fourier_block",
        &FourierKnot::describe_fourier_block,
        py::arg("block"), py::arg("nsamples") = 2048, py::arg("exclude_window") = 4,
        "Compute geometric descriptors (length, bending energy, self-distance, writhe, mode energies) for a Fourier block.");

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
)pbdoc");

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
        R"pbdoc(Compute Biot-Savart velocity field from a closed curve at grid points.)pbdoc");

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
        R"pbdoc(Compute vorticity from velocity field on a regular grid.)pbdoc");

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
        R"pbdoc(Extract cubic interior field subset.)pbdoc");

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
        R"pbdoc(Compute helicity invariants (H_charge, H_mass, a_mu).)pbdoc");

  m.def("compute_helicity_from_fourier_block",
        [](const FourierBlock& block,
           int grid_size, double spacing, int interior_margin, int nsamples) {
          auto [H_charge, H_mass, a_mu] = KnotDynamics::compute_helicity_from_fourier_block(
              block, grid_size, spacing, interior_margin, nsamples);
          return py::make_tuple(H_charge, H_mass, a_mu);
        },
        py::arg("block"), py::arg("grid_size") = 32, py::arg("spacing") = 0.1,
        py::arg("interior_margin") = 8, py::arg("nsamples") = 1000,
        R"pbdoc(Compute helicity invariants from a Fourier block.)pbdoc");

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
        R"pbdoc(Compute discrete curvature from points.)pbdoc");
  m.def("get_embedded_ideal_files", &sst::get_embedded_ideal_files,
        "Return embedded ideal*.txt resources as {relative_name: content}.");

  m.def("load_embedded_ideal_text", &sst::load_embedded_ideal_text,
        py::arg("name") = "ideal.txt",
        "Load embedded ideal text resource from library (basename fallback supported).");

  m.def("parse_embedded_ideal_txt",
        [](const std::string& name) {
            return sst::FourierKnot::parse_ideal_txt_from_string(sst::load_embedded_ideal_text(name));
        },
        py::arg("name") = "ideal.txt",
        "Parse embedded ideal*.txt resource into AB blocks.");

  m.def("parse_embedded_ideal_ab_by_id",
        [](const std::string& ab_id, const std::string& name) {
            return sst::FourierKnot::parse_ideal_ab_by_id_from_embedded(ab_id, name);
        },
        py::arg("ab_id"), py::arg("name") = "ideal.txt",
        "Parse a single AB block by Id from an embedded ideal*.txt resource.");

  m.def("parse_ideal_ab_by_id_from_string",
        &sst::FourierKnot::parse_ideal_ab_by_id_from_string,
        py::arg("content"), py::arg("ab_id"),
        "Parse a single AB block by Id from ideal.txt-style content string.");

  m.def("format_ideal_ab_header",
        &sst::FourierKnot::format_ideal_ab_header,
        py::arg("ab"),
        "Format AB metadata as: AB Id=\"...\" Conway=\"...\" L=\"...\" D=\"...\" n=\"...\"");

  // Embedded .fseries registry from compiled resources
  m.def("get_embedded_knot_files", &sst::get_embedded_knot_files,
        "Return embedded .fseries resources as {knot_id: file_content}.");

  // Parse .fseries content directly from a string (if not already exposed)
  m.def("parse_fseries_from_string", &sst::FourierKnot::parse_fseries_from_string,
        py::arg("content"),
        "Parse .fseries content string into Fourier blocks.");

  // Convenience: load embedded knot id -> select largest Fourier block
  m.def("load_embedded_knot_block",
        [](const std::string& knot_id) {
            auto files = sst::get_embedded_knot_files();
            auto it = files.find(knot_id);
            if (it == files.end()) {
                throw std::runtime_error("Embedded knot id not found: " + knot_id);
            }
            auto blocks = sst::FourierKnot::parse_fseries_from_string(it->second);
            int idx = sst::FourierKnot::index_of_largest_block(blocks);
            if (idx < 0) throw std::runtime_error("No Fourier block found in embedded knot: " + knot_id);
            return blocks[(size_t)idx];
        },
        py::arg("knot_id"),
        "Load embedded knot by id and return its largest Fourier block.");

  m.def("evaluate_ideal_component",
        [](const IdealABComponent& comp,
           py::array_t<double, py::array::c_style | py::array::forcecast> s_arr) {
          if (s_arr.ndim() != 1) throw std::invalid_argument("s must be 1D");
          std::vector<double> s;
          s.reserve(static_cast<size_t>(s_arr.shape(0)));
          auto sraw = s_arr.unchecked<1>();
          for (py::ssize_t i = 0; i < s_arr.shape(0); ++i) s.push_back(sraw(i));
          auto pts = sst::FourierKnot::evaluate_ideal_component(comp, s);
          py::array_t<double> out({(py::ssize_t)pts.size(), (py::ssize_t)3});
          auto o = out.mutable_unchecked<2>();
          for (size_t i = 0; i < pts.size(); ++i) {
              o((py::ssize_t)i, 0) = pts[i][0];
              o((py::ssize_t)i, 1) = pts[i][1];
              o((py::ssize_t)i, 2) = pts[i][2];
          }
          return out;
        },
        py::arg("component"), py::arg("s"),
        "Evaluate a single ideal AB component (includes I=0 offset).");

  m.def("evaluate_ideal_ab_components",
        [](const IdealABBlock& ab,
           py::array_t<double, py::array::c_style | py::array::forcecast> s_arr) {
          if (s_arr.ndim() != 1) throw std::invalid_argument("s must be 1D");
          std::vector<double> s;
          s.reserve(static_cast<size_t>(s_arr.shape(0)));
          auto sraw = s_arr.unchecked<1>();
          for (py::ssize_t i = 0; i < s_arr.shape(0); ++i) s.push_back(sraw(i));
          auto all = sst::FourierKnot::evaluate_ideal_ab_components(ab, s);
          py::list result;
          for (const auto& pts : all) {
              py::array_t<double> out({(py::ssize_t)pts.size(), (py::ssize_t)3});
              auto o = out.mutable_unchecked<2>();
              for (size_t i = 0; i < pts.size(); ++i) {
                  o((py::ssize_t)i, 0) = pts[i][0];
                  o((py::ssize_t)i, 1) = pts[i][1];
                  o((py::ssize_t)i, 2) = pts[i][2];
              }
              result.append(std::move(out));
          }
          return result;
        },
        py::arg("ab"), py::arg("s"),
        "Evaluate all components of an ideal AB block.");

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
        R"pbdoc(Load all knots from a list of .fseries file paths.)pbdoc");

  py::class_<VortexKnotSystem, std::shared_ptr<VortexKnotSystem>>(m, "VortexKnotSystem")
      .def(py::init<double>(), py::arg("circulation") = 1.0,
           R"pbdoc(Initialize a VortexKnotSystem with optional circulation parameter.)pbdoc")
      .def("initialize_trefoil_knot", &VortexKnotSystem::initialize_trefoil_knot,
           py::arg("resolution") = 400,
           R"pbdoc(Initialize a trefoil knot with given resolution.)pbdoc")
      .def("initialize_figure8_knot", &VortexKnotSystem::initialize_figure8_knot,
           py::arg("resolution") = 400,
           R"pbdoc(Initialize a figure-eight knot with given resolution.)pbdoc")
      .def("initialize_knot_from_name", &VortexKnotSystem::initialize_knot_from_name,
           py::arg("knot_id"), py::arg("resolution") = 1000,
           R"pbdoc(Initialize any knot from bundled .fseries file by identifier.)pbdoc")
      .def("evolve", &VortexKnotSystem::evolve,
           py::arg("dt"), py::arg("steps"),
           R"pbdoc(Evolve vortex knot using Biot–Savart dynamics.)pbdoc")
      .def("get_positions", &VortexKnotSystem::get_positions,
           py::return_value_policy::reference,
           R"pbdoc(Get current 3D positions of the knot.)pbdoc")
      .def("get_tangents", &VortexKnotSystem::get_tangents,
           py::return_value_policy::reference,
           R"pbdoc(Get current tangent vectors of the knot.)pbdoc");
}