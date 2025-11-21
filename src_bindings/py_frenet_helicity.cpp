//
// Created by mr on 3/22/2025.
//
// bindings/py_frenet_helicity.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/frenet_helicity.h"

namespace py = pybind11;

void bind_frenet_helicity(py::module_& m) {
        m.def("compute_frenet_frames", [](const std::vector<sst::Vec3>& X) {
                std::vector<sst::Vec3> T, N, B;
                sst::FrenetHelicity::compute_frenet_frames(X, T, N, B);
		return std::make_tuple(T, N, B);
	}, R"pbdoc(
        Compute Frenet frames (T, N, B) from 3D filament points.
        Returns: (T, N, B) as tuple of lists.
    )pbdoc");

	m.def("compute_curvature_torsion", [](const std::vector<sst::Vec3>& T,
										  const std::vector<sst::Vec3>& N) {
		std::vector<double> curvature, torsion;
                sst::FrenetHelicity::compute_curvature_torsion(T, N, curvature, torsion);
		return std::make_tuple(curvature, torsion);
	}, R"pbdoc(
		Compute curvature and torsion from tangent and normal vectors.
		Returns: (curvature, torsion) as tuple of lists.
	)pbdoc");

	m.def("compute_helicity", [](const std::vector<sst::Vec3>& velocity,
								 const std::vector<sst::Vec3>& vorticity) {
                return sst::FrenetHelicity::compute_helicity(velocity, vorticity);
	}, R"pbdoc(
        Compute helicity H = ∫ v · ω dV.
    )pbdoc");

        m.def("evolve_vortex_knot", &sst::FrenetHelicity::evolve_vortex_knot, R"pbdoc(
        Evolve vortex knot filaments using Biot–Savart dynamics.
    )pbdoc");

        m.def("rk4_integrate", &sst::FrenetHelicity::rk4_integrate, R"pbdoc(
        Runge-Kutta 4th order time integrator for vortex elements.
    )pbdoc");
}