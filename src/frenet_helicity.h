//
// Created by mr on 3/22/2025.
//

#ifndef VAMCORE_FRENET_HELICITY_H
#define VAMCORE_FRENET_HELICITY_H

// include/frenet_helicity.hpp
#pragma once
#include "../include/vec3_utils.h"
#include <array>
#include <vector>

namespace vam {

	using Vec3 = std::array<double, 3>;

// Compute normalized tangent, normal, binormal vectors
	void compute_frenet_frames(const std::vector<Vec3>& X,
							   std::vector<Vec3>& T,
							   std::vector<Vec3>& N,
							   std::vector<Vec3>& B);

// Compute local curvature and torsion
	void compute_curvature_torsion(const std::vector<Vec3>& T,
								   const std::vector<Vec3>& N,
								   std::vector<double>& curvature,
								   std::vector<double>& torsion);

// Compute helicity H = ∫ v · ω dV for filament
// Takes induced velocity and tangent vectors
// Assumes Biot–Savart already used to compute v
	float compute_helicity(const std::vector<Vec3>& velocity,
						   const std::vector<Vec3>& vorticity);

	// RK4 Integrator
	std::vector<Vec3> rk4_integrate(const std::vector<Vec3>& positions,
									const std::vector<Vec3>& tangents,
									double dt,
									double gamma = 1.0);

// Direct evolution step using Biot–Savart
	std::vector<Vec3> evolve_vortex_knot(const std::vector<Vec3>& positions,
										 const std::vector<Vec3>& tangents,
										 double dt,
										 double gamma = 1.0);

} // namespace vam


#endif //VAMCORE_FRENET_HELICITY_H
