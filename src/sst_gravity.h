// sst_gravity.h
#ifndef SWIRL_STRING_CORE_SST_GRAVITY_H
#define SWIRL_STRING_CORE_SST_GRAVITY_H
#pragma once

#include <array>
#include <vector>
#include <cmath>
#include <stdexcept>

namespace sst {

    using Vec3 = std::array<double, 3>;

    class SSTGravity {
    public:
        // ---------------------------------------------------------------------
        // Metric 1: Beltrami Topological Shear
        // S(i) = || B(i) x (Curl B(i)) ||
        // ---------------------------------------------------------------------
        [[nodiscard]] static std::vector<double> compute_beltrami_shear(
            const std::vector<Vec3>& B_field,
            const std::vector<Vec3>& Curl_B)
        {
            if (B_field.size() != Curl_B.size()) {
                throw std::invalid_argument("B_field and Curl_B must have the same size.");
            }

            std::vector<double> shear(B_field.size());

            for (std::size_t i = 0; i < B_field.size(); ++i) {
                const Vec3& b = B_field[i];
                const Vec3& c = Curl_B[i];

                // Cross product: B x CurlB
                const double x = b[1]*c[2] - b[2]*c[1];
                const double y = b[2]*c[0] - b[0]*c[2];
                const double z = b[0]*c[1] - b[1]*c[0];

                shear[i] = std::sqrt(x*x + y*y + z*z);
            }
            return shear;
        }

        // ---------------------------------------------------------------------
        // Metric 2: Phenomenological EM-Driven Gravity Dilation
        // G_local = 1 - [(B/B_sat) * log10(omega_drive)]^2, clamped to [0,1]
        //
        // Interpret as "gravity reduction factor" from EM driving,
        // not as the canonical Swirl Clock.
        // ---------------------------------------------------------------------
        [[nodiscard]] static std::vector<double> compute_gravity_dilation(
            const std::vector<Vec3>& B_field,
            double omega_drive,
            double v_swirl = 1.09384563e6, // kept for future variants
            double B_saturation = 100.0    // Tesla
        ) {
            if (B_saturation <= 0.0) {
                throw std::invalid_argument("B_saturation must be positive.");
            }

            std::vector<double> g_map(B_field.size());

            // Log-frequency scaling; omega_drive is assumed > 0 in Hz or rad/s
            double freq_scale = 0.0;
            if (omega_drive > 0.0) {
                // Optional: normalize by a reference frequency if desired
                const double omega_ref = 1.0;
                freq_scale = std::log10(omega_drive / omega_ref);
            }

            const double inv_B_sat = 1.0 / B_saturation;

            for (std::size_t i = 0; i < B_field.size(); ++i) {
                const Vec3& b = B_field[i];
                const double B_mag = std::sqrt(b[0]*b[0] + b[1]*b[1] + b[2]*b[2]);

                const double coupling = (B_mag * inv_B_sat) * freq_scale;
                double G = 1.0 - coupling * coupling;

                if (G < 0.0) G = 0.0;
                if (G > 1.0) G = 1.0;

                g_map[i] = G;
            }
            return g_map;
        }

        // ---------------------------------------------------------------------
        // Metric 3: Magnetic Helicity Density
        // h(i) = A(i) . B(i)
        // ---------------------------------------------------------------------
        [[nodiscard]] static std::vector<double> compute_helicity_density(
            const std::vector<Vec3>& A_field,
            const std::vector<Vec3>& B_field)
        {
            if (A_field.size() != B_field.size()) {
                throw std::invalid_argument("A_field and B_field must have the same size.");
            }

            std::vector<double> h_map(A_field.size());

            for (std::size_t i = 0; i < A_field.size(); ++i) {
                const Vec3& a = A_field[i];
                const Vec3& b = B_field[i];

                h_map[i] = a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
            }
            return h_map;
        }

        // ---------------------------------------------------------------------
        // Metric 4: Swirl Clock Factor S_t from local swirl velocity
        // S_t = sqrt(1 - ||v_swirl||^2 / c^2), clamped to [0,1].
        // This is the canonical SST time-dilation factor.
        // ---------------------------------------------------------------------
        [[nodiscard]] static std::vector<double> compute_swirl_clock(
            const std::vector<Vec3>& v_swirl_field,
            double c = 2.99792458e8 // m/s
        ) {
            std::vector<double> St_map(v_swirl_field.size());
            const double c2 = c * c;

            for (std::size_t i = 0; i < v_swirl_field.size(); ++i) {
                const Vec3& v = v_swirl_field[i];
                const double v2 = v[0]*v[0] + v[1]*v[1] + v[2]*v[2];

                double arg = 1.0 - v2 / c2;
                if (arg < 0.0) arg = 0.0; // superluminal guard
                St_map[i] = std::sqrt(arg);
            }
            return St_map;
        }

        // ---------------------------------------------------------------------
        // Metric 5: Swirl Coulomb Potential (Hydrogenic)
        // V(r) = -Lambda / sqrt(r^2 + r_c^2)
        //
        // radii: vector of r >= 0
        // ---------------------------------------------------------------------
        [[nodiscard]] static std::vector<double> compute_swirl_coulomb_potential(
            const std::vector<double>& radii,
            double Lambda,
            double r_c
        ) {
            if (r_c <= 0.0) {
                throw std::invalid_argument("r_c must be positive.");
            }

            std::vector<double> V(radii.size());
            const double rc2 = r_c * r_c;

            for (std::size_t i = 0; i < radii.size(); ++i) {
                const double r = radii[i];
                const double denom = std::sqrt(r * r + rc2);
                V[i] = -Lambda / denom;
            }
            return V;
        }

        // ---------------------------------------------------------------------
        // Metric 6: Swirl Coulomb Radial Force
        // F_r(r) = -dV/dr = -Lambda * r / (r^2 + r_c^2)^(3/2)
        // (sign convention: negative => attractive towards r=0).
        // ---------------------------------------------------------------------
        [[nodiscard]] static std::vector<double> compute_swirl_coulomb_force(
            const std::vector<double>& radii,
            double Lambda,
            double r_c
        ) {
            if (r_c <= 0.0) {
                throw std::invalid_argument("r_c must be positive.");
            }

            std::vector<double> F(radii.size());
            const double rc2 = r_c * r_c;

            for (std::size_t i = 0; i < radii.size(); ++i) {
                const double r = radii[i];
                const double denom = std::pow(r * r + rc2, 1.5);
                F[i] = (denom > 0.0) ? (-Lambda * r / denom) : 0.0;
            }
            return F;
        }

        // ---------------------------------------------------------------------
        // Metric 7: Swirl Energy Density
        // rho_E = 0.5 * rho_f * ||v||^2
        // ---------------------------------------------------------------------
        [[nodiscard]] static std::vector<double> compute_swirl_energy_density(
            const std::vector<Vec3>& v_field,
            double rho_f
        ) {
            std::vector<double> rhoE(v_field.size());

            for (std::size_t i = 0; i < v_field.size(); ++i) {
                const Vec3& v = v_field[i];
                const double v2 = v[0]*v[0] + v[1]*v[1] + v[2]*v[2];
                rhoE[i] = 0.5 * rho_f * v2;
            }
            return rhoE;
        }

        // ---------------------------------------------------------------------
        // Metric 8: Effective Swirl Gravitational Coupling
        // G_swirl = v_swirl * c^5 * t_p^2 / (2 * F_max * r_c^2)
        // (Canon mapping to Newton's G).
        // ---------------------------------------------------------------------
        [[nodiscard]] static double compute_G_swirl(
            double v_swirl,
            double t_p,
            double F_max,
            double r_c,
            double c = 2.99792458e8
        ) {
            if (F_max <= 0.0 || r_c <= 0.0) {
                throw std::invalid_argument("F_max and r_c must be positive.");
            }

            const double c5 = c * c * c * c * c;
            return v_swirl * c5 * t_p * t_p / (2.0 * F_max * r_c * r_c);
        }
    };

} // namespace sst

#endif // SWIRL_STRING_CORE_SST_GRAVITY_H