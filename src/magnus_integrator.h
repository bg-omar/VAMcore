#pragma once
#include <array>
#include <cmath>

// Standardizing vector input for native PyBind11 <-> Python List conversion
typedef std::array<double, 3> Vec3D;

class MagnusBernoulliIntegrator {
private:
  // Canonical SST Continuum Parameters
  double rho_f;    // Effective fluid density (kg/m^3)
  double v_swirl;  // Characteristic swirl speed (m/s)
  double r_c;      // Classical core radius (m)
  double Gamma;    // Quantum of circulation (m^2/s)

public:
  MagnusBernoulliIntegrator(double rho_f_in, double v_swirl_in, double r_c_in, double Gamma_in);

  /**
   * VAM-10: Computes the transverse Magnus-Curvature force on a vortex segment.
   * F_perp = rho_f * Gamma * [ T x (v_knot - v_bg) + (1/R)*N ]
   */
  Vec3D compute_magnus_force(const Vec3D& tangent,
                             const Vec3D& normal,
                             double curvature_radius,
                             const Vec3D& v_knot,
                             const Vec3D& v_bg) const;

  /**
   * VAM-10 / Hydrogen Paper: Computes the continuous radial Swirl-Coulomb acceleration.
   * a_r = - (v_swirl^2 / r) * exp(-2r / r_c) * r_hat
   */
  Vec3D compute_swirl_coulomb_accel(const Vec3D& eval_pos,
                                    const Vec3D& source_pos) const;
};