//
// Created by oscar on 3/2/2026.
//

#ifndef SWIRL_STRING_CORE_SST_CONSTANTS_H
#define SWIRL_STRING_CORE_SST_CONSTANTS_H


#include <cmath>

/**
 * @namespace SST::Constants::pi
 * @brief High-precision physical constants for Swirl-String Theory (SST).
 * Includes CODATA 2018 quantum standards and derived SST fluid primitives.
 */
namespace SST {
    namespace Constants {

        // --- CODATA 2018 Fundamental Quantum Constants ---
        constexpr long double C_VACUUM  = 299792458.0L;             // [m/s] Speed of Light
        constexpr long double H_BAR     = 1.054571817e-34L;         // [J s] Reduced Planck Constant
        constexpr long double ALPHA     = 0.0072973525693L;         // [-]   Fine Structure Constant
        constexpr long double M_ELECTRON = 9.1093837015e-31L;       // [kg]  Electron Rest Mass
        constexpr long double E_CHARGE   = 1.602176634e-19L;        // [C]   Elementary Charge

        // --- Mathematical Constants ---
        const long double PI          = std::acos(-1.0L);
        inline constexpr const double pi = 3.141592653589793238462643383279502884L;
        const long double PHI         = (1.0L + std::sqrt(5.0L)) / 2.0L; // Golden Ratio (1.61803398...)

        // --- SST Derived Fluid Continuum Primitives (Canonical Triad) ---
        // Derived from: r_c = (alpha * h_bar) / (2 * m_e * c)
        constexpr long double RC_CORE   = 1.40897017e-15L;          // [m]   Core Radius (Half-classic)

        // Derived from: v_swirl = (alpha * c) / 2
        constexpr long double V_SWIRL   = 1093845.63L;              // [m/s] Characteristic Swirl Speed

        // Derived from SST Rest Mass Functional (NLS-Golden)
        constexpr long double RHO_CORE  = 3.8934358266918687e18L;   // [kg/m^3] Core Density
        constexpr long double RHO_FLUID = 6.8398588e-07L;           // [kg/m^3] Effective Fluid Density

        // Derived from quantization: Gamma_0 = h / m_eff
        constexpr long double GAMMA_0   = 9.68455e-09L;             // [m^2/s] Circulation Quantum

        // --- Energy and Force Limits ---
        // Maximum tangential force sustained by the swirl before reconnection
        constexpr long double F_SWIRL_MAX = 29.053507L;             // [N]

        /**
         * @brief Mass-to-Energy prefactor for the NLS-Golden Functional.
         * Used to scale topological invariants (b, g) into physical mass units.
         */
        inline long double get_mass_prefactor() {
            return (RHO_FLUID * std::pow(GAMMA_0, 2) * RC_CORE) / std::pow(C_VACUUM, 2);
        }

    } // namespace Constants
} // namespace SST

#endif // SWIRL_STRING_CORE_SST_CONSTANTS_H