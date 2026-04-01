import math

class SSTHydrogenSpectrum:
    """
    Derives the Hydrogen emission spectrum purely from the continuous
    incompressible fluid parameters of Swirl-String Theory.
    """
    def __init__(self):
        # 1. SST Canonical Primitive Triad (SST-53 Table 1)
        self.rho_core = 3.8934358266918687e18  # Micro-scale core density [kg/m^3]
        self.v_swirl = 1.09384563e6            # Characteristic swirl speed [m/s]
        self.r_c = 1.40897017e-15              # Filament core radius [m]
        self.c = 299792458.0                   # Speed of light [m/s]

        # Standard electron mass (acting as the topological M_0 inertia)
        self.m_e = 9.1093837015e-31            # [kg]

        # 2. Derived Invariants (Zero-Parameter Program)
        self.alpha = 2.0 * self.v_swirl / self.c
        self.A_c = 4.0 * math.pi * self.rho_core * (self.v_swirl**2) * (self.r_c**4)

        # Derived Planck's constant
        self.hbar = self.A_c / (self.alpha * self.c)
        self.h = 2.0 * math.pi * self.hbar

        # Derived Ground State Binding Energy: E_B = 2 * m_e * ||v_swirl||^2
        self.E_B_Joules = 2.0 * self.m_e * (self.v_swirl**2)

        self.J_to_eV = 6.241509e18

    def evaluate_orbital_state(self, n):
        """Calculates the stable hydrodynamic radius and energy for principal phase n."""
        # Orbital velocity via resonance condition
        v_n = (self.alpha * self.c) / n

        # Stable phase-locked radius
        r_n = (n * self.hbar) / (self.m_e * v_n)

        # Total fluid energy (Kinetic + Pressure-Work Potential)
        K_n = 0.5 * self.m_e * (v_n**2)
        U_n = -self.A_c / r_n
        E_n_Joules = K_n + U_n

        return r_n, E_n_Joules

    def compute_emission_line(self, n_initial, n_final):
        """Calculates the photon wavelength (nm) emitted during a topological Kairos transition."""
        _, E_i = self.evaluate_orbital_state(n_initial)
        _, E_f = self.evaluate_orbital_state(n_final)

        delta_E = E_i - E_f
        wavelength_m = (self.h * self.c) / delta_E
        return wavelength_m * 1e9  # Convert to nanometers

if __name__ == "__main__":
    sst_hydrogen = SSTHydrogenSpectrum()

    print("\n=== SST AB INITIO HYDROGEN SPECTRUM ===")
    print(f"[*] Derived Fine-Structure (alpha) : {sst_hydrogen.alpha:.7e}")
    print(f"[*] Derived Planck (h)           : {sst_hydrogen.h:.7e} J s")

    print("\n[>] Stable Hydrodynamic Energy Levels:")
    for n in range(1, 5):
        r_n, E_j = sst_hydrogen.evaluate_orbital_state(n)
        print(f"    n={n} | Radius: {r_n*1e11:.2f} pm | Energy: {E_j * sst_hydrogen.J_to_eV:6.2f} eV")

    print("\n[>] Balmer Series (Visible Light) Emissions:")
    transitions = {"H-alpha": (3, 2), "H-beta": (4, 2), "H-gamma": (5, 2), "H-delta": (6, 2)}

    for name, (ni, nf) in transitions.items():
        wl_nm = sst_hydrogen.compute_emission_line(ni, nf)
        print(f"    {name} ({ni} -> {nf}): {wl_nm:.2f} nm")
    print("=======================================\n")