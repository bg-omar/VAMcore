//
// Created by oscar on 2/26/2026.
//

#ifndef SWIRL_STRING_CORE_AB_INITIO_MASS_H
#define SWIRL_STRING_CORE_AB_INITIO_MASS_H

#pragma once
#include <cmath>
#include <cstddef>
#include <vector>
#include <string>
#include <array>
#include <functional>

namespace sst {
using Vec3 = std::array<double, 3>;

class ParticleEvaluator {
private:
  // --- SST Canon Invariants ---

  static constexpr double F_max = 29.053507;
  static constexpr double c_light = 299792458.0;
  static constexpr double r_c = 1.40897017e-15;
  static constexpr double v_swirl = 1.09384563e6;
  static constexpr double rho_core = 3.8934358266918687e18;
  static constexpr double rho_fluid = 6.87e-7;
  static constexpr double MeV_J_ = 1.602176634e-13;  // J/MeV

  bool extract_and_build_filament(const std::string& db_content, const std::string& ab_id, int resolution);

public:
  std::vector<std::vector<Vec3>> filaments;
  static void print_canonical_derivation();
  explicit ParticleEvaluator(const std::string& knot_ab_id, int resolution = 4000);
  // [NEW] The direct array constructor (Bypasses ideal.txt, takes Python arrays)
  explicit ParticleEvaluator(const std::vector<std::vector<Vec3>>& input_filaments);

  void relax_hamiltonian(int iterations, double timestep, std::function<void()> interrupt_callback = nullptr);

  // Existing API
  double get_dimless_ropelength(double stretch_lambda = 1.0) const;

  // ------------------------------------------------------------
  // NEW: True ab initio mass path (core-only baseline)
  // ------------------------------------------------------------
  // Returns physical filament arclength after relaxation [m].
  double get_physical_length_m() const;

  // Core kinetic energy using SST dense-core tube model [J]
  // E_core = \oint (1/2 rho_core v_swirl^2 * pi r_c^2) ds
  double compute_core_energy_J() const;

  // Tail energy placeholder [J].
  // Keep 0.0 for now until Biot-Savart volume integral is implemented.
  double compute_tail_energy_J(bool include_tail = false) const;

  // Total ab initio mass from energies [MeV/c^2 numeric value in MeV]
  // M = (E_core + E_tail)/c^2
  double get_mass_mev_ab_initio(bool include_tail = false) const;

  // Optional helper for transparency in logs/debugging
  double get_core_mass_mev_only() const;

  // ------------------------------------------------------------
  // NEW: practical tail-energy surrogate controls
  // ------------------------------------------------------------
  struct TailApproxConfig {
    bool enabled = false;
    int radial_samples = 8;           // shells outside core
    int azimuth_samples = 8;          // ring samples around local tangent
    double r_min_factor = 1.25;       // start at r = r_min_factor * r_c
    double r_max_factor = 8.0;        // truncate tail at r = r_max_factor * r_c
    double exclusion_ds_factor = 3.0; // exclude local segment neighborhood to avoid singularity
    bool use_log_shell_weight = false;// optional weighting mode
  };

  void set_tail_approx_config(const TailApproxConfig& cfg);
  TailApproxConfig get_tail_approx_config() const;
  double compute_tail_energy_surrogate_J() const;

  // ------------------------------------------------------------
  // Relativistic metrics (Helicity, Swirl-Clock time dilation)
  // ------------------------------------------------------------
  struct RelativisticMetrics {
    double helicity;
    std::vector<double> time_dilation_map;
    double core_time_dilation;
  };

  RelativisticMetrics compute_relativistic_metrics(double circulation = 9.683619203e-9) const;

private:
  TailApproxConfig tail_cfg_{};

  // Vector helpers for Biot–Savart surrogate
  static Vec3 v_add(const Vec3& a, const Vec3& b);
  static Vec3 v_sub(const Vec3& a, const Vec3& b);
  static Vec3 v_mul(const Vec3& a, double s);
  static double v_dot(const Vec3& a, const Vec3& b);
  static Vec3 v_cross(const Vec3& a, const Vec3& b);
  static double v_norm(const Vec3& a);
  static Vec3 v_unit(const Vec3& a);

  // Build local orthonormal frame (t,n,b) at polyline index i
  void local_frame_at_index(std::size_t f, std::size_t i,
                            Vec3& t_hat, Vec3& n_hat, Vec3& b_hat) const;

  // Return relaxed polyline in physical coordinates [m]
  std::vector<Vec3> get_relaxed_polyline_m() const;

  // Biot–Savart induced velocity surrogate at point p [m/s]
  // excluding local neighborhood around sample (f_center, i_center).
  Vec3 induced_velocity_bs_surrogate(const Vec3& p, std::size_t f_center,
                                     std::size_t i_center, double exclusion_len_m) const;
};
}

#endif // SWIRL_STRING_CORE_AB_INITIO_MASS_H