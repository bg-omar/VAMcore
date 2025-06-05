//
// Created by mr on 3/22/2025.
//

#include "knot_dynamics.h"
// src/knot_dynamics.cpp
#include <cmath>

namespace vam {
	double compute_writhe(const std::vector<Vec3>& X) {
		double W = 0.0;
		size_t N = X.size();
		for (size_t i = 0; i < N - 1; ++i) {
			for (size_t j = i + 1; j < N - 1; ++j) {
				Vec3 r = diff(X[i], X[j]);
				double r_norm = norm(r);
				if (r_norm < 1e-6) continue;
				Vec3 t1 = diff(X[i+1], X[i]);
				Vec3 t2 = diff(X[j+1], X[j]);
				W += dot(cross(t1, t2), r) / (r_norm * r_norm * r_norm);
			}
		}
		return W / (2.0 * M_PI);
	}

	int compute_linking_number(const std::vector<Vec3>& X, const std::vector<Vec3>& Y) {
		double Lk = 0.0;
		size_t N = X.size(), M = Y.size();
		for (size_t i = 0; i < N - 1; ++i) {
			Vec3 xi = X[i];
			Vec3 dx = diff(X[i+1], xi);
			for (size_t j = 0; j < M - 1; ++j) {
				Vec3 yj = Y[j];
				Vec3 dy = diff(Y[j+1], yj);
				Vec3 r = diff(xi, yj);
				double r_norm = norm(r);
				if (r_norm < 1e-6) continue;
				Lk += dot(cross(dx, dy), r) / (r_norm * r_norm * r_norm);
			}
		}
		return static_cast<int>(std::round(Lk / (4.0 * M_PI)));
	}

	double compute_twist(const std::vector<Vec3>& T, const std::vector<Vec3>& B) {
		double Tw = 0.0;
		size_t N = T.size();
		for (size_t i = 1; i < N - 1; ++i) {
			Vec3 dB = diff(B[i+1], B[i-1]);
			Vec3 dB_ds = {dB[0]/2.0, dB[1]/2.0, dB[2]/2.0};
			Tw += dot(cross(T[i], dB_ds), B[i]);
		}
		return Tw / (2.0 * M_PI);
	}

	double compute_centerline_helicity(const std::vector<Vec3>& curve,
									   const std::vector<Vec3>& tangent) {
		return compute_writhe(curve); // Simplified: H_cl ~ Wr for single loop
	}

	std::vector<std::pair<int, int>> detect_reconnection_candidates(
			const std::vector<Vec3>& curve, double threshold) {

		std::vector<std::pair<int, int>> candidates;
		size_t N = curve.size();
		for (size_t i = 0; i < N; ++i) {
			for (size_t j = i + 5; j < N; ++j) { // Skip close neighbors
				Vec3 d = diff(curve[i], curve[j]);
				if (norm(d) < threshold) {
					candidates.emplace_back(i, j);
				}
			}
		}
		return candidates;
	}

} // namespace vam