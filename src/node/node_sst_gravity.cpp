// node_sst_gravity.cpp - Node.js bindings for SSTGravity (stub - to be implemented)
#include <napi.h>
#include "../sst_gravity.h"

void bind_sst_gravity(Napi::Env env, Napi::Object exports) {
    // TODO: Implement SSTGravity bindings
    exports.Set("sstGravityAvailable", Napi::Boolean::New(env, false));
}

