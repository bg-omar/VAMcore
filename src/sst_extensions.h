#ifndef SWIRL_STRING_CORE_SST_EXTENSIONS_H
#define SWIRL_STRING_CORE_SST_EXTENSIONS_H

#pragma once
#include <map>
#include <optional>
#include <string>
#include <vector>

#include "../include/vec3_utils.h"

namespace sst {

namespace sstext {

struct CanonicalizeResult {
    std::string path;
    int found_numeric_rows = 0;
    bool changed = false;
    std::string reason;
};

struct HelicityResult {
    std::string path;
    double a_mu = 0.0;
    double Hc = 0.0;
    double Hm = 0.0;

    double L = 0.0;
    double kappa_max = 0.0;
    double kappa_mean = 0.0;
    double bend_energy = 0.0;
    double min_non_neighbor_dist = 0.0;
    double reach_proxy = 0.0;
    int nsamples = 0;
};

struct FilamentEnergyParams {
    double rho_outer = 7.0e-7;
    double rho_local = 7.0e-7;
    double Gamma = 1.0;
    double a_core = 1.0;
    double delta = 0.0;
    double s_cut_local = 0.0;
    bool include_nonlocal = true;
    bool include_local_match = true;
    bool include_core_int = true;
    double c_rankine_outer = 0.0;
    int nsamples = 1024;
    int skip_neighbors_base = 1;
};

struct FilamentEnergyResult {
    std::string path;
    double L = 0.0;
    double ds_avg = 0.0;
    int m_loc = 0;
    double E_nonlocal = 0.0;
    double E_local_match = 0.0;
    double E_core_int = 0.0;
    double E_total = 0.0;

    double kappa_max = 0.0;
    double kappa_mean = 0.0;
    double bend_energy = 0.0;
    double min_non_neighbor_dist = 0.0;
    double reach_proxy = 0.0;

    double rho_outer = 0.0;
    double rho_local = 0.0;
    double Gamma = 0.0;
    double a_core = 0.0;
    double delta = 0.0;
    double s_cut_local = 0.0;
    double c_rankine_outer = 0.0;
    int nsamples = 0;
};

std::optional<std::vector<double>> parse_floats_line(const std::string& line);
bool is_comment_or_blank(const std::string& s);

CanonicalizeResult canonicalize_fseries_file_inplace(const std::string& path);

HelicityResult helicity_from_fseries(
    const std::string& path,
    int grid_size,
    double spacing,
    int interior_margin,
    int nsamples
);

std::vector<sst::Vec3> sample_curve_centered(const std::string& path, int nsamples);
double curve_length(const std::vector<sst::Vec3>& pts);
double min_non_neighbor_distance(const std::vector<sst::Vec3>& pts, int skip);
double reach_proxy(const std::vector<sst::Vec3>& pts, int skip);
void curve_metrics_from_points(
    const std::vector<sst::Vec3>& pts,
    double& L,
    double& kappa_max,
    double& kappa_mean,
    double& bend_energy
);

FilamentEnergyResult curve_metrics_from_fseries(
    const std::string& path,
    int nsamples,
    int skip
);

FilamentEnergyResult filament_energy_from_fseries(
    const std::string& path,
    const FilamentEnergyParams& p
);

std::vector<HelicityResult> batch_helicity_from_dir(
    const std::string& root_dir,
    int grid_size,
    double spacing,
    int interior_margin,
    int nsamples,
    bool recurse = false
);

std::map<std::string, double> compare_fseries_files(
    const std::string& path_a,
    const std::string& path_b,
    int nsamples,
    int skip
);

} // namespace sstext

} // namespace sst

#endif // SWIRL_STRING_CORE_SST_EXTENSIONS_H
