#include "thermo_dynamics.h"
#include <cmath>

namespace sst {

	double ThermoDynamics::potential_temperature(double T, double p0, double p, double R, double cp) {
		double k = R / cp;
		return T * std::pow(p0 / p, k);
	}

	double ThermoDynamics::entropy_from_theta(double cp, double theta, double dtheta) {
		return cp * dtheta / theta;
	}

	double ThermoDynamics::entropy_from_pv(double N, double R, double p, double V, double gamma) {
		return (N * R / (gamma - 1)) * (std::log(p) + std::log(V));
	}

	double ThermoDynamics::enthalpy(double internal_energy, double p, double V) {
		return internal_energy + p * V;
	}

}