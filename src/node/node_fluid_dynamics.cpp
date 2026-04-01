// node_fluid_dynamics.cpp - Node.js bindings for FluidDynamics
#include <napi.h>
#include "../fluid_dynamics.h"
#include "node_utils.h"

using namespace sst;

void bind_fluid_dynamics(Napi::Env env, Napi::Object exports) {
    // compute_pressure_field
    exports.Set("computePressureField", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: velocity_magnitude, rho_ae, P_infinity");
        }
        std::vector<double> velocity_magnitude = js_array_to_double_vector(info[0].As<Napi::Array>());
        double rho_ae = info[1].As<Napi::Number>().DoubleValue();
        double P_infinity = info[2].As<Napi::Number>().DoubleValue();
        std::vector<double> result = FluidDynamics::compute_pressure_field(velocity_magnitude, rho_ae, P_infinity);
        return double_vector_to_js_array(env, result);
    }, "computePressureField"));
    
    // compute_velocity_magnitude
    exports.Set("computeVelocityMagnitude", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) {
            throw Napi::Error::New(env, "Expected 1 argument: velocity");
        }
        std::vector<Vec3> velocity;
        if (info[0].IsArray()) {
            velocity = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            velocity = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "velocity must be array or Float64Array");
        }
        std::vector<double> result = FluidDynamics::compute_velocity_magnitude(velocity);
        return double_vector_to_js_array(env, result);
    }, "computeVelocityMagnitude"));
    
    // evolve_positions_euler
    exports.Set("evolvePositionsEuler", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: positions, velocity, dt");
        }
        std::vector<Vec3> positions;
        if (info[0].IsArray()) {
            positions = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            positions = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "positions must be array or Float64Array");
        }
        std::vector<Vec3> velocity;
        if (info[1].IsArray()) {
            velocity = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            velocity = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "velocity must be array or Float64Array");
        }
        double dt = info[2].As<Napi::Number>().DoubleValue();
        FluidDynamics::evolve_positions_euler(positions, velocity, dt);
        return vec3_list_to_js_typedarray(env, positions);
    }, "evolvePositionsEuler"));
    
    // compute_helicity (with volume element dV for discretized field)
    exports.Set("computeHelicityField", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: velocity, vorticity, dV");
        }
        std::vector<Vec3> velocity, vorticity;
        if (info[0].IsArray()) {
            velocity = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            velocity = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "velocity must be array or Float64Array");
        }
        if (info[1].IsArray()) {
            vorticity = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            vorticity = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "vorticity must be array or Float64Array");
        }
        double dV = info[2].As<Napi::Number>().DoubleValue();
        double result = FluidDynamics::compute_helicity(velocity, vorticity, dV);
        return Napi::Number::New(env, result);
    }, "computeHelicityField"));
    
    // Additional utility functions
    exports.Set("swirlClockRate", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            throw Napi::Error::New(env, "Expected 2 arguments: dv_dx, du_dy");
        }
        double dv_dx = info[0].As<Napi::Number>().DoubleValue();
        double du_dy = info[1].As<Napi::Number>().DoubleValue();
        return Napi::Number::New(env, FluidDynamics::swirl_clock_rate(dv_dx, du_dy));
    }, "swirlClockRate"));
    
    exports.Set("computeKineticEnergy", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            throw Napi::Error::New(env, "Expected 2 arguments: velocity, rho_ae");
        }
        std::vector<Vec3> velocity;
        if (info[0].IsArray()) {
            velocity = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            velocity = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "velocity must be array or Float64Array");
        }
        double rho_ae = info[1].As<Napi::Number>().DoubleValue();
        return Napi::Number::New(env, FluidDynamics::compute_kinetic_energy(velocity, rho_ae));
    }, "computeKineticEnergy"));
}

