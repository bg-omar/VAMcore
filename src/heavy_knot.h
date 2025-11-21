//
// Created by mr on 8/15/2025.
//

#ifndef SSTCORE_HEAVY_KNOT_H
#define SSTCORE_HEAVY_KNOT_H

#pragma once
#include <vector>
#include <array>

namespace sst {
using Vec3 = std::array<double, 3>;

struct FourierResult {
  std::vector<Vec3> positions;
  std::vector<Vec3> tangents;
};

FourierResult evaluate_fourier_series(
    const std::vector<std::array<double, 6>>& coeffs,
    const std::vector<double>& t_vals
);

double writhe_gauss_curve(
    const std::vector<Vec3>& r,
    const std::vector<Vec3>& r_t
);

int estimate_crossing_number(
    const std::vector<Vec3>& r,
    int directions = 24,
    int seed = 12345
);
}


#endif // SSTCORE_HEAVY_KNOT_H