//
// Created by mr on 7/28/2025.
//

#ifndef RADIATION_FLOW_H
#define RADIATION_FLOW_H



#pragma once
#include <cmath>

namespace vam {

class RadiationFlow {
public:
  // Radiation pressure force
  static double radiation_force(double I0, double Qm, double lambda1, double lambda2, double lambda_g);

  // Van der Pol oscillator derivatives
  static double dxdt(double x, double y);
  static double dydt(double x, double y, double mu);
};

}



#endif //RADIATION_FLOW_H
