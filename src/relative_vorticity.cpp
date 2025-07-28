//
// Created by mr on 7/18/2025.
//

#include "relative_vorticity.h"


namespace vam {

	Vec3 Relative_Vorticity::rotating_frame_rhs(
			const Vec3& velocity,
			const Vec3& vorticity,
			const Vec3& grad_phi,
			const Vec3& grad_p,
			const Vec3& omega,
			double rho)
	{
		Vec3 omega_cross_u = {
				omega[1]*velocity[2] - omega[2]*velocity[1],
				omega[2]*velocity[0] - omega[0]*velocity[2],
				omega[0]*velocity[1] - omega[1]*velocity[0]
		};

		Vec3 rhs;
		for (int i = 0; i < 3; ++i)
			rhs[i] = -2.0 * omega_cross_u[i] - grad_phi[i] - grad_p[i] / rho;

		return rhs;
	}

	Vec3 Relative_Vorticity::crocco_gradient(
			const Vec3& velocity,
			const Vec3& vorticity,
			const Vec3& grad_phi,
			const Vec3& grad_p,
			double rho)
	{
		Vec3 omega_cross_u = {
				vorticity[1]*velocity[2] - vorticity[2]*velocity[1],
				vorticity[2]*velocity[0] - vorticity[0]*velocity[2],
				vorticity[0]*velocity[1] - vorticity[1]*velocity[0]
		};

		double kinetic_energy = 0.5 * (
				velocity[0]*velocity[0] +
				velocity[1]*velocity[1] +
				velocity[2]*velocity[2]);

		Vec3 grad_H;
		for (int i = 0; i < 3; ++i)
			grad_H[i] = rho * (omega_cross_u[i]) + grad_phi[i] + grad_p[i] / rho;

		return grad_H;
	}

}
