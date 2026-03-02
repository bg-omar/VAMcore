// node_biot_savart.cpp - Node.js bindings for BiotSavart
#include <napi.h>
#include "node_utils.h"
#include "../biot_savart.h"

using namespace sst;

// Forward declarations
void bind_biot_savart(Napi::Env env, Napi::Object exports);

void bind_biot_savart(Napi::Env env, Napi::Object exports) {
    // BiotSavart class with static methods
    Napi::Function biotSavartClass = Napi::Object::New(env).Get("constructor").As<Napi::Function>();
    
    // Static method: computeVelocity
    exports.Set("computeVelocity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            throw Napi::Error::New(env, "Expected 2 arguments: curve, grid_points");
        }
        
        std::vector<Vec3> curve, grid_points;
        
        // Handle curve - can be array of arrays or TypedArray
        if (info[0].IsArray()) {
            curve = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            curve = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "curve must be array or Float64Array");
        }
        
        // Handle grid_points
        if (info[1].IsArray()) {
            grid_points = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            grid_points = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "grid_points must be array or Float64Array");
        }
        
        std::vector<Vec3> result = BiotSavart::computeVelocity(curve, grid_points);
        return vec3_list_to_js_typedarray(env, result);
    }, "computeVelocity"));
    
    // Static method: computeVorticity
    exports.Set("computeVorticity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: velocity, shape, spacing");
        }
        
        std::vector<Vec3> velocity;
        if (info[0].IsArray()) {
            velocity = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            velocity = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "velocity must be array or Float64Array");
        }
        
        Napi::Array shapeArr = info[1].As<Napi::Array>();
        if (shapeArr.Length() != 3) {
            throw Napi::TypeError::New(env, "shape must be [x, y, z]");
        }
        std::array<int, 3> shape;
        shape[0] = shapeArr.Get((uint32_t)0u).As<Napi::Number>().Int32Value();
        shape[1] = shapeArr.Get((uint32_t)1u).As<Napi::Number>().Int32Value();
        shape[2] = shapeArr.Get((uint32_t)2u).As<Napi::Number>().Int32Value();

        double spacing = info[2].As<Napi::Number>().DoubleValue();
        
        std::vector<Vec3> result = BiotSavart::computeVorticity(velocity, shape, spacing);
        return vec3_list_to_js_typedarray(env, result);
    }, "computeVorticity"));
    
    // Static method: extractInterior
    exports.Set("extractInterior", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: field, shape, margin");
        }
        
        std::vector<Vec3> field;
        if (info[0].IsArray()) {
            field = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            field = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "field must be array or Float64Array");
        }
        
        Napi::Array shapeArr = info[1].As<Napi::Array>();
        if (shapeArr.Length() != 3) {
            throw Napi::TypeError::New(env, "shape must be [x, y, z]");
        }
        std::array<int, 3> shape;
        shape[0] = shapeArr.Get((uint32_t)0u).As<Napi::Number>().Int32Value();
        shape[1] = shapeArr.Get((uint32_t)1u).As<Napi::Number>().Int32Value();
        shape[2] = shapeArr.Get((uint32_t)2u).As<Napi::Number>().Int32Value();

        int margin = info[2].As<Napi::Number>().Int32Value();
        
        std::vector<Vec3> result = BiotSavart::extractInterior(field, shape, margin);
        return vec3_list_to_js_typedarray(env, result);
    }, "extractInterior"));
    
    // Static method: computeInvariants
    exports.Set("computeInvariants", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: v_sub, w_sub, r_sq");
        }
        
        std::vector<Vec3> v_sub, w_sub;
        if (info[0].IsArray()) {
            v_sub = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            v_sub = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "v_sub must be array or Float64Array");
        }
        
        if (info[1].IsArray()) {
            w_sub = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            w_sub = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "w_sub must be array or Float64Array");
        }
        
        std::vector<double> r_sq = js_array_to_double_vector(info[2].As<Napi::Array>());
        
        auto [h_charge, h_mass, a_mu] = BiotSavart::computeInvariants(v_sub, w_sub, r_sq);
        
        Napi::Object result = Napi::Object::New(env);
        result.Set("hCharge", Napi::Number::New(env, h_charge));
        result.Set("hMass", Napi::Number::New(env, h_mass));
        result.Set("aMu", Napi::Number::New(env, a_mu));
        return result;
    }, "computeInvariants"));
    
    // Function: biot_savart_velocity (single point)
    exports.Set("biotSavartVelocity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected at least 3 arguments: r, filament_points, tangent_vectors");
        }
        
        Vec3 r;
        if (info[0].IsArray()) {
            Napi::Array rArr = info[0].As<Napi::Array>();
            if (rArr.Length() != 3) {
                throw Napi::TypeError::New(env, "r must be [x, y, z]");
            }
            r[0] = rArr.Get((uint32_t)0u).As<Napi::Number>().DoubleValue();
            r[1] = rArr.Get((uint32_t)1u).As<Napi::Number>().DoubleValue();
            r[2] = rArr.Get((uint32_t)2u).As<Napi::Number>().DoubleValue();
        } else {
            throw Napi::TypeError::New(env, "r must be [x, y, z]");
        }
        
        std::vector<Vec3> filament_points, tangent_vectors;
        if (info[1].IsArray()) {
            filament_points = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            filament_points = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "filament_points must be array or Float64Array");
        }
        
        if (info[2].IsArray()) {
            tangent_vectors = js_array_to_vec3_list(info[2].As<Napi::Array>());
        } else if (info[2].IsTypedArray()) {
            tangent_vectors = js_typedarray_to_vec3_list(info[2].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "tangent_vectors must be array or Float64Array");
        }
        
        double circulation = 1.0;
        if (info.Length() > 3) {
            circulation = info[3].As<Napi::Number>().DoubleValue();
        }
        
        Vec3 result = BiotSavart::velocity(r, filament_points, tangent_vectors, circulation);
        
        Napi::Array resultArr = Napi::Array::New(env, 3);
        resultArr.Set((uint32_t)0u, Napi::Number::New(env, result[0]));
        resultArr.Set((uint32_t)1u, Napi::Number::New(env, result[1]));
        resultArr.Set((uint32_t)2u, Napi::Number::New(env, result[2]));
        return resultArr;
    }, "biotSavartVelocity"));
    
    // Function: biot_savart_velocity_grid (grid-based)
    exports.Set("biotSavartVelocityGrid", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            throw Napi::Error::New(env, "Expected 2 arguments: polyline, grid");
        }
        
        std::vector<Vec3> polyline, grid;
        if (info[0].IsArray()) {
            polyline = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            polyline = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "polyline must be array or Float64Array");
        }
        
        if (info[1].IsArray()) {
            grid = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            grid = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "grid must be array or Float64Array");
        }
        
        std::vector<Vec3> result = BiotSavart::computeVelocity(polyline, grid);
        return vec3_list_to_js_typedarray(env, result);
    }, "biotSavartVelocityGrid"));
}