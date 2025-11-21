//
// Created by mr on 7/18/2025.
//

#ifndef SSTCORE_POTENTIAL_FLOW_H
#define SSTCORE_POTENTIAL_FLOW_H


#pragma once
#include <array>

namespace sst {

	using Vec3 = std::array<double, 3>;

	class PotentialFlow {
	public:
		static double laplacian_phi(double d2phidx2, double d2phidy2, double d2phidz2);
		static Vec3 grad_phi(const Vec3& phi_grad);
		static double bernoulli_pressure(double velocity_squared, double V);
	};

}


#endif //SSTCORE_POTENTIAL_FLOW_H