//
// Created by mr on 8/21/2025.
//

#ifndef SSTCORE_KNOT_PD_H
#define SSTCORE_KNOT_PD_H

// ./src/knot_pd.h
#pragma once
#include <vector>
#include <array>
#include <random>
#include <stdexcept>

namespace sst {

using Vec3 = std::array<double,3>;
using Vec2 = std::array<double,2>;
using Crossing = std::array<int,4>;                 // (a,b,c,d)
using PD = std::vector<Crossing>;

PD pd_from_curve(const std::vector<Vec3>& P3,
                 int tries = 40,
                 unsigned int seed = 12345,
                 double min_angle_deg = 1.0,
                 double depth_tol = 1e-6);

} // namespace sst


#endif // SSTCORE_KNOT_PD_H