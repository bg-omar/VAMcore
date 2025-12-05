#include "potential_timefield.h"
#include <cmath>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

        std::vector<double> TimeField::compute_gravitational_potential_gradient(
                        const std::vector<Vec3>& positions,
                        const std::vector<Vec3>& vorticity,
                        double epsilon) {
                size_t n = positions.size();
                std::vector<double> potential(n, 0.0);

                for (size_t i = 0; i < n; ++i) {
                        Vec3 grad_w = {0.0, 0.0, 0.0};
                        for (size_t j = 0; j < n; ++j) {
                                if (i == j) continue;
                                Vec3 dr = {positions[i][0] - positions[j][0],
                                                   positions[i][1] - positions[j][1],
                                                   positions[i][2] - positions[j][2]};
                                double r2 = dr[0]*dr[0] + dr[1]*dr[1] + dr[2]*dr[2];
                                double w = std::exp(-r2 / (2 * epsilon * epsilon));
                                grad_w[0] += w * vorticity[j][0];
                                grad_w[1] += w * vorticity[j][1];
                                grad_w[2] += w * vorticity[j][2];
                        }
                        double mag2 = grad_w[0]*grad_w[0] + grad_w[1]*grad_w[1] + grad_w[2]*grad_w[2];
                        potential[i] = -0.5 * mag2;
                }

                return potential;
        }

        std::vector<double> TimeField::compute_time_dilation_map_sqrt(const std::vector<Vec3>& tangents,
                        double C_e) {
                size_t n = tangents.size();
                std::vector<double> time_factor(n, 1.0);

                for (size_t i = 0; i < n; ++i) {
                        double v2 = tangents[i][0]*tangents[i][0] +
                                                tangents[i][1]*tangents[i][1] +
                                                tangents[i][2]*tangents[i][2];
                        double ratio = v2 / (C_e * C_e);
                        if (ratio >= 1.0) ratio = 0.999999;
                        time_factor[i] = std::sqrt(1.0 - ratio);
                }

                return time_factor;
        }

        // Direct computation method from GravityTimeField
        std::vector<double> TimeField::compute_gravitational_potential_direct(const std::vector<Vec3>& positions,
                                                                               const std::vector<Vec3>& vorticity,
                                                                               double epsilon) {
                size_t n = positions.size();
                std::vector<double> potential(n, 0.0);
                constexpr double inv_prefactor = 1.0 / (4.0 * M_PI);

                for (size_t i = 0; i < n; ++i) {
                        double phi = 0.0;
                        const auto& ri = positions[i];

                        for (size_t j = 0; j < n; ++j) {
                                if (i == j) continue;
                                const auto& rj = positions[j];
                                const auto& wj = vorticity[j];

                                Vec3 dr = { ri[0] - rj[0], ri[1] - rj[1], ri[2] - rj[2] };
                                double r2 = dr[0]*dr[0] + dr[1]*dr[1] + dr[2]*dr[2] + epsilon * epsilon;
                                double dot = dr[0]*wj[0] + dr[1]*wj[1] + dr[2]*wj[2];

                                phi += dot / std::pow(r2, 1.5);
                        }
                        potential[i] = -inv_prefactor * phi;
                }
                return potential;
        }

        // Linear method from GravityTimeField
        std::vector<double> TimeField::compute_time_dilation_map_linear(const std::vector<Vec3>& tangents,
                                                                         double C_e) {
                std::vector<double> gamma;
                gamma.reserve(tangents.size());
                for (const auto& t : tangents) {
                        double v2 = t[0]*t[0] + t[1]*t[1] + t[2]*t[2];
                        double factor = 1.0 - (v2 / (C_e * C_e));
                        gamma.push_back(factor);
                }
                return gamma;
        }

} // namespace sst