// tests/test_sst_integrator.cpp
#include "../src/sst_integrator.h"
#include <iostream>
#include <cmath>

int main() {
    using namespace sst;

    const int N = 4000;
    std::vector<Vec3> ring(N);
    const double R_ring = 1e-14;

    for (int i = 0; i < N; ++i) {
        double theta = 2.0 * 3.14159265358979323846 * i / N;
        ring[i] = { R_ring * std::cos(theta), R_ring * std::sin(theta), 0.0 };
    }

    double m_core = 0.0, m_fluid = 0.0;
    double chi_spin = 2.0;

    std::cout << "[*] SST integrator: " << N << " points (ring), chi_spin=" << chi_spin << "\n";
    compute_sst_mass(ring, chi_spin, m_core, m_fluid);

    const double kg_to_MeV = 1.0 / 1.78266192e-30;
    std::cout << "    M_core  : " << (m_core * kg_to_MeV) << " MeV/c^2\n";
    std::cout << "    M_fluid : " << (m_fluid * kg_to_MeV) << " MeV/c^2\n";
    std::cout << "    M_total : " << ((m_core + m_fluid) * kg_to_MeV) << " MeV/c^2\n";
    std::cout << "[+] Done.\n";
    return 0;
}
