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
    {"Link 6^3_2 (Borromean)", {3.0, 1, 3, {-1, 2, -1, 2, -1, 2}}},

    // --- 8 Crossings (Nucleon Core Series) ---
    {"Knot 8_1 (Twist)", {3.0, 1, 1, {-1, -2, 3, -4, 3, 5, 2, -6, 1, 3, -4, 3, 5, -2, -4, 3, -4, -5, 4, 6, -5, 4, 3, 2}}},
    {"Knot 8_2", {3.0, 2, 1, {-1, 2, -1, -1, -1, -1, -1, 2}}},
    {"Knot 8_9", {3.0, 1, 1, {-1, 2, 2, 2, -1, -1, -1, 2}}},
    {"Knot 8_12", {3.0, 2, 1, {-1, 2, -3, 2, 1, 2, -3, 4, -3, 2, -3, -4}}},
    {"Knot 8_17", {3.0, 1, 1, {-1, 2, -1, -1, 2, 2, -1, 2}}},
    {"Knot 8_19 (T_3,4)", {3.0, 3, 1, {1, 2, 1, 2, 1, 1, 2, 1}}},
    {"Knot 8_21", {3.0, 2, 1, {1, 2, -1, -2, 1, 2, 1, 2}}},

    // --- Heavy/Exotic States ---
    {"Knot 9_1 (Torus)", {2.0, 4, 1, {-1, -1, -1, -1, -1, -1, -1, -1, -1}}},
    {"Knot 10_1 (Twist)", {3.0, 1, 1, {-1, -2, 3, -4, 5, -4, -3, 2, -4, 1, -5, 6, -7, -6, 5, -4, -3, 2, -4, -5, 6, 7, -8, -7, -6, 5, -4, -3, -4, -5, 6, 5, 7, -4, 8, 3, 5, -2, -6, 3}}},
    {"Knot 12a1202", {3.0, 3, 1, {1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2}}},
    {"Knot 15a331", {3.0, 4, 1, {1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1}}}
};

#endif // SWIRL_STRING_CORE_SST_MASTER_DICTIONARY_H