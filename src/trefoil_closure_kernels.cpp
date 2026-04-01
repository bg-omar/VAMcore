// Port of trefoil_closure/sst_core.cpp geometry kernels (keep numerics in sync).
#include "trefoil_closure_kernels.h"
#include <algorithm>
#include <cmath>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

double trefoil_neumann_self_energy(const double* r, std::size_t n, double rc) {
    if (n < 2) {
        return 0.0;
    }
    double integral_val = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        const std::size_t next_i = (i + 1) % n;
        const double dx1 = r[next_i * 3 + 0] - r[i * 3 + 0];
        const double dy1 = r[next_i * 3 + 1] - r[i * 3 + 1];
        const double dz1 = r[next_i * 3 + 2] - r[i * 3 + 2];
        for (std::size_t j = i + 1; j < n; ++j) {
            const std::size_t next_j = (j + 1) % n;
            const double dx2 = r[next_j * 3 + 0] - r[j * 3 + 0];
            const double dy2 = r[next_j * 3 + 1] - r[j * 3 + 1];
            const double dz2 = r[next_j * 3 + 2] - r[j * 3 + 2];
            const double rx = r[j * 3 + 0] - r[i * 3 + 0];
            const double ry = r[j * 3 + 1] - r[i * 3 + 1];
            const double rz = r[j * 3 + 2] - r[i * 3 + 2];
            const double dist2 = rx * rx + ry * ry + rz * rz;
            const double reg_dist = std::sqrt(dist2 + rc * rc);
            const double dot_product = dx1 * dx2 + dy1 * dy2 + dz1 * dz2;
            integral_val += 2.0 * (dot_product / reg_dist);
        }
    }
    return integral_val;
}

double trefoil_core_repulsion(const double* r, std::size_t n, double rc) {
    if (n < 3) {
        return 0.0;
    }
    double U_rep = 0.0;
    const double core_diameter = 2.0 * rc;
    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = i + 2; j < n; ++j) {
            if (i == 0 && j == n - 1) {
                continue;
            }
            const double rx = r[j * 3 + 0] - r[i * 3 + 0];
            const double ry = r[j * 3 + 1] - r[i * 3 + 1];
            const double rz = r[j * 3 + 2] - r[i * 3 + 2];
            double dist = std::sqrt(rx * rx + ry * ry + rz * rz);
            if (dist < 1e-30) {
                dist = 1e-30;
            }
            const double ratio = core_diameter / dist;
            if (ratio > 0.1) {
                U_rep += std::pow(ratio, 12.0);
            }
        }
    }
    return U_rep;
}

double trefoil_polyline_length(const double* r, std::size_t n) {
    if (n < 2) {
        return 0.0;
    }
    double length = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        const std::size_t next_i = (i + 1) % n;
        const double dx = r[next_i * 3 + 0] - r[i * 3 + 0];
        const double dy = r[next_i * 3 + 1] - r[i * 3 + 1];
        const double dz = r[next_i * 3 + 2] - r[i * 3 + 2];
        length += std::sqrt(dx * dx + dy * dy + dz * dz);
    }
    return length;
}

double trefoil_writhe_reg(const double* r, std::size_t n, double rc) {
    if (n < 2) {
        return 0.0;
    }
    double writhe_val = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        const std::size_t next_i = (i + 1) % n;
        const double dx1 = r[next_i * 3 + 0] - r[i * 3 + 0];
        const double dy1 = r[next_i * 3 + 1] - r[i * 3 + 1];
        const double dz1 = r[next_i * 3 + 2] - r[i * 3 + 2];
        for (std::size_t j = i + 1; j < n; ++j) {
            const std::size_t next_j = (j + 1) % n;
            const double dx2 = r[next_j * 3 + 0] - r[j * 3 + 0];
            const double dy2 = r[next_j * 3 + 1] - r[j * 3 + 1];
            const double dz2 = r[next_j * 3 + 2] - r[j * 3 + 2];
            const double rx = r[j * 3 + 0] - r[i * 3 + 0];
            const double ry = r[j * 3 + 1] - r[i * 3 + 1];
            const double rz = r[j * 3 + 2] - r[i * 3 + 2];
            const double cx = dy1 * dz2 - dz1 * dy2;
            const double cy = dz1 * dx2 - dx1 * dz2;
            const double cz = dx1 * dy2 - dy1 * dx2;
            const double triple_scalar = rx * cx + ry * cy + rz * cz;
            const double dist2 = rx * rx + ry * ry + rz * rz;
            const double dist_reg = std::sqrt(dist2 + rc * rc);
            writhe_val += 2.0 * triple_scalar / (dist_reg * dist_reg * dist_reg);
        }
    }
    return writhe_val / (4.0 * M_PI);
}

double trefoil_curvature_penalty_menger(const double* r, std::size_t n) {
    if (n < 2) {
        return 0.0;
    }
    double total_curvature_sq = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        const std::size_t prev = (i - 1 + n) % n;
        const std::size_t next = (i + 1) % n;
        const double v1x = r[i * 3 + 0] - r[prev * 3 + 0];
        const double v1y = r[i * 3 + 1] - r[prev * 3 + 1];
        const double v1z = r[i * 3 + 2] - r[prev * 3 + 2];
        const double v2x = r[next * 3 + 0] - r[i * 3 + 0];
        const double v2y = r[next * 3 + 1] - r[i * 3 + 1];
        const double v2z = r[next * 3 + 2] - r[i * 3 + 2];
        const double v3x = r[next * 3 + 0] - r[prev * 3 + 0];
        const double v3y = r[next * 3 + 1] - r[prev * 3 + 1];
        const double v3z = r[next * 3 + 2] - r[prev * 3 + 2];
        const double cx = v1y * v2z - v1z * v2y;
        const double cy = v1z * v2x - v1x * v2z;
        const double cz = v1x * v2y - v1y * v2x;
        const double cross_norm = std::sqrt(cx * cx + cy * cy + cz * cz);
        const double v1_norm = std::sqrt(v1x * v1x + v1y * v1y + v1z * v1z);
        const double v2_norm = std::sqrt(v2x * v2x + v2y * v2y + v2z * v2z);
        const double v3_norm = std::sqrt(v3x * v3x + v3y * v3y + v3z * v3z);
        double kappa = 0.0;
        if (v1_norm > 1e-20 && v2_norm > 1e-20 && v3_norm > 1e-20) {
            kappa = (2.0 * cross_norm) / (v1_norm * v2_norm * v3_norm);
        }
        const double ds = (v1_norm + v2_norm) / 2.0;
        total_curvature_sq += kappa * kappa * ds;
    }
    return total_curvature_sq;
}

}  // namespace sst
