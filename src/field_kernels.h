//
// Created by omar.iskandarani on 8/12/2025.
//

#ifndef SWIRL_STRING_CORE_FIELD_KERNELS_H
#define SWIRL_STRING_CORE_FIELD_KERNELS_H
// field_kernels.h
// Static kernels for Biot–Savart over a wire polyline and dipole superposition.
// Units: mu0 = 1, so factor = 1/(4π).
#pragma once
#include <array>
#include <vector>
#include <cstddef>
#include <cmath>
#include <algorithm>

namespace sst {

using Vec3 = std::array<double, 3>;

class FieldKernels {
public:
    // Analytical point dipole field:
    // B(r) = (1/(4π r^3)) [3 (m·r̂) r̂ - m], with mu0=1.
    static Vec3 dipole_field_at_point(const Vec3& r, const Vec3& m) {
        constexpr double PI = 3.1415926535897932384626433832795;
        constexpr double K  = 1.0 / (4.0 * PI);
        const double eps = 1e-12;

        const double R2 = r[0]*r[0] + r[1]*r[1] + r[2]*r[2];
        const double R  = std::sqrt(R2);
        if (R < eps) return {0.0, 0.0, 0.0};

        // c = 3 (m·r̂) = 3 (m·r)/|r|
        const double mdotr = (m[0]*r[0] + m[1]*r[1] + m[2]*r[2]) / R;
        const double c_over_R = 3.0 * mdotr / R;               // 3 (m·r̂)/|r|
        // 3 (m·r̂) r̂ - m  == (c_over_R) * (r/|r|) - m == (c_over_R/R) * r - m
        const double c_over_R2 = c_over_R / R;                 // 3 (m·r)/R^2
        const Vec3 term { c_over_R2 * r[0] - m[0],
                          c_over_R2 * r[1] - m[1],
                          c_over_R2 * r[2] - m[2] };

        const double invR3 = 1.0 / (R2 * R);
        return { K * term[0] * invR3, K * term[1] * invR3, K * term[2] * invR3 };
    }

    // Biot–Savart over a polyline defined by wire_points[N,3] (midpoint rule).
    // Inputs: flattened grid arrays X,Y,Z (length n_grid).
    // Output: accumulates into Bx,By,Bz (length n_grid).
    static void biot_savart_wire_grid(const double* X,
                                      const double* Y,
                                      const double* Z,
                                      std::size_t n_grid,
                                      const std::vector<Vec3>& wire_points,
                                      double current,
                                      double* Bx,
                                      double* By,
                                      double* Bz)
    {
        constexpr double PI = 3.1415926535897932384626433832795;
        constexpr double K  = 1.0 / (4.0 * PI);
        const double factor = K * current;
        const double eps = 1e-12;

        if (wire_points.size() < 2) return;

        // Precompute segments (dl) and midpoints
        const std::size_t S = wire_points.size() - 1;
        std::vector<Vec3> mid(S), dl(S);
        for (std::size_t i = 0; i < S; ++i) {
            const Vec3& p0 = wire_points[i];
            const Vec3& p1 = wire_points[i+1];
            mid[i] = { 0.5*(p0[0]+p1[0]), 0.5*(p0[1]+p1[1]), 0.5*(p0[2]+p1[2]) };
            dl[i]  = { p1[0]-p0[0],       p1[1]-p0[1],       p1[2]-p0[2]       };
        }

        for (std::size_t s = 0; s < S; ++s) {
            const Vec3& mp = mid[s];
            const Vec3& d  = dl[s];
            for (std::size_t i = 0; i < n_grid; ++i) {
                const Vec3 r { X[i] - mp[0], Y[i] - mp[1], Z[i] - mp[2] };
                const double R2 = r[0]*r[0] + r[1]*r[1] + r[2]*r[2];
                const double R  = std::sqrt(R2);
                if (R < eps) continue;
                const double invR3 = 1.0 / (R2 * R);
                const Vec3 c { d[1]*r[2] - d[2]*r[1],
                               d[2]*r[0] - d[0]*r[2],
                               d[0]*r[1] - d[1]*r[0] };
                Bx[i] += factor * c[0] * invR3;
                By[i] += factor * c[1] * invR3;
                Bz[i] += factor * c[2] * invR3;
            }
        }
    }

    // Superposition of M point dipoles on grid.
    static void dipole_ring_field_grid(const double* X,
                                       const double* Y,
                                       const double* Z,
                                       std::size_t n_grid,
                                       const std::vector<Vec3>& positions,
                                       const std::vector<Vec3>& moments,
                                       double* Bx,
                                       double* By,
                                       double* Bz)
    {
        const std::size_t M = std::min(positions.size(), moments.size());
        for (std::size_t d = 0; d < M; ++d) {
            const Vec3& p = positions[d];
            const Vec3& m = moments[d];
            for (std::size_t i = 0; i < n_grid; ++i) {
                const Vec3 r { X[i] - p[0], Y[i] - p[1], Z[i] - p[2] };
                const Vec3 B = dipole_field_at_point(r, m);
                Bx[i] += B[0];
                By[i] += B[1];
                Bz[i] += B[2];
            }
        }
    }
};

} // namespace sst


#endif // SWIRL_STRING_CORE_FIELD_KERNELS_H