cmake_minimum_required(VERSION 3.23)
project(sstcore LANGUAGES CXX)

# Ensure C++ compiler is set
if(NOT CMAKE_CXX_COMPILER)
    message(FATAL_ERROR "CMAKE_CXX_COMPILER is not set. Please specify a C++ compiler (e.g., by setting the CXX environment variable or using -DCMAKE_CXX_COMPILER=...).")
endif()

# === Python Executable Compatibility ===
# If Python3_EXECUTABLE is set but not Python_EXECUTABLE, map it
if(Python3_EXECUTABLE AND NOT Python_EXECUTABLE)
    set(Python_EXECUTABLE ${Python3_EXECUTABLE})
endif()

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Platform detection
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(IS_LINUX TRUE)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(IS_WINDOWS TRUE)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    set(IS_MACOS TRUE)
endif()

# Optimization flags for scientific calculation
if(MSVC)
    add_compile_options(/O2 /fp:fast)
else()
    add_compile_options(-O3 -march=native -ffast-math)
    # Linux-specific optimizations
    if(IS_LINUX)
        add_compile_options(-fPIC)  # Position-independent code for shared libraries
    endif()
endif()
# Use vendored pybind11 from extern/ directory
add_subdirectory(extern/pybind11)

# Core SST library sources
add_library(sstcore_lib STATIC
        src/biot_savart.cpp
        src/fluid_dynamics.cpp
        src/field_kernels.cpp
        src/frenet_helicity.cpp
        src/potential_timefield.cpp
        src/hyperbolic_volume.cpp
        src/knot_dynamics.cpp
        src/radiation_flow.cpp
        src/swirl_field.cpp
        src/thermo_dynamics.cpp
        src/time_evolution.cpp
        src/vortex_ring.cpp
        src/vorticity_dynamics.cpp
        src/sst_gravity.cpp
        src/sst_gravity.h
)

target_include_directories(sstcore_lib PUBLIC src)

# Python bindings
# pybind11 will automatically use .pyd on Windows and .so on Linux/Mac

# Main module: sstcore
pybind11_add_module(sstcore src_bindings/module_sst.cpp)
target_sources(sstcore PRIVATE
        src_bindings/py_biot_savart.cpp
        src_bindings/py_field_kernels.cpp
        src_bindings/py_field_ops.cpp
        src_bindings/py_fluid_dynamics.cpp
        src_bindings/py_knot.cpp
        src_bindings/py_frenet_helicity.cpp
        src_bindings/py_potential_timefield.cpp
        src_bindings/py_hyperbolic_volume.cpp
        src_bindings/py_radiation_flow.cpp
        src_bindings/py_swirl_field.cpp
        src_bindings/py_thermo_dynamics.cpp
        src_bindings/py_time_evolution.cpp
        src_bindings/py_vortex_ring.cpp
        src_bindings/py_vorticity_dynamics.cpp
        src_bindings/py_sst_gravity.cpp)

target_link_libraries(sstcore PRIVATE sstcore_lib)
target_include_directories(sstcore PRIVATE extern/pybind11/include)

# Backwards compatibility module: sstbindings
pybind11_add_module(sstbindings src_bindings/module_sstbindings.cpp)
target_sources(sstbindings PRIVATE
        src_bindings/py_biot_savart.cpp
        src_bindings/py_field_kernels.cpp
        src_bindings/py_field_ops.cpp
        src_bindings/py_fluid_dynamics.cpp
        src_bindings/py_knot.cpp
        src_bindings/py_frenet_helicity.cpp
        src_bindings/py_potential_timefield.cpp
        src_bindings/py_hyperbolic_volume.cpp
        src_bindings/py_radiation_flow.cpp
        src_bindings/py_swirl_field.cpp
        src_bindings/py_thermo_dynamics.cpp
        src_bindings/py_time_evolution.cpp
        src_bindings/py_vortex_ring.cpp
        src_bindings/py_vorticity_dynamics.cpp
        src_bindings/py_sst_gravity.cpp)

target_link_libraries(sstbindings PRIVATE sstcore_lib)
target_include_directories(sstbindings PRIVATE extern/pybind11/include)

# Linux-specific linker settings
if(IS_LINUX)
    # Ensure proper linking on Linux
    set_target_properties(sstcore PROPERTIES
        LINK_FLAGS "-Wl,--no-undefined"
    )
    set_target_properties(sstbindings PROPERTIES
        LINK_FLAGS "-Wl,--no-undefined"
    )
endif()
add_executable(test_frenet tests/test_frenet_helicity.cpp)
target_link_libraries(test_frenet PRIVATE sstcore_lib)


# Install targets
install(TARGETS sstcore_lib sstcore sstbindings
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin)
install(DIRECTORY include/ DESTINATION include)

# === ✅ AUTO-COPY PYBIND MODULE TO PROJECT ROOT ===
# After sstcore is built, copy it to ${CMAKE_SOURCE_DIR}
# So you can easily import it from Python scripts in the root directory

add_custom_command(TARGET sstcore POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:sstcore>
        ${CMAKE_SOURCE_DIR}/$<TARGET_FILE_NAME:sstcore>
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:sstcore>
        ${CMAKE_SOURCE_DIR}/examples/$<TARGET_FILE_NAME:sstcore>
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:sstcore>
        ${CMAKE_SOURCE_DIR}/../SwirlStringTheory/SST_Mathematical_Proof_Python/$<TARGET_FILE_NAME:sstcore>
        COMMENT "Copied sstcore module to project root, examples/, and ../SwirlStringTheory/ for easy import"
)

# Also copy sstbindings for backwards compatibility
add_custom_command(TARGET sstbindings POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:sstbindings>
        ${CMAKE_SOURCE_DIR}/$<TARGET_FILE_NAME:sstbindings>
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:sstbindings>
        ${CMAKE_SOURCE_DIR}/examples/$<TARGET_FILE_NAME:sstbindings>
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:sstbindings>
        ${CMAKE_SOURCE_DIR}/../SwirlStringTheory/SST_Mathematical_Proof_Python/$<TARGET_FILE_NAME:sstbindings>
        COMMENT "Copied sstbindings module (backwards compatibility) to project root, examples/, and ../SwirlStringTheory/ for easy import"
)