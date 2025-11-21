// src_bindings/py_sst_gravity.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "../src/sst_gravity.h"

namespace py = pybind11;
using namespace sst;

// Helper to ensure numpy arrays are converted to vector<Vec3>
// (You may already have this in a shared utils header, but implemented here for safety)
static std::vector<Vec3> sst_to_vec3_list(
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

void bind_sst_gravity(py::module_& m) {
    py::class_<SSTGravity>(m, "SSTGravity")
        // 1. Beltrami Shear Binding
        .def_static("compute_beltrami_shear",
            [](py::array_t<double> B_field, py::array_t<double> Curl_B) {
                auto b_vec = sst_to_vec3_list(B_field);
                auto c_vec = sst_to_vec3_list(Curl_B);
                return SSTGravity::compute_beltrami_shear(b_vec, c_vec);
            },
            py::arg("B_field"), py::arg("Curl_B"),
            R"pbdoc(
                Compute the Beltrami Shear metric: S = || B x (Curl B) ||.
                Returns a 1D array of scalar shear values.
            )pbdoc"
        )

        // 2. Gravity Dilation Binding
        .def_static("compute_gravity_dilation",
            [](py::array_t<double> B_field, double omega, double v_swirl, double B_sat) {
                auto b_vec = sst_to_vec3_list(B_field);
                return SSTGravity::compute_gravity_dilation(b_vec, omega, v_swirl, B_sat);
            },
            py::arg("B_field"),
            py::arg("omega_drive"),
            py::arg("v_swirl") = 1.09384563e6,
            py::arg("B_saturation") = 100.0,
            R"pbdoc(
                Compute the scalar Gravity Map (G_local).
                Returns 1D array where 1.0 = Normal G, 0.0 = Zero G.
            )pbdoc"
        )

        // 3. Helicity Density Binding
        .def_static("compute_helicity_density",
            [](py::array_t<double> A_field, py::array_t<double> B_field) {
                auto a_vec = sst_to_vec3_list(A_field);
                auto b_vec = sst_to_vec3_list(B_field);
                return SSTGravity::compute_helicity_density(a_vec, b_vec);
            },
            py::arg("A_field"), py::arg("B_field"),
            R"pbdoc(
                    Compute Helicity Density h = A . B.
                    Returns 1D scalar array.
                )pbdoc"
        );
}