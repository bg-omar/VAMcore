//
// Created by mr on 8/21/2025.
//

#ifndef SWIRL_STRING_CORE_HYPERBOLIC_VOLUME_H
#define SWIRL_STRING_CORE_HYPERBOLIC_VOLUME_H

// ./src/hyperbolic_volume.h
#pragma once
#include <vector>
#include <array>

namespace sst {

using Crossing = std::array<int,4>;
using PD = std::vector<Crossing>;

/**
 * Compute hyperbolic volume from PD.
 * Note: Provide a concrete implementation or enable binding conditionally.
 */
double hyperbolic_volume_from_pd(const PD& pd);

} // namespace sst


#endif // SWIRL_STRING_CORE_HYPERBOLIC_VOLUME_H