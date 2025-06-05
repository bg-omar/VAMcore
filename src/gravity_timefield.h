//
// Created by mr on 3/22/2025.
//

#ifndef VAMCORE_GRAVITY_TIMEFIELD_H
#define VAMCORE_GRAVITY_TIMEFIELD_H

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
// include/gravity_timefield.hpp
#pragma once

#include <vector>
#include <array>

namespace vam {

	using Vec3 = std::array<double, 3>;

// Computes gravitational potential based on vorticity gradient
	std::vector<double> compute_gravitational_potential(const std::vector<Vec3>& positions,
														const std::vector<Vec3>& vorticity,
														double epsilon = 0.1);

// Computes time dilation factor at each point from tangential velocity magnitudes
	std::vector<double> compute_time_dilation_map(const std::vector<Vec3>& tangents,
												  double C_e);

} // namespace vam


#endif //VAMCORE_GRAVITY_TIMEFIELD_H
