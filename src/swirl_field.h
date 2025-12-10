// swirl_field.h
#ifndef SWIRL_STRING_CORE_SWIRL_FIELD_H
#define SWIRL_STRING_CORE_SWIRL_FIELD_H

#include <vector>
#include <array>

namespace sst {
	using Vec2f = std::array<float, 2>;

	std::vector<Vec2f> compute_swirl_field(int res, float time);
}

#endif  // SWIRL_STRING_CORE_SWIRL_FIELD_H