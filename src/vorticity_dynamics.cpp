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

} // namespace sst