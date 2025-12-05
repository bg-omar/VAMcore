//
// Created by mr on 7/28/2025.
//

#include "vortex_ring.h"
#include <cmath>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

    double VortexRing::lamb_oseen_velocity(double gamma, double R, double nu, double t) {
      return (gamma / (2.0 * M_PI * R)) * (1.0 - std::exp(-R*R / (4.0 * nu * t)));
    }

    double VortexRing::lamb_oseen_vorticity(double gamma, double r, double nu, double t) {
      return (gamma / (4.0 * M_PI * nu * t)) * std::exp(-r*r / (4.0 * nu * t));
    }

    double VortexRing::hill_streamfunction(double A, double r, double z, double R) {
      double rsq = r*r + z*z;
      if (rsq < R*R)
        return A * r * (R*R - rsq);
      return 0.0;
    }

    double VortexRing::hill_vorticity(double A, double r, double z, double R) {
      double rsq = r*r + z*z;
      if (rsq < R*R)
        return A * (4.0 * z*z + r*r - R*R);
      return 0.0;
    }

    double VortexRing::hill_circulation(double A, double R) {
      return (2.0 * M_PI * A * std::pow(R, 3)) / 3.0;
    }

    double VortexRing::hill_velocity(double gamma, double R) {
      return gamma / (5.0 * R);
    }

}