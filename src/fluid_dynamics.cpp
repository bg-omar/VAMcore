//
// Created by mr on 3/22/2025.
//

#include "fluid_dynamics.h"
#include <cmath>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

        std::vector<double> FluidDynamics::compute_pressure_field(
                        const std::vector<double>& velocity_magnitude,
                        double rho_ae,
                        double P_infinity) {
		size_t n = velocity_magnitude.size();
		std::vector<double> pressure(n);
		for (size_t i = 0; i < n; ++i) {
			pressure[i] = P_infinity - 0.5 * rho_ae * velocity_magnitude[i] * velocity_magnitude[i];
		}
		return pressure;
	}

        std::vector<double> FluidDynamics::compute_velocity_magnitude(const std::vector<Vec3>& velocity) {
		std::vector<double> mag;
		mag.reserve(velocity.size());
		for (const auto& v : velocity) {
			mag.push_back(std::sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]));
		}
		return mag;
	}

        void FluidDynamics::evolve_positions_euler(
                        std::vector<Vec3>& positions,
                        const std::vector<Vec3>& velocity,
                        double dt) {
		size_t n = positions.size();
		for (size_t i = 0; i < n; ++i) {
			positions[i][0] += dt * velocity[i][0];
			positions[i][1] += dt * velocity[i][1];
			positions[i][2] += dt * velocity[i][2];
		}
        }

        bool FluidDynamics::is_incompressible(const Vec3& dudx, const Vec3& dvdy, const Vec3& dwdz) {
                return std::abs(dudx[0] + dvdy[1] + dwdz[2]) < 1e-8;
        }

        Vec3 FluidDynamics::compute_vorticity(const std::array<std::array<double, 3>, 3>& grad) {
                return {
                                grad[2][1] - grad[1][2], // wx
                                grad[0][2] - grad[2][0], // wy
                                grad[1][0] - grad[0][1]  // wz
                };
        }

        double FluidDynamics::swirl_clock_rate(double dv_dx, double du_dy) {
                return 0.5 * (dv_dx - du_dy);
        }

        double FluidDynamics::vorticity_from_curvature(double V, double R) {
                return V / R;
        }

        double FluidDynamics::vortex_pressure_drop(double rho, double c) {
                return 0.5 * rho * c * c;
        }

        double FluidDynamics::vortex_transverse_pressure_diff(double rho, double c) {
                return 0.25 * rho * c * c;
        }

        double FluidDynamics::swirl_energy(double rho, double omega) {
                return 0.5 * rho * omega * omega;
        }

        bool FluidDynamics::kairos_energy_trigger(double rho, double omega, double Ce) {
                return swirl_energy(rho, omega) > 0.5 * rho * Ce * Ce;
        }

        double FluidDynamics::compute_helicity(const std::vector<Vec3>& velocity, const std::vector<Vec3>& vorticity, double dV) {
                double H = 0.0;
                for (size_t i = 0; i < velocity.size(); ++i) {
                        H += velocity[i][0] * vorticity[i][0] +
                                 velocity[i][1] * vorticity[i][1] +
                                 velocity[i][2] * vorticity[i][2];
                }
                return H * dV;
        }

        double FluidDynamics::potential_vorticity(double fa, double zeta_r, double h) {
                return (fa + zeta_r) / h;
        }

		double FluidDynamics::circulation_surface_integral(
				const std::vector<Vec3> &omega_field,
				const std::vector<Vec3> &dA_field) {
			double Gamma = 0.0;
			size_t n = omega_field.size();
			for (size_t i = 0; i < n; ++i) {
				Gamma += omega_field[i][0] * dA_field[i][0] +
						 omega_field[i][1] * dA_field[i][1] +
						 omega_field[i][2] * dA_field[i][2];
			}
			return Gamma;
		}

		double FluidDynamics::enstrophy(
				const std::vector<double> &omega_squared,
				const std::vector<double> &ds_area) {
			double E = 0.0;
			size_t n = omega_squared.size();
			for (size_t i = 0; i < n; ++i) {
				E += omega_squared[i] * ds_area[i];
			}
			return E;
		}

		// Pressure field methods (from PressureField)
		std::vector<double> FluidDynamics::compute_bernoulli_pressure(const std::vector<double>& velocity_magnitude,
																	   double rho,
																	   double p_inf) {
			std::vector<double> pressure;
			pressure.reserve(velocity_magnitude.size());
			for (double v : velocity_magnitude) {
				pressure.push_back(p_inf - 0.5 * rho * v * v);
			}
			return pressure;
		}

	std::vector<std::vector<Vec3>> FluidDynamics::pressure_gradient(const std::vector<std::vector<double>>& pressure_field,
																	  double dx,
																	  double dy) {
		// Check for empty input
		if (pressure_field.empty()) {
			return std::vector<std::vector<Vec3>>();
		}
		if (pressure_field[0].empty()) {
			return std::vector<std::vector<Vec3>>(pressure_field.size(), std::vector<Vec3>());
		}

		size_t nx = pressure_field.size();
		size_t ny = pressure_field[0].size();
		std::vector<std::vector<Vec3>> grad(nx, std::vector<Vec3>(ny, {0.0, 0.0, 0.0}));

		// Compute interior gradients using central differences
		for (size_t i = 1; i < nx - 1; ++i) {
			for (size_t j = 1; j < ny - 1; ++j) {
				double dpdx = (pressure_field[i + 1][j] - pressure_field[i - 1][j]) / (2.0 * dx);
				double dpdy = (pressure_field[i][j + 1] - pressure_field[i][j - 1]) / (2.0 * dy);
				grad[i][j] = {-dpdx, -dpdy, 0.0};
			}
		}

		// Handle border cells with one-sided differences for better accuracy
		// Left and right borders (i = 0 and i = nx-1)
		if (nx > 1) {
			for (size_t j = 1; j < ny - 1; ++j) {
				// Left border: forward difference
				double dpdx_left = (pressure_field[1][j] - pressure_field[0][j]) / dx;
				double dpdy_left = (pressure_field[0][j + 1] - pressure_field[0][j - 1]) / (2.0 * dy);
				grad[0][j] = {-dpdx_left, -dpdy_left, 0.0};

				// Right border: backward difference
				double dpdx_right = (pressure_field[nx - 1][j] - pressure_field[nx - 2][j]) / dx;
				double dpdy_right = (pressure_field[nx - 1][j + 1] - pressure_field[nx - 1][j - 1]) / (2.0 * dy);
				grad[nx - 1][j] = {-dpdx_right, -dpdy_right, 0.0};
			}
		}

		// Top and bottom borders (j = 0 and j = ny-1)
		if (ny > 1) {
			for (size_t i = 1; i < nx - 1; ++i) {
				// Bottom border: forward difference
				double dpdx_bottom = (pressure_field[i + 1][0] - pressure_field[i - 1][0]) / (2.0 * dx);
				double dpdy_bottom = (pressure_field[i][1] - pressure_field[i][0]) / dy;
				grad[i][0] = {-dpdx_bottom, -dpdy_bottom, 0.0};

				// Top border: backward difference
				double dpdx_top = (pressure_field[i + 1][ny - 1] - pressure_field[i - 1][ny - 1]) / (2.0 * dx);
				double dpdy_top = (pressure_field[i][ny - 1] - pressure_field[i][ny - 2]) / dy;
				grad[i][ny - 1] = {-dpdx_top, -dpdy_top, 0.0};
			}
		}

		// Handle corner cells
		if (nx > 1 && ny > 1) {
			// Bottom-left corner (0, 0)
			double dpdx_bl = (pressure_field[1][0] - pressure_field[0][0]) / dx;
			double dpdy_bl = (pressure_field[0][1] - pressure_field[0][0]) / dy;
			grad[0][0] = {-dpdx_bl, -dpdy_bl, 0.0};

			// Bottom-right corner (nx-1, 0)
			double dpdx_br = (pressure_field[nx - 1][0] - pressure_field[nx - 2][0]) / dx;
			double dpdy_br = (pressure_field[nx - 1][1] - pressure_field[nx - 1][0]) / dy;
			grad[nx - 1][0] = {-dpdx_br, -dpdy_br, 0.0};

			// Top-left corner (0, ny-1)
			double dpdx_tl = (pressure_field[1][ny - 1] - pressure_field[0][ny - 1]) / dx;
			double dpdy_tl = (pressure_field[0][ny - 1] - pressure_field[0][ny - 2]) / dy;
			grad[0][ny - 1] = {-dpdx_tl, -dpdy_tl, 0.0};

			// Top-right corner (nx-1, ny-1)
			double dpdx_tr = (pressure_field[nx - 1][ny - 1] - pressure_field[nx - 2][ny - 1]) / dx;
			double dpdy_tr = (pressure_field[nx - 1][ny - 1] - pressure_field[nx - 1][ny - 2]) / dy;
			grad[nx - 1][ny - 1] = {-dpdx_tr, -dpdy_tr, 0.0};
		}

		return grad;
	}

		// Potential flow methods (from PotentialFlow)
		double FluidDynamics::laplacian_phi(double d2phidx2, double d2phidy2, double d2phidz2) {
			return d2phidx2 + d2phidy2 + d2phidz2;
		}

		Vec3 FluidDynamics::grad_phi(const Vec3& phi_grad) {
			return phi_grad;
		}

		double FluidDynamics::bernoulli_pressure_potential(double velocity_squared, double V) {
			return -V + 0.5 * velocity_squared;
		}

		// Kinetic energy methods (from KineticEnergy)
		double FluidDynamics::compute_kinetic_energy(const std::vector<Vec3>& velocity, double rho_ae) {
			double sum = 0.0;
			for (const auto& v : velocity) {
				sum += v[0]*v[0] + v[1]*v[1] + v[2]*v[2];
			}
			return 0.5 * rho_ae * sum;
		}

		// Fluid rotation methods (from FluidRotation)
		double FluidDynamics::rossby_number(double U, double omega, double d) {
			return U / (2.0 * omega * d);
		}

		double FluidDynamics::ekman_number(double nu, double omega, double H) {
			return nu / (omega * H * H);
		}

		double FluidDynamics::cylinder_mass(double rho, double R, double H) {
			return rho * M_PI * R * R * H;
		}

		double FluidDynamics::cylinder_inertia(double mass, double R) {
			return 0.5 * mass * R * R;
		}

		double FluidDynamics::torque(double inertia, double alpha) {
			return inertia * alpha;
		}
}