// src/sst_gravity_py.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "sst_gravity.h"

namespace py = pybind11;
using namespace sst;

static std::vector<Vec3> sst_to_vec3_list(
    py::array_t<double, py::array::c_style | py::array::forcecast> arr)
{
    if (arr.ndim() != 2 || arr.shape(1) != 3) {
        throw std::invalid_argument("Expected array with shape (N, 3)");
    }
    const py::ssize_t N = arr.shape(0);
    std::vector<Vec3> out(static_cast<std::size_t>(N));
    auto a = arr.unchecked<2>();
    for (py::ssize_t i = 0; i < N; ++i) {
        out[static_cast<std::size_t>(i)] = { a(i, 0), a(i, 1), a(i, 2) };
    }
    return out;
}

static std::vector<double> sst_to_scalar_list(
    py::array_t<double, py::array::c_style | py::array::forcecast> arr)
{
    if (arr.ndim() != 1) {
        throw std::invalid_argument("Expected 1D array with shape (N,)");
    }
    const py::ssize_t N = arr.shape(0);
    std::vector<double> out(static_cast<std::size_t>(N));
    auto a = arr.unchecked<1>();
    for (py::ssize_t i = 0; i < N; ++i) {
        out[static_cast<std::size_t>(i)] = a(i);
    }
    return out;
}

void bind_sst_gravity(py::module_& m) {
    py::class_<SSTGravity>(m, "SSTGravity")
        .def_static(
            "compute_beltrami_shear",
            [](py::array_t<double> B_field,
               py::array_t<double> Curl_B) {
                auto b_vec = sst_to_vec3_list(B_field);
                auto c_vec = sst_to_vec3_list(Curl_B);
                return SSTGravity::compute_beltrami_shear(b_vec, c_vec);
            },
            py::arg("B_field"),
            py::arg("Curl_B"),
            R"pbdoc(
                Compute the Beltrami shear metric S = || B x (curl B) ||.
            )pbdoc"
        )
        .def_static(
            "compute_gravity_dilation",
            [](py::array_t<double> B_field,
               double omega_drive,
               double v_swirl,
               double B_saturation) {
                auto b_vec = sst_to_vec3_list(B_field);
                return SSTGravity::compute_gravity_dilation(
                    b_vec, omega_drive, v_swirl, B_saturation
                );
            },
            py::arg("B_field"),
            py::arg("omega_drive"),
            py::arg("v_swirl")      = 1.09384563e6,
            py::arg("B_saturation") = 100.0,
            R"pbdoc(
                Compute a phenomenological gravity reduction factor G_local
                driven by EM excitation.
            )pbdoc"
        )
        .def_static(
            "compute_helicity_density",
            [](py::array_t<double> A_field,
               py::array_t<double> B_field) {
                auto a_vec = sst_to_vec3_list(A_field);
                auto b_vec = sst_to_vec3_list(B_field);
                return SSTGravity::compute_helicity_density(a_vec, b_vec);
            },
            py::arg("A_field"),
            py::arg("B_field"),
            R"pbdoc(
                Compute magnetic helicity density h = A · B.
            )pbdoc"
        )
        .def_static(
            "compute_swirl_clock",
            [](py::array_t<double> v_swirl_field,
               double c) {
                auto v_vec = sst_to_vec3_list(v_swirl_field);
                return SSTGravity::compute_swirl_clock(v_vec, c);
            },
            py::arg("v_swirl_field"),
            py::arg("c") = 2.99792458e8,
            R"pbdoc(
                Compute the Swirl Clock factor S_t at each sample.
            )pbdoc"
        )
        .def_static(
            "compute_swirl_coulomb_potential",
            [](py::array_t<double> radii,
               double Lambda,
               double r_c) {
                auto r_vec = sst_to_scalar_list(radii);
                return SSTGravity::compute_swirl_coulomb_potential(
                    r_vec, Lambda, r_c
                );
            },
            py::arg("radii"),
            py::arg("Lambda"),
            py::arg("r_c"),
            R"pbdoc(
                Compute the Swirl Coulomb potential V(r) = -Lambda / sqrt(r^2 + r_c^2).
            )pbdoc"
        )
        .def_static(
            "compute_swirl_coulomb_force",
            [](py::array_t<double> radii,
               double Lambda,
               double r_c) {
                auto r_vec = sst_to_scalar_list(radii);
                return SSTGravity::compute_swirl_coulomb_force(
                    r_vec, Lambda, r_c
                );
            },
            py::arg("radii"),
            py::arg("Lambda"),
            py::arg("r_c"),
            R"pbdoc(
                Compute the radial Swirl Coulomb force F_r(r).
            )pbdoc"
        )
        .def_static(
            "compute_swirl_energy_density",
            [](py::array_t<double> v_field,
               double rho_f) {
                auto v_vec = sst_to_vec3_list(v_field);
                return SSTGravity::compute_swirl_energy_density(
                    v_vec, rho_f
                );
            },
            py::arg("v_field"),
            py::arg("rho_f"),
            R"pbdoc(
                Compute swirl kinetic energy density rho_E = 0.5 * rho_f * ||v||^2.
            )pbdoc"
        )
        .def_static(
            "compute_G_swirl",
            &SSTGravity::compute_G_swirl,
            py::arg("v_swirl"),
            py::arg("t_p"),
            py::arg("F_max"),
            py::arg("r_c"),
            py::arg("c") = 2.99792458e8,
            R"pbdoc(
                Compute the effective Swirl gravitational coupling G_swirl.
            )pbdoc"
        );
}
