//
// Created by mr on 3/22/2025.
//

#ifndef SWIRL_STRING_CORE_KNOT_DYNAMICS_H
#define SWIRL_STRING_CORE_KNOT_DYNAMICS_H

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
#include <tuple>
#include <map>

namespace sst {

	using Vec3 = std::array<double, 3>;

	// Forward declaration
	struct FourierBlock;
	
	// Forward declaration for embedded knot files (generated during build)
	std::map<std::string, std::string> get_embedded_knot_files();

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

                // Biot-Savart and helicity calculations (wrappers for BiotSavart)
                // Compute Biot-Savart velocity field from a closed curve at grid points
                static std::vector<Vec3> compute_biot_savart_velocity_grid(
                        const std::vector<Vec3>& curve,
                        const std::vector<Vec3>& grid_points);

                // Compute vorticity from velocity field on a regular grid
                static std::vector<Vec3> compute_vorticity_grid(
                        const std::vector<Vec3>& velocity,
                        const std::array<int, 3>& shape,
                        double spacing);

                // Extract cubic interior field subset
                static std::vector<Vec3> extract_interior_field(
                        const std::vector<Vec3>& field,
                        const std::array<int, 3>& shape,
                        int margin);

                // Compute helicity invariants (H_charge, H_mass, a_mu)
                static std::tuple<double, double, double> compute_helicity_invariants(
                        const std::vector<Vec3>& v_sub,
                        const std::vector<Vec3>& w_sub,
                        const std::vector<double>& r_sq);

                // High-level method: compute helicity from Fourier block
                // Returns (H_charge, H_mass, a_mu)
                static std::tuple<double, double, double> compute_helicity_from_fourier_block(
                        const FourierBlock& block,
                        int grid_size = 32,
                        double spacing = 0.1,
                        int interior_margin = 8,
                        int nsamples = 1000);
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
                
                // Parse .fseries content from a string (for embedded files)
                static std::vector<FourierBlock> parse_fseries_from_string(const std::string& content);

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

                // Structure for loaded knot data
                struct LoadedKnot {
                        std::string name;                    // filename without extension
                        std::vector<Vec3> points;            // evaluated points
                        std::vector<double> curvature;        // curvature at each point
                };

                // Load all knots from a list of file paths, return vector of LoadedKnot
                // Each knot uses the largest block and is evaluated with nsamples points
                static std::vector<LoadedKnot>
                load_all_knots(const std::vector<std::string>& paths, int nsamples = 1000);

        private:
                static Vec3 evalPoint(const Block& blk, double s);
        };

        // Vortex knot system (from vortex_knot_system)
        class VortexKnotSystem {
        public:
                VortexKnotSystem(double gamma = 1.0);

                void initialize_trefoil_knot(size_t resolution = 400);
                void initialize_figure8_knot(size_t resolution = 400);
                
                // Initialize any knot from .fseries file by identifier (e.g., "3_1", "4_1", "5_1")
                // Searches in standard locations for knot_fseries directory
                void initialize_knot_from_name(const std::string& knot_id, size_t resolution = 1000);

                void evolve(double dt, size_t steps);

                const std::vector<Vec3>& get_positions() const;
                const std::vector<Vec3>& get_tangents() const;

        private:
                std::vector<Vec3> positions;
                std::vector<Vec3> tangents;
                double circulation;

                void compute_tangents();
                static std::string find_knot_file(const std::string& knot_id);
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


#endif //SWIRL_STRING_CORE_KNOT_DYNAMICS_H