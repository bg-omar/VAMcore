// module_node.cpp - Main Node.js module entry point
#include <napi.h>

// Forward declarations
void bind_biot_savart(Napi::Env env, Napi::Object exports);
void bind_fluid_dynamics(Napi::Env env, Napi::Object exports);
void bind_field_kernels(Napi::Env env, Napi::Object exports);
void bind_field_ops(Napi::Env env, Napi::Object exports);
void bind_knot(Napi::Env env, Napi::Object exports);
void bind_frenet_helicity(Napi::Env env, Napi::Object exports);
void bind_timefield(Napi::Env env, Napi::Object exports);
void bind_hyperbolic_volume(Napi::Env env, Napi::Object exports);
void bind_radiation_flow(Napi::Env env, Napi::Object exports);
void bind_swirl_field(Napi::Env env, Napi::Object exports);
void bind_thermo_dynamics(Napi::Env env, Napi::Object exports);
void bind_time_evolution(Napi::Env env, Napi::Object exports);
void bind_vortex_ring(Napi::Env env, Napi::Object exports);
void bind_vorticity_dynamics(Napi::Env env, Napi::Object exports);
void bind_sst_gravity(Napi::Env env, Napi::Object exports);

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    exports.Set(Napi::String::New(env, "version"), Napi::String::New(env, "0.1.3"));
    
    // Bind all modules
    bind_biot_savart(env, exports);
    bind_fluid_dynamics(env, exports);
    bind_field_kernels(env, exports);
    bind_field_ops(env, exports);
    bind_knot(env, exports);
    bind_frenet_helicity(env, exports);
    bind_timefield(env, exports);
    bind_hyperbolic_volume(env, exports);
    bind_radiation_flow(env, exports);
    bind_swirl_field(env, exports);
    bind_thermo_dynamics(env, exports);
    bind_time_evolution(env, exports);
    bind_vortex_ring(env, exports);
    bind_vorticity_dynamics(env, exports);
    bind_sst_gravity(env, exports);
    
    return exports;
}

NODE_API_MODULE(swirl_string_core, Init)

