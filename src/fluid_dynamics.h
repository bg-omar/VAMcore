//
// Created by mr on 3/22/2025.
//

#ifndef SWIRL_STRING_CORE_FLUID_DYNAMICS_H
#define SWIRL_STRING_CORE_FLUID_DYNAMICS_H


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

			// Pressure field methods (from PressureField)
			static std::vector<double> compute_bernoulli_pressure(
					const std::vector<double>& velocity_magnitude,
					double rho = 7.0e-7,
					double p_inf = 0.0);
			static std::vector<std::vector<Vec3>> pressure_gradient(
					const std::vector<std::vector<double>>& pressure_field,
					double dx = 1.0,
					double dy = 1.0);

			// Potential flow methods (from PotentialFlow)
			static double laplacian_phi(double d2phidx2, double d2phidy2, double d2phidz2);
			static Vec3 grad_phi(const Vec3& phi_grad);
			static double bernoulli_pressure_potential(double velocity_squared, double V);

			// Kinetic energy methods (from KineticEnergy)
			static double compute_kinetic_energy(const std::vector<Vec3>& velocity, double rho_ae);

			// Fluid rotation methods (from FluidRotation)
			static double rossby_number(double U, double omega, double d);
			static double ekman_number(double nu, double omega, double H);
			static double cylinder_mass(double rho, double R, double H);
			static double cylinder_inertia(double mass, double R);
			static double torque(double inertia, double alpha);
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



#endif //SWIRL_STRING_CORE_FLUID_DYNAMICS_H