#include "kinetic_energy.h"
#include <cmath>

namespace vam {

        double KineticEnergy::compute(const std::vector<Vec3>& velocity, double rho_ae) {
                double sum = 0.0;
                for (const auto& v : velocity) {
                        sum += v[0]*v[0] + v[1]*v[1] + v[2]*v[2];
                }
                return 0.5 * rho_ae * sum;
        }

} // namespace vam
