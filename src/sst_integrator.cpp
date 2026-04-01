#include "sst_integrator.h"
#include "../include/SST_Constants.h"
#include <cmath>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace sst {

namespace {
    inline Vec3 subtract(const Vec3& a, const Vec3& b) {
        return { a[0] - b[0], a[1] - b[1], a[2] - b[2] };
    }
    inline double dot_product(const Vec3& a, const Vec3& b) {
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
    }
    inline double norm_squared(const Vec3& a) {
        return a[0]*a[0] + a[1]*a[1] + a[2]*a[2];
    }
    inline double norm(const Vec3& a) {
        return std::sqrt(norm_squared(a));
    }
}

void compute_sst_mass(const std::vector<Vec3>& points, double chi_spin,
                      double& m_core, double& m_fluid) {
    using namespace SST::Constants;
    const size_t N = points.size();
    std::vector<Vec3> dp(N);
    double L_K = 0.0;

    for (size_t i = 0; i < N; ++i) {
        size_t next = (i + 1) % N;
        dp[i] = subtract(points[next], points[i]);
        L_K += norm(dp[i]);
    }

    m_core = static_cast<double>(pi * (RC_CORE * RC_CORE) * RHO_CORE * L_K);

    double neumann_integral = 0.0;
    const double r_c = static_cast<double>(RC_CORE);
    const double r_c_sq = r_c * r_c;

#ifdef _OPENMP
    #pragma omp parallel for reduction(+:neumann_integral) schedule(dynamic)
#endif
    for (size_t i = 0; i < N; ++i) {
        double local_sum = 0.0;
        for (size_t j = 0; j < N; ++j) {
            Vec3 r_diff = subtract(points[i], points[j]);
            double dist_sq = norm_squared(r_diff);
            double denom = std::sqrt(dist_sq + r_c_sq);
            double num = dot_product(dp[i], dp[j]);
            local_sum += num / denom;
        }
        neumann_integral += local_sum;
    }

    const double v_swirl = static_cast<double>(V_SWIRL);
    const double rho_f = static_cast<double>(RHO_FLUID);
    const double c_light = static_cast<double>(C_VACUUM);
    double gamma = 2.0 * static_cast<double>(pi) * r_c * v_swirl;
    double e_fluid = (rho_f * gamma * gamma / (8.0 * static_cast<double>(pi))) * (chi_spin * chi_spin) * neumann_integral;
    m_fluid = e_fluid / (c_light * c_light);
}

} // namespace sst
