try:
    import sstcore as sst
except ImportError:
    import sstbindings as sst

import math

def main():
    # Canonical physical electron rest mass
    m_e = 9.10938356e-31
    r_c = 1.40897017e-15

    # Initialize the Golden NLS model in the Core-Dominated regime
    # This automatically invokes rho_core for mass scaling
    nls_model = sst.GoldenNLSClosure(sst.DensityRegime.CORE_DOMINATED)

    try:
        # Step 1: Infer the dimensionless geometric ratio (R_e / r_c)
        ratio_x = nls_model.infer_geometric_ratio_safe(target_mass=m_e)

        # Step 2: Calculate explicit physical radius Re
        R_e = ratio_x * r_c

        # Step 3: Re-verify mass calculation functionally
        calculated_mass = nls_model.calculate_loop_mass(R_e)

        print(f"--- SSTcore: Golden NLS Closure Validation ---")
        print(f"Density Regime    : CORE_DOMINATED (rho_core)")
        print(f"Target Mass (m_e) : {m_e:.8e} kg")
        print(f"Inferred Ratio (x): {ratio_x:.8f}")
        print(f"Implied Radius Re : {R_e:.8e} m")
        print(f"Re-computed Mass  : {calculated_mass:.8e} kg")
        try:
            fres = nls_model.geometric_ratio_residual(ratio_x)
            print(f"Residual f(x)     : {fres:.3e}")
        except Exception:
            pass
        print(f"----------------------------------------------")

        if ratio_x < 1.0:
            print("Status: Topological collapse condition met (R_e < r_c).")
            print("Convergence toward Hill-like spherical vortex limit indicated.")

    except Exception as e:
        print(f"Error executing closure inference: {e}")

    # Canonical physical masses in MeV/c^2
    m_tau_physical = 1776.86
    m_mu_physical = 105.66
    m_e_physical = 0.511

    # Initialize the Golden NLS closure
    nls_model = sst.GoldenNLSClosure(sst.DensityRegime.CORE_DOMINATED)

    print("--- SSTcore: Lepton Mass Spectrum via Golden NLS Screening ---")

    # The unscreened bare mass is assigned to the Tau state (2k = 0)
    bare_mass = m_tau_physical

    # Topological screening states (double_k = 2k)
    states = [
        {"name": "Tau (tau)", "2k": 0, "physical": m_tau_physical},
        {"name": "Muon (mu)", "2k": 6, "physical": m_mu_physical},
        {"name": "Electron (e)", "2k": 17, "physical": m_e_physical}
    ]

    for state in states:
        name = state["name"]
        double_k = state["2k"]
        physical_mass = state["physical"]

        # Calculate the theoretical mass using the phi^{-2k} scaling
        calc_mass = nls_model.calculate_screened_mass(bare_mass, double_k)

        # Calculate percentage match
        accuracy = (1.0 - abs(calc_mass - physical_mass) / physical_mass) * 100.0

        print(f"\nState: {name} | Topological Shell Index (2k): {double_k}")
        print(f"  Theoretical Mass : {calc_mass:>10.4f} MeV/c^2")
        print(f"  Physical Mass    : {physical_mass:>10.4f} MeV/c^2")
        print(f"  Topological Match: {accuracy:>10.2f} %")

    print("\n--------------------------------------------------------------")
    print("Status: The fractional deviations (e.g., ~2.7% for the electron)")
    print("are hypothesized to arise from higher-order acoustic surface")
    print("dressing analogous to the anomalous magnetic moment (a_e).")

    lepton_base_stresstest()


def lepton_base_stresstest():
    """Stress-test whether phi is special vs nearby bases for lepton gap scaling."""
    print("\n--- SSTcore: Base Stress Test for Lepton Gap Scaling ---")
    phi = (1 + math.sqrt(5)) / 2

    # observed ratios
    tau_over_mu = 1776.86 / 105.66
    tau_over_e = 1776.86 / 0.511

    # assumed integer exponents from current hypothesis
    n_mu = 6
    n_e = 17

    # implied bases if those exponents are exact
    b_mu = sst.GoldenNLSClosure.infer_effective_base(tau_over_mu, n_mu)
    b_e = sst.GoldenNLSClosure.infer_effective_base(tau_over_e, n_e)

    print(f"Observed tau/mu ratio : {tau_over_mu:.8f}")
    print(f"Observed tau/e ratio  : {tau_over_e:.8f}")
    print(f"Implied base from mu with n=6  : {b_mu:.10f}")
    print(f"Implied base from e  with n=17 : {b_e:.10f}")
    print(f"Golden ratio phi             : {phi:.10f}")

    # Compare prediction errors for phi and a few nearby bases
    candidates = [1.60, 1.61, 1.615, phi, 1.62, 1.625, 1.63]
    print("\nBase        err(tau/mu @ n=6)   err(tau/e @ n=17)")
    for b in candidates:
        pred_mu = sst.GoldenNLSClosure.predicted_ratio_from_base(b, n_mu)
        pred_e = sst.GoldenNLSClosure.predicted_ratio_from_base(b, n_e)
        err_mu = sst.GoldenNLSClosure.relative_error(pred_mu, tau_over_mu)
        err_e = sst.GoldenNLSClosure.relative_error(pred_e, tau_over_e)
        print(f"{b:>6.10f}   {err_mu:>14.6%}   {err_e:>14.6%}")

    print("\nInterpretation: if many nearby bases fit similarly, phi is not uniquely selected by these two gaps alone.")


if __name__ == "__main__":
    main()