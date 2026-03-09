#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "./sst_extensions.h"

namespace py = pybind11;

void bind_extensions(py::module_& m) {
    py::class_<sstext::CanonicalizeResult>(m, "CanonicalizeResult")
        .def(py::init<>())
        .def_readwrite("path", &sstext::CanonicalizeResult::path)
        .def_readwrite("found_numeric_rows", &sstext::CanonicalizeResult::found_numeric_rows)
        .def_readwrite("changed", &sstext::CanonicalizeResult::changed)
        .def_readwrite("reason", &sstext::CanonicalizeResult::reason);

    py::class_<sstext::HelicityResult>(m, "HelicityResult")
        .def(py::init<>())
        .def_readwrite("path", &sstext::HelicityResult::path)
        .def_readwrite("a_mu", &sstext::HelicityResult::a_mu)
        .def_readwrite("Hc", &sstext::HelicityResult::Hc)
        .def_readwrite("Hm", &sstext::HelicityResult::Hm)
        .def_readwrite("L", &sstext::HelicityResult::L)
        .def_readwrite("kappa_max", &sstext::HelicityResult::kappa_max)
        .def_readwrite("kappa_mean", &sstext::HelicityResult::kappa_mean)
        .def_readwrite("bend_energy", &sstext::HelicityResult::bend_energy)
        .def_readwrite("min_non_neighbor_dist", &sstext::HelicityResult::min_non_neighbor_dist)
        .def_readwrite("reach_proxy", &sstext::HelicityResult::reach_proxy)
        .def_readwrite("nsamples", &sstext::HelicityResult::nsamples);

    py::class_<sstext::FilamentEnergyParams>(m, "FilamentEnergyParams")
        .def(py::init<>())
        .def_readwrite("rho_outer", &sstext::FilamentEnergyParams::rho_outer)
        .def_readwrite("rho_local", &sstext::FilamentEnergyParams::rho_local)
        .def_readwrite("Gamma", &sstext::FilamentEnergyParams::Gamma)
        .def_readwrite("a_core", &sstext::FilamentEnergyParams::a_core)
        .def_readwrite("delta", &sstext::FilamentEnergyParams::delta)
        .def_readwrite("s_cut_local", &sstext::FilamentEnergyParams::s_cut_local)
        .def_readwrite("include_nonlocal", &sstext::FilamentEnergyParams::include_nonlocal)
        .def_readwrite("include_local_match", &sstext::FilamentEnergyParams::include_local_match)
        .def_readwrite("include_core_int", &sstext::FilamentEnergyParams::include_core_int)
        .def_readwrite("c_rankine_outer", &sstext::FilamentEnergyParams::c_rankine_outer)
        .def_readwrite("nsamples", &sstext::FilamentEnergyParams::nsamples)
        .def_readwrite("skip_neighbors_base", &sstext::FilamentEnergyParams::skip_neighbors_base);

    py::class_<sstext::FilamentEnergyResult>(m, "FilamentEnergyResult")
        .def(py::init<>())
        .def_readwrite("path", &sstext::FilamentEnergyResult::path)
        .def_readwrite("L", &sstext::FilamentEnergyResult::L)
        .def_readwrite("ds_avg", &sstext::FilamentEnergyResult::ds_avg)
        .def_readwrite("m_loc", &sstext::FilamentEnergyResult::m_loc)
        .def_readwrite("E_nonlocal", &sstext::FilamentEnergyResult::E_nonlocal)
        .def_readwrite("E_local_match", &sstext::FilamentEnergyResult::E_local_match)
        .def_readwrite("E_core_int", &sstext::FilamentEnergyResult::E_core_int)
        .def_readwrite("E_total", &sstext::FilamentEnergyResult::E_total)
        .def_readwrite("kappa_max", &sstext::FilamentEnergyResult::kappa_max)
        .def_readwrite("kappa_mean", &sstext::FilamentEnergyResult::kappa_mean)
        .def_readwrite("bend_energy", &sstext::FilamentEnergyResult::bend_energy)
        .def_readwrite("min_non_neighbor_dist", &sstext::FilamentEnergyResult::min_non_neighbor_dist)
        .def_readwrite("reach_proxy", &sstext::FilamentEnergyResult::reach_proxy)
        .def_readwrite("rho_outer", &sstext::FilamentEnergyResult::rho_outer)
        .def_readwrite("rho_local", &sstext::FilamentEnergyResult::rho_local)
        .def_readwrite("Gamma", &sstext::FilamentEnergyResult::Gamma)
        .def_readwrite("a_core", &sstext::FilamentEnergyResult::a_core)
        .def_readwrite("delta", &sstext::FilamentEnergyResult::delta)
        .def_readwrite("s_cut_local", &sstext::FilamentEnergyResult::s_cut_local)
        .def_readwrite("c_rankine_outer", &sstext::FilamentEnergyResult::c_rankine_outer)
        .def_readwrite("nsamples", &sstext::FilamentEnergyResult::nsamples);

    m.def("canonicalize_fseries_file_inplace",
          &sstext::canonicalize_fseries_file_inplace,
          py::arg("path"));

    m.def("compute_helicity_from_fseries",
          &sstext::helicity_from_fseries,
          py::arg("path"),
          py::arg("grid_size")=32,
          py::arg("spacing")=0.1,
          py::arg("interior_margin")=8,
          py::arg("nsamples")=1000);

    m.def("sample_curve_centered",
          &sstext::sample_curve_centered,
          py::arg("path"),
          py::arg("nsamples")=1024);

    m.def("compute_curve_metrics_from_fseries",
          &sstext::curve_metrics_from_fseries,
          py::arg("path"),
          py::arg("nsamples")=2048,
          py::arg("skip")=3);

    m.def("curve_length_from_fseries",
          [](const std::string& path, int nsamples) {
              auto pts = sstext::sample_curve_centered(path, nsamples);
              return sstext::curve_length(pts);
          },
          py::arg("path"),
          py::arg("nsamples")=2048);

    m.def("min_non_neighbor_distance_from_fseries",
          [](const std::string& path, int nsamples, int skip) {
              auto pts = sstext::sample_curve_centered(path, nsamples);
              return sstext::min_non_neighbor_distance(pts, skip);
          },
          py::arg("path"),
          py::arg("nsamples")=2048,
          py::arg("skip")=3);

    m.def("reach_proxy_from_fseries",
          [](const std::string& path, int nsamples, int skip) {
              auto pts = sstext::sample_curve_centered(path, nsamples);
              return sstext::reach_proxy(pts, skip);
          },
          py::arg("path"),
          py::arg("nsamples")=2048,
          py::arg("skip")=3);

    m.def("compute_filament_energy_from_fseries",
          &sstext::filament_energy_from_fseries,
          py::arg("path"),
          py::arg("params"));

    m.def("batch_helicity_from_dir",
          &sstext::batch_helicity_from_dir,
          py::arg("root_dir"),
          py::arg("grid_size")=32,
          py::arg("spacing")=0.1,
          py::arg("interior_margin")=8,
          py::arg("nsamples")=1000,
          py::arg("recurse")=false);

    m.def("compare_fseries_files",
          &sstext::compare_fseries_files,
          py::arg("path_a"),
          py::arg("path_b"),
          py::arg("nsamples")=2048,
          py::arg("skip")=3);
}