#ifndef SWIRL_STRING_CORE_SST_INTEGRATOR_H
#define SWIRL_STRING_CORE_SST_INTEGRATOR_H

#pragma once
#include <array>
#include <vector>
#include <cstddef>

namespace sst {

using Vec3 = std::array<double, 3>;

/**
 * SST mass from closed curve: core (static) + fluid (Neumann hydrodynamic dressing).
 * Uses Rosenhead–Moore regularization on the Neumann mutual inductance integral.
 *
 * @param points  Closed polyline (points[0] and points[N-1] need not coincide; curve is closed by convention).
 * @param chi_spin Spin factor (e.g. 2 for fermion).
 * @param m_core  Output: core mass [kg].
 * @param m_fluid Output: fluid dressing mass [kg].
 */
void compute_sst_mass(const std::vector<Vec3>& points, double chi_spin,
                      double& m_core, double& m_fluid);

} // namespace sst

#endif // SWIRL_STRING_CORE_SST_INTEGRATOR_H
