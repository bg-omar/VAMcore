//
// Created by mr on 7/18/2025.
//

#include "potential_flow.h"


namespace vam {

	double PotentialFlow::laplacian_phi(double d2phidx2, double d2phidy2, double d2phidz2) {
		return d2phidx2 + d2phidy2 + d2phidz2;
	}

	Vec3 PotentialFlow::grad_phi(const Vec3& phi_grad) {
		return phi_grad;
	}

	double PotentialFlow::bernoulli_pressure(double velocity_squared, double V) {
		return -V + 0.5 * velocity_squared;
	}

}
