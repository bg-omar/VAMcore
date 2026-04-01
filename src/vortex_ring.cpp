//
// Created by mr on 7/28/2025.
//

#include "vortex_ring.h"
#include <cmath>
#include <stdexcept>
#include <iostream>
#include <limits>
#include <algorithm>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif


namespace sst {

    double VortexRing::lamb_oseen_velocity(double gamma, double R, double nu, double t) {
      return (gamma / (2.0 * M_PI * R)) * (1.0 - std::exp(-R*R / (4.0 * nu * t)));
    }

    double VortexRing::lamb_oseen_vorticity(double gamma, double r, double nu, double t) {
      return (gamma / (4.0 * M_PI * nu * t)) * std::exp(-r*r / (4.0 * nu * t));
    }

    double VortexRing::hill_streamfunction(double A, double r, double z, double R) {
      double rsq = r*r + z*z;
      if (rsq < R*R)
        return A * r * (R*R - rsq);
      return 0.0;
    }

    double VortexRing::hill_vorticity(double A, double r, double z, double R) {
      double rsq = r*r + z*z;
      if (rsq < R*R)
        return A * (4.0 * z*z + r*r - R*R);
      return 0.0;
    }

    double VortexRing::hill_circulation(double A, double R) {
      return (2.0 * M_PI * A * std::pow(R, 3)) / 3.0;
    }

    double VortexRing::hill_velocity(double gamma, double R) {
      return gamma / (5.0 * R);
    }

    // ========================================================================
    // Golden NLS Closure Implementation
    // ========================================================================

    GoldenNLSClosure::GoldenNLSClosure(DensityRegime regime) : current_regime(regime) {}

    void GoldenNLSClosure::set_regime(DensityRegime regime) {
        current_regime = regime;
    }

    double GoldenNLSClosure::get_active_density() const {
        switch (current_regime) {
            case DensityRegime::EFFECTIVE_FLUID:
                return rho_f;
            case DensityRegime::CORE_DOMINATED:
                return rho_core;
            default:
                throw std::runtime_error("Unknown density regime selected.");
        }
    }

    double GoldenNLSClosure::calculate_loop_energy(double R) const {
        double rho = get_active_density();
        double log_term = std::log((8.0 * R) / r_c);

        return 0.5 * rho * (Gamma_0 * Gamma_0) * R * (log_term - PHI);
    }

    double GoldenNLSClosure::calculate_loop_mass(double R) const {
            double E = calculate_loop_energy(R);
            return E / (c * c);
    }

    double GoldenNLSClosure::calculate_screened_mass(double bare_mass, int double_k) const {
            // Applies the DSI scaling factor: M_eff = M_bare * (phi)^(-2k)
            return bare_mass * std::pow(PHI, -double_k);
    }



    double GoldenNLSClosure::infer_geometric_ratio(double target_mass, double tolerance, int max_iter) const {
        if (current_regime != DensityRegime::CORE_DOMINATED) {
            std::cerr << "Warning: Inferring fundamental mass geometric ratio outside of CORE_DOMINATED regime.\n";
        }

        double rho = get_active_density();
        double K_core = (rho * (Gamma_0 * Gamma_0)) / (2.0 * (c * c));
        double target_C = target_mass / (K_core * r_c);

        double x = 1.0; // Initial guess (R_e approx r_c)

        for (int i = 0; i < max_iter; ++i) {
            double f_x = x * (std::log(8.0 * x) - PHI) - target_C;
            double f_prime_x = std::log(8.0 * x) + 1.0 - PHI;

            double dx = f_x / f_prime_x;
            x -= dx;

            if (std::abs(dx) < tolerance) {
                return x;
            }
        }

        throw std::runtime_error("Newton-Raphson failed to converge for geometric ratio.");
    }

    double GoldenNLSClosure::geometric_ratio_residual(double x, double target_mass) const {
        if (x <= 0.0) {
            throw std::domain_error("geometric_ratio_residual: x must be > 0.");
        }

        if (current_regime != DensityRegime::CORE_DOMINATED) {
            std::cerr << "Warning: geometric ratio residual evaluated outside CORE_DOMINATED regime.\n";
        }

        const double rho = get_active_density();
        const double K_core = (rho * (Gamma_0 * Gamma_0)) / (2.0 * (c * c));
        const double target_C = target_mass / (K_core * r_c);

        return x * (std::log(8.0 * x) - PHI) - target_C;
    }

    double GoldenNLSClosure::infer_geometric_ratio_safe(double target_mass,
                                                        double x0,
                                                        double x_min,
                                                        double x_max,
                                                        double x_tol,
                                                        double f_tol,
                                                        int max_iter) const {
        if (x_min <= 0.0 || x_max <= 0.0 || x_min >= x_max) {
            throw std::invalid_argument("infer_geometric_ratio_safe: require 0 < x_min < x_max.");
        }

        auto f = [&](double x) -> double {
            return geometric_ratio_residual(x, target_mass);
        };

        // 1) Try Newton first (guarded)
        double x = std::clamp(x0, x_min, x_max);
        bool newton_ok = false;

        for (int i = 0; i < max_iter; ++i) {
            if (x <= 0.0) break;

            double fx = f(x);
            if (std::abs(fx) < f_tol) {
                return x;
            }

            double fpx = std::log(8.0 * x) + 1.0 - PHI;  // derivative of x(log(8x)-phi)-C
            if (!std::isfinite(fpx) || std::abs(fpx) < 1e-14) {
                break; // fallback
            }

            double dx = fx / fpx;
            double x_next = x - dx;

            // Guard against stepping out of domain/bracket
            if (!std::isfinite(x_next) || x_next <= x_min || x_next >= x_max) {
                break;
            }

            x = x_next;

            if (std::abs(dx) < x_tol && std::abs(f(x)) < f_tol) {
                newton_ok = true;
                break;
            }
        }

        if (newton_ok) {
            return x;
        }

        // 2) Bracket check for bisection fallback
        double a = x_min;
        double b = x_max;
        double fa = f(a);
        double fb = f(b);

        if (!std::isfinite(fa) || !std::isfinite(fb)) {
            throw std::runtime_error("infer_geometric_ratio_safe: non-finite residual at bracket endpoints.");
        }

        // If bracket does not straddle root, attempt auto-expand (limited)
        if (fa * fb > 0.0) {
            double aa = x_min;
            double bb = x_max;
            bool found = false;
            for (int k = 0; k < 12; ++k) {
                aa = std::max(1e-12, aa * 0.5);
                bb = bb * 2.0;
                fa = f(aa);
                fb = f(bb);
                if (std::isfinite(fa) && std::isfinite(fb) && fa * fb <= 0.0) {
                    a = aa; b = bb; found = true; break;
                }
            }
            if (!found) {
                throw std::runtime_error("infer_geometric_ratio_safe: could not bracket root for bisection fallback.");
            }
        }

        // 3) Bisection
        for (int i = 0; i < max_iter * 4; ++i) {
            double m = 0.5 * (a + b);
            double fm = f(m);

            if (!std::isfinite(fm)) {
                throw std::runtime_error("infer_geometric_ratio_safe: non-finite residual during bisection.");
            }

            if (std::abs(fm) < f_tol || 0.5 * (b - a) < x_tol) {
                return m;
            }

            if (fa * fm <= 0.0) {
                b = m;
                fb = fm;
            } else {
                a = m;
                fa = fm;
            }
        }

        throw std::runtime_error("infer_geometric_ratio_safe: failed to converge.");
    }

    double GoldenNLSClosure::infer_effective_base(double ratio, int exponent_n) {
        if (ratio <= 0.0) {
            throw std::domain_error("infer_effective_base: ratio must be > 0.");
        }
        if (exponent_n <= 0) {
            throw std::invalid_argument("infer_effective_base: exponent_n must be positive.");
        }
        return std::pow(ratio, 1.0 / static_cast<double>(exponent_n));
    }

    double GoldenNLSClosure::predicted_ratio_from_base(double base, int exponent_n) {
        if (base <= 0.0) {
            throw std::domain_error("predicted_ratio_from_base: base must be > 0.");
        }
        return std::pow(base, static_cast<double>(exponent_n));
    }

    double GoldenNLSClosure::relative_error(double predicted, double observed) {
        if (observed == 0.0) {
            throw std::domain_error("relative_error: observed must be nonzero.");
        }
        return std::abs(predicted - observed) / std::abs(observed);
    }

}