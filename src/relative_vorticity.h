//
// Created by mr on 7/18/2025.
//

#ifndef SSTCORE_RELATIVE_VORTICITY_H
#define SSTCORE_RELATIVE_VORTICITY_H

#pragma once
#include <array>

namespace sst {

	using Vec3 = std::array<double, 3>;

	class Relative_Vorticity {
	public:
		// Compute RHS of rotating frame momentum equation
		static Vec3 rotating_frame_rhs(
				const Vec3& velocity,
				const Vec3& vorticity,
				const Vec3& grad_phi,
				const Vec3& grad_p,
				const Vec3& omega,
				double rho);

		// Compute Crocco's gradient vector
		static Vec3 crocco_gradient(
				const Vec3& velocity,
				const Vec3& vorticity,
				const Vec3& grad_phi,
				const Vec3& grad_p,
				double rho);
	};

}



#endif //SSTCORE_RELATIVE_VORTICITY_H