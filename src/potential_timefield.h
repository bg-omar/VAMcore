//
// Created by mr on 3/22/2025.
//

#ifndef SWIRL_STRING_CORE_TIMEFIELD_H
#define SWIRL_STRING_CORE_TIMEFIELD_H


// include/potential_timefield.hpp
#pragma once

#include <array>
#include <vector>

namespace sst {

	using Vec3 = std::array<double, 3>;

        class TimeField {
        public:
                // Compute scalar gravitational potential field due to vorticity gradients (gradient-based method)
                static std::vector<double> compute_gravitational_potential_gradient(
                                const std::vector<Vec3>& positions,
                                const std::vector<Vec3>& vorticity,
                                double epsilon = 7e-7);

                // Compute time dilation factor using sqrt (1 - v^2 / c^2) due to knot tangential velocities
                static std::vector<double> compute_time_dilation_map_sqrt(
                                const std::vector<Vec3>& tangential_velocities,
                                double ce = 1093845.63);

                // Compute gravitational potential field (direct computation method from GravityTimeField)
                static std::vector<double> compute_gravitational_potential_direct(
                                const std::vector<Vec3>& positions,
                                const std::vector<Vec3>& vorticity,
                                double epsilon = 0.1);

                // Compute time dilation factor (linear method from GravityTimeField)
                static std::vector<double> compute_time_dilation_map_linear(
                                const std::vector<Vec3>& tangents,
                                double C_e);
        };

        // Inline wrappers for backward compatibility
        inline std::vector<double> compute_gravitational_potential(
                        const std::vector<Vec3>& positions,
                        const std::vector<Vec3>& vorticity,
                        double epsilon = 7e-7) {
                return TimeField::compute_gravitational_potential_gradient(positions, vorticity, epsilon);
        }

        inline std::vector<double> compute_time_dilation_map(
                        const std::vector<Vec3>& tangential_velocities,
                        double ce = 1093845.63) {
                return TimeField::compute_time_dilation_map_sqrt(tangential_velocities, ce);
        }

} // namespace sst


#endif //SWIRL_STRING_CORE_TIMEFIELD_H