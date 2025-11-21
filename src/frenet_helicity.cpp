//
// Created by mr on 3/22/2025.
//

// src/frenet_helicity.cpp
#include "frenet_helicity.h"
#include <cmath>
#include <numeric>

namespace sst {

	Vec3 normalize(const Vec3& v) {
		double norm = std::sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
		return {v[0]/norm, v[1]/norm, v[2]/norm};
	}

// Define subtraction operator for Vec3
	auto operator-(const Vec3& a, const Vec3& b) -> Vec3 {
		return diff(a, b);
	}

// 1. Compute TNB Frenet frame vectors
        void FrenetHelicity::compute_frenet_frames(const std::vector<Vec3>& X,
                                                           std::vector<Vec3>& T,
                                                           std::vector<Vec3>& N,
                                                           std::vector<Vec3>& B) {
		size_t n = X.size();
		T.resize(n);
		N.resize(n);
		B.resize(n);

		for (size_t i = 1; i < n - 1; ++i) {
			Vec3 d1 = diff(X[i+1], X[i-1]);
			Vec3 d2 = diff(X[i+1], X[i]) - diff(X[i], X[i-1]);
			Vec3 tangent = normalize(d1);
			Vec3 normal = normalize(d2);
			Vec3 binormal = cross(tangent, normal);

			T[i] = tangent;
			N[i] = normal;
			B[i] = binormal;
		}
		T[0] = T[1]; N[0] = N[1]; B[0] = B[1];
		T[n-1] = T[n-2]; N[n-1] = N[n-2]; B[n-1] = B[n-2];
	}

// 2. Compute curvature and torsion
        void FrenetHelicity::compute_curvature_torsion(const std::vector<Vec3>& T,
                                                                   const std::vector<Vec3>& N,
                                                                   std::vector<double>& curvature,
                                                                   std::vector<double>& torsion) {
		size_t n = T.size();
		curvature.resize(n);
		torsion.resize(n);
		for (size_t i = 1; i < n - 1; ++i) {
			Vec3 dT = diff(T[i+1], T[i-1]);
			Vec3 dN = diff(N[i+1], N[i-1]);
			curvature[i] = 0.5 * std::sqrt(dT[0]*dT[0] + dT[1]*dT[1] + dT[2]*dT[2]);
			Vec3 B = cross(T[i], N[i]);
			torsion[i] = 0.5 * (dN[0]*B[0] + dN[1]*B[1] + dN[2]*B[2]);
		}
		curvature[0] = curvature[1];
		curvature[n-1] = curvature[n-2];
		torsion[0] = torsion[1];
		torsion[n-1] = torsion[n-2];
	}

// 3. Compute helicity
        float FrenetHelicity::compute_helicity(const std::vector<Vec3>& velocity,
                                                   const std::vector<Vec3>& vorticity) {
		size_t n = velocity.size();
		float sum = 0.0f;
		for (size_t i = 0; i < n; ++i) {
			sum += static_cast<float>(velocity[i][0]*vorticity[i][0] +
									  velocity[i][1]*vorticity[i][1] +
									  velocity[i][2]*vorticity[i][2]);
		}
		return sum / static_cast<float>(n);
	}
// RK4 integration of position updates
        std::vector<Vec3> FrenetHelicity::rk4_integrate(const std::vector<Vec3>& positions,
									const std::vector<Vec3>& tangents,
									double dt,
									double gamma) {
		std::vector<Vec3> result = positions;
		size_t n = positions.size();
		for (size_t i = 0; i < n; ++i) {
			result[i][0] += dt * gamma * tangents[i][0];
			result[i][1] += dt * gamma * tangents[i][1];
			result[i][2] += dt * gamma * tangents[i][2];
		}
		return result;
	}

        std::vector<Vec3> FrenetHelicity::evolve_vortex_knot(const std::vector<Vec3>& positions,
										 const std::vector<Vec3>& tangents,
										 double dt,
										 double gamma) {
		return rk4_integrate(positions, tangents, dt, gamma);
	}
} // namespace sst