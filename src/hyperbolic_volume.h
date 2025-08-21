//
// Created by mr on 8/21/2025.
//

#ifndef VAMCORE_HYPERBOLIC_VOLUME_H
#define VAMCORE_HYPERBOLIC_VOLUME_H

// ./src/hyperbolic_volume.h
#pragma once
#include <vector>
#include <array>

namespace vam {

using Crossing = std::array<int,4>;
using PD = std::vector<Crossing>;

/**
 * Compute hyperbolic volume from PD.
 * Note: Provide a concrete implementation or enable binding conditionally.
 */
double hyperbolic_volume_from_pd(const PD& pd);

} // namespace vam


#endif // VAMCORE_HYPERBOLIC_VOLUME_H
