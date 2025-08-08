#include "biot_savart.h"
#include <cmath>
#include <numeric>

namespace vam {

    std::vector<Vec3> BiotSavart::computeVelocity(
        const std::vector<Vec3>& curve,
        const std::vector<Vec3>& grid_points
    ) {
      std::vector<Vec3> vel(grid_points.size(), {0.0, 0.0, 0.0});
      const size_t N = curve.size();
      const double factor = 1.0 / (4.0 * M_PI);

      for (size_t i = 0; i < N; ++i) {
        const Vec3& r0 = curve[i];
        const Vec3& r1 = curve[(i + 1) % N];
        Vec3 dl = { r1[0] - r0[0], r1[1] - r0[1], r1[2] - r0[2] };
        Vec3 mid = { 0.5*(r0[0] + r1[0]), 0.5*(r0[1] + r1[1]), 0.5*(r0[2] + r1[2]) };

        for (size_t g = 0; g < grid_points.size(); ++g) {
          Vec3 R = { grid_points[g][0] - mid[0],
                    grid_points[g][1] - mid[1],
                    grid_points[g][2] - mid[2] };

          double normR = std::pow(R[0]*R[0] + R[1]*R[1] + R[2]*R[2], 1.5) + 1e-12;
          Vec3 cross = {
              dl[1]*R[2] - dl[2]*R[1],
              dl[2]*R[0] - dl[0]*R[2],
              dl[0]*R[1] - dl[1]*R[0]
          };
          vel[g][0] += cross[0] / normR;
          vel[g][1] += cross[1] / normR;
          vel[g][2] += cross[2] / normR;
        }
      }

      for (auto& v : vel) {
        v[0] *= factor; v[1] *= factor; v[2] *= factor;
      }
      return vel;
    }

    std::vector<Vec3> BiotSavart::computeVorticity(
        const std::vector<Vec3>& velocity,
        const std::array<int, 3>& shape,
        double spacing
    ) {
      int nx = shape[0], ny = shape[1], nz = shape[2];
      auto idx = [&](int i, int j, int k) {
        return ((i + nx) % nx) * ny * nz + ((j + ny) % ny) * nz + ((k + nz) % nz);
      };

      std::vector<Vec3> vort(velocity.size(), {0,0,0});

      for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
          for (int k = 0; k < nz; ++k) {
            const Vec3& vx_ip = velocity[idx(i+1,j,k)];
            const Vec3& vx_im = velocity[idx(i-1,j,k)];
            const Vec3& vy_ip = velocity[idx(i,j+1,k)];
            const Vec3& vy_im = velocity[idx(i,j-1,k)];
            const Vec3& vz_ip = velocity[idx(i,j,k+1)];
            const Vec3& vz_im = velocity[idx(i,j,k-1)];

            double curl_x = (vz_ip[1] - vz_im[1])/(2*spacing) - (vy_ip[2] - vy_im[2])/(2*spacing);
            double curl_y = (vx_ip[2] - vx_im[2])/(2*spacing) - (vz_ip[0] - vz_im[0])/(2*spacing);
            double curl_z = (vy_ip[0] - vy_im[0])/(2*spacing) - (vx_ip[1] - vx_im[1])/(2*spacing);

            vort[idx(i,j,k)] = {curl_x, curl_y, curl_z};
          }
        }
      }
      return vort;
    }

    std::vector<Vec3> BiotSavart::extractInterior(
        const std::vector<Vec3>& field,
        const std::array<int, 3>& shape,
        int margin
    ) {
      int nx = shape[0], ny = shape[1], nz = shape[2];
      std::vector<Vec3> sub;
      for (int i = margin; i < nx - margin; ++i) {
        for (int j = margin; j < ny - margin; ++j) {
          for (int k = margin; k < nz - margin; ++k) {
            sub.push_back(field[i*ny*nz + j*nz + k]);
          }
        }
      }
      return sub;
    }

    std::tuple<double,double,double> BiotSavart::computeInvariants(
        const std::vector<Vec3>& v_sub,
        const std::vector<Vec3>& w_sub,
        const std::vector<double>& r_sq
    ) {
      double Hc = 0.0;
      for (size_t i = 0; i < v_sub.size(); ++i) {
        Hc += v_sub[i][0]*w_sub[i][0] + v_sub[i][1]*w_sub[i][1] + v_sub[i][2]*w_sub[i][2];
      }

      double Hm = 0.0;
      for (size_t i = 0; i < w_sub.size(); ++i) {
        double normw = std::sqrt(w_sub[i][0]*w_sub[i][0] + w_sub[i][1]*w_sub[i][1] + w_sub[i][2]*w_sub[i][2]);
        Hm += normw*normw * r_sq[i];
      }

      double amu = 0.5 * (Hc/Hm - 1.0);
      return {Hc, Hm, amu};
    }


    Vec3 BiotSavart::velocity(const Vec3& r,
                              const std::vector<Vec3>& X,
                              const std::vector<Vec3>& T,
                              double Gamma)
    {
        Vec3 v{0.0, 0.0, 0.0};
        constexpr double coeff = 1.0 / (4.0 * M_PI);

        for (size_t i = 0; i < X.size(); ++i) {
                Vec3 dr{
                                r[0] - X[i][0],
                                r[1] - X[i][1],
                                r[2] - X[i][2]
                };

                double norm_dr = std::sqrt(dr[0]*dr[0] + dr[1]*dr[1] + dr[2]*dr[2]);
                if (norm_dr > 1e-6) {
                        Vec3 cross{
                                        T[i][1] * dr[2] - T[i][2] * dr[1],
                                        T[i][2] * dr[0] - T[i][0] * dr[2],
                                        T[i][0] * dr[1] - T[i][1] * dr[0]
                        };

                        double scale = Gamma / (norm_dr * norm_dr * norm_dr);
                        v[0] += coeff * cross[0] * scale;
                        v[1] += coeff * cross[1] * scale;
                        v[2] += coeff * cross[2] * scale;
                }
        }

        return v;
    }

}
