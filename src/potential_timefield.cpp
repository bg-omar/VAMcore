#include "potential_timefield.h"
#include <cmath>

namespace vam {

        std::vector<double> PotentialTimeField::compute_gravitational_potential(
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

        std::vector<double> PotentialTimeField::compute_time_dilation_map(const std::vector<Vec3>& tangents,
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

} // namespace vam
