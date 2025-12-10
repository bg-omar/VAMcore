//
// Created by mr on 3/22/2025.
//

#ifndef SWIRL_STRING_CORE_TIME_EVOLUTION_H
#define SWIRL_STRING_CORE_TIME_EVOLUTION_H


#pragma once

#include <vector>
#include <array>

namespace sst {

	using Vec3 = std::array<double, 3>;

	class TimeEvolution {
	public:
		TimeEvolution(std::vector<Vec3> initial_positions,
					  std::vector<Vec3> initial_tangents,
					  double gamma = 1.0);

		void evolve(double dt, int steps);

		const std::vector<Vec3>& get_positions() const;
		const std::vector<Vec3>& get_tangents() const;

	private:
		std::vector<Vec3> positions;
		std::vector<Vec3> tangents;
		double circulation;
	};

} // namespace sst


#endif //SWIRL_STRING_CORE_TIME_EVOLUTION_H