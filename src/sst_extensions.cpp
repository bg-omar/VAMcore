#include "sst_extensions.h"

#include <fstream>
#include <sstream>
#include <cmath>
#include <stdexcept>
#include <algorithm>
#include <filesystem>

#include "../src/knot_dynamics.h"
#include "../src/biot_savart.h"

namespace sstext {
namespace fs = std::filesystem;

std::optional<std::vector<double>> parse_floats_line(const std::string& line) {
    std::istringstream iss(line);
    std::vector<double> vals;
    double x;
    while (iss >> x) vals.push_back(x);
    if (vals.empty()) return std::nullopt;
    return vals;
}

bool is_comment_or_blank(const std::string& s) {
    for (char c : s) {
        if (c==' '||c=='\t'||c=='\r'||c=='\n') continue;
        return c=='%';
    }
    return true;
}

CanonicalizeResult canonicalize_fseries_file_inplace(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("cannot open file: " + path);

    std::vector<std::string> lines;
    std::string line;
    while (std::getline(in, line)) lines.push_back(line);
    in.close();

    std::vector<size_t> num_idx;
    std::vector<std::vector<double>> rows;

    for (size_t i=0;i<lines.size();++i) {
        const std::string& s = lines[i];
        if (is_comment_or_blank(s)) continue;
        auto vals_opt = parse_floats_line(s);
        if (!vals_opt) continue;
        auto vals = *vals_opt;
        if (vals.size()==3 || vals.size()==6) {
            num_idx.push_back(i);
            rows.push_back(vals);
        }
    }

    CanonicalizeResult out;
    out.path = path;
    out.found_numeric_rows = static_cast<int>(rows.size());

    if (rows.empty()) {
        out.reason = "no numeric rows found";
        return out;
    }

    if (rows[0].size()==6) {
        out.reason = "already has 6-column j=0 row";
        return out;
    }

    size_t next_i = static_cast<size_t>(-1);
    for (size_t k=1;k<rows.size();++k) {
        if (rows[k].size()==3 || rows[k].size()==6) { next_i = k; break; }
    }
    if (next_i==static_cast<size_t>(-1)) {
        out.reason = "no second numeric row";
        return out;
    }
    if (rows[next_i].size()!=6) {
        out.reason = "file appears to be 3-column legacy throughout; not auto-converted";
        return out;
    }

    std::ostringstream oss;
    oss.setf(std::ios::fixed);
    oss.precision(6);
    oss << "    " << 0.0 << "    " << 0.0 << "    " << 0.0
        << "    " << 0.0 << "    " << 0.0 << "    " << 0.0;
    lines[num_idx[0]] = oss.str();

    std::ofstream out_f(path, std::ios::trunc);
    if (!out_f) throw std::runtime_error("cannot write file: " + path);
    for (size_t i=0;i<lines.size();++i) {
        out_f << lines[i] << "\n";
    }
    out_f.close();

    out.changed = true;
    out.reason = "upgraded leading 3-col zeros row to 6-col j=0 row";
    return out;
}

HelicityResult helicity_from_fseries(
    const std::string& path,
    int grid_size,
    double spacing,
    int interior_margin,
    int nsamples
) {
    auto pts = sample_curve_centered(path, nsamples);
    double L = 0.0, kappa_max = 0.0, kappa_mean = 0.0, bend_energy = 0.0;
    curve_metrics_from_points(pts, L, kappa_max, kappa_mean, bend_energy);
    double dmin = min_non_neighbor_distance(pts, 3);
    double rproxy = 0.5 * dmin;

    auto blocks = sst::FourierKnot::parse_fseries_multi(path);
    if (blocks.empty()) throw std::runtime_error("no blocks parsed from: " + path);
    int idx = sst::FourierKnot::index_of_largest_block(blocks);
    if (idx < 0 || idx >= static_cast<int>(blocks.size())) idx = 0;
    auto [Hc, Hm, a_mu] = sst::KnotDynamics::compute_helicity_from_fourier_block(
        blocks[static_cast<size_t>(idx)], grid_size, spacing, interior_margin, nsamples
    );
    HelicityResult out;
    out.path = path;
    out.a_mu = a_mu;
    out.Hc = Hc;
    out.Hm = Hm;
    out.L = L;
    out.kappa_max = kappa_max;
    out.kappa_mean = kappa_mean;
    out.bend_energy = bend_energy;
    out.min_non_neighbor_dist = dmin;
    out.reach_proxy = rproxy;
    out.nsamples = nsamples;
    return out;
}

std::vector<sst::Vec3> sample_curve_centered(const std::string& path, int nsamples) {
    auto blocks = sst::FourierKnot::parse_fseries_multi(path);
    if (blocks.empty()) throw std::runtime_error("no blocks parsed from: " + path);
    int idx = sst::FourierKnot::index_of_largest_block(blocks);
    if (idx < 0 || idx >= static_cast<int>(blocks.size())) idx = 0;

    std::vector<double> s;
    s.reserve(static_cast<size_t>(nsamples));
    const double two_pi = 2.0 * M_PI;
    for (int i=0;i<nsamples;++i) s.push_back(two_pi * static_cast<double>(i) / static_cast<double>(nsamples));

    auto pts = sst::FourierKnot::evaluate(blocks[static_cast<size_t>(idx)], s);
    return sst::FourierKnot::center_points(pts);
}

double curve_length(const std::vector<sst::Vec3>& pts) {
    if (pts.size()<2) return 0.0;
    double L=0.0;
    for (size_t i=0;i<pts.size();++i) {
        const auto& a = pts[i];
        const auto& b = pts[(i+1)%pts.size()];
        L += sst::norm(sst::diff(b,a));
    }
    return L;
}

void curve_metrics_from_points(
    const std::vector<sst::Vec3>& pts,
    double& L,
    double& kappa_max,
    double& kappa_mean,
    double& bend_energy
) {
    const size_t N = pts.size();
    L = curve_length(pts);
    kappa_max = 0.0;
    kappa_mean = 0.0;
    bend_energy = 0.0;
    if (N < 3 || L <= 0.0) return;

    double ksum = 0.0;
    for (size_t i = 0; i < N; ++i) {
        const auto& xm = pts[(i + N - 1) % N];
        const auto& x0 = pts[i];
        const auto& xp = pts[(i + 1) % N];

        auto d1 = sst::diff(x0, xm);
        auto d2 = sst::diff(xp, x0);
        double ds1 = sst::norm(d1);
        double ds2 = sst::norm(d2);
        double ds_loc = 0.5 * (ds1 + ds2);
        if (ds1 <= 0.0 || ds2 <= 0.0 || ds_loc <= 0.0) continue;

        sst::Vec3 t1 = {d1[0] / ds1, d1[1] / ds1, d1[2] / ds1};
        sst::Vec3 t2 = {d2[0] / ds2, d2[1] / ds2, d2[2] / ds2};
        double kappa = sst::norm(sst::diff(t2, t1)) / ds_loc;
        ksum += kappa;
        bend_energy += kappa * kappa * ds_loc;
        if (kappa > kappa_max) kappa_max = kappa;
    }
    kappa_mean = ksum / static_cast<double>(N);
}

double min_non_neighbor_distance(const std::vector<sst::Vec3>& pts, int skip) {
    const size_t N = pts.size();
    if (N<4) return 0.0;
    double dmin = 1e300;
    for (size_t i=0;i<N;++i) {
        for (size_t j=0;j<N;++j) {
            if (i==j) continue;
            long ad = std::labs(static_cast<long>(j) - static_cast<long>(i));
            long cd = std::min<long>(ad, static_cast<long>(N) - ad);
            if (cd <= skip) continue;
            double d = sst::norm(sst::diff(pts[j], pts[i]));
            if (d < dmin) dmin = d;
        }
    }
    return dmin;
}

double reach_proxy(const std::vector<sst::Vec3>& pts, int skip) {
    return 0.5 * min_non_neighbor_distance(pts, skip);
}

FilamentEnergyResult curve_metrics_from_fseries(const std::string& path, int nsamples, int skip) {
    auto pts = sample_curve_centered(path, nsamples);
    FilamentEnergyResult out;
    out.path = path;
    out.nsamples = nsamples;
    curve_metrics_from_points(pts, out.L, out.kappa_max, out.kappa_mean, out.bend_energy);
    out.ds_avg = (pts.empty() ? 0.0 : out.L / static_cast<double>(pts.size()));
    out.min_non_neighbor_dist = min_non_neighbor_distance(pts, skip);
    out.reach_proxy = 0.5 * out.min_non_neighbor_dist;
    return out;
}

FilamentEnergyResult filament_energy_from_fseries(const std::string& path, const FilamentEnergyParams& p) {
    auto pts = sample_curve_centered(path, p.nsamples);

    const size_t N = pts.size();
    double L = 0.0, kappa_max = 0.0, kappa_mean = 0.0, bend_energy = 0.0;
    curve_metrics_from_points(pts, L, kappa_max, kappa_mean, bend_energy);
    const double ds = (N>0) ? (L / static_cast<double>(N)) : 0.0;
    const double dmin = min_non_neighbor_distance(pts, std::max(1, p.skip_neighbors_base));
    const double rproxy = 0.5 * dmin;

    std::vector<sst::Vec3> t(N);
    for (size_t i=0;i<N;++i) {
        auto d = sst::diff(pts[(i+1)%N], pts[i]);
        double n = sst::norm(d);
        if (n<=0) t[i] = {0,0,0};
        else t[i] = {d[0]/n, d[1]/n, d[2]/n};
    }

    int m_loc = 0;
    if (p.s_cut_local > 0.0 && ds > 0.0) {
        m_loc = static_cast<int>(std::ceil(p.s_cut_local / ds));
    }
    if (m_loc < p.skip_neighbors_base) m_loc = p.skip_neighbors_base;

    double E_nonlocal = 0.0;
    if (p.include_nonlocal && N>1) {
        const double pref = p.rho_outer * p.Gamma * p.Gamma / (8.0 * M_PI);
        double sum = 0.0;
        for (size_t i=0;i<N;++i) {
            for (size_t j=0;j<N;++j) {
                long ad = std::labs(static_cast<long>(j) - static_cast<long>(i));
                long cd = std::min<long>(ad, static_cast<long>(N) - ad);
                if (cd <= m_loc) continue;
                auto rij = sst::diff(pts[j], pts[i]);
                double dist = sst::norm(rij);
                if (p.delta > 0.0 && dist <= p.delta) continue;
                if (dist <= 0) continue;
                double dot_tt = sst::dot(t[i], t[j]);
                sum += (dot_tt / dist) * ds * ds;
            }
        }
        E_nonlocal = pref * sum;
    }

    double E_local_match = 0.0;
    if (p.include_local_match && p.s_cut_local > 0.0 && p.a_core > 0.0) {
        const double pref = p.rho_local * p.Gamma * p.Gamma / (4.0 * M_PI);
        E_local_match = pref * L * (std::log(p.s_cut_local / p.a_core) + p.c_rankine_outer);
    }

    double E_core_int = 0.0;
    if (p.include_core_int) {
        E_core_int = p.rho_local * p.Gamma * p.Gamma / (16.0 * M_PI) * L;
    }

    FilamentEnergyResult out;
    out.path = path;
    out.L = L;
    out.ds_avg = ds;
    out.m_loc = m_loc;
    out.E_nonlocal = E_nonlocal;
    out.E_local_match = E_local_match;
    out.E_core_int = E_core_int;
    out.E_total = E_nonlocal + E_local_match + E_core_int;

    out.kappa_max = kappa_max;
    out.kappa_mean = kappa_mean;
    out.bend_energy = bend_energy;
    out.min_non_neighbor_dist = dmin;
    out.reach_proxy = rproxy;

    out.rho_outer = p.rho_outer;
    out.rho_local = p.rho_local;
    out.Gamma = p.Gamma;
    out.a_core = p.a_core;
    out.delta = p.delta;
    out.s_cut_local = p.s_cut_local;
    out.c_rankine_outer = p.c_rankine_outer;
    out.nsamples = p.nsamples;
    return out;
}

std::vector<HelicityResult> batch_helicity_from_dir(
    const std::string& root_dir,
    int grid_size,
    double spacing,
    int interior_margin,
    int nsamples,
    bool recurse
) {
    std::vector<HelicityResult> out;
    fs::path root(root_dir);
    if (!fs::exists(root)) throw std::runtime_error("directory does not exist: " + root_dir);

    if (recurse) {
        for (const auto& entry : fs::recursive_directory_iterator(root)) {
            if (!entry.is_regular_file()) continue;
            if (entry.path().extension() != ".fseries") continue;
            out.push_back(helicity_from_fseries(entry.path().string(), grid_size, spacing, interior_margin, nsamples));
        }
    } else {
        for (const auto& entry : fs::directory_iterator(root)) {
            if (!entry.is_regular_file()) continue;
            if (entry.path().extension() != ".fseries") continue;
            out.push_back(helicity_from_fseries(entry.path().string(), grid_size, spacing, interior_margin, nsamples));
        }
    }
    std::sort(out.begin(), out.end(), [](const HelicityResult& a, const HelicityResult& b) {
        return a.path < b.path;
    });
    return out;
}

std::map<std::string, double> compare_fseries_files(
    const std::string& path_a,
    const std::string& path_b,
    int nsamples,
    int skip
) {
    auto ma = curve_metrics_from_fseries(path_a, nsamples, skip);
    auto mb = curve_metrics_from_fseries(path_b, nsamples, skip);

    auto pa = sample_curve_centered(path_a, nsamples);
    auto pb = sample_curve_centered(path_b, nsamples);
    size_t N = std::min(pa.size(), pb.size());
    double rms_point_delta = 0.0;
    if (N > 0) {
        double acc = 0.0;
        for (size_t i = 0; i < N; ++i) {
            double d = sst::norm(sst::diff(pa[i], pb[i]));
            acc += d * d;
        }
        rms_point_delta = std::sqrt(acc / static_cast<double>(N));
    }

    std::map<std::string, double> out;
    out["L_a"] = ma.L; out["L_b"] = mb.L; out["dL"] = mb.L - ma.L;
    out["kappa_max_a"] = ma.kappa_max; out["kappa_max_b"] = mb.kappa_max; out["dkappa_max"] = mb.kappa_max - ma.kappa_max;
    out["kappa_mean_a"] = ma.kappa_mean; out["kappa_mean_b"] = mb.kappa_mean; out["dkappa_mean"] = mb.kappa_mean - ma.kappa_mean;
    out["bend_energy_a"] = ma.bend_energy; out["bend_energy_b"] = mb.bend_energy; out["dbend_energy"] = mb.bend_energy - ma.bend_energy;
    out["reach_proxy_a"] = ma.reach_proxy; out["reach_proxy_b"] = mb.reach_proxy; out["dreach_proxy"] = mb.reach_proxy - ma.reach_proxy;
    out["rms_point_delta"] = rms_point_delta;
    return out;
}

} // namespace sstext
