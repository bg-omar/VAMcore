//
// Created by mr on 3/22/2025.
//

#ifndef SSTCORE_FLUID_DYNAMICS_H
#define SSTCORE_FLUID_DYNAMICS_H


#pragma once

#include <array>
#include <vector>
#include <cmath>

namespace sst {

        using Vec3 = std::array<double, 3>;

        class FluidDynamics {
        public:
                // Compute Bernoulli pressure field from velocity magnitude
                static std::vector<double> compute_pressure_field(
                                const std::vector<double>& velocity_magnitude,
                                double rho_ae,
                                double P_infinity);

                // Compute velocity magnitude from vector field
                static std::vector<double> compute_velocity_magnitude(
                                const std::vector<Vec3>& velocity);

                // Simple Euler step for particle advection
                static void evolve_positions_euler(
                                std::vector<Vec3>& positions,
                                const std::vector<Vec3>& velocity,
                                double dt);

			static Vec3 compute_vorticity(const std::array<std::array<double, 3>, 3> &grad);

			static bool is_incompressible(const Vec3 &dudx, const Vec3 &dvdy, const Vec3 &dwdz);

			static double swirl_clock_rate(double dv_dx, double du_dy);

			static double vorticity_from_curvature(double V, double R);

			static double vortex_pressure_drop(double rho, double c);

			static double vortex_transverse_pressure_diff(double rho, double c);

			static bool kairos_energy_trigger(double rho, double omega, double Ce);

			static double compute_helicity(const std::vector<Vec3> &velocity, const std::vector<Vec3> &vorticity, double dV);

			static double potential_vorticity(double fa, double zeta_r, double h);

			static double swirl_energy(double rho, double omega);

			static double circulation_surface_integral(
					const std::vector<Vec3> &omega_field,
					const std::vector<Vec3> &dA_field);

			static double enstrophy(
					const std::vector<double> &omega_squared,
					const std::vector<double> &ds_area);
		};

        inline std::vector<double> compute_pressure_field(
                        const std::vector<double>& velocity_magnitude,
                        double rho_ae,
                        double P_infinity) {
                return FluidDynamics::compute_pressure_field(velocity_magnitude, rho_ae, P_infinity);
        }

        inline std::vector<double> compute_velocity_magnitude(
                        const std::vector<Vec3>& velocity) {
                return FluidDynamics::compute_velocity_magnitude(velocity);
        }

        inline void evolve_positions_euler(
                        std::vector<Vec3>& positions,
                        const std::vector<Vec3>& velocity,
                        double dt) {
                FluidDynamics::evolve_positions_euler(positions, velocity, dt);
        }

} // namespace sst



#endif //SSTCORE_FLUID_DYNAMICS_H