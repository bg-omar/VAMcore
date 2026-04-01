// Kernels matching trefoil_closure/sst_core.cpp (discrete curve, shape (N,3) row-major).
#pragma once

#include <cstddef>

namespace sst {

// r points to n*3 doubles, row-major (vertex i at r[i*3 + c]).
double trefoil_neumann_self_energy(const double* r, std::size_t n, double rc);
double trefoil_core_repulsion(const double* r, std::size_t n, double rc);
double trefoil_polyline_length(const double* r, std::size_t n);
double trefoil_writhe_reg(const double* r, std::size_t n, double rc);
double trefoil_curvature_penalty_menger(const double* r, std::size_t n);

}  // namespace sst
