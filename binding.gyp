{
  "targets": [
    {
      "target_name": "swirl_string_core",
      "sources": [
        "src/node/module_node.cpp",
        "src/node/node_biot_savart.cpp",
        "src/node/node_field_kernels.cpp",
        "src/node/node_field_ops.cpp",
        "src/node/node_fluid_dynamics.cpp",
        "src/node/node_knot.cpp",
        "src/node/node_frenet_helicity.cpp",
        "src/node/node_potential_timefield.cpp",
        "src/node/node_hyperbolic_volume.cpp",
        "src/node/node_radiation_flow.cpp",
        "src/node/node_swirl_field.cpp",
        "src/node/node_thermo_dynamics.cpp",
        "src/node/node_time_evolution.cpp",
        "src/node/node_vortex_ring.cpp",
        "src/node/node_vorticity_dynamics.cpp",
        "src/node/node_sst_gravity.cpp",
        "src/biot_savart.cpp",
        "src/fluid_dynamics.cpp",
        "src/field_kernels.cpp",
        "src/frenet_helicity.cpp",
        "src/potential_timefield.cpp",
        "src/hyperbolic_volume.cpp",
        "src/knot_dynamics.cpp",
        "src/radiation_flow.cpp",
        "src/swirl_field.cpp",
        "src/thermo_dynamics.cpp",
        "src/time_evolution.cpp",
        "src/vortex_ring.cpp",
        "src/vorticity_dynamics.cpp",
        "src/sst_gravity.cpp",
        "build_node/generated/knot_files_embedded.cpp"
      ],
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")",
        "src",
        "include",
        "<(module_root_dir)/build_node/generated",
        "<(module_root_dir)/extern/pybind11/include"
      ],
      "defines": [
        "NAPI_DISABLE_CPP_EXCEPTIONS"
      ],
      "cflags!": [ "-fno-exceptions" ],
      "cflags_cc!": [ "-fno-exceptions" ],
      "conditions": [
        ["OS=='win'", {
          "defines": [ "_CRT_SECURE_NO_WARNINGS" ],
          "msvs_settings": {
            "VCCLCompilerTool": {
              "ExceptionHandling": 1,
              "AdditionalOptions": [ "/std:c++20" ]
            }
          }
        }],
        ["OS=='mac'", {
          "cflags_cc": [ "-std=c++20", "-O3" ],
          "xcode_settings": {
            "OTHER_CPPFLAGS": [ "-std=c++20", "-O3" ],
            "GCC_ENABLE_CPP_EXCEPTIONS": "YES"
          }
        }],
        ["OS=='linux'", {
          "cflags_cc": [ "-std=c++20", "-O3", "-fPIC" ],
          "ldflags": [ "-Wl,--no-undefined" ]
        }]
      ]
    }
  ]
}