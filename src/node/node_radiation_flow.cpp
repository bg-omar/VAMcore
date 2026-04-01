// node_radiation_flow.cpp - Node.js bindings for RadiationFlow (stub - to be implemented)
#include <napi.h>
#include "../radiation_flow.h"

void bind_radiation_flow(Napi::Env env, Napi::Object exports) {
    // TODO: Implement RadiationFlow bindings
    exports.Set("radiationFlowAvailable", Napi::Boolean::New(env, false));
}

