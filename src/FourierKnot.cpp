#include "FourierKnot.hpp"
#include "biot_savart.h"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <numeric>
#include <sstream>
#include <stdexcept>

namespace vam {
static inline double wrap_index(int i, int n) {
  int r = i % n;
  return (r < 0) ? r + n : r;
}

std::vector<FourierBlock> FourierKnot::parse_fseries_multi(const std::string& path) {
  std::ifstream in(path);
  std::vector<FourierBlock> blocks;
  if (!in) return blocks;

  FourierBlock cur;
  auto flush_block = [&]() {
    if (!cur.a_x.empty()) {
      blocks.emplace_back(cur);
      cur = FourierBlock{};
    }
  };

  std::string line;
  while (std::getline(in, line)) {
    // trim
    while (!line.empty() && (line.back()=='\r' || line.back()=='\n' || line.back()==' ' || line.back()=='\t')) line.pop_back();
    if (line.empty()) { flush_block(); continue; }
    if (line.size() && line[0] == '%') {
      flush_block();
      cur.header = std::string(line.begin()+1, line.end());
      // trim leading spaces
      while (!cur.header.empty() && (cur.header.front()==' ' || cur.header.front()=='\t')) cur.header.erase(cur.header.begin());
      continue;
    }
    std::istringstream iss(line);
    double ax,bx,ay,by,az,bz;
    if (iss >> ax >> bx >> ay >> by >> az >> bz) {
      cur.a_x.push_back(ax); cur.b_x.push_back(bx);
      cur.a_y.push_back(ay); cur.b_y.push_back(by);
      cur.a_z.push_back(az); cur.b_z.push_back(bz);
    }
  }
  flush_block();
  return blocks;
}

int FourierKnot::index_of_largest_block(const std::vector<FourierBlock>& blocks) {
  if (blocks.empty()) return -1;
  int idx = 0;
  size_t best = blocks[0].a_x.size();
  for (int i=1;i<(int)blocks.size();++i) {
    size_t n = blocks[i].a_x.size();
    if (n > best) { best = n; idx = i; }
  }
  return idx;
}

std::vector<Vec3> FourierKnot::evaluate(const FourierBlock& b, const std::vector<double>& s) {
  const int N = (int)b.a_x.size();
  std::vector<Vec3> out(s.size(), {0.0,0.0,0.0});
  for (size_t i=0;i<s.size();++i) {
    double si = s[i];
    double x=0, y=0, z=0;
    for (int j=0;j<N;++j) {
      int n = j+1;
      double cn = std::cos(n*si), sn = std::sin(n*si);
      x += b.a_x[j]*cn + b.b_x[j]*sn;
      y += b.a_y[j]*cn + b.b_y[j]*sn;
      z += b.a_z[j]*cn + b.b_z[j]*sn;
    }
    out[i] = {x,y,z};
  }
  return out;
}

std::vector<Vec3> FourierKnot::center_points(const std::vector<Vec3>& pts) {
  if (pts.empty()) return {};
  double cx=0, cy=0, cz=0;
  for (auto &p: pts) { cx+=p[0]; cy+=p[1]; cz+=p[2]; }
  cx/=pts.size(); cy/=pts.size(); cz/=pts.size();
  std::vector<Vec3> out; out.reserve(pts.size());
  for (auto &p: pts) out.push_back({p[0]-cx, p[1]-cy, p[2]-cz});
  return out;
}

std::vector<double> FourierKnot::curvature(const std::vector<Vec3>& pts, double eps) {
  const int n = (int)pts.size();
  std::vector<double> k(n, 0.0);
  if (n < 3) return k;

  auto minus = [](const Vec3& a, const Vec3& b)->Vec3 { return {a[0]-b[0], a[1]-b[1], a[2]-b[2]}; };
  auto cross = [](const Vec3& a, const Vec3& b)->Vec3 {
    return {a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]};
  };
  auto norm = [](const Vec3& a)->double { return std::sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2]); };

  // Uniform parameterization, periodic central differences
  for (int i=0;i<n;++i) {
    const Vec3& pm = pts[(i-1+n)%n];
    const Vec3& p0 = pts[i];
    const Vec3& pp = pts[(i+1)%n];
    // first derivative ~ (pp - pm)/2
    Vec3 r1 = { (pp[0]-pm[0])*0.5, (pp[1]-pm[1])*0.5, (pp[2]-pm[2])*0.5 };
    // second derivative ~ (pp - 2*p0 + pm)
    Vec3 r2 = { pp[0]-2*p0[0]+pm[0], pp[1]-2*p0[1]+pm[1], pp[2]-2*p0[2]+pm[2] };
    Vec3 cr = cross(r1, r2);
    double num = norm(cr);
    double den = std::pow(norm(r1), 3.0) + eps;
    k[i] = num / den;
  }
  return k;
}

std::pair<std::vector<Vec3>, std::vector<double>>
FourierKnot::load_knot(const std::string& path, int nsamples) {
  auto blocks = parse_fseries_multi(path);
  int idx = index_of_largest_block(blocks);
  if (idx < 0) return {{}, {}};
  std::vector<double> s(nsamples);
  const double twoPi = 6.2831853071795864769;
  for (int i=0;i<nsamples;++i) s[i] = twoPi * double(i) / double(nsamples-1);
  auto pts = center_points(evaluate(blocks[idx], s));
  auto kap = curvature(pts);
  return {pts, kap};
}




void FourierKnot::loadBlocks(const std::string& filename) {
  blocks.clear();
  std::ifstream file(filename);
  if (!file.is_open()) {
    throw std::runtime_error("Cannot open file: " + filename);
  }

  Block current;
  std::string line;
  while (std::getline(file, line)) {
    // trim
    if (line.empty()) {
      if (!current.a_x.empty()) {
        blocks.push_back(current);
        current = Block{};
      }
      continue;
    }
    if (line[0] == '%') {
      if (!current.a_x.empty()) {
        blocks.push_back(current);
        current = Block{};
      }
      continue;
    }

    std::istringstream iss(line);
    std::vector<double> parts;
    double val;
    while (iss >> val) parts.push_back(val);

    if (parts.size() == 6) {
      current.a_x.push_back(parts[0]);
      current.b_x.push_back(parts[1]);
      current.a_y.push_back(parts[2]);
      current.b_y.push_back(parts[3]);
      current.a_z.push_back(parts[4]);
      current.b_z.push_back(parts[5]);
    }
  }
  if (!current.a_x.empty()) {
    blocks.push_back(current);
  }
}

void FourierKnot::selectMaxHarmonics() {
  if (blocks.empty()) {
    throw std::runtime_error("No Fourier blocks loaded");
  }
  size_t maxSize = 0;
  size_t maxIdx = 0;
  for (size_t i = 0; i < blocks.size(); ++i) {
    if (blocks[i].a_x.size() > maxSize) {
      maxSize = blocks[i].a_x.size();
      maxIdx = i;
    }
  }
  activeBlock = blocks[maxIdx];
}

void FourierKnot::reconstruct(size_t N) {
  if (activeBlock.a_x.empty()) {
    throw std::runtime_error("No active Fourier block selected");
  }
  points.clear();
  points.reserve(N);
  double step = 2.0 * M_PI / static_cast<double>(N);
  for (size_t i = 0; i < N; ++i) {
    double s = step * static_cast<double>(i);
    points.push_back(evalPoint(activeBlock, s));
  }
}

Vec3 FourierKnot::evalPoint(const Block& blk, double s) {
  double x = 0.0, y = 0.0, z = 0.0;
  size_t N = blk.a_x.size();
  for (size_t j = 0; j < N; ++j) {
    auto n = static_cast<double>(j + 1);
    double cs = std::cos(n * s);
    double sn = std::sin(n * s);
    x += blk.a_x[j] * cs + blk.b_x[j] * sn;
    y += blk.a_y[j] * cs + blk.b_y[j] * sn;
    z += blk.a_z[j] * cs + blk.b_z[j] * sn;
  }
  return Vec3{x, y, z};
}
} // namespace vam

