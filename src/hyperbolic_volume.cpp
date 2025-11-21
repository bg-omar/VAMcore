//
// Created by mr on 8/21/2025.
//

// ./src/hyperbolic_volume.cpp
#include "hyperbolic_volume.h"
#include <stdexcept>

namespace sst {

// Placeholder to keep translation units happy when SST_ENABLE_HYPVOL is OFF.
// The actual callable is provided in py_hyperbolic_volume.cpp (delegates to Python).
double hyperbolic_volume_from_pd(const PD&){ return 0.0; }

} // namespace sst