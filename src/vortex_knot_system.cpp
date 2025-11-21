//
// Created by mr on 3/21/2025.
//

#include "vortex_knot_system.h"
#include "biot_savart.h"
#include <cmath>

namespace sst {

	VortexKnotSystem::VortexKnotSystem() = default;

	void VortexKnotSystem::initialize_trefoil_knot(size_t resolution) {
		positions.clear();
		tangents.clear();
		positions.reserve(resolution);

		for (size_t i = 0; i < resolution; ++i) {
			double s = 2.0 * M_PI * static_cast<double>(i) / static_cast<double>(resolution);
			double x = (2.0 + std::cos(3.0 * s)) * std::cos(2.0 * s);
			double y = (2.0 + std::cos(3.0 * s)) * std::sin(2.0 * s);
			double z = std::sin(3.0 * s);
			positions.push_back({x, y, z});
		}

		compute_tangents();
	}

    void VortexKnotSystem::initialize_figure8_knot(size_t resolution) {
        positions.clear();
        tangents.clear();
        positions.reserve(resolution);

        for (size_t i = 0; i < resolution; ++i) {
            double s = 2.0 * M_PI * static_cast<double>(i) / static_cast<double>(resolution);
            double x = (2.0 + std::cos(2.0 * s)) * std::cos(3.0 * s);
            double y = (2.0 + std::cos(2.0 * s)) * std::sin(3.0 * s);
            double z = std::sin(4.0 * s);
            positions.push_back({x, y, z});
        }

        compute_tangents();
    }

	void VortexKnotSystem::compute_tangents() {
		tangents.resize(positions.size());
		size_t N = positions.size();
		for (size_t i = 0; i < N; ++i) {
			const Vec3& prev = positions[(i + N - 1) % N];
			const Vec3& next = positions[(i + 1) % N];
			Vec3 tangent{
					(next[0] - prev[0]) * 0.5,
					(next[1] - prev[1]) * 0.5,
					(next[2] - prev[2]) * 0.5
			};
			tangents[i] = tangent;
		}
	}

	void VortexKnotSystem::evolve(double dt, size_t steps) {
		for (size_t step = 0; step < steps; ++step) {
			std::vector<Vec3> new_positions = positions;
			for (size_t i = 0; i < positions.size(); ++i) {
				Vec3 v = biot_savart_velocity(positions[i], positions, tangents);
				for (int d = 0; d < 3; ++d) {
					new_positions[i][d] += dt * v[d];
				}
			}
			positions = new_positions;
			compute_tangents();
		}
	}

	const std::vector<Vec3>& VortexKnotSystem::get_positions() const {
		return positions;
	}

	const std::vector<Vec3>& VortexKnotSystem::get_tangents() const {
		return tangents;
	}


} // namespace sst