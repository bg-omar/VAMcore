// node_field_kernels.cpp - Node.js bindings for FieldKernels (stub - to be implemented)
#include <napi.h>
#include "../field_kernels.h"

void bind_field_kernels(Napi::Env env, Napi::Object exports) {
    // TODO: Implement FieldKernels bindings
    // This is a placeholder to allow the module to compile
    exports.Set("fieldKernelsAvailable", Napi::Boolean::New(env, false));
}

