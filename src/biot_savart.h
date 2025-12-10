//
// Created by mr on 3/21/2025.
//

#ifndef SWIRL_STRING_CORE_BIOT_SAVART_H
#define SWIRL_STRING_CORE_BIOT_SAVART_H

#pragma once
#include <array>
#include <vector>
#include <tuple>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {
        using Vec3 = std::array<double, 3>;

        class BiotSavart {
        public:

          // Compute Biot–Savart velocity field from a closed curve (points) at given grid points
          static std::vector<Vec3> computeVelocity(
              const std::vector<Vec3>& curve,
              const std::vector<Vec3>& grid_points
          );

          // Compute vorticity from velocity field on a regular grid
          static std::vector<Vec3> computeVorticity(
              const std::vector<Vec3>& velocity,
              const std::array<int, 3>& shape,
              double spacing
          );

          // Extract cubic interior field subset
          static std::vector<Vec3> extractInterior(
              const std::vector<Vec3>& field,
              const std::array<int, 3>& shape,
              int margin
          );

          // Compute H_charge, H_mass, and a_mu from velocity/vorticity
          static std::tuple<double, double, double> computeInvariants(
              const std::vector<Vec3>& v_sub,
              const std::vector<Vec3>& w_sub,
              const std::vector<double>& r_sq
          );

          static Vec3 velocity(const Vec3& r,
              const std::vector<Vec3>& X,
              const std::vector<Vec3>& T,
              double Gamma = 1.0);
        };

        inline Vec3 biot_savart_velocity(const Vec3& r,
              const std::vector<Vec3>& X,
              const std::vector<Vec3>& T,
              double Gamma = 1.0) {
      return BiotSavart::velocity(r, X, T, Gamma);
        }
}

#endif //SWIRL_STRING_CORE_BIOT_SAVART_H