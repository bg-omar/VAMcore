#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "ab_initio_mass.h"

namespace py = pybind11;
using namespace sst;

void bind_ab_initio(py::module_& m) {
    py::class_<ParticleEvaluator::TailApproxConfig>(m, "TailApproxConfig")
        .def(py::init<>())
        .def_readwrite("enabled", &ParticleEvaluator::TailApproxConfig::enabled)
        .def_readwrite("radial_samples", &ParticleEvaluator::TailApproxConfig::radial_samples)
        .def_readwrite("azimuth_samples", &ParticleEvaluator::TailApproxConfig::azimuth_samples)
        .def_readwrite("r_min_factor", &ParticleEvaluator::TailApproxConfig::r_min_factor)
        .def_readwrite("r_max_factor", &ParticleEvaluator::TailApproxConfig::r_max_factor)
        .def_readwrite("exclusion_ds_factor", &ParticleEvaluator::TailApproxConfig::exclusion_ds_factor)
        .def_readwrite("use_log_shell_weight", &ParticleEvaluator::TailApproxConfig::use_log_shell_weight);

    py::class_<ParticleEvaluator::RelativisticMetrics>(m, "RelativisticMetrics")
        .def(py::init<>())
        .def_readwrite("helicity", &ParticleEvaluator::RelativisticMetrics::helicity)
        .def_readwrite("time_dilation_map", &ParticleEvaluator::RelativisticMetrics::time_dilation_map)
        .def_readwrite("core_time_dilation", &ParticleEvaluator::RelativisticMetrics::core_time_dilation);

    py::class_<ParticleEvaluator>(m, "ParticleEvaluator")
        // 1. The old String-based constructor
        .def(py::init<const std::string &, int>(),
             py::arg("knot_ab_id"), py::arg("resolution") = 4000)

        // 2. The new Array-based constructor
        .def(py::init<const std::vector<std::vector<std::array<double, 3>>> &>(),
             py::arg("input_filaments"))

        .def("relax", [](ParticleEvaluator& self, int iterations, double timestep) {
            self.relax_hamiltonian(iterations, timestep, []() {
                if (PyErr_CheckSignals() != 0) {
                    throw py::error_already_set();
                }
            });
        }, py::arg("iterations") = 1000, py::arg("timestep") = 0.01)

        // Expose the stretch_lambda parameter to Python
        .def("get_dimless_ropelength", &ParticleEvaluator::get_dimless_ropelength, py::arg("stretch_lambda") = 1.0)

        // NEW: expose ab initio core-energy mass path
        .def("get_physical_length_m", &ParticleEvaluator::get_physical_length_m)
        .def("compute_core_energy_J", &ParticleEvaluator::compute_core_energy_J)
        .def("compute_tail_energy_J", &ParticleEvaluator::compute_tail_energy_J, py::arg("include_tail") = false)
        .def("get_mass_mev_ab_initio", &ParticleEvaluator::get_mass_mev_ab_initio, py::arg("include_tail") = false)
        .def("get_core_mass_mev_only", &ParticleEvaluator::get_core_mass_mev_only)

        // Tail-energy surrogate
        .def("set_tail_approx_config", &ParticleEvaluator::set_tail_approx_config)
        .def("get_tail_approx_config", &ParticleEvaluator::get_tail_approx_config)
        .def("compute_tail_energy_surrogate_J", &ParticleEvaluator::compute_tail_energy_surrogate_J)

        .def("compute_relativistic_metrics", &ParticleEvaluator::compute_relativistic_metrics,
             py::arg("circulation") = 9.683619203e-9)
        .def_static("print_canonical_derivation", &ParticleEvaluator::print_canonical_derivation,
                            "Prints the dynamic fluid derivation of the core density.")
        .def("get_filaments", [](const ParticleEvaluator& self) {
            std::vector<std::vector<std::array<double, 3>>> py_filaments;
            for (const auto& fil : self.filaments) {
                std::vector<std::array<double, 3>> py_fil;
                py_fil.reserve(fil.size());
                for (const auto& pt : fil) {
                    py_fil.push_back({pt[0], pt[1], pt[2]});
                }
                py_filaments.push_back(py_fil);
            }
            return py_filaments;
        }, "Export the 3D coordinates of all present vortex rings.");


}