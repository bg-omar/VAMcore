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

        class FluidDynamics {
        public:
                static std::vector<double> compute_pressure_field(
                                const std::vector<double>& velocity_magnitude,
                                double rho_ae,
                                double P_infinity);

                static std::vector<double> compute_velocity_magnitude(
                                const std::vector<Vec3>& velocity);

                static void evolve_positions_euler(
                                std::vector<Vec3>& positions,
                                const std::vector<Vec3>& velocity,
                                double dt);
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

} // namespace vam



#endif //VAMCORE_FLUID_DYNAMICS_H
