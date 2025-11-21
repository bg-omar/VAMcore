// swirl_field.cpp
#include "swirl_field.h"
#include <cmath>

namespace sst {

		std::vector<Vec2f> compute_swirl_field(int res, float time) {
		std::vector<Vec2f> field(res * res);

		for (int i = 0; i < res; ++i) {
			for (int j = 0; j < res; ++j) {
				float u = static_cast<float>(i) / res - 0.5f;
				float v = static_cast<float>(j) / res - 0.5f;

				float r2 = u * u + v * v + 1e-5f;
				float r = std::sqrt(r2);

				Vec2f swirl = { -v * (0.25f / r), u * (0.25f / r) };
				Vec2f inward = { -u * (0.1f / r2), -v * (0.1f / r2) };
				float pulse = 0.03f * std::sin(10.0f * r - 6.0f * time);

				field[i * res + j][0] = (swirl[0] + inward[0]) * (1.0f + pulse);
				field[i * res + j][1] = (swirl[1] + inward[1]) * (1.0f + pulse);
			}
		}

		return field;
	}

}