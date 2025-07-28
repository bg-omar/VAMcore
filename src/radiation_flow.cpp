//
// Created by mr on 7/28/2025.
//

#include "radiation_flow.h"

namespace vam {

double RadiationFlow::radiation_force(double I0, double Qm, double lambda1, double lambda2, double lambda_g) {
  double factor = (lambda1 / lambda_g) * (lambda2 / lambda_g);
  double denom = 1.0 - std::pow(lambda1 / lambda_g, 2);
  return (2.0 * I0 / 3e8) * Qm * factor / denom; // assuming c = 3e8 m/s
}

double RadiationFlow::dxdt(double x, double y) {
  return y;
}

double RadiationFlow::dydt(double x, double y, double mu) {
  return mu * (1 - x*x) * y - x;
}

}
