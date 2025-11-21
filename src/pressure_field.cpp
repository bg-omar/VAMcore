#include "pressure_field.h"
#include <cmath>

namespace sst {

        std::vector<double> PressureField::compute_bernoulli_pressure(const std::vector<double>& velocity_magnitude,
                                                                        double rho,
                                                                        double p_inf) {
                std::vector<double> pressure;
                pressure.reserve(velocity_magnitude.size());
                for (double v : velocity_magnitude) {
                        pressure.push_back(p_inf - 0.5 * rho * v * v);
                }
                return pressure;
        }

        std::vector<std::vector<Vec3>> PressureField::pressure_gradient(const std::vector<std::vector<double>>& pressure_field,
                                                                        double dx) {
                size_t nx = pressure_field.size();
                size_t ny = pressure_field[0].size();
                std::vector<std::vector<Vec3>> grad(nx, std::vector<Vec3>(ny));

                for (size_t i = 1; i < nx - 1; ++i) {
                        for (size_t j = 1; j < ny - 1; ++j) {
                                double dpdx = (pressure_field[i + 1][j] - pressure_field[i - 1][j]) / (2.0 * dx);
                                double dpdy = (pressure_field[i][j + 1] - pressure_field[i][j - 1]) / (2.0 * dx);
                                grad[i][j] = {-dpdx, -dpdy, 0.0};
                        }
                }
                return grad;
        }

} // namespace sst