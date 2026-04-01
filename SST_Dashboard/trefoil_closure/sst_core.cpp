// Discrete curve kernels for Python module `sst_core`. C++ reference copy lives in
// src/trefoil_closure_kernels.cpp (used by CMake module `sstcore`); keep formulas aligned.
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <vector>
#include <algorithm>
#include <stdexcept>

namespace py = pybind11;

const double PI = 3.14159265358979323846;

// 1. Neumann Zelf-Energie Integraal (voorheen foutief Biot-Savart genoemd)
double calculate_neumann_self_energy(py::array_t<double> points, double rc) {
    auto r = points.unchecked<2>();
    py::ssize_t n = r.shape(0);
    double integral_val = 0.0;

    for (py::ssize_t i = 0; i < n; ++i) {
        py::ssize_t next_i = (i + 1) % n;
        double dx1 = r(next_i, 0) - r(i, 0);
        double dy1 = r(next_i, 1) - r(i, 1);
        double dz1 = r(next_i, 2) - r(i, 2);

        for (py::ssize_t j = i + 1; j < n; ++j) {
            py::ssize_t next_j = (j + 1) % n;
            double dx2 = r(next_j, 0) - r(j, 0);
            double dy2 = r(next_j, 1) - r(j, 1);
            double dz2 = r(next_j, 2) - r(j, 2);

            double rx = r(j, 0) - r(i, 0);
            double ry = r(j, 1) - r(i, 1);
            double rz = r(j, 2) - r(i, 2);

            double dist2 = rx*rx + ry*ry + rz*rz;
            double reg_dist = std::sqrt(dist2 + rc*rc);
            double dot_product = dx1*dx2 + dy1*dy2 + dz1*dz2;

            integral_val += 2.0 * (dot_product / reg_dist);
        }
    }
    return integral_val;
}

// 2. Hard-Core Repulsie (Volume uitsluiting)
double calculate_core_repulsion(py::array_t<double> points, double rc) {
    auto r = points.unchecked<2>();
    py::ssize_t n = r.shape(0);
    double U_rep = 0.0;

    // De diameter van de wervelkern is 2 * rc
    double core_diameter = 2.0 * rc;

    for (py::ssize_t i = 0; i < n; ++i) {
        // Begin bij i+2 om direct aangrenzende segmenten over te slaan
        for (py::ssize_t j = i + 2; j < n; ++j) {
            // Sla ook het cyclisch aangrenzende segment over (als i=0 en j=n-1)
            if (i == 0 && j == n - 1) continue;

            double rx = r(j, 0) - r(i, 0);
            double ry = r(j, 1) - r(i, 1);
            double rz = r(j, 2) - r(i, 2);

            double dist = std::sqrt(rx*rx + ry*ry + rz*rz);

            // Vermijd deling door nul bij extreme zelf-doorsnijding
            if (dist < 1e-30) dist = 1e-30;

            double ratio = core_diameter / dist;

            // Lennard-Jones achtige repulsie r^(-12)
            // Om overflow te voorkomen berekenen we dit alleen als segmenten relatief dichtbij zijn
            if (ratio > 0.1) {
                U_rep += std::pow(ratio, 12.0);
            }
        }
    }
    return U_rep;
}

// 3. Padlengte
double calculate_length(py::array_t<double> points) {
    auto r = points.unchecked<2>();
    py::ssize_t n = r.shape(0);
    double length = 0.0;

    for (py::ssize_t i = 0; i < n; ++i) {
        py::ssize_t next_i = (i + 1) % n;
        double dx = r(next_i, 0) - r(i, 0);
        double dy = r(next_i, 1) - r(i, 1);
        double dz = r(next_i, 2) - r(i, 2);
        length += std::sqrt(dx*dx + dy*dy + dz*dz);
    }
    return length;
}

// 4. Writhe (Heliciteit)
double calculate_writhe(py::array_t<double> points, double rc) {
    auto r = points.unchecked<2>();
    py::ssize_t n = r.shape(0);
    double writhe_val = 0.0;

    for (py::ssize_t i = 0; i < n; ++i) {
        py::ssize_t next_i = (i + 1) % n;
        double dx1 = r(next_i, 0) - r(i, 0);
        double dy1 = r(next_i, 1) - r(i, 1);
        double dz1 = r(next_i, 2) - r(i, 2);

        for (py::ssize_t j = i + 1; j < n; ++j) {
            py::ssize_t next_j = (j + 1) % n;
            double dx2 = r(next_j, 0) - r(j, 0);
            double dy2 = r(next_j, 1) - r(j, 1);
            double dz2 = r(next_j, 2) - r(j, 2);

            double rx = r(j, 0) - r(i, 0);
            double ry = r(j, 1) - r(i, 1);
            double rz = r(j, 2) - r(i, 2);

            double cx = dy1 * dz2 - dz1 * dy2;
            double cy = dz1 * dx2 - dx1 * dz2;
            double cz = dx1 * dy2 - dy1 * dx2;

            double triple_scalar = rx * cx + ry * cy + rz * cz;

            double dist2 = rx*rx + ry*ry + rz*rz;
            double dist_reg = std::sqrt(dist2 + rc*rc);

            writhe_val += 2.0 * triple_scalar / (dist_reg * dist_reg * dist_reg);
        }
    }
    return writhe_val / (4.0 * PI);
}

// 5. Buigingsstijfheid (Curvature Penalty) via Menger-kromming
double calculate_curvature_penalty(py::array_t<double> points) {
    auto r = points.unchecked<2>();
    py::ssize_t n = r.shape(0);
    double total_curvature_sq = 0.0;

    for (py::ssize_t i = 0; i < n; ++i) {
        py::ssize_t prev = (i - 1 + n) % n;
        py::ssize_t next = (i + 1) % n;

        // Vorm vectoren tussen opeenvolgende punten
        double v1x = r(i, 0) - r(prev, 0);
        double v1y = r(i, 1) - r(prev, 1);
        double v1z = r(i, 2) - r(prev, 2);

        double v2x = r(next, 0) - r(i, 0);
        double v2y = r(next, 1) - r(i, 1);
        double v2z = r(next, 2) - r(i, 2);

        // Vector van prev naar next (de basis van de driehoek)
        double v3x = r(next, 0) - r(prev, 0);
        double v3y = r(next, 1) - r(prev, 1);
        double v3z = r(next, 2) - r(prev, 2);

        // Kruisproduct v1 x v2 voor de oppervlakte van de driehoek
        double cx = v1y * v2z - v1z * v2y;
        double cy = v1z * v2x - v1x * v2z;
        double cz = v1x * v2y - v1y * v2x;

        double cross_norm = std::sqrt(cx*cx + cy*cy + cz*cz);
        double v1_norm = std::sqrt(v1x*v1x + v1y*v1y + v1z*v1z);
        double v2_norm = std::sqrt(v2x*v2x + v2y*v2y + v2z*v2z);
        double v3_norm = std::sqrt(v3x*v3x + v3y*v3y + v3z*v3z);

        double kappa = 0.0;
        // Menger-kromming: k = 4 * Area / (a * b * c) = 2 * |v1 x v2| / (|v1| * |v2| * |v3|)
        if (v1_norm > 1e-20 && v2_norm > 1e-20 && v3_norm > 1e-20) {
            kappa = (2.0 * cross_norm) / (v1_norm * v2_norm * v3_norm);
        }

        // Infinitesimale booglengte ds (gemiddelde van de twee segmenten)
        double ds = (v1_norm + v2_norm) / 2.0;

        total_curvature_sq += kappa * kappa * ds;
    }
    return total_curvature_sq;
}

// 6. Cutoff-scanned Biot-Savart / Neumann-style energy for the ideal-trefoil closure script
//
// This matches the Python kernel:
//   E_BS(a) = (1 / 8pi) * sum_{i != j, dist(i,j) > a}
//             [ (t_i · t_j) / dist(i,j) ] ds_i ds_j
//
// Important:
// - `points`    : shape (N, 3)
// - `tangents`  : shape (N, 3), already normalized
// - `ds_arr`    : shape (N,)
// - `a_values`  : shape (M,), sorted ascending
//
// The implementation uses a difference-array trick so that a whole cutoff scan
// is accumulated in one C++ pass, rather than calling Python M times.
py::array_t<double> calculate_bs_cutoff_energy_scan(
    py::array_t<double, py::array::c_style | py::array::forcecast> points,
    py::array_t<double, py::array::c_style | py::array::forcecast> tangents,
    py::array_t<double, py::array::c_style | py::array::forcecast> ds_arr,
    py::array_t<double, py::array::c_style | py::array::forcecast> a_values
) {
    auto p = points.unchecked<2>();
    auto t = tangents.unchecked<2>();
    auto ds = ds_arr.unchecked<1>();
    auto a = a_values.unchecked<1>();

    const py::ssize_t n = p.shape(0);
    const py::ssize_t m = a.shape(0);

    if (t.shape(0) != n || ds.shape(0) != n) {
        throw std::runtime_error("calculate_bs_cutoff_energy_scan: inconsistent N dimensions");
    }
    if (p.shape(1) != 3 || t.shape(1) != 3) {
        throw std::runtime_error("calculate_bs_cutoff_energy_scan: points/tangents must have shape (N, 3)");
    }

    std::vector<double> cutoffs(static_cast<std::size_t>(m));
    for (py::ssize_t k = 0; k < m; ++k) {
        cutoffs[static_cast<std::size_t>(k)] = a(k);
    }

    std::vector<double> diff(static_cast<std::size_t>(m + 1), 0.0);

    for (py::ssize_t i = 0; i < n; ++i) {
        const double pix = p(i, 0);
        const double piy = p(i, 1);
        const double piz = p(i, 2);

        const double tix = t(i, 0);
        const double tiy = t(i, 1);
        const double tiz = t(i, 2);

        const double dsi = ds(i);

        for (py::ssize_t j = 0; j < n; ++j) {
            if (i == j) continue;

            const double rx = p(j, 0) - pix;
            const double ry = p(j, 1) - piy;
            const double rz = p(j, 2) - piz;

            const double dist2 = rx * rx + ry * ry + rz * rz;
            if (dist2 <= 0.0) continue;

            const double dist = std::sqrt(dist2);
            const auto it = std::lower_bound(cutoffs.begin(), cutoffs.end(), dist);
            const py::ssize_t k = static_cast<py::ssize_t>(it - cutoffs.begin());

            // Pair contributes only to cutoff values a_k with a_k < dist.
            if (k <= 0) continue;

            const double dot_tt = tix * t(j, 0) + tiy * t(j, 1) + tiz * t(j, 2);
            const double q = (dot_tt / dist) * dsi * ds(j);

            diff[0] += q;
            diff[static_cast<std::size_t>(k)] -= q;
        }
    }

    py::array_t<double> out(m);
    auto e = out.mutable_unchecked<1>();

    double running = 0.0;
    for (py::ssize_t k = 0; k < m; ++k) {
        running += diff[static_cast<std::size_t>(k)];
        e(k) = running / (8.0 * PI);
    }

    return out;
}

// Convenience wrapper for a single cutoff value.
double calculate_bs_cutoff_energy(
    py::array_t<double, py::array::c_style | py::array::forcecast> points,
    py::array_t<double, py::array::c_style | py::array::forcecast> tangents,
    py::array_t<double, py::array::c_style | py::array::forcecast> ds_arr,
    double a_cutoff
) {
    py::array_t<double> a_values(1);
    auto a = a_values.mutable_unchecked<1>();
    a(0) = a_cutoff;

    py::array_t<double> out = calculate_bs_cutoff_energy_scan(points, tangents, ds_arr, a_values);
    auto e = out.unchecked<1>();
    return e(0);
}

PYBIND11_MODULE(sst_core, m) {
    m.doc() = "SSTcore C++ plugin for Python";
    m.def("calculate_neumann_self_energy", &calculate_neumann_self_energy, "Calculate Neumann integral C_N(K)");
    m.def("calculate_core_repulsion", &calculate_core_repulsion, "Calculate hard-core volume repulsion");
    m.def("calculate_length", &calculate_length, "Calculate L(K)");
    m.def("calculate_writhe", &calculate_writhe, "Calculate topological Writhe H(K)");
    m.def("calculate_curvature_penalty", &calculate_curvature_penalty, "Calculate integral of squared curvature");
    m.def("calculate_bs_cutoff_energy", &calculate_bs_cutoff_energy,
          "Calculate single-cutoff Biot-Savart energy for the closure scan");
    m.def("calculate_bs_cutoff_energy_scan", &calculate_bs_cutoff_energy_scan,
          "Calculate a whole cutoff scan in one C++ pass");
}