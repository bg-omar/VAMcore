//
// Created by mr on 3/22/2025.
//

#include "time_evolution.h"

// src/time_evolution.cpp
#include "biot_savart.h"  // assumes vam::biot_savart_velocity is defined
#include "frenet_helicity.h"

namespace vam {

	TimeEvolution::TimeEvolution(std::vector<Vec3> initial_positions,
								 std::vector<Vec3> initial_tangents,
								 double gamma)
			: positions(std::move(initial_positions)),
			  tangents(std::move(initial_tangents)),
			  circulation(gamma) {}

	void TimeEvolution::evolve(double dt, int steps) {
		for (int step = 0; step < steps; ++step) {
			std::vector<Vec3> velocity;
			for (const auto& p : positions) {
				velocity.push_back(biot_savart_velocity(p, positions, tangents, circulation));
			}
			for (size_t i = 0; i < positions.size(); ++i) {
				positions[i][0] += dt * velocity[i][0];
				positions[i][1] += dt * velocity[i][1];
				positions[i][2] += dt * velocity[i][2];
			}
			compute_frenet_frames(positions, tangents, tangents, tangents); // T updated, dummy for N, B
		}
	}

	const std::vector<Vec3>& TimeEvolution::get_positions() const {
		return positions;
	}

	const std::vector<Vec3>& TimeEvolution::get_tangents() const {
		return tangents;
	}

} // namespace vam
