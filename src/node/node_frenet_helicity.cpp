// node_frenet_helicity.cpp - Node.js bindings for FrenetHelicity
#include <napi.h>
#include "../frenet_helicity.h"
#include "node_utils.h"

using namespace sst;

void bind_frenet_helicity(Napi::Env env, Napi::Object exports) {
    // compute_frenet_frames
    exports.Set("computeFrenetFrames", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) {
            throw Napi::Error::New(env, "Expected 1 argument: X");
        }
        std::vector<Vec3> X;
        if (info[0].IsArray()) {
            X = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            X = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "X must be array or Float64Array");
        }
        std::vector<Vec3> T, N, B;
        FrenetHelicity::compute_frenet_frames(X, T, N, B);
        Napi::Object result = Napi::Object::New(env);
        result.Set("T", vec3_list_to_js_typedarray(env, T));
        result.Set("N", vec3_list_to_js_typedarray(env, N));
        result.Set("B", vec3_list_to_js_typedarray(env, B));
        return result;
    }, "computeFrenetFrames"));
    
    // compute_curvature_torsion
    exports.Set("computeCurvatureTorsion", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            throw Napi::Error::New(env, "Expected 2 arguments: T, N");
        }
        std::vector<Vec3> T, N;
        if (info[0].IsArray()) {
            T = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            T = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "T must be array or Float64Array");
        }
        if (info[1].IsArray()) {
            N = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            N = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "N must be array or Float64Array");
        }
        std::vector<double> curvature, torsion;
        FrenetHelicity::compute_curvature_torsion(T, N, curvature, torsion);
        Napi::Object result = Napi::Object::New(env);
        result.Set("curvature", double_vector_to_js_array(env, curvature));
        result.Set("torsion", double_vector_to_js_array(env, torsion));
        return result;
    }, "computeCurvatureTorsion"));
    
    // compute_helicity
    exports.Set("computeHelicity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            throw Napi::Error::New(env, "Expected 2 arguments: velocity, vorticity");
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
        float result = FrenetHelicity::compute_helicity(velocity, vorticity);
        return Napi::Number::New(env, result);
    }, "computeHelicity"));
    
    // evolve_vortex_knot
    exports.Set("evolveVortexKnot", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: positions, tangents, dt");
        }
        std::vector<Vec3> positions, tangents;
        if (info[0].IsArray()) {
            positions = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            positions = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "positions must be array or Float64Array");
        }
        if (info[1].IsArray()) {
            tangents = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            tangents = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "tangents must be array or Float64Array");
        }
        double dt = info[2].As<Napi::Number>().DoubleValue();
        double gamma = 1.0;
        if (info.Length() > 3) {
            gamma = info[3].As<Napi::Number>().DoubleValue();
        }
        std::vector<Vec3> result = FrenetHelicity::evolve_vortex_knot(positions, tangents, dt, gamma);
        return vec3_list_to_js_typedarray(env, result);
    }, "evolveVortexKnot"));
    
    // rk4_integrate
    exports.Set("rk4Integrate", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: positions, tangents, dt");
        }
        std::vector<Vec3> positions, tangents;
        if (info[0].IsArray()) {
            positions = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            positions = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "positions must be array or Float64Array");
        }
        if (info[1].IsArray()) {
            tangents = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            tangents = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "tangents must be array or Float64Array");
        }
        double dt = info[2].As<Napi::Number>().DoubleValue();
        double gamma = 1.0;
        if (info.Length() > 3) {
            gamma = info[3].As<Napi::Number>().DoubleValue();
        }
        std::vector<Vec3> result = FrenetHelicity::rk4_integrate(positions, tangents, dt, gamma);
        return vec3_list_to_js_typedarray(env, result);
    }, "rk4Integrate"));
}

