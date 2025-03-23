//
// Created by mr on 3/22/2025.
//

#ifndef VAMCORE_FLUID_DYNAMICS_H
#define VAMCORE_FLUID_DYNAMICS_H


#pragma once

#include <vector>
#include <array>

namespace vam {

	using Vec3 = std::array<double, 3>;

// Compute Bernoulli pressure field from velocity magnitude
	std::vector<double> compute_pressure_field(
			const std::vector<double>& velocity_magnitude,
			double rho_ae,
			double P_infinity);

// Compute velocity magnitude from vector field
	std::vector<double> compute_velocity_magnitude(
			const std::vector<Vec3>& velocity);

// Simple Euler step for particle advection
	void evolve_positions_euler(
			std::vector<Vec3>& positions,
			const std::vector<Vec3>& velocity,
			double dt);

} // namespace vam



#endif //VAMCORE_FLUID_DYNAMICS_H
