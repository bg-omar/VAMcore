//
// Created by mr on 3/22/2025.
//

#ifndef SSTCORE_POTENTIAL_TIMEFIELD_H
#define SSTCORE_POTENTIAL_TIMEFIELD_H


// include/potential_timefield.hpp
#pragma once

#include <array>
#include <vector>

namespace sst {

	using Vec3 = std::array<double, 3>;

        class PotentialTimeField {
        public:
                // Compute scalar gravitational potential field due to vorticity gradients
                static std::vector<double> compute_gravitational_potential(
                                const std::vector<Vec3>& positions,
                                const std::vector<Vec3>& vorticity,
                                double aether_density = 7e-7);

                // Compute time dilation factor (1 - v^2 / c^2) due to knot tangential velocities
                static std::vector<double> compute_time_dilation_map(
                                const std::vector<Vec3>& tangential_velocities,
                                double ce = 1093845.63);
        };

        inline std::vector<double> compute_gravitational_potential(
                        const std::vector<Vec3>& positions,
                        const std::vector<Vec3>& vorticity,
                        double aether_density = 7e-7) {
                return PotentialTimeField::compute_gravitational_potential(positions, vorticity, aether_density);
        }

        inline std::vector<double> compute_time_dilation_map(
                        const std::vector<Vec3>& tangential_velocities,
                        double ce = 1093845.63) {
                return PotentialTimeField::compute_time_dilation_map(tangential_velocities, ce);
        }

} // namespace sst


#endif //SSTCORE_POTENTIAL_TIMEFIELD_H