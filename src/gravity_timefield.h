#ifndef VAMCORE_GRAVITY_TIMEFIELD_H
#define VAMCORE_GRAVITY_TIMEFIELD_H
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#pragma once
#include <vector>
#include <array>

namespace vam {
        using Vec3 = std::array<double, 3>;

        class GravityTimeField {
        public:
                // Compute gravitational-like potential: Φ = -½ |∇×ω| ² (scalar field from vorticity gradient)
                static std::vector<double> compute_gravitational_potential(const std::vector<Vec3>& positions,
                                                                         const std::vector<Vec3>& vorticity,
                                                                         double epsilon = 0.1);

                // Compute time dilation factor (1 - v^2 / c^2) due to knot tangential velocities
                static std::vector<double> compute_time_dilation_map(const std::vector<Vec3>& tangents,
                                                                         double C_e);
        };

        inline std::vector<double> compute_gravitational_potential(const std::vector<Vec3>& positions,
                                                                         const std::vector<Vec3>& vorticity,
                                                                         double epsilon = 0.1) {
                return GravityTimeField::compute_gravitational_potential(positions, vorticity, epsilon);
        }

        inline std::vector<double> compute_time_dilation_map(const std::vector<Vec3>& tangents,
                                                                         double C_e) {
                return GravityTimeField::compute_time_dilation_map(tangents, C_e);
        }
}

#endif //VAMCORE_GRAVITY_TIMEFIELD_H
