//
// Created by mr on 7/28/2025.
//

#include "fluid_rotation.h"
#include "knot_dynamics.h"
#include <cmath>

namespace sst {

double FluidRotation::rossby_number(double U, double omega, double d) {
  return U / (2.0 * omega * d);
}

double FluidRotation::ekman_number(double nu, double omega, double H) {
  return nu / (omega * H * H);
}

double FluidRotation::cylinder_mass(double rho, double R, double H) {
  return rho * M_PI * R * R * H;
}

double FluidRotation::cylinder_inertia(double mass, double R) {
  return 0.5 * mass * R * R;
}

double FluidRotation::torque(double inertia, double alpha) {
  return inertia * alpha;
}

}