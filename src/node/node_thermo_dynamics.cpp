// node_thermo_dynamics.cpp - Node.js bindings for ThermoDynamics (stub - to be implemented)
#include <napi.h>
#include "../thermo_dynamics.h"

void bind_thermo_dynamics(Napi::Env env, Napi::Object exports) {
    // TODO: Implement ThermoDynamics bindings
    exports.Set("thermoDynamicsAvailable", Napi::Boolean::New(env, false));
}

