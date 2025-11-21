// swirl_field.h
#ifndef SSTCORE_SWIRL_FIELD_H
#define SSTCORE_SWIRL_FIELD_H

#include <vector>
#include <array>

namespace sst {
	using Vec2f = std::array<float, 2>;

	std::vector<Vec2f> compute_swirl_field(int res, float time);
}

#endif  // SSTCORE_SWIRL_FIELD_H