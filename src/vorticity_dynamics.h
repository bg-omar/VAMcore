// vorticity_dynamics.h
#ifndef VAMCORE_VORTICITY_DYNAMICS_H
#define VAMCORE_VORTICITY_DYNAMICS_H

#include <array>
#include <vector>
#include <cmath>

namespace vam {
/**
 * @brief Compute vorticity ω = ∂v/∂x - ∂u/∂y for 2D fields.
 */
	class VorticityDynamics {
	public:
		/**
		 * @param u Flattened 2D array (row-major) size (nx*ny)
		 * @param v Flattened 2D array (nx*ny)
		 * @param nx Number of cells in x
		 * @param ny Number of cells in y
		 * @param dx Grid spacing in x
		 * @param dy Grid spacing in y
		 * @return std::vector<double> vorticity field of size nx*ny
		 */
		static std::vector<double> compute_vorticity2D(const std::vector<double>& u, const std::vector<double>& v, int nx, int ny, double dx, double dy);
		static double vorticity_z_2D(double dv_dx, double du_dy);
		static double local_circulation_density(double dv_dx, double du_dy);
		static double solid_body_rotation_vorticity(double omega);
		static double couette_vorticity(double alpha);
		static std::array<double, 3> crocco_relation(const std::array<double, 3>& vorticity, double rho, const std::array<double, 3>& pressure_gradient);
	};

} // namespace vam

#endif
