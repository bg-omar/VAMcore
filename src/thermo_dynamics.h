#ifndef SWIRL_STRING_CORE_THERMO_DYNAMICS_H
#define SWIRL_STRING_CORE_THERMO_DYNAMICS_H

#include <vector>
#include <cmath>

namespace sst {

	class ThermoDynamics {
	public:
		static double potential_temperature(double T, double p0, double p, double R, double cp);
		static double entropy_from_theta(double cp, double theta, double dtheta);
		static double entropy_from_pv(double N, double R, double p, double V, double gamma);
		static double enthalpy(double internal_energy, double p, double V);
	};

}

#endif