//
// Created by mr on 3/22/2025.
//

#ifndef VAMCORE_KNOT_DYNAMICS_H
#define VAMCORE_KNOT_DYNAMICS_H

#include "../include/vec3_utils.h"
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
// include/knot_dynamics.hpp
#pragma once

#include <vector>
#include <array>

namespace vam {

	using Vec3 = std::array<double, 3>;

// Compute writhe from filament centerline
// Ref: Cálugăreanu-White formula (approximated)
	double compute_writhe(const std::vector<Vec3>& centerline);

// Compute linking number between two vortex filaments
	int compute_linking_number(const std::vector<Vec3>& curve1, const std::vector<Vec3>& curve2);

// Compute twist given tangent and normal
// Twist = ∫ (T × dN/ds) ⋅ B ds
	double compute_twist(const std::vector<Vec3>& T, const std::vector<Vec3>& B);

	// Compute centerline helicity invariant H_cl
// H_cl = Lk + Wr, combines link and writhe
	double compute_centerline_helicity(const std::vector<Vec3>& curve,
									   const std::vector<Vec3>& tangent);

	// Check for reconnection events
// Returns indices of close approach
	std::vector<std::pair<int, int>> detect_reconnection_candidates(
			const std::vector<Vec3>& curve, double threshold);

} // namespace vam


#endif //VAMCORE_KNOT_DYNAMICS_H
