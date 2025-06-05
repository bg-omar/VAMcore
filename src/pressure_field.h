#ifndef VAMCORE_PRESSURE_FIELD_H
#define VAMCORE_PRESSURE_FIELD_H
#pragma once
#include <array>
#include <vector>

namespace vam {
        using Vec3 = std::array<double, 3>;

        class PressureField {
        public:
                static std::vector<double> compute_bernoulli_pressure(const std::vector<double>& velocity_magnitude,
                                                                        double rho = 7.0e-7,
                                                                        double p_inf = 0.0);

                static std::vector<std::vector<Vec3>> pressure_gradient(const std::vector<std::vector<double>>& pressure_field,
                                                                        double dx = 1.0);
        };

        inline std::vector<double> compute_bernoulli_pressure(const std::vector<double>& velocity_magnitude,
                                                                        double rho = 7.0e-7,
                                                                        double p_inf = 0.0) {
                return PressureField::compute_bernoulli_pressure(velocity_magnitude, rho, p_inf);
        }

        inline std::vector<std::vector<Vec3>> pressure_gradient(const std::vector<std::vector<double>>& pressure_field,
                                                                        double dx = 1.0) {
                return PressureField::pressure_gradient(pressure_field, dx);
        }
}

#endif //VAMCORE_PRESSURE_FIELD_H
