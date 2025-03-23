//
// Created by mr on 3/21/2025.
//

#ifndef VAMCORE_VORTEX_KNOT_SYSTEM_H
#define VAMCORE_VORTEX_KNOT_SYSTEM_H

#pragma once
#include <vector>
#include <array>

namespace vam {

	using Vec3 = std::array<double, 3>;

	class VortexKnotSystem {
	public:
		VortexKnotSystem();

		void initialize_trefoil_knot(size_t resolution = 400);
		void evolve(double dt, size_t steps);

		const std::vector<Vec3>& get_positions() const;
		const std::vector<Vec3>& get_tangents() const;

	private:
		std::vector<Vec3> positions;
		std::vector<Vec3> tangents;

		void compute_tangents();
	};

}


#endif //VAMCORE_VORTEX_KNOT_SYSTEM_H
