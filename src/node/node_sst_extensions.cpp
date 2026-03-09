// node_vorticity_dynamics.cpp - Node.js bindings for VorticityDynamics (stub - to be implemented)
#include <napi.h>
#include "../vorticity_dynamics.h"

void bind_sst_extensions(Napi::Env env, Napi::Object exports) {
    // TODO: Implement VorticityDynamics bindings
    exports.Set("sstExtensionsAvailable", Napi::Boolean::New(env, false));
}