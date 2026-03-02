#include "ab_initio_mass.h"
#include "biot_savart.h"
#include "frenet_helicity.h"
#include "knot_files_embedded.h"
#include "potential_timefield.h"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <knot_dynamics.h>
#include <regex>
#include <sstream>
#include <stdexcept>

namespace sst {

    static std::string load_ideal_database_from_file() {
        const char* paths[] = {
            "ideal_database.txt",
            "Front-End/knot_fseries/ideal_database.txt",
            "../Front-End/knot_fseries/ideal_database.txt",
            "../../Front-End/knot_fseries/ideal_database.txt",
        };
        const char* env_path = std::getenv("SST_IDEAL_DATABASE");
        if (env_path && env_path[0] != '\0') {
            std::ifstream f(env_path);
            if (f) {
                std::ostringstream ss;
                ss << f.rdbuf();
                return ss.str();
            }
        }
        for (const char* p : paths) {
            std::ifstream f(p);
            if (f) {
                std::ostringstream ss;
                ss << f.rdbuf();
                return ss.str();
            }
        }
        return "";
    }

    ParticleEvaluator::ParticleEvaluator(const std::string& knot_ab_id, int resolution) {
        std::string db_content;
        auto embedded_files = get_embedded_knot_files();
        for (const auto& pair : embedded_files) {
            if (pair.first.find("ideal_database.txt") != std::string::npos) {
                db_content = pair.second;
                break;
            }
        }
        if (db_content.empty()) {
            db_content = load_ideal_database_from_file();
        }
        if (db_content.empty()) {
            throw std::runtime_error("[!] SSTcore: ideal_database.txt niet gevonden.");
        }

        if (!extract_and_build_filament(db_content, knot_ab_id, resolution)) {
            throw std::runtime_error("[!] SSTcore: Knoop ID " + knot_ab_id + " niet gevonden in database.");
        }
    }

    // [NEW] Direct injection constructor
    ParticleEvaluator::ParticleEvaluator(const std::vector<std::vector<Vec3>>& input_filaments) {
            this->filaments = input_filaments;
        }
    bool ParticleEvaluator::extract_and_build_filament(const std::string& db_content, const std::string& ab_id, int resolution) {
        std::string search_tag = "<AB Id=\"" + ab_id + "\"";
        size_t start_pos = db_content.find(search_tag);
        if (start_pos == std::string::npos) return false;
        size_t end_pos = db_content.find("</AB>", start_pos);
        if (end_pos == std::string::npos) return false;

        std::string block = db_content.substr(start_pos, end_pos - start_pos);
        filaments.clear();

        // Helper lambda om een specifieke component/ring in te lezen
        auto parse_component = [&](const std::string& comp_block) {
            std::vector<Vec3> A_coeffs(20, {0,0,0});
            std::vector<Vec3> B_coeffs(20, {0,0,0});
            int max_i = 0;

            size_t coeff_pos = 0;
            while ((coeff_pos = comp_block.find("<Coeff", coeff_pos)) != std::string::npos) {
                size_t end_coeff = comp_block.find("/>", coeff_pos);
                if (end_coeff == std::string::npos) break;
                std::string line = comp_block.substr(coeff_pos, end_coeff - coeff_pos);

                int idx = 1;
                size_t i_start = line.find("I=\"");
                if (i_start != std::string::npos) idx = std::stoi(line.substr(i_start + 3));

                size_t a_start = line.find("A=\"");
                size_t b_start = line.find("B=\"");
                if (a_start != std::string::npos && b_start != std::string::npos) {
                    Vec3 A_vec{0,0,0}, B_vec{0,0,0};
                    sscanf(line.c_str() + a_start + 3, "%lf,%lf,%lf", &A_vec[0], &A_vec[1], &A_vec[2]);
                    sscanf(line.c_str() + b_start + 3, "%lf,%lf,%lf", &B_vec[0], &B_vec[1], &B_vec[2]);
                    if(idx < 20) {
                        A_coeffs[idx] = A_vec; B_coeffs[idx] = B_vec;
                        if(idx > max_i) max_i = idx;
                    }
                }
                coeff_pos = end_coeff + 2;
            }

            std::vector<Vec3> fil(resolution, {0,0,0});
            for (int i = 0; i < resolution; ++i) {
                double t = 2.0 * M_PI * i / resolution;
                Vec3 pt = A_coeffs[0]; // Offset (translatie)
                for (int j = 1; j <= max_i; ++j) {
                    pt[0] += A_coeffs[j][0] * std::cos(j*t) + B_coeffs[j][0] * std::sin(j*t);
                    pt[1] += A_coeffs[j][1] * std::cos(j*t) + B_coeffs[j][1] * std::sin(j*t);
                    pt[2] += A_coeffs[j][2] * std::cos(j*t) + B_coeffs[j][2] * std::sin(j*t);
                }
                fil[i] = pt;
            }
            filaments.push_back(fil);
        };

        // Check of het een Link is (bestaat uit <Component> tags)
        size_t comp_pos = block.find("<Component");
        if (comp_pos != std::string::npos) {
            while (comp_pos != std::string::npos) {
                size_t end_comp = block.find("</Component>", comp_pos);
                if (end_comp == std::string::npos) break;
                parse_component(block.substr(comp_pos, end_comp - comp_pos));
                comp_pos = block.find("<Component", end_comp);
            }
        } else {
            // Backwards compatibility voor enkele knopen (Electron, Top Quark, etc.)
            parse_component(block);
        }
        return !filaments.empty();
    }

    void ParticleEvaluator::relax_hamiltonian(int iterations, double timestep, std::function<void()> interrupt_callback) {
        if (filaments.empty()) return;

        double k_spring = 25.0;
        double k_pressure = 15.0;
        double k_repulsion = 0.5;
        double repulsion_radius = 0.2;
        double damping = 0.70;

        std::vector<std::vector<Vec3>> velocities(filaments.size());
        for (size_t f = 0; f < filaments.size(); ++f) {
            velocities[f].resize(filaments[f].size(), {0.0, 0.0, 0.0});
        }

        auto start_time = std::chrono::high_resolution_clock::now();

        for (int iter = 0; iter < iterations; ++iter) {
            // --- Console Output logica hier (overslaan voor beknoptheid) ---

            // 1. Bereken globaal zwaartepunt van ALLE draden samen
            Vec3 global_centroid = {0.0, 0.0, 0.0};
            size_t total_points = 0;
            for (const auto& fil : filaments) {
                for (const auto& pt : fil) {
                    global_centroid[0] += pt[0]; global_centroid[1] += pt[1]; global_centroid[2] += pt[2];
                }
                total_points += fil.size();
            }
            global_centroid[0] /= total_points; global_centroid[1] /= total_points; global_centroid[2] /= total_points;

            std::vector<std::vector<Vec3>> forces = velocities; // init met 0
            for (auto& row : forces) std::fill(row.begin(), row.end(), Vec3{0,0,0});

            #pragma omp parallel for
            for (int f = 0; f < (int)filaments.size(); ++f) {
                int N = filaments[f].size();
                for (int i = 0; i < N; ++i) {
                    int prev = (i - 1 + N) % N;
                    int next = (i + 1) % N;
                    Vec3 pt = filaments[f][i];

                    // Lijnspanning: uitsluitend binnen DEZELFDE draad
                    forces[f][i][0] += k_spring * ((filaments[f][prev][0] - pt[0]) + (filaments[f][next][0] - pt[0]));
                    forces[f][i][1] += k_spring * ((filaments[f][prev][1] - pt[1]) + (filaments[f][next][1] - pt[1]));
                    forces[f][i][2] += k_spring * ((filaments[f][prev][2] - pt[2]) + (filaments[f][next][2] - pt[2]));

                    // Compressie: richting het globale zwaartepunt
                    forces[f][i][0] += k_pressure * (global_centroid[0] - pt[0]);
                    forces[f][i][1] += k_pressure * (global_centroid[1] - pt[1]);
                    forces[f][i][2] += k_pressure * (global_centroid[2] - pt[2]);

                    // Afstoting: tegen ELK punt in ELKE draad (inter- én intra-filament Pauli uitsluiting)
                    for (size_t f_other = 0; f_other < filaments.size(); ++f_other) {
                        for (size_t j = 0; j < filaments[f_other].size(); ++j) {
                            if (f == f_other && (i == (int)j || (int)j == prev || (int)j == next)) continue;

                            double dx = pt[0] - filaments[f_other][j][0];
                            double dy = pt[1] - filaments[f_other][j][1];
                            double dz = pt[2] - filaments[f_other][j][2];
                            double dist_sq = dx*dx + dy*dy + dz*dz;

                            if (dist_sq < repulsion_radius * repulsion_radius && dist_sq > 1e-8) {
                                double dist = std::sqrt(dist_sq);
                                double rep = k_repulsion * (1.0 / (dist_sq * dist_sq));
                                if (rep > 200.0) rep = 200.0;
                                forces[f][i][0] += rep * (dx / dist);
                                forces[f][i][1] += rep * (dy / dist);
                                forces[f][i][2] += rep * (dz / dist);
                            }
                        }
                    }
                }
            }

            // Toepassen snelheden
            for (size_t f = 0; f < filaments.size(); ++f) {
                for (size_t i = 0; i < filaments[f].size(); ++i) {
                    velocities[f][i][0] = (velocities[f][i][0] + forces[f][i][0] * timestep) * damping;
                    velocities[f][i][1] = (velocities[f][i][1] + forces[f][i][1] * timestep) * damping;
                    velocities[f][i][2] = (velocities[f][i][2] + forces[f][i][2] * timestep) * damping;

                    filaments[f][i][0] += velocities[f][i][0] * timestep;
                    filaments[f][i][1] += velocities[f][i][1] * timestep;
                    filaments[f][i][2] += velocities[f][i][2] * timestep;
                }
            }
        }

        // --- HORN TORUS SCHALING (Multi-Component) ---
        Vec3 global_centroid = {0.0, 0.0, 0.0};
        size_t total_points = 0;
        double max_dist_sq = 0.0;

        for (const auto& fil : filaments) {
            for (const auto& pt : fil) {
                global_centroid[0] += pt[0]; global_centroid[1] += pt[1]; global_centroid[2] += pt[2];
                total_points++;
            }
        }
        global_centroid[0] /= total_points; global_centroid[1] /= total_points; global_centroid[2] /= total_points;

        // Bepaal de Horn Torus box voor de totale bundel
        for (const auto& fil : filaments) {
            for (const auto& pt : fil) {
                double dx = pt[0] - global_centroid[0];
                double dy = pt[1] - global_centroid[1];
                double dz = pt[2] - global_centroid[2];
                double d_sq = dx*dx + dy*dy + dz*dz;
                if (d_sq > max_dist_sq) max_dist_sq = d_sq;
            }
        }

        double r_raw = std::sqrt(max_dist_sq);
        if (r_raw < 1e-12) r_raw = 1e-6;
        double scale = (2.0 * r_c) / r_raw;

        for (auto& fil : filaments) {
            for (auto& pt : fil) {
                pt[0] = global_centroid[0] + (pt[0] - global_centroid[0]) * scale;
                pt[1] = global_centroid[1] + (pt[1] - global_centroid[1]) * scale;
                pt[2] = global_centroid[2] + (pt[2] - global_centroid[2]) * scale;
            }
        }
    }

    double ParticleEvaluator::get_dimless_ropelength(double stretch_lambda) const {
            if (filaments.empty()) return 0.0;

            double L_K = 0.0;
            for (const auto& fil : filaments) {
                size_t N = fil.size();
                for (size_t i = 0; i < N; ++i) {
                    size_t next = (i + 1) % N;
                    double dx = fil[next][0] - fil[i][0];
                    double dy = fil[next][1] - fil[i][1];
                    double dz = fil[next][2] - fil[i][2];
                    L_K += std::sqrt(dx*dx + dy*dy + dz*dz);
                }
            }

            // Convert to dimensionless units (2 * r_c)
            double dimless_L = L_K / (2.0 * r_c);

            // Apply the quadratic scaling of the vortex stretch limit
            // For chiral fermions, stretch_lambda = 1.0 (no effect).
            // For bosons, stretch_lambda = sqrt(10), reducing effective hydrodynamic length by 10.
            return dimless_L / (stretch_lambda * stretch_lambda);
        }

    // ------------------------------------------------------------
    // NEW: physical length and energy-based mass
    // ------------------------------------------------------------
    double ParticleEvaluator::get_physical_length_m() const {
        // After Horn Torus scaling, filaments are in physical coordinates [m].
        // L_K = get_dimless_ropelength(lambda) * (2*r_c) * lambda^2
        const double lambda = 1.0;
        const double L_dimless = get_dimless_ropelength(lambda);
        return L_dimless * (2.0 * r_c) * (lambda * lambda);
    }

    double ParticleEvaluator::compute_core_energy_J() const {
        // E_core = (1/2 rho_core v_swirl^2) * (pi r_c^2) * L
        const double L = get_physical_length_m();
        const double tube_area = M_PI * r_c * r_c;
        const double u_core = 0.5 * rho_core * v_swirl * v_swirl;  // J/m^3
        return u_core * tube_area * L;
    }

    double ParticleEvaluator::compute_tail_energy_J(bool include_tail) const {
        if (!include_tail) return 0.0;
        return compute_tail_energy_surrogate_J();
    }

    double ParticleEvaluator::get_mass_mev_ab_initio(bool include_tail) const {
        const double E = compute_core_energy_J() + compute_tail_energy_J(include_tail);
        return E / MeV_J_;
    }

    double ParticleEvaluator::get_core_mass_mev_only() const {
        return compute_core_energy_J() / MeV_J_;
    }

    // ------------------------------------------------------------
    // Tail-energy surrogate
    // ------------------------------------------------------------
    void ParticleEvaluator::set_tail_approx_config(const TailApproxConfig& cfg) {
        tail_cfg_ = cfg;
    }

    ParticleEvaluator::TailApproxConfig ParticleEvaluator::get_tail_approx_config() const {
        return tail_cfg_;
    }

    std::vector<Vec3> ParticleEvaluator::get_relaxed_polyline_m() const {
        std::vector<Vec3> out;
        for (const auto& fil : filaments) {
            for (const auto& pt : fil) {
                out.push_back(pt);
            }
        }
        return out;
    }

    Vec3 ParticleEvaluator::v_add(const Vec3& a, const Vec3& b) {
        return {a[0] + b[0], a[1] + b[1], a[2] + b[2]};
    }
    Vec3 ParticleEvaluator::v_sub(const Vec3& a, const Vec3& b) {
        return {a[0] - b[0], a[1] - b[1], a[2] - b[2]};
    }
    Vec3 ParticleEvaluator::v_mul(const Vec3& a, double s) {
        return {a[0] * s, a[1] * s, a[2] * s};
    }
    double ParticleEvaluator::v_dot(const Vec3& a, const Vec3& b) {
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
    }
    Vec3 ParticleEvaluator::v_cross(const Vec3& a, const Vec3& b) {
        return {
            a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]
        };
    }
    double ParticleEvaluator::v_norm(const Vec3& a) {
        return std::sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2]);
    }
    Vec3 ParticleEvaluator::v_unit(const Vec3& a) {
        double n = v_norm(a);
        if (n < 1e-30) return {1, 0, 0};
        return v_mul(a, 1.0 / n);
    }

    void ParticleEvaluator::local_frame_at_index(std::size_t f, std::size_t i,
                                                 Vec3& t_hat, Vec3& n_hat, Vec3& b_hat) const {
        if (filaments.empty() || f >= filaments.size()) {
            t_hat = {1, 0, 0}; n_hat = {0, 1, 0}; b_hat = {0, 0, 1};
            return;
        }
        const auto& fil = filaments[f];
        const size_t N = fil.size();
        if (N < 3) {
            t_hat = {1, 0, 0}; n_hat = {0, 1, 0}; b_hat = {0, 0, 1};
            return;
        }

        size_t im1 = (i + N - 1) % N;
        size_t ip1 = (i + 1) % N;
        Vec3 t = v_sub(fil[ip1], fil[im1]);
        t_hat = v_unit(t);

        // Stable reference not parallel to tangent
        Vec3 ref = (std::abs(t_hat[2]) < 0.9) ? Vec3{0, 0, 1} : Vec3{0, 1, 0};
        n_hat = v_unit(v_cross(ref, t_hat));
        if (v_norm(n_hat) < 1e-12) n_hat = {1, 0, 0};
        b_hat = v_unit(v_cross(t_hat, n_hat));
        n_hat = v_cross(b_hat, t_hat);
    }

    Vec3 ParticleEvaluator::induced_velocity_bs_surrogate(const Vec3& p,
            std::size_t f_center, std::size_t i_center, double exclusion_len_m) const {
        // Biot–Savart: v = (Gamma/4pi) * int (dl x r) / |r|^3
        const double Gamma = 2.0 * M_PI * r_c * v_swirl;
        const double coeff = Gamma / (4.0 * M_PI);
        const double eps2 = 1e-24;

        Vec3 v_tot = {0, 0, 0};
        for (size_t ff = 0; ff < filaments.size(); ++ff) {
            const auto& fil = filaments[ff];
            const size_t N = fil.size();
            if (N < 2) continue;

            double ds_mean = 0.0;
            for (size_t k = 0; k < N; ++k) {
                size_t kn = (k + 1) % N;
                ds_mean += v_norm(v_sub(fil[kn], fil[k]));
            }
            ds_mean /= static_cast<double>(N);
            const int excl_idx = std::max(1, static_cast<int>(std::ceil(exclusion_len_m / std::max(ds_mean, 1e-30))));

            for (size_t j = 0; j < N; ++j) {
                if (ff == f_center) {
                    int di = static_cast<int>(j) - static_cast<int>(i_center);
                    int wrapped = std::min(std::abs(di), static_cast<int>(N) - std::abs(di));
                    if (wrapped <= excl_idx) continue;
                }
                size_t jn = (j + 1) % N;
                Vec3 a = fil[j];
                Vec3 b = fil[jn];
                Vec3 dl = v_sub(b, a);
                Vec3 mid = v_mul(v_add(a, b), 0.5);
                Vec3 r = v_sub(p, mid);
                double r2 = v_dot(r, r) + eps2;
                double rmag = std::sqrt(r2);
                double invr3 = 1.0 / (r2 * rmag);
                v_tot = v_add(v_tot, v_mul(v_cross(dl, r), coeff * invr3));
            }
        }
        return v_tot;
    }

    double ParticleEvaluator::compute_tail_energy_surrogate_J() const {
        if (!tail_cfg_.enabled || filaments.empty()) return 0.0;

        const int Nr = std::max(1, tail_cfg_.radial_samples);
        const int Nphi = std::max(1, tail_cfg_.azimuth_samples);
        const double rmin = std::max(1.01, tail_cfg_.r_min_factor) * r_c;
        const double rmax = std::max(rmin * 1.1, tail_cfg_.r_max_factor * r_c);

        std::vector<double> r_edges(Nr + 1);
        for (int k = 0; k <= Nr; ++k) {
            double u = static_cast<double>(k) / static_cast<double>(Nr);
            r_edges[k] = rmin + (rmax - rmin) * u;
        }

        double E_tail = 0.0;
        for (size_t f = 0; f < filaments.size(); ++f) {
            const auto& fil = filaments[f];
            const size_t N = fil.size();
            if (N < 3) continue;

            std::vector<double> ds(N, 0.0);
            double Ltot = 0.0;
            for (size_t i = 0; i < N; ++i) {
                size_t j = (i + 1) % N;
                ds[i] = v_norm(v_sub(fil[j], fil[i]));
                Ltot += ds[i];
            }
            const double ds_mean = Ltot / static_cast<double>(N);
            const double exclusion_len_m = tail_cfg_.exclusion_ds_factor * ds_mean;

            for (size_t i = 0; i < N; ++i) {
                Vec3 t_hat, n_hat, b_hat;
                local_frame_at_index(f, i, t_hat, n_hat, b_hat);
                const Vec3 c = fil[i];
                const double dsi = ds[i];

                for (int k = 0; k < Nr; ++k) {
                    const double ra = r_edges[k];
                    const double rb = r_edges[k + 1];
                    const double rmid = 0.5 * (ra + rb);
                    const double annulus_area = M_PI * (rb * rb - ra * ra);

                    double v2_avg = 0.0;
                    for (int m = 0; m < Nphi; ++m) {
                        double phi = 2.0 * M_PI * (static_cast<double>(m) + 0.5) / static_cast<double>(Nphi);
                        Vec3 offset = v_add(v_mul(n_hat, rmid * std::cos(phi)), v_mul(b_hat, rmid * std::sin(phi)));
                        Vec3 p = v_add(c, offset);
                        Vec3 vbs = induced_velocity_bs_surrogate(p, f, i, exclusion_len_m);
                        v2_avg += v_dot(vbs, vbs);
                    }
                    v2_avg /= static_cast<double>(Nphi);

                    const double dV = annulus_area * dsi;
                    E_tail += 0.5 * rho_fluid * v2_avg * dV;
                }
            }
        }
        return E_tail;
    }

    ParticleEvaluator::RelativisticMetrics ParticleEvaluator::compute_relativistic_metrics(double circulation) const {
        RelativisticMetrics metrics;
        metrics.helicity = 0.0;
        metrics.core_time_dilation = 1.0;

        if (filaments.empty() || filaments[0].empty()) return metrics;

        const auto& fil = filaments[0];
        size_t N = fil.size();

        std::vector<Vec3> T, N_vec, B;
        FrenetHelicity::compute_frenet_frames(fil, T, N_vec, B);

        std::vector<Vec3> velocity(N);
        std::vector<Vec3> vorticity(N);

        double omega_mag = circulation / (M_PI * r_c * r_c);

        for (size_t i = 0; i < N; ++i) {
            velocity[i] = BiotSavart::velocity(fil[i], fil, T, circulation);
            vorticity[i] = {T[i][0] * omega_mag, T[i][1] * omega_mag, T[i][2] * omega_mag};
        }

        metrics.helicity = static_cast<double>(FrenetHelicity::compute_helicity(velocity, vorticity));
        metrics.time_dilation_map = TimeField::compute_time_dilation_map_sqrt(velocity, v_swirl);

        double sum_St = 0.0;
        for (double st : metrics.time_dilation_map) {
            sum_St += st;
        }
        metrics.core_time_dilation = sum_St / static_cast<double>(N);

        return metrics;
    }

    // Add this implementation at the bottom of src/ab_initio_mass.cpp

    void ParticleEvaluator::print_canonical_derivation() {
        // Dynamically calculate the closure
        double calc_rho_core = F_max / (M_PI * r_c * r_c * v_swirl * v_swirl);
        double calc_rho_E = calc_rho_core * c_light * c_light;

        std::cout << "\n==================================================================\n";
        std::cout << "SST CANON: DYNAMIC CLOSURE OF CORE DENSITY\n";
        std::cout << "==================================================================\n";
        std::cout << "The effective mass density of the vortex core (rho_core) is strictly\n";
        std::cout << "derived as a dynamic closure relation. The maximum tangential tension\n";
        std::cout << "(F_max) perfectly balances the hydrodynamic inertia of the fluid.\n\n";
        std::cout << "Formula: rho_core = F_max / (pi * r_c^2 * ||v_swirl||^2)\n\n";

        std::cout << "[*] Core Primitives:\n";
        std::cout << std::defaultfloat << std::setprecision(8);
        std::cout << "    F_max   = " << F_max << " N\n";
        std::cout << std::scientific << std::setprecision(8);
        std::cout << "    r_c     = " << r_c << " m\n";
        std::cout << "    v_swirl = " << v_swirl << " m/s\n\n";

        std::cout << "[*] Derived Invariant Densities:\n";
        std::cout << std::scientific << std::setprecision(16);
        std::cout << "    rho_core = " << calc_rho_core << " kg/m^3\n";
        std::cout << "    rho_E    = " << calc_rho_E << " J/m^3\n";
        std::cout << "==================================================================\n\n";
    }

}