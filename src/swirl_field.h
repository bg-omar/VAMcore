// swirl_field.h
#ifndef VAMCORE_SWIRL_FIELD_H
#define VAMCORE_SWIRL_FIELD_H

#include <vector>
#include <array>

namespace vam {
	using Vec2f = std::array<float, 2>;

	std::vector<Vec2f> compute_swirl_field(int res, float time);
}

#endif  // VAMCORE_SWIRL_FIELD_H
