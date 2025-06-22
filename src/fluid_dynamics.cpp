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

        bool FluidDynamics::is_incompressible(const Vec3& dudx, const Vec3& dvdy, const Vec3& dwdz) {
                return std::abs(dudx[0] + dvdy[1] + dwdz[2]) < 1e-8;
        }

        Vec3 FluidDynamics::compute_vorticity(const std::array<std::array<double, 3>, 3>& grad) {
                return {
                                grad[2][1] - grad[1][2], // wx
                                grad[0][2] - grad[2][0], // wy
                                grad[1][0] - grad[0][1]  // wz
                };
        }

        double FluidDynamics::swirl_clock_rate(double dv_dx, double du_dy) {
                return 0.5 * (dv_dx - du_dy);
        }

        double FluidDynamics::vorticity_from_curvature(double V, double R) {
                return V / R;
        }

        double FluidDynamics::vortex_pressure_drop(double rho, double c) {
                return 0.5 * rho * c * c;
        }

        double FluidDynamics::vortex_transverse_pressure_diff(double rho, double c) {
                return 0.25 * rho * c * c;
        }

        double FluidDynamics::swirl_energy(double rho, double omega) {
                return 0.5 * rho * omega * omega;
        }

        bool FluidDynamics::kairos_energy_trigger(double rho, double omega, double Ce) {
                return swirl_energy(rho, omega) > 0.5 * rho * Ce * Ce;
        }

        double FluidDynamics::compute_helicity(const std::vector<Vec3>& velocity, const std::vector<Vec3>& vorticity, double dV) {
                double H = 0.0;
                for (size_t i = 0; i < velocity.size(); ++i) {
                        H += velocity[i][0] * vorticity[i][0] +
                                 velocity[i][1] * vorticity[i][1] +
                                 velocity[i][2] * vorticity[i][2];
                }
                return H * dV;
        }

        double FluidDynamics::potential_vorticity(double fa, double zeta_r, double h) {
                return (fa + zeta_r) / h;
        }
}
