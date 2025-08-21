//
// Created by mr on 8/15/2025.
//

#include "heavy_knot.h"

#include <cmath>
#include <random>
#include <numeric>

namespace vam {

FourierResult evaluate_fourier_series(
    const std::vector<std::array<double, 6>>& coeffs,
    const std::vector<double>& t_vals
) {
  size_t N = coeffs.size();
  size_t T = t_vals.size();
  FourierResult result;
  result.positions.resize(T);
  result.tangents.resize(T);

  for (size_t ti = 0; ti < T; ++ti) {
    double t = t_vals[ti];
    Vec3 r = {0, 0, 0}, r_t = {0, 0, 0};

    for (size_t n = 0; n < N; ++n) {
      double nt = n * t;
      double cos_nt = std::cos(nt), sin_nt = std::sin(nt);
      auto& c = coeffs[n];

      r[0] += c[0]*cos_nt + c[1]*sin_nt;
      r[1] += c[2]*cos_nt + c[3]*sin_nt;
      r[2] += c[4]*cos_nt + c[5]*sin_nt;

      if (n > 0) {
        r_t[0] += -n * c[0]*sin_nt + n * c[1]*cos_nt;
        r_t[1] += -n * c[2]*sin_nt + n * c[3]*cos_nt;
        r_t[2] += -n * c[4]*sin_nt + n * c[5]*cos_nt;
      }
    }

    result.positions[ti] = r;
    result.tangents[ti] = r_t;
  }
  return result;
}

double writhe_gauss_curve(
    const std::vector<Vec3>& r,
    const std::vector<Vec3>& r_t
) {
  const double pi = 3.141592653589793;
  size_t M = r.size();
  double sum = 0.0;
  double dt = 2 * pi / M;

  for (size_t i = 0; i < M; ++i) {
    for (size_t j = 0; j < M; ++j) {
      if (i == j) continue;
      Vec3 dR = {
          r[i][0] - r[j][0],
          r[i][1] - r[j][1],
          r[i][2] - r[j][2]
      };
      double dist = std::sqrt(dR[0]*dR[0] + dR[1]*dR[1] + dR[2]*dR[2]);
      if (dist < 1e-6) continue;

      Vec3 Ti = r_t[i];
      Vec3 Tj = r_t[j];
      Vec3 cross = {
          Ti[1]*Tj[2] - Ti[2]*Tj[1],
          Ti[2]*Tj[0] - Ti[0]*Tj[2],
          Ti[0]*Tj[1] - Ti[1]*Tj[0]
      };
      double dot = cross[0]*dR[0] + cross[1]*dR[1] + cross[2]*dR[2];
      sum += dot / (dist*dist*dist);
    }
  }
  return (dt*dt * sum) / (4 * pi);
}

int estimate_crossing_number(
    const std::vector<Vec3>& r,
    int directions,
    int seed
) {
  size_t M = r.size();
  std::mt19937 gen(seed);
  std::normal_distribution<> d(0.0, 1.0);

  int min_cross = M*M;

  for (int d_iter = 0; d_iter < directions; ++d_iter) {
    Vec3 w = {d(gen), d(gen), d(gen)};
    double norm_w = std::sqrt(w[0]*w[0] + w[1]*w[1] + w[2]*w[2]);
    for (auto& x : w) x /= norm_w + 1e-12;

    Vec3 tmp = {1,0,0};
    if (std::abs(w[0]) > 0.9) tmp = {0,1,0};

    Vec3 u = {
        w[1]*tmp[2] - w[2]*tmp[1],
        w[2]*tmp[0] - w[0]*tmp[2],
        w[0]*tmp[1] - w[1]*tmp[0]
    };
    double norm_u = std::sqrt(u[0]*u[0] + u[1]*u[1] + u[2]*u[2]);
    for (auto& x : u) x /= norm_u + 1e-12;

    Vec3 v = {
        w[1]*u[2] - w[2]*u[1],
        w[2]*u[0] - w[0]*u[2],
        w[0]*u[1] - w[1]*u[0]
    };

    std::vector<std::array<double,2>> proj(M), proj2(M);
    for (size_t i = 0; i < M; ++i) {
      proj[i] = {r[i][0]*u[0] + r[i][1]*u[1] + r[i][2]*u[2],
                 r[i][0]*v[0] + r[i][1]*v[1] + r[i][2]*v[2]};
    }

    int count = 0;
    for (size_t i = 0; i < M; ++i) {
      auto p1 = proj[i], p2 = proj[(i+1)%M];
      for (size_t j = i+2; j < M; ++j) {
        if (j == (i-1+M)%M) continue;
        auto q1 = proj[j], q2 = proj[(j+1)%M];

        auto orient = [](const auto& a, const auto& b, const auto& c) {
          return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]);
        };
        double o1 = orient(p1,p2,q1);
        double o2 = orient(p1,p2,q2);
        double o3 = orient(q1,q2,p1);
        double o4 = orient(q1,q2,p2);
        if ((o1*o2 < 0) && (o3*o4 < 0)) ++count;
      }
    }

    if (count < min_cross) min_cross = count;
  }

  return min_cross;
}

}  // namespace vam
