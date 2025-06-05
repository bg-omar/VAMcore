//
// Created by mr on 3/23/2025.
//

#ifndef VAMCORE_KINETIC_ENERGY_H
#define VAMCORE_KINETIC_ENERGY_H

// include/kinetic_energy.hpp
#pragma once

#include <vector>
#include <array>

namespace vam {

	using Vec3 = std::array<double, 3>;

        class KineticEnergy {
        public:
                static double compute(const std::vector<Vec3>& velocity, double rho_ae);
        };

        inline double compute_kinetic_energy(const std::vector<Vec3>& velocity, double rho_ae) {
                return KineticEnergy::compute(velocity, rho_ae);
        }

} // namespace vam

#endif //VAMCORE_KINETIC_ENERGY_H
