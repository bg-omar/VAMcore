// src_bindings/py_sst_gravity.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "../src/sst_gravity.h"

namespace py = pybind11;
using namespace sst;

// Helper: NumPy (N,3) -> std::vector<Vec3>
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

// Helper: NumPy (N,) -> std::vector<double>
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
        // ---------------------------------------------------------------------
        // 1. Beltrami Shear
        // ---------------------------------------------------------------------
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

                Parameters
                ----------
                B_field : ndarray of shape (N, 3)
                    Magnetic field samples.
                Curl_B : ndarray of shape (N, 3)
                    Curl of the magnetic field at the same sample points.

                Returns
                -------
                shear : list[float]
                    1D array of shear magnitudes.
            )pbdoc"
        )

        // ---------------------------------------------------------------------
        // 2. Phenomenological Gravity Dilation
        // ---------------------------------------------------------------------
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

                Parameters
                ----------
                B_field : ndarray of shape (N, 3)
                    Magnetic field samples (Tesla).
                omega_drive : float
                    Drive angular frequency (units consistent across calls).
                v_swirl : float, optional
                    Canonical swirl velocity (m/s). Kept as a parameter for
                    future variants.
                B_saturation : float, optional
                    Saturation field scale (Tesla).

                Returns
                -------
                G_map : list[float]
                    Dimensionless values in [0, 1], with 1 = nominal gravity,
                    0 = fully suppressed in this metric.
            )pbdoc"
        )

        // ---------------------------------------------------------------------
        // 3. Magnetic Helicity Density h = A·B
        // ---------------------------------------------------------------------
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

                Parameters
                ----------
                A_field : ndarray of shape (N, 3)
                    Vector potential samples.
                B_field : ndarray of shape (N, 3)
                    Magnetic field samples.

                Returns
                -------
                h_map : list[float]
                    Helicity density values per sample.
            )pbdoc"
        )

        // ---------------------------------------------------------------------
        // 4. Swirl Clock S_t from local swirl velocity
        // ---------------------------------------------------------------------
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
                Compute the Swirl Clock factor S_t at each sample:

                    S_t = sqrt(1 - ||v_swirl||^2 / c^2),

                clamped to [0, 1].

                Parameters
                ----------
                v_swirl_field : ndarray of shape (N, 3)
                    Local swirl velocity field (m/s).
                c : float, optional
                    Speed of light (m/s).

                Returns
                -------
                S_t : list[float]
                    Local time-dilation factors S_t in [0, 1].
            )pbdoc"
        )

        // ---------------------------------------------------------------------
        // 5. Swirl Coulomb Potential V(r) = -Lambda / sqrt(r^2 + r_c^2)
        // ---------------------------------------------------------------------
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
                Compute the Swirl Coulomb potential

                    V(r) = -Lambda / sqrt(r^2 + r_c^2)

                for a list of radii.

                Parameters
                ----------
                radii : ndarray of shape (N,)
                    Radial distances r >= 0.
                Lambda : float
                    Swirl Coulomb scale (energy·length units).
                r_c : float
                    Core radius (m or same length units as r).

                Returns
                -------
                V : list[float]
                    Potential values V(r) per radius sample.
            )pbdoc"
        )

        // ---------------------------------------------------------------------
        // 6. Swirl Coulomb Radial Force F_r(r)
        // ---------------------------------------------------------------------
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
                Compute the radial Swirl Coulomb force

                    F_r(r) = -dV/dr
                           = -Lambda * r / (r^2 + r_c^2)^(3/2).

                Negative values correspond to attraction towards r = 0.

                Parameters
                ----------
                radii : ndarray of shape (N,)
                    Radial distances r >= 0.
                Lambda : float
                    Swirl Coulomb scale.
                r_c : float
                    Core radius.

                Returns
                -------
                F_r : list[float]
                    Radial force values per radius sample.
            )pbdoc"
        )

        // ---------------------------------------------------------------------
        // 7. Swirl Energy Density rho_E = 0.5 * rho_f * ||v||^2
        // ---------------------------------------------------------------------
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
                Compute swirl kinetic energy density

                    rho_E = 0.5 * rho_f * ||v||^2

                at each sample.

                Parameters
                ----------
                v_field : ndarray of shape (N, 3)
                    Velocity field samples (m/s).
                rho_f : float
                    Effective fluid density (kg/m^3).

                Returns
                -------
                rho_E : list[float]
                    Energy density values (J/m^3).
            )pbdoc"
        )

        // ---------------------------------------------------------------------
        // 8. Effective Swirl Gravitational Coupling G_swirl
        // ---------------------------------------------------------------------
        .def_static(
            "compute_G_swirl",
            &SSTGravity::compute_G_swirl,
            py::arg("v_swirl"),
            py::arg("t_p"),
            py::arg("F_max"),
            py::arg("r_c"),
            py::arg("c") = 2.99792458e8,
            R"pbdoc(
                Compute the effective Swirl gravitational coupling

                    G_swirl = v_swirl * c^5 * t_p^2
                              / (2 * F_max * r_c^2).

                Parameters
                ----------
                v_swirl : float
                    Characteristic swirl velocity (m/s).
                t_p : float
                    Planck time (s).
                F_max : float
                    Canonical maximum swirl force (N).
                r_c : float
                    Core radius (m).
                c : float, optional
                    Speed of light (m/s).

                Returns
                -------
                G_swirl : float
                    Effective gravitational coupling (SI: m^3 / (kg·s^2)).
            )pbdoc"
        );
}