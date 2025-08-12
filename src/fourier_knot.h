#pragma once
#include <array>
#include <string>
#include <vector>
#include "../include/vec3_utils.h" // Your existing Vec3 struct and math
namespace vam {

using Vec3 = std::array<double, 3>;

struct FourierBlock {
    std::string header;                 // optional header (may be empty)
    std::vector<double> a_x, b_x;
    std::vector<double> a_y, b_y;
    std::vector<double> a_z, b_z;
};


class fourier_knot {
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

} // namespace vam

