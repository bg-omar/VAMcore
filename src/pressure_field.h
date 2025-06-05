//
// Created by mr on 3/22/2025.
//

#ifndef VAMCORE_PRESSURE_FIELD_H
#define VAMCORE_PRESSURE_FIELD_H


// include/pressure_field.hpp
#pragma once

#include <array>
#include <vector>

namespace vam {

	using Vec3 = std::array<double, 3>;

// Compute Bernoulli pressure field given velocity magnitude and fluid density
	std::vector<double> compute_bernoulli_pressure(const std::vector<double>& velocity_magnitude,
												   double rho = 7.0e-7,
												   double p_inf = 0.0);

// Compute pressure gradient from 2D pressure grid (assumes square grid)
	std::vector<std::vector<Vec3>> pressure_gradient(const std::vector<std::vector<double>>& pressure_field,
													 double dx = 1.0);

} // namespace vam



#endif //VAMCORE_PRESSURE_FIELD_H
