//
// Created by mr on 7/28/2025.
//

#ifndef VORTEX_RING_H
#define VORTEX_RING_H



#pragma once
#include <vector>
#include <array>

namespace sst {

using Vec3 = std::array<double, 3>;

class VortexRing {
public:
  // Lamb-Oseen azimuthal velocity at radius R and time t
  static double lamb_oseen_velocity(double gamma, double R, double nu, double t);

  // Lamb-Oseen vorticity
  static double lamb_oseen_vorticity(double gamma, double r, double nu, double t);

  // Hill's vortex streamfunction (ψ) and vorticity inside sphere of radius R
  static double hill_streamfunction(double A, double r, double z, double R);
  static double hill_vorticity(double A, double r, double z, double R);

  // Circulation of Hill's vortex
  static double hill_circulation(double A, double R);

  // Propagation speed
  static double hill_velocity(double gamma, double R);
};

}



#endif //VORTEX_RING_H