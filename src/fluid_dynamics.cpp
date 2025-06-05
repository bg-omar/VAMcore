//
// Created by mr on 3/22/2025.
//

#include "fluid_dynamics.h"
#include <cmath>

namespace vam {

        std::vector<double> FluidDynamics::compute_pressure_field(
                        const std::vector<double>& velocity_magnitude,
                        double rho_ae,
                        double P_infinity) {
		size_t n = velocity_magnitude.size();
		std::vector<double> pressure(n);
		for (size_t i = 0; i < n; ++i) {
			pressure[i] = P_infinity - 0.5 * rho_ae * velocity_magnitude[i] * velocity_magnitude[i];
		}
		return pressure;
	}

        std::vector<double> FluidDynamics::compute_velocity_magnitude(const std::vector<Vec3>& velocity) {
		std::vector<double> mag;
		mag.reserve(velocity.size());
		for (const auto& v : velocity) {
			mag.push_back(std::sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]));
		}
		return mag;
	}

        void FluidDynamics::evolve_positions_euler(
                        std::vector<Vec3>& positions,
                        const std::vector<Vec3>& velocity,
                        double dt) {
		size_t n = positions.size();
		for (size_t i = 0; i < n; ++i) {
			positions[i][0] += dt * velocity[i][0];
			positions[i][1] += dt * velocity[i][1];
			positions[i][2] += dt * velocity[i][2];
		}
        }

} // namespace vam
