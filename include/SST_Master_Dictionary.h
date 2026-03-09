//
// Created by oscar on 3/2/2026.
//

#ifndef SWIRL_STRING_CORE_SST_MASTER_DICTIONARY_H
#define SWIRL_STRING_CORE_SST_MASTER_DICTIONARY_H


#include <string>
#include <vector>
#include <map>

/**
 * @brief SST Knot Invariants Structure
 * Coupled to the NLS-Golden Mass Functional.
 * b: Bridge Number (Strand Density)
 * g: Genus (NLS Screening Layers)
 * n: Component Number (Fermionic n=1 / Bosonic n>1)
 */
struct SSTKnotInvariants {
    double b;
    int g;
    int n;
    std::vector<int> braid_word;
};

/**
 * @brief SST_MASTER_DICTIONARY
 * A maximalist topological catalog for ab initio mass derivations.
 */
static const std::map<std::string, SSTKnotInvariants> SST_MASTER_DICTIONARY = {
    // --- 0 to 2 Crossings ---
    {"Unknot", {1.0, 0, 1, {1}}},
    {"Unlink", {1.0, 0, 2, {1, -1}}},
    {"Link 2^2_1 (Hopf Link)", {2.0, 0, 2, {-1, -1}}},

    // --- 3 to 5 Crossings ---
    {"Knot 3_1 (Trefoil)", {2.0, 1, 1, {-1, -1, -1}}},
    {"Knot 4_1 (Figure-Eight)", {3.0, 1, 1, {1, -2, 1, -2}}},
    {"Link 4^2_1 (Solomon's)", {2.0, 1, 2, {-1, -1, -1, -1}}},
    {"Knot 5_1 (Torus)", {2.0, 2, 1, {-1, -1, -1, -1, -1}}},
    {"Knot 5_2 (Twist)", {3.0, 1, 1, {-1, 2, -3, 2, 2, 1, 2, 3, 2}}},
    {"Link 5^2_1 (Whitehead)", {3.0, 1, 2, {-1, -1, 2, -1, 2}}},

    // --- 6 Crossings ---
    {"Knot 6_1 (Twist)", {3.0, 1, 1, {-1, 2, -3, 4, -3, 2, 1, -3, 2, -4, 3, 2}}},
    {"Knot 6_2", {3.0, 1, 1, {1, -2, 1, 1, 1, -2}}},
    {"Knot 6_3", {3.0, 1, 1, {1, -2, 1, -2, -2, 1}}},
    {"Link 6^2_1", {3.0, 1, 2, {1, -2, 1, -2, 1, -2}}},
    {"Link 6^3_1", {3.0, 0, 3, {-1, 2, 2, -1, 2, 2}}},
    {"Link 6^3_2 (Borromean)", {3.0, 1, 3, {-1, 2, -1, 2, -1, 2}}},
    {"Link 6^3_3", {3.0, 1, 3, {-1, 2, 2, -1, -2, -2}}},

    // --- 7 Crossings ---
    {"Knot 7_1 (Torus)", {2.0, 3, 1, {-1, -1, -1, -1, -1, -1, -1}}},
    {"Knot 7_2 (Twist)", {3.0, 1, 1, {-1, -1, -1, -2, 1, -2, -3, 2, -3}}},

    // --- 8 Crossings (Nucleon Core Series) ---
    {"Link 8^2_1", {3.0, 2, 2, {-1, 2, -3, 4, -5, 4, 6, 3, 7, -2, 1, 3, -2, 3, 4, 5, 4, -3, 2, 4, -5, -6, 5, 4, -3, 4, -5, 6, -7, -6, 5, 4}}},
    {"Knot 8_1 (Twist)", {3.0, 1, 1, {-1, -2, 3, -4, 3, 5, 2, -6, 1, 3, -4, 3, 5, -2, -4, 3, -4, -5, 4, 6, -5, 4, 3, 2}}},
    {"Knot 8_2", {3.0, 2, 1, {-1, 2, -1, -1, -1, -1, -1, 2}}},
    {"Knot 8_9", {3.0, 1, 1, {-1, 2, 2, 2, -1, -1, -1, 2}}},
    {"Knot 8_12", {3.0, 2, 1, {-1, 2, -3, 2, 1, 2, -3, 4, -3, 2, -3, -4}}},
    {"Knot 8_17", {3.0, 1, 1, {-1, 2, -1, -1, 2, 2, -1, 2}}},
    {"Knot 8_19 (T_3,4)", {3.0, 3, 1, {1, 2, 1, 2, 1, 1, 2, 1}}},
    {"Knot 8_21", {3.0, 2, 1, {1, 2, -1, -2, 1, 2, 1, 2}}},

    // --- Heavy/Exotic States ---
    {"Knot 9_1 (Torus)", {2.0, 4, 1, {-1, -1, -1, -1, -1, -1, -1, -1, -1}}},
    {"Knot 9_2 (Twist)", {2.0, 1, 1, {-1, -1, -1, -2, 1, -2, -3, 2, -3, -4, 3, -4}}},
    {"Knot 10_1 (Twist)", {3.0, 1, 1, {-1, -2, 3, -4, 5, -4, -3, 2, -4, 1, -5, 6, -7, -6, 5, -4, -3, 2, -4, -5, 6, 7, -8, -7, -6, 5, -4, -3, -4, -5, 6, 5, 7, -4, 8, 3, 5, -2, -6, 3}}},
    {"Knot 11_1 (Torus)", {2.0, 5, 1, {-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1}}},
    {"Knot 12a1202", {3.0, 3, 1, {1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2}}},
    {"Knot 15a331", {3.0, 4, 1, {1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1}}}
};

/**
 * @brief Standard Model particle entry (reference masses, charge, spin).
 * Used for catalog / UI; mass is string for display (e.g. "0.511 MeV/c^2").
 */
struct SSTParticleEntry {
    std::string category;
    std::string generation;
    std::string symbol;
    std::string name;
    std::string mass;
    std::string charge;  // "2/3", "-1/3", "0", "-1", "±1"
    double spin;
};

/** Standard Model particle catalog (quarks, leptons, gauge bosons). */
static const std::vector<SSTParticleEntry> SST_STANDARD_MODEL_PARTICLES = {
    // Quarks (generations I, II, III)
    {"quark", "I",   "u",  "up",       "2.4 MeV/c^2",   "2/3",  0.5},
    {"quark", "II",  "c",  "charm",    "1.27 GeV/c^2",  "2/3",  0.5},
    {"quark", "III", "t",  "top",      "171.2 GeV/c^2", "2/3",  0.5},
    {"quark", "I",   "d",  "down",     "4.8 MeV/c^2",   "-1/3", 0.5},
    {"quark", "II",  "s",  "strange",  "104 MeV/c^2",   "-1/3", 0.5},
    {"quark", "III", "b",  "bottom",   "4.2 GeV/c^2",   "-1/3", 0.5},
    // Leptons (generations I, II, III)
    {"lepton", "I",   "nu_e", "electron neutrino", "<2.2 eV/c^2",    "0", 0.5},
    {"lepton", "II",  "nu_mu","muon neutrino",     "<0.17 MeV/c^2",  "0", 0.5},
    {"lepton", "III", "nu_tau","tau neutrino",      "<15.5 MeV/c^2",  "0", 0.5},
    {"lepton", "I",   "e",  "electron", "0.511 MeV/c^2",  "-1", 0.5},
    {"lepton", "II",  "mu", "muon",     "105.7 MeV/c^2", "-1", 0.5},
    {"lepton", "III", "tau","tau",      "1.777 GeV/c^2",  "-1", 0.5},
    // Gauge bosons
    {"gauge boson", "-", "gamma", "photon",   "0",            "0",  1.0},
    {"gauge boson", "-", "g",     "gluon",    "0",            "0",  1.0},
    {"gauge boson", "-", "Z0",    "Z boson",  "91.2 GeV/c^2", "0",  1.0},
    {"gauge boson", "-", "Wpm",   "W boson",  "80.4 GeV/c^2",  "pm1", 1.0},
    // Scalar boson
    {"scalar boson", "-", "H",    "Higgs boson", "125.1 GeV/c^2", "0", 0.0},
    // Hadrons (mesons, baryons)
    {"meson", "-", "pi0", "pion (pi0)",  "134.97 MeV/c^2", "0", 0.0},
    {"baryon", "-", "p+",  "proton",      "938.272 MeV/c^2", "1", 0.5},
    {"baryon", "-", "n",   "neutron",     "939.565 MeV/c^2", "0", 0.5},
};

#endif // SWIRL_STRING_CORE_SST_MASTER_DICTIONARY_H