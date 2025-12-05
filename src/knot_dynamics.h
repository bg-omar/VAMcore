//
// Created by mr on 3/22/2025.
//

#ifndef SSTCORE_KNOT_DYNAMICS_H
#define SSTCORE_KNOT_DYNAMICS_H

#include "../include/vec3_utils.h"
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
// include/knot_dynamics.hpp
#pragma once

#include <vector>
#include <array>
#include <string>
#include <stdexcept>

namespace sst {

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

                // Fourier series evaluation (from heavy_knot)
                struct FourierResult {
                        std::vector<Vec3> positions;
                        std::vector<Vec3> tangents;
                };
                static FourierResult evaluate_fourier_series(
                        const std::vector<std::array<double, 6>>& coeffs,
                        const std::vector<double>& t_vals);

                // Writhe computation using Gauss integral with tangents (from heavy_knot)
                static double writhe_gauss_curve(
                        const std::vector<Vec3>& r,
                        const std::vector<Vec3>& r_t);

                // Estimate crossing number from projections (from heavy_knot)
                static int estimate_crossing_number(
                        const std::vector<Vec3>& r,
                        int directions = 24,
                        int seed = 12345);

                // Planar diagram from curve (from knot_pd)
                using Crossing = std::array<int, 4>;
                using PD = std::vector<Crossing>;
                static PD pd_from_curve(
                        const std::vector<Vec3>& P3,
                        int tries = 40,
                        unsigned int seed = 12345,
                        double min_angle_deg = 1.0,
                        double depth_tol = 1e-6);
        };

        // Fourier knot representation (from fourier_knot)
        struct FourierBlock {
                std::string header;                 // optional header (may be empty)
                std::vector<double> a_x, b_x;
                std::vector<double> a_y, b_y;
                std::vector<double> a_z, b_z;
        };

        class FourierKnot {
        public:
                struct Block {
                        std::vector<double> a_x, b_x, a_y, b_y, a_z, b_z;
                };
                std::vector<Block> blocks;
                Block activeBlock;
                std::vector<Vec3> points;

                void loadBlocks(const std::string& filename);
                void selectMaxHarmonics();
                void reconstruct(size_t N = 1000);
                // Parse a .fseries file into blocks. Each block is separated by either a '%' header
                // or by a blank line. Lines contain 6 doubles: a_x b_x a_y b_y a_z b_z
                static std::vector<FourierBlock> parse_fseries_multi(const std::string& path);

                // Choose the block with the largest number of harmonics
                static int index_of_largest_block(const std::vector<FourierBlock>& blocks);

                // Evaluate r(s) for a block on samples s (radians in [0,2π])
                static std::vector<Vec3> evaluate(const FourierBlock& block, const std::vector<double>& s);

                // Center points at their centroid and return centered points
                static std::vector<Vec3> center_points(const std::vector<Vec3>& pts);

                // Discrete curvature from points using central differences (periodic curve)
                static std::vector<double> curvature(const std::vector<Vec3>& pts, double eps = 1e-8);

                // Convenience: load file, pick largest block, evaluate on ns samples in [0,2π],
                // center the result and return (points, curvature)
                static std::pair<std::vector<Vec3>, std::vector<double>>
                load_knot(const std::string& path, int nsamples);

        private:
                static Vec3 evalPoint(const Block& blk, double s);
        };

        // Vortex knot system (from vortex_knot_system)
        class VortexKnotSystem {
        public:
                VortexKnotSystem(double gamma = 1.0);

                void initialize_trefoil_knot(size_t resolution = 400);
                void initialize_figure8_knot(size_t resolution = 400);

                void evolve(double dt, size_t steps);

                const std::vector<Vec3>& get_positions() const;
                const std::vector<Vec3>& get_tangents() const;

        private:
                std::vector<Vec3> positions;
                std::vector<Vec3> tangents;
                double circulation;

                void compute_tangents();
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

} // namespace sst


#endif //SSTCORE_KNOT_DYNAMICS_H