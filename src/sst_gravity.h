//
// Created by oscar on 11/21/2025.
//

#ifndef SSTCORE_SST_GRAVITY_H
#define SSTCORE_SST_GRAVITY_H
// src/sst_gravity.h

#pragma once
#include <array>
#include <vector>
#include <cmath>
#include <stdexcept>
#include <algorithm>

namespace sst {

    using Vec3 = std::array<double, 3>;

    class SSTGravity {
    public:
        // -------------------------------------------------------------------------
        // Metric 1: Beltrami Topological Shear
        // Calculates S = || B x (Curl B) ||
        //
        // Physical Significance:
        // In a Beltrami Flow, the field is parallel to its curl (Force-Free).
        // A non-zero Cross Product indicates "Vacuum Stress" — regions where
        // the magnetic topology is actively shearing the underlying Swirl Lattice.
        // -------------------------------------------------------------------------
        static std::vector<double> compute_beltrami_shear(
            const std::vector<Vec3>& B_field,
            const std::vector<Vec3>& Curl_B)
        {
            if (B_field.size() != Curl_B.size()) {
                throw std::invalid_argument("B_field and Curl_B must have the same dimension.");
            }

            std::vector<double> shear(B_field.size());

            for (size_t i = 0; i < B_field.size(); ++i) {
                const Vec3& b = B_field[i];
                const Vec3& c = Curl_B[i];

                // Cross Product: B x CurlB
                double x = b[1]*c[2] - b[2]*c[1];
                double y = b[2]*c[0] - b[0]*c[2];
                double z = b[0]*c[1] - b[1]*c[0];

                // Magnitude
                shear[i] = std::sqrt(x*x + y*y + z*z);
            }
            return shear;
        }

        // -------------------------------------------------------------------------
        // Metric 2: SST Gravity Dilation (G_local)
        // Calculates G_local = G0 * [ 1 - (v_induced / v_swirl)^2 ]
        //
        // Physical Significance:
        // Maps the local Magnetic Intensity & Frequency to the time-dilation
        // of the Swirl-Clock (T_micro).
        // Returns a scalar map where 1.0 = Standard Gravity, 0.0 = Null Gravity.
        // -------------------------------------------------------------------------
        static std::vector<double> compute_gravity_dilation(
            const std::vector<Vec3>& B_field,
            double omega_drive,
            double v_swirl = 1.09384563e6, // Canonical SST Swirl Velocity (m/s)
            double B_saturation = 100.0    // Saturation limit (Tesla)
        ) {
            std::vector<double> g_map(B_field.size());

            // Logarithmic frequency scaling (SST coupling efficiency)
            // Avoid log(0) by clamping omega
            double freq_scale = (omega_drive > 1.0) ? std::log10(omega_drive) : 0.0;
            double inv_B_sat = 1.0 / B_saturation;

            for (size_t i = 0; i < B_field.size(); ++i) {
                const Vec3& b = B_field[i];
                double B_mag = std::sqrt(b[0]*b[0] + b[1]*b[1] + b[2]*b[2]);

                // induced velocity proxy: v = v_swirl * (B/B_sat) * log10(f)
                double coupling = (B_mag * inv_B_sat) * freq_scale;

                // v_induced = v_swirl * coupling
                // ratio = v_induced / v_swirl = coupling
                // G = 1 - ratio^2
                double G = 1.0 - (coupling * coupling);

                // Clamp to [0, 1] (Gravity cannot be negative in this metric, only reduced)
                if (G < 0.0) G = 0.0;
                if (G > 1.0) G = 1.0; // Should not happen with B > 0, but safety first

                g_map[i] = G;
            }
            return g_map;
        }

        // -------------------------------------------------------------------------
        // Metric 3: Magnetic Helicity Density (h)
        // h = A . B
        //
        // Physical Significance:
        // Measures the "Knottedness" or topological linking of the field lines.
        // High Helicity Density indicates a stable "Vacuum Vortex" that resists decay.
        // In SST, this is the "Locking Mechanism" for modified gravity bubbles.
        // -------------------------------------------------------------------------
        static std::vector<double> compute_helicity_density(
            const std::vector<Vec3>& A_field,
            const std::vector<Vec3>& B_field)
        {
            if (A_field.size() != B_field.size()) {
                throw std::invalid_argument("A_field and B_field must have the same dimension.");
            }

            std::vector<double> h_map(A_field.size());

            for (size_t i = 0; i < A_field.size(); ++i) {
                const Vec3& a = A_field[i];
                const Vec3& b = B_field[i];

                // Dot Product: A . B
                h_map[i] = a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
            }
            return h_map;
        }
    };

} // namespace vam

#endif // SSTCORE_SST_GRAVITY_H