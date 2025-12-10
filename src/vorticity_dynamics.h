// vorticity_dynamics.h
#ifndef SWIRL_STRING_CORE_VORTICITY_DYNAMICS_H
#define SWIRL_STRING_CORE_VORTICITY_DYNAMICS_H

#include <array>
#include <vector>
#include <cmath>

namespace sst {
	using Vec3 = std::array<double, 3>;

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

		// Relative vorticity methods (from Relative_Vorticity)
		static Vec3 rotating_frame_rhs(
				const Vec3& velocity,
				const Vec3& vorticity,
				const Vec3& grad_phi,
				const Vec3& grad_p,
				const Vec3& omega,
				double rho);
		static Vec3 crocco_gradient(
				const Vec3& velocity,
				const Vec3& vorticity,
				const Vec3& grad_phi,
				const Vec3& grad_p,
				double rho);

		// Vorticity transport methods (from VorticityTransport)
		static Vec3 baroclinic_term(const Vec3& grad_rho, const Vec3& grad_p, double rho);
		static Vec3 compute_vorticity_rhs(const Vec3& omega, const std::array<Vec3, 3>& grad_u,
										 double div_u, const Vec3& grad_rho, const Vec3& grad_p, double rho);
	};

} // namespace sst

#endif