//
// Created by mr on 3/22/2025.
//

#include "gravity_timefield.h"
// src/gravity_timefield.cpp

#include <cmath>

namespace vam {

	std::vector<double> compute_gravitational_potential(const std::vector<Vec3>& positions,
														const std::vector<Vec3>& vorticity,
														double epsilon) {
		size_t n = positions.size();
		std::vector<double> potential(n, 0.0);
		constexpr double inv_prefactor = 1.0 / (4.0 * M_PI);

		for (size_t i = 0; i < n; ++i) {
			double phi = 0.0;
			const auto& ri = positions[i];

			for (size_t j = 0; j < n; ++j) {
				if (i == j) continue;
				const auto& rj = positions[j];
				const auto& wj = vorticity[j];

				Vec3 dr = { ri[0] - rj[0], ri[1] - rj[1], ri[2] - rj[2] };
				double r2 = dr[0]*dr[0] + dr[1]*dr[1] + dr[2]*dr[2] + epsilon * epsilon;
				double dot = dr[0]*wj[0] + dr[1]*wj[1] + dr[2]*wj[2];

				phi += dot / std::pow(r2, 1.5);
			}
			potential[i] = -inv_prefactor * phi;
		}
		return potential;
	}

	std::vector<double> compute_time_dilation_map(const std::vector<Vec3>& tangents,
												  double C_e) {
		std::vector<double> gamma;
		gamma.reserve(tangents.size());
		for (const auto& t : tangents) {
			double v2 = t[0]*t[0] + t[1]*t[1] + t[2]*t[2];
			double factor = 1.0 - (v2 / (C_e * C_e));
			gamma.push_back(factor);
		}
		return gamma;
	}

} // namespace vam
