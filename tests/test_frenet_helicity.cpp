//
// Created by mr on 3/22/2025.
//
// tests/test_frenet_helicity.cpp
#include "../src/frenet_helicity.h"
#include <iostream>
#include <cmath>

int main() {
	using namespace sst;

	std::vector<Vec3> X = {
			{1.0, 0.0, 0.0},
			{0.0, 1.0, 0.0},
			{-1.0, 0.0, 0.0},
			{0.0, -1.0, 0.0},
			{1.0, 0.0, 0.0}
	};

	std::vector<Vec3> T, N, B;
	compute_frenet_frames(X, T, N, B);

	std::vector<double> kappa, tau;
	compute_curvature_torsion(T, N, kappa, tau);

	std::cout << "Curvature:\n";
	for (double k : kappa) std::cout << k << " ";
	std::cout << "\nTorsion:\n";
	for (double t : tau) std::cout << t << " ";

	std::vector<Vec3> v = T;
	std::vector<Vec3> w = T;
	float H = compute_helicity(v, w);
	std::cout << "\nHelicity: " << H << std::endl;
	return 0;
}