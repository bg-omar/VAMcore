//
// Created by mr on 3/21/2025.
//

#ifndef VAMCORE_BIOT_SAVART_H
#define VAMCORE_BIOT_SAVART_H

#pragma once
#include <array>
#include <vector>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace vam {
        using Vec3 = std::array<double, 3>;

        class BiotSavart {
        public:
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

#endif //VAMCORE_BIOT_SAVART_H
