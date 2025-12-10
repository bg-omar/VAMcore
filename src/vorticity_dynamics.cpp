// vorticity_dynamics.cpp
#include "vorticity_dynamics.h"
#include <cassert>

namespace sst {

		/**
	 * @param u Flattened 2D array (row-major) size (nx*ny)
	 * @param v Flattened 2D array (nx*ny)
	 * @param nx Number of cells in x
	 * @param ny Number of cells in y
	 * @param dx Grid spacing in x
	 * @param dy Grid spacing in y
	 * @return std::vector<double> vorticity field of size nx*ny
	 */
	 std::vector<double> VorticityDynamics::compute_vorticity2D(
				const std::vector<double>& u,
				const std::vector<double>& v,
				int nx, int ny,
				double dx, double dy)
		{
			assert(u.size() == v.size());
			int N = nx * ny;
			std::vector<double> omega(N, 0.0);

			for (int j = 1; j < ny-1; ++j) {
				for (int i = 1; i < nx-1; ++i) {
					int idx = i + j*nx;
					double dvdx = (v[idx+1] - v[idx-1]) / (2*dx);
					double dudy = (u[idx+nx] - u[idx-nx]) / (2*dy);
					omega[idx] = dvdx - dudy;
				}
			}

			return omega;
		}


	double VorticityDynamics::vorticity_z_2D(double dv_dx, double du_dy) {
		return dv_dx - du_dy;
	}

	double VorticityDynamics::local_circulation_density(double dv_dx, double du_dy) {
		return vorticity_z_2D(dv_dx, du_dy);
	}

	double VorticityDynamics::solid_body_rotation_vorticity(double omega) {
		return 2.0 * omega;
	}

	double VorticityDynamics::couette_vorticity(double alpha) {
		return -alpha;
	}

	std::array<double, 3> VorticityDynamics::crocco_relation(const std::array<double, 3>& vorticity, double rho, const std::array<double, 3>& pressure_gradient) {
		return {
				pressure_gradient[0] / rho,
				pressure_gradient[1] / rho,
				pressure_gradient[2] / rho
		};
	}

	// Relative vorticity methods (from Relative_Vorticity)
	Vec3 VorticityDynamics::rotating_frame_rhs(
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

	Vec3 VorticityDynamics::crocco_gradient(
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

	// Vorticity transport methods (from VorticityTransport)
	Vec3 VorticityDynamics::baroclinic_term(const Vec3& grad_rho, const Vec3& grad_p, double rho) {
		return {
				(grad_rho[1]*grad_p[2] - grad_rho[2]*grad_p[1]) / (rho*rho),
				(grad_rho[2]*grad_p[0] - grad_rho[0]*grad_p[2]) / (rho*rho),
				(grad_rho[0]*grad_p[1] - grad_rho[1]*grad_p[0]) / (rho*rho)
		};
	}

	Vec3 VorticityDynamics::compute_vorticity_rhs(const Vec3& omega, const std::array<Vec3, 3>& grad_u,
										 double div_u, const Vec3& grad_rho, const Vec3& grad_p, double rho) {
		Vec3 stretch = {
				omega[0]*grad_u[0][0] + omega[1]*grad_u[0][1] + omega[2]*grad_u[0][2],
				omega[0]*grad_u[1][0] + omega[1]*grad_u[1][1] + omega[2]*grad_u[1][2],
				omega[0]*grad_u[2][0] + omega[1]*grad_u[2][1] + omega[2]*grad_u[2][2]
		};

		Vec3 compress = {
				-div_u * omega[0],
				-div_u * omega[1],
				-div_u * omega[2]
		};

		Vec3 baroclinic = baroclinic_term(grad_rho, grad_p, rho);

		return {
				stretch[0] + compress[0] + baroclinic[0],
				stretch[1] + compress[1] + baroclinic[1],
				stretch[2] + compress[2] + baroclinic[2]
		};
	}

} // namespace sst