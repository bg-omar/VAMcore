#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "./sst_extensions.h"

namespace py = pybind11;
using namespace sst::sstext;

void bind_extensions(py::module_& m) {
    py::class_<CanonicalizeResult>(m, "CanonicalizeResult")
        .def(py::init<>())
        .def_readwrite("path", &CanonicalizeResult::path)
        .def_readwrite("found_numeric_rows", &CanonicalizeResult::found_numeric_rows)
        .def_readwrite("changed", &CanonicalizeResult::changed)
        .def_readwrite("reason", &CanonicalizeResult::reason);

    py::class_<HelicityResult>(m, "HelicityResult")
        .def(py::init<>())
        .def_readwrite("path", &HelicityResult::path)
        .def_readwrite("a_mu", &HelicityResult::a_mu)
        .def_readwrite("Hc", &HelicityResult::Hc)
        .def_readwrite("Hm", &HelicityResult::Hm)
        .def_readwrite("L", &HelicityResult::L)
        .def_readwrite("kappa_max", &HelicityResult::kappa_max)
        .def_readwrite("kappa_mean", &HelicityResult::kappa_mean)
        .def_readwrite("bend_energy", &HelicityResult::bend_energy)
        .def_readwrite("min_non_neighbor_dist", &HelicityResult::min_non_neighbor_dist)
        .def_readwrite("reach_proxy", &HelicityResult::reach_proxy)
        .def_readwrite("nsamples", &HelicityResult::nsamples);

    py::class_<FilamentEnergyParams>(m, "FilamentEnergyParams")
        .def(py::init<>())
        .def_readwrite("rho_outer", &FilamentEnergyParams::rho_outer)
        .def_readwrite("rho_local", &FilamentEnergyParams::rho_local)
        .def_readwrite("Gamma", &FilamentEnergyParams::Gamma)
        .def_readwrite("a_core", &FilamentEnergyParams::a_core)
        .def_readwrite("delta", &FilamentEnergyParams::delta)
        .def_readwrite("s_cut_local", &FilamentEnergyParams::s_cut_local)
        .def_readwrite("include_nonlocal", &FilamentEnergyParams::include_nonlocal)
        .def_readwrite("include_local_match", &FilamentEnergyParams::include_local_match)
        .def_readwrite("include_core_int", &FilamentEnergyParams::include_core_int)
        .def_readwrite("c_rankine_outer", &FilamentEnergyParams::c_rankine_outer)
        .def_readwrite("nsamples", &FilamentEnergyParams::nsamples)
        .def_readwrite("skip_neighbors_base", &FilamentEnergyParams::skip_neighbors_base);

    py::class_<FilamentEnergyResult>(m, "FilamentEnergyResult")
        .def(py::init<>())
        .def_readwrite("path", &FilamentEnergyResult::path)
        .def_readwrite("L", &FilamentEnergyResult::L)
        .def_readwrite("ds_avg", &FilamentEnergyResult::ds_avg)
        .def_readwrite("m_loc", &FilamentEnergyResult::m_loc)
        .def_readwrite("E_nonlocal", &FilamentEnergyResult::E_nonlocal)
        .def_readwrite("E_local_match", &FilamentEnergyResult::E_local_match)
        .def_readwrite("E_core_int", &FilamentEnergyResult::E_core_int)
        .def_readwrite("E_total", &FilamentEnergyResult::E_total)
        .def_readwrite("kappa_max", &FilamentEnergyResult::kappa_max)
        .def_readwrite("kappa_mean", &FilamentEnergyResult::kappa_mean)
        .def_readwrite("bend_energy", &FilamentEnergyResult::bend_energy)
        .def_readwrite("min_non_neighbor_dist", &FilamentEnergyResult::min_non_neighbor_dist)
        .def_readwrite("reach_proxy", &FilamentEnergyResult::reach_proxy)
        .def_readwrite("rho_outer", &FilamentEnergyResult::rho_outer)
        .def_readwrite("rho_local", &FilamentEnergyResult::rho_local)
        .def_readwrite("Gamma", &FilamentEnergyResult::Gamma)
        .def_readwrite("a_core", &FilamentEnergyResult::a_core)
        .def_readwrite("delta", &FilamentEnergyResult::delta)
        .def_readwrite("s_cut_local", &FilamentEnergyResult::s_cut_local)
        .def_readwrite("c_rankine_outer", &FilamentEnergyResult::c_rankine_outer)
        .def_readwrite("nsamples", &FilamentEnergyResult::nsamples);

    m.def("canonicalize_fseries_file_inplace",
          &canonicalize_fseries_file_inplace,
          py::arg("path"));

    m.def("compute_helicity_from_fseries",
          &helicity_from_fseries,
          py::arg("path"),
          py::arg("grid_size")=32,
          py::arg("spacing")=0.1,
          py::arg("interior_margin")=8,
          py::arg("nsamples")=1000);

    m.def("sample_curve_centered",
          &sample_curve_centered,
          py::arg("path"),
          py::arg("nsamples")=1024);

    m.def("compute_curve_metrics_from_fseries",
          &curve_metrics_from_fseries,
          py::arg("path"),
          py::arg("nsamples")=2048,
          py::arg("skip")=3);

    m.def("curve_length_from_fseries",
          [](const std::string& path, int nsamples) {
              auto pts = sample_curve_centered(path, nsamples);
              return curve_length(pts);
          },
          py::arg("path"),
          py::arg("nsamples")=2048);

    m.def("min_non_neighbor_distance_from_fseries",
          [](const std::string& path, int nsamples, int skip) {
              auto pts = sample_curve_centered(path, nsamples);
              return min_non_neighbor_distance(pts, skip);
          },
          py::arg("path"),
          py::arg("nsamples")=2048,
          py::arg("skip")=3);

    m.def("reach_proxy_from_fseries",
          [](const std::string& path, int nsamples, int skip) {
              auto pts = sample_curve_centered(path, nsamples);
              return reach_proxy(pts, skip);
          },
          py::arg("path"),
          py::arg("nsamples")=2048,
          py::arg("skip")=3);

    m.def("compute_filament_energy_from_fseries",
          &filament_energy_from_fseries,
          py::arg("path"),
          py::arg("params"));

    m.def("batch_helicity_from_dir",
          &batch_helicity_from_dir,
          py::arg("root_dir"),
          py::arg("grid_size")=32,
          py::arg("spacing")=0.1,
          py::arg("interior_margin")=8,
          py::arg("nsamples")=1000,
          py::arg("recurse")=false);

    m.def("compare_fseries_files",
          &compare_fseries_files,
          py::arg("path_a"),
          py::arg("path_b"),
          py::arg("nsamples")=2048,
          py::arg("skip")=3);
}