//
// Created by mr on 7/28/2025.
//

#ifndef FLUID_ROTATION_H
#define FLUID_ROTATION_H



#pragma once
#include <cmath>

namespace sst {

class FluidRotation {
public:
  // Rossby number: Ro = U / (2Ωd)
  static double rossby_number(double U, double omega, double d);

  // Ekman number: Ek = ν / (Ω H²)
  static double ekman_number(double nu, double omega, double H);

  // Cylinder mass: m = ρ π R² H
  static double cylinder_mass(double rho, double R, double H);

  // Moment of inertia: I = (1/2) m R²
  static double cylinder_inertia(double mass, double R);

  // Torque: τ = I α
  static double torque(double inertia, double alpha);
};

}



#endif //FLUID_ROTATION_H