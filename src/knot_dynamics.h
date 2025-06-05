//
// Created by mr on 3/22/2025.
//

#ifndef VAMCORE_KNOT_DYNAMICS_H
#define VAMCORE_KNOT_DYNAMICS_H

#include "../include/vec3_utils.h"
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
// include/knot_dynamics.hpp
#pragma once

#include <vector>
#include <array>

namespace vam {

	using Vec3 = std::array<double, 3>;

        class KnotDynamics {
        public:
                // Compute writhe from filament centerline
                // Ref: Călugăreanu-White formula (approximated)
                static double compute_writhe(const std::vector<Vec3>& centerline);

                // Compute linking number between two vortex filaments
                static int compute_linking_number(const std::vector<Vec3>& curve1, const std::vector<Vec3>& curve2);

                // Compute twist given tangent and normal
                // Twist = ∫ (T × dN/ds) ⋅ B ds
                static double compute_twist(const std::vector<Vec3>& T, const std::vector<Vec3>& B);

                // Compute centerline helicity invariant H_cl
                // H_cl = Lk + Wr, combines link and writhe
                static double compute_centerline_helicity(const std::vector<Vec3>& curve,
                                                                           const std::vector<Vec3>& tangent);

                // Check for reconnection events
                // Returns indices of close approach
                static std::vector<std::pair<int, int>> detect_reconnection_candidates(
                        const std::vector<Vec3>& curve, double threshold);
        };

        inline double compute_writhe(const std::vector<Vec3>& centerline) {
                return KnotDynamics::compute_writhe(centerline);
        }

        inline int compute_linking_number(const std::vector<Vec3>& curve1, const std::vector<Vec3>& curve2) {
                return KnotDynamics::compute_linking_number(curve1, curve2);
        }

        inline double compute_twist(const std::vector<Vec3>& T, const std::vector<Vec3>& B) {
                return KnotDynamics::compute_twist(T, B);
        }

        inline double compute_centerline_helicity(const std::vector<Vec3>& curve,
                                                                           const std::vector<Vec3>& tangent) {
                return KnotDynamics::compute_centerline_helicity(curve, tangent);
        }

        inline std::vector<std::pair<int, int>> detect_reconnection_candidates(
                        const std::vector<Vec3>& curve, double threshold) {
                return KnotDynamics::detect_reconnection_candidates(curve, threshold);
        }

} // namespace vam


#endif //VAMCORE_KNOT_DYNAMICS_H
