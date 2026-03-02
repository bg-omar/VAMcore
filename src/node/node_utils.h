// node_utils.h - Utility functions for Node.js bindings
#ifndef NODE_UTILS_H
#define NODE_UTILS_H

#include <napi.h>
#include <vector>
#include <array>
#include "../../include/vec3_utils.h"

namespace sst {
    // Vec3 is defined in vec3_utils.h
}

// Convert JavaScript array of [x, y, z] arrays to std::vector<Vec3>
static std::vector<sst::Vec3> js_array_to_vec3_list(const Napi::Array& arr) {
    std::vector<sst::Vec3> result;
    for (uint32_t i = 0; i < arr.Length(); i++) {
        // Use Get() instead of operator[] to avoid ambiguity with node-addon-api v7
        Napi::Value val = arr.Get(i);
        if (!val.IsArray()) {
            throw Napi::TypeError::New(arr.Env(), "Expected array of [x, y, z] arrays");
        }
        Napi::Array vec = val.As<Napi::Array>();
        if (vec.Length() != 3) {
            throw Napi::TypeError::New(arr.Env(), "Each vector must have 3 elements [x, y, z]");
        }
        sst::Vec3 v;
        v[0] = vec.Get((uint32_t)0u).As<Napi::Number>().DoubleValue();
        v[1] = vec.Get((uint32_t)1u).As<Napi::Number>().DoubleValue();
        v[2] = vec.Get((uint32_t)2u).As<Napi::Number>().DoubleValue();
        result.push_back(v);
    }
    return result;
}

// Convert JavaScript TypedArray (Float64Array) with shape [N, 3] to std::vector<Vec3>
static std::vector<sst::Vec3> js_typedarray_to_vec3_list(const Napi::TypedArray& arr) {
    if (arr.TypedArrayType() != napi_float64_array) {
        throw Napi::TypeError::New(arr.Env(), "Expected Float64Array");
    }
    Napi::ArrayBuffer buffer = arr.ArrayBuffer();
    double* data = static_cast<double*>(buffer.Data());
    size_t length = arr.ElementLength();
    
    if (length % 3 != 0) {
        throw Napi::TypeError::New(arr.Env(), "Array length must be multiple of 3");
    }
    
    std::vector<sst::Vec3> result;
    size_t count = length / 3;
    for (size_t i = 0; i < count; i++) {
        sst::Vec3 v;
        v[0] = data[i * 3];
        v[1] = data[i * 3 + 1];
        v[2] = data[i * 3 + 2];
        result.push_back(v);
    }
    return result;
}

// Convert std::vector<Vec3> to JavaScript array
static Napi::Array vec3_list_to_js_array(Napi::Env env, const std::vector<sst::Vec3>& vecs) {
    Napi::Array result = Napi::Array::New(env, vecs.size());
    for (size_t i = 0; i < vecs.size(); i++) {
        Napi::Array vec = Napi::Array::New(env, 3);
        vec.Set((uint32_t)0u, Napi::Number::New(env, vecs[i][0]));
        vec.Set((uint32_t)1u, Napi::Number::New(env, vecs[i][1]));
        vec.Set((uint32_t)2u, Napi::Number::New(env, vecs[i][2]));
        result.Set((uint32_t)i, vec);
    }
    return result;
}

// Convert std::vector<Vec3> to JavaScript Float64Array (flat [x1, y1, z1, x2, y2, z2, ...])
static Napi::TypedArray vec3_list_to_js_typedarray(Napi::Env env, const std::vector<sst::Vec3>& vecs) {
    size_t length = vecs.size() * 3;
    Napi::ArrayBuffer buffer = Napi::ArrayBuffer::New(env, length * sizeof(double));
    double* data = static_cast<double*>(buffer.Data());
    
    for (size_t i = 0; i < vecs.size(); i++) {
        data[i * 3] = vecs[i][0];
        data[i * 3 + 1] = vecs[i][1];
        data[i * 3 + 2] = vecs[i][2];
    }
    
    return Napi::Float64Array::New(env, length, buffer, 0);
}

// Convert JavaScript array to std::vector<double>
static std::vector<double> js_array_to_double_vector(const Napi::Array& arr) {
    std::vector<double> result;
    for (uint32_t i = 0; i < arr.Length(); i++) {
        Napi::Value v = arr.Get(i);
        result.push_back(v.As<Napi::Number>().DoubleValue());
    }
    return result;
}

// Convert std::vector<double> to JavaScript array
static Napi::Array double_vector_to_js_array(Napi::Env env, const std::vector<double>& vec) {
    Napi::Array result = Napi::Array::New(env, vec.size());
    for (size_t i = 0; i < vec.size(); i++) {
        result.Set((uint32_t)i, Napi::Number::New(env, vec[i]));
    }
    return result;
}

#endif // NODE_UTILS_H