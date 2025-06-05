#ifndef VAMCORE_FRENET_HELICITY_H
#define VAMCORE_FRENET_HELICITY_H
#pragma once
#include "../include/vec3_utils.h"
#include <array>
#include <vector>

namespace vam {

        using Vec3 = std::array<double, 3>;

        class FrenetHelicity {
        public:
                static void compute_frenet_frames(const std::vector<Vec3>& X,
                                                           std::vector<Vec3>& T,
                                                           std::vector<Vec3>& N,
                                                           std::vector<Vec3>& B);

                static void compute_curvature_torsion(const std::vector<Vec3>& T,
                                                                   const std::vector<Vec3>& N,
                                                                   std::vector<double>& curvature,
                                                                   std::vector<double>& torsion);

                static float compute_helicity(const std::vector<Vec3>& velocity,
                                                   const std::vector<Vec3>& vorticity);

                static std::vector<Vec3> rk4_integrate(const std::vector<Vec3>& positions,
                                                                        const std::vector<Vec3>& tangents,
                                                                        double dt,
                                                                        double gamma = 1.0);

                static std::vector<Vec3> evolve_vortex_knot(const std::vector<Vec3>& positions,
                                                                        const std::vector<Vec3>& tangents,
                                                                        double dt,
                                                                        double gamma = 1.0);
        };

        inline void compute_frenet_frames(const std::vector<Vec3>& X,
                                                           std::vector<Vec3>& T,
                                                           std::vector<Vec3>& N,
                                                           std::vector<Vec3>& B) {
                FrenetHelicity::compute_frenet_frames(X, T, N, B);
        }

        inline void compute_curvature_torsion(const std::vector<Vec3>& T,
                                                                   const std::vector<Vec3>& N,
                                                                   std::vector<double>& curvature,
                                                                   std::vector<double>& torsion) {
                FrenetHelicity::compute_curvature_torsion(T, N, curvature, torsion);
        }

        inline float compute_helicity(const std::vector<Vec3>& velocity,
                                                   const std::vector<Vec3>& vorticity) {
                return FrenetHelicity::compute_helicity(velocity, vorticity);
        }

        inline std::vector<Vec3> rk4_integrate(const std::vector<Vec3>& positions,
                                                                        const std::vector<Vec3>& tangents,
                                                                        double dt,
                                                                        double gamma = 1.0) {
                return FrenetHelicity::rk4_integrate(positions, tangents, dt, gamma);
        }

        inline std::vector<Vec3> evolve_vortex_knot(const std::vector<Vec3>& positions,
                                                                        const std::vector<Vec3>& tangents,
                                                                        double dt,
                                                                        double gamma = 1.0) {
                return FrenetHelicity::evolve_vortex_knot(positions, tangents, dt, gamma);
        }

} // namespace vam

#endif //VAMCORE_FRENET_HELICITY_H
