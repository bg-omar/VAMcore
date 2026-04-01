#include "magnus_integrator.h"
#include <stdexcept>

// Vector helper functions for std::array
inline Vec3D cross_product(const Vec3D& a, const Vec3D& b) {
    return { a[1] * b[2] - a[2] * b[1],
             a[2] * b[0] - a[0] * b[2],
             a[0] * b[1] - a[1] * b[0] };
}
inline Vec3D add(const Vec3D& a, const Vec3D& b) { return {a[0] + b[0], a[1] + b[1], a[2] + b[2]}; }
inline Vec3D sub(const Vec3D& a, const Vec3D& b) { return {a[0] - b[0], a[1] - b[1], a[2] - b[2]}; }
inline Vec3D scale(const Vec3D& a, double s) { return {a[0] * s, a[1] * s, a[2] * s}; }
inline double norm(const Vec3D& a) { return std::sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2]); }
inline Vec3D normalize(const Vec3D& a) {
    double n = norm(a);
    return (n > 0) ? scale(a, 1.0/n) : Vec3D{0.0, 0.0, 0.0};
}

// --- Constructor ---
MagnusBernoulliIntegrator::MagnusBernoulliIntegrator(double rho_f_in, double v_swirl_in, double r_c_in, double Gamma_in)
    : rho_f(rho_f_in), v_swirl(v_swirl_in), r_c(r_c_in), Gamma(Gamma_in) {}

// --- Transverse Magnus Force ---
Vec3D MagnusBernoulliIntegrator::compute_magnus_force(const Vec3D& tangent,
                                                      const Vec3D& normal,
                                                      double curvature_radius,
                                                      const Vec3D& v_knot,
                                                      const Vec3D& v_bg) const {
    // 1. Relative velocity of the vortex segment through the continuum
    Vec3D v_rel = sub(v_knot, v_bg);

    // 2. Classical Magnus Lift: T x v_rel
    Vec3D magnus_cross = cross_product(tangent, v_rel);

    // 3. Curvature-induced Lift: (1/R) * N
    // Prevents division by zero for straight filaments
    Vec3D curvature_lift = {0.0, 0.0, 0.0};
    if (curvature_radius > 1e-30) {
        curvature_lift = scale(normal, 1.0 / curvature_radius);
    }

    // 4. Sum inner bracket
    Vec3D total_bracket = add(magnus_cross, curvature_lift);

    // 5. Apply universal fluid coefficient: rho_f * Gamma
    return scale(total_bracket, rho_f * Gamma);
}

// --- Radial Swirl-Coulomb Acceleration ---
Vec3D MagnusBernoulliIntegrator::compute_swirl_coulomb_accel(const Vec3D& eval_pos, const Vec3D& source_pos) const {
    // 1. Find radial vector and distance
    Vec3D r_vec = sub(eval_pos, source_pos);
    double r = norm(r_vec);

    // Prevent singularity at exact center (though exponential dampens it anyway)
    if (r < 1e-30) return {0.0, 0.0, 0.0};

    Vec3D r_hat = normalize(r_vec);

    // 2. Exact Bernoulli pressure gradient evaluating strictly outside the core
    // a_r = - (v_swirl^2 / r) * exp(-2r / r_c)
    double exponent = -2.0 * (r / r_c);

    // Safety check for extreme distances where exp() underflows to 0
    if (exponent < -700.0) return {0.0, 0.0, 0.0};

    double magnitude = -1.0 * ((v_swirl * v_swirl) / r) * std::exp(exponent);

    // 3. Return directed acceleration
    return scale(r_hat, magnitude);
}