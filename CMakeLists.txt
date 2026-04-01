cmake_minimum_required(VERSION 3.23)
project(SSTcore LANGUAGES CXX)

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

# === Runtime resource directories ===
set(SST_RESOURCES_DIR "${CMAKE_CURRENT_SOURCE_DIR}/resources")
set(SST_KNOT_FSERIES_DIR "${SST_RESOURCES_DIR}/knot_fseries")
set(SST_KNOTS_FOURIER_DIR "${SST_RESOURCES_DIR}/Knots_FourierSeries")

# Optimization flags for scientific calculation
if(MSVC)
    # Only apply /O2 in Release mode (Debug uses /RTC1 which is incompatible)
    add_compile_options($<$<CONFIG:Release>:/O2> /fp:fast)
else()
    add_compile_options(-O3 -march=native -ffast-math)
    # Linux-specific optimizations
    if(IS_LINUX)
        add_compile_options(-fPIC)  # Position-independent code for shared libraries
    endif()
endif()
# Use vendored pybind11 from extern/ directory
add_subdirectory(extern/pybind11)

# Embed .fseries files into C++ source (must run before building)
# This generates knot_files_embedded.cpp and .h in the build directory
include(cmake/embed_knot_files.cmake)

# Mark the generated files as source files that need to be compiled
set_source_files_properties(${CMAKE_BINARY_DIR}/generated/knot_files_embedded.cpp PROPERTIES GENERATED TRUE)
set_source_files_properties(${CMAKE_BINARY_DIR}/generated/knot_files_embedded.h PROPERTIES GENERATED TRUE)

# Create a custom target to ensure knot files are generated
add_custom_target(knot_files_embedded ALL
    DEPENDS ${CMAKE_BINARY_DIR}/generated/knot_files_embedded.cpp
    ${CMAKE_BINARY_DIR}/generated/knot_files_embedded.h
    COMMENT "Ensuring knot files are embedded"
)

# Core SST library sources
add_library(sstcore_lib STATIC
        src/ab_initio_mass.cpp
        src/trefoil_closure_kernels.cpp
        src/biot_savart.cpp
        src/fluid_dynamics.cpp
        src/field_kernels.cpp
        src/frenet_helicity.cpp
        src/potential_timefield.cpp
        src/magnus_integrator.cpp
        src/hyperbolic_volume.cpp
        src/knot_dynamics.cpp
        src/radiation_flow.cpp
        src/swirl_field.cpp
        src/thermo_dynamics.cpp
        src/time_evolution.cpp
        src/vortex_ring.cpp
        src/vorticity_dynamics.cpp
        src/sst_gravity.cpp
        src/sst_extensions.cpp
        src/sst_integrator.cpp
        ${CMAKE_BINARY_DIR}/generated/knot_files_embedded.cpp
)

target_include_directories(sstcore_lib PUBLIC 
        src
        ${CMAKE_BINARY_DIR}/generated
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)
target_compile_definitions(sstcore_lib PRIVATE
    SST_DEFAULT_RESOURCE_SUBDIR="share/sstcore/resources"
    SST_DEFAULT_KNOT_FSERIES_SUBDIR="share/sstcore/resources/knot_fseries"
    SST_DEFAULT_KNOTS_FOURIER_SUBDIR="share/sstcore/resources/Knots_FourierSeries"
)

# Python bindings
# pybind11 will automatically use .pyd on Windows and .so on Linux/Mac

# Main module: sstcore
pybind11_add_module(sstcore src/module_sst.cpp)
target_sources(sstcore PRIVATE
        src/ab_initio_mass_py.cpp
        src/biot_savart_py.cpp
        src/field_kernels_py.cpp
        src/field_ops_py.cpp
        src/fluid_dynamics_py.cpp
        src/magnus_integrator_py.cpp
        src/knot_dynamics_py.cpp
        src/frenet_helicity_py.cpp
        src/potential_timefield_py.cpp
        src/hyperbolic_volume_py.cpp
        src/radiation_flow_py.cpp
        src/swirl_field_py.cpp
        src/thermo_dynamics_py.cpp
        src/time_evolution_py.cpp
        src/vortex_ring_py.cpp
        src/vorticity_dynamics_py.cpp
        src/sst_gravity_py.cpp
        src/sst_extensions_py.cpp
        src/sst_integrator_py.cpp)

target_link_libraries(sstcore PRIVATE sstcore_lib)
target_include_directories(sstcore PRIVATE extern/pybind11/include)
target_compile_definitions(sstcore PRIVATE
    SST_DEFAULT_RESOURCE_SUBDIR="share/sstcore/resources"
    SST_DEFAULT_KNOT_FSERIES_SUBDIR="share/sstcore/resources/knot_fseries"
    SST_DEFAULT_KNOTS_FOURIER_SUBDIR="share/sstcore/resources/Knots_FourierSeries"
)

# Backwards compatibility module: sstbindings
pybind11_add_module(sstbindings src/module_sstbindings.cpp)
target_sources(sstbindings PRIVATE
        src/ab_initio_mass_py.cpp
        src/biot_savart_py.cpp
        src/field_kernels_py.cpp
        src/field_ops_py.cpp
        src/fluid_dynamics_py.cpp
        src/magnus_integrator_py.cpp
        src/knot_dynamics_py.cpp
        src/frenet_helicity_py.cpp
        src/potential_timefield_py.cpp
        src/hyperbolic_volume_py.cpp
        src/radiation_flow_py.cpp
        src/swirl_field_py.cpp
        src/thermo_dynamics_py.cpp
        src/time_evolution_py.cpp
        src/vortex_ring_py.cpp
        src/vorticity_dynamics_py.cpp
        src/sst_gravity_py.cpp
        src/sst_extensions_py.cpp
        src/sst_integrator_py.cpp)

target_link_libraries(sstbindings PRIVATE sstcore_lib)
target_include_directories(sstbindings PRIVATE extern/pybind11/include)
target_compile_definitions(sstbindings PRIVATE
    SST_DEFAULT_RESOURCE_SUBDIR="share/sstcore/resources"
    SST_DEFAULT_KNOT_FSERIES_SUBDIR="share/sstcore/resources/knot_fseries"
    SST_DEFAULT_KNOTS_FOURIER_SUBDIR="share/sstcore/resources/Knots_FourierSeries"
)

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

# Copy runtime resources into build tree for local runs (examples/tests/python)
if(EXISTS "${SST_RESOURCES_DIR}")
    add_custom_target(copy_sst_resources ALL
        COMMAND ${CMAKE_COMMAND} -E make_directory
                "${CMAKE_BINARY_DIR}/share/sstcore/resources"
        COMMAND ${CMAKE_COMMAND} -E copy_directory
                "${SST_RESOURCES_DIR}"
                "${CMAKE_BINARY_DIR}/share/sstcore/resources"
        COMMENT "Copying SST runtime resources to build tree"
    )
    add_dependencies(sstcore copy_sst_resources)
    add_dependencies(sstcore_lib copy_sst_resources)
    if(TARGET sstbindings)
        add_dependencies(sstbindings copy_sst_resources)
    endif()
endif()

add_executable(test_frenet tests/test_frenet_helicity.cpp)
target_link_libraries(test_frenet PRIVATE sstcore_lib)

add_executable(test_sst_integrator tests/test_sst_integrator.cpp)
target_link_libraries(test_sst_integrator PRIVATE sstcore_lib)

# Standalone examples/atoms (optional; requires GLFW3. Set -DSST_BUILD_ATOMS=ON and provide glfw3/GLEW/OpenGL.)
set(SST_BUILD_ATOMS OFF CACHE BOOL "Build examples/atoms (requires GLFW3, GLEW, OpenGL)")
if(SST_BUILD_ATOMS)
    add_subdirectory(examples/atoms)
else()
    message(STATUS "Skipping examples/atoms (set SST_BUILD_ATOMS=ON and install GLFW3 to build)")
endif()

# === Node.js Native Addon Build ===
# Check if node-addon-api is available
find_program(NODE_EXECUTABLE NAMES node)

# Allow manual override of node-addon-api include dir for robustness (especially on Windows)
set(NODE_ADDON_API_INCLUDE_DIR "" CACHE PATH "Path to node-addon-api include directory (optional override)")

set(HAVE_SWIRL_STRING_CORE_NODE OFF CACHE BOOL "Node.js addon target is available")

if(NODE_EXECUTABLE)
    # Try to find node-addon-api include directory if not provided explicitly
    if(NOT NODE_ADDON_API_INCLUDE_DIR)
        execute_process(
            COMMAND ${NODE_EXECUTABLE} -p "require('node-addon-api').include"
            OUTPUT_VARIABLE NODE_ADDON_API_INCLUDE_RAW
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )
        set(NODE_ADDON_API_INCLUDE_DIR ${NODE_ADDON_API_INCLUDE_RAW})
    endif()

    # Normalize path and strip any quotes for CMake's EXISTS check (important on Windows)
    if(NODE_ADDON_API_INCLUDE_DIR)
        file(TO_CMAKE_PATH "${NODE_ADDON_API_INCLUDE_DIR}" NODE_ADDON_API_INCLUDE_NORM)
        string(REPLACE "\"" "" NODE_ADDON_API_INCLUDE_NORM "${NODE_ADDON_API_INCLUDE_NORM}")
    endif()

    # Node.js core headers (node_api.h) - required by node-addon-api's napi.h
    # Prefer: 1) NODE_CORE_INCLUDE_DIR override, 2) <node_install>/include/node, 3) node-gyp cache
    set(NODE_CORE_INCLUDE_DIR "" CACHE PATH "Path to Node.js core include directory (optional override)")
    if(NOT NODE_CORE_INCLUDE_DIR)
        execute_process(
            COMMAND ${NODE_EXECUTABLE} -p "require('path').join(require('path').dirname(process.execPath), 'include', 'node')"
            OUTPUT_VARIABLE NODE_CORE_INCLUDE_RAW
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )
        set(NODE_CORE_INCLUDE_DIR "${NODE_CORE_INCLUDE_RAW}")
    endif()
    if(NODE_CORE_INCLUDE_DIR)
        file(TO_CMAKE_PATH "${NODE_CORE_INCLUDE_DIR}" NODE_CORE_INCLUDE_NORM)
        string(REPLACE "\"" "" NODE_CORE_INCLUDE_NORM "${NODE_CORE_INCLUDE_NORM}")
    endif()

    # Fallback: node-gyp cache (e.g. after "node-gyp install") when Node install has no include/
    set(NODE_CORE_HEADER "${NODE_CORE_INCLUDE_NORM}/node_api.h")
    if(NODE_CORE_INCLUDE_NORM AND NOT EXISTS "${NODE_CORE_HEADER}")
        execute_process(
            COMMAND ${NODE_EXECUTABLE} -p "process.versions.node"
            OUTPUT_VARIABLE NODE_VERSION_RAW
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )
        if(NODE_VERSION_RAW)
            string(STRIP "${NODE_VERSION_RAW}" NODE_VERSION_RAW)
            if(IS_WINDOWS)
                execute_process(
                    COMMAND ${NODE_EXECUTABLE} -p "require('path').join(process.env.LOCALAPPDATA || '', 'node-gyp', 'Cache', process.versions.node, 'include', 'node')"
                    OUTPUT_VARIABLE NODE_GYP_INCLUDE_RAW
                    OUTPUT_STRIP_TRAILING_WHITESPACE
                    ERROR_QUIET
                )
            else()
                execute_process(
                    COMMAND ${NODE_EXECUTABLE} -p "require('path').join(process.env.HOME || '', '.node-gyp', process.versions.node, 'include', 'node')"
                    OUTPUT_VARIABLE NODE_GYP_INCLUDE_RAW
                    OUTPUT_STRIP_TRAILING_WHITESPACE
                    ERROR_QUIET
                )
            endif()
            if(NODE_GYP_INCLUDE_RAW)
                file(TO_CMAKE_PATH "${NODE_GYP_INCLUDE_RAW}" NODE_GYP_INCLUDE_NORM)
                string(REPLACE "\"" "" NODE_GYP_INCLUDE_NORM "${NODE_GYP_INCLUDE_NORM}")
                if(EXISTS "${NODE_GYP_INCLUDE_NORM}/node_api.h")
                    set(NODE_CORE_INCLUDE_NORM "${NODE_GYP_INCLUDE_NORM}")
                    set(NODE_CORE_HEADER "${NODE_CORE_INCLUDE_NORM}/node_api.h")
                    message(STATUS "Using Node.js headers from node-gyp cache: ${NODE_CORE_INCLUDE_NORM}")
                endif()
            endif()
        endif()
    endif()

    # Require both node-addon-api and Node core include dir (with node_api.h) to enable addon
    if(NODE_ADDON_API_INCLUDE_NORM AND EXISTS "${NODE_ADDON_API_INCLUDE_NORM}"
       AND NODE_CORE_INCLUDE_NORM AND EXISTS "${NODE_CORE_HEADER}")
        # Find node.lib (Windows) so N-API symbols resolve at link time. On Windows the addon
        # is only built when node.lib is found; otherwise linking would fail with unresolved napi_*.
        set(NODE_LIBRARY "" CACHE FILEPATH "Path to node.lib (Windows). Auto-detected if not set.")
        if(IS_WINDOWS AND NOT NODE_LIBRARY)
            execute_process(
                COMMAND ${NODE_EXECUTABLE} -p "require('path').dirname(process.execPath)"
                OUTPUT_VARIABLE NODE_DIR_RAW
                OUTPUT_STRIP_TRAILING_WHITESPACE
                ERROR_QUIET
            )
            if(NODE_DIR_RAW)
                file(TO_CMAKE_PATH "${NODE_DIR_RAW}" NODE_DIR)
                string(REPLACE "\"" "" NODE_DIR "${NODE_DIR}")
                foreach(SUFFIX "/node.lib" "/lib/node.lib")
                    if(EXISTS "${NODE_DIR}${SUFFIX}")
                        set(NODE_LIBRARY "${NODE_DIR}${SUFFIX}")
                        break()
                    endif()
                endforeach()
            endif()
            # Fallback: node-gyp cache (e.g. C:/Users/.../AppData/Local/node-gyp/Cache/24.14.0/win32/x64/node.lib)
            if(NOT NODE_LIBRARY AND NODE_CORE_INCLUDE_NORM)
                get_filename_component(NODE_GYP_CACHE "${NODE_CORE_INCLUDE_NORM}/../.." ABSOLUTE)
                foreach(CANDIDATE
                    "${NODE_GYP_CACHE}/win32/x64/node.lib"
                    "${NODE_GYP_CACHE}/x64/node.lib"
                    "${NODE_GYP_CACHE}/node.lib"
                )
                    if(EXISTS "${CANDIDATE}")
                        set(NODE_LIBRARY "${CANDIDATE}")
                        message(STATUS "Node library from node-gyp cache: ${NODE_LIBRARY}")
                        break()
                    endif()
                endforeach()
            endif()
            if(NOT NODE_LIBRARY)
                message(STATUS "node.lib not found; skipping Node.js addon. Set -DNODE_LIBRARY=<path>/node.lib or run 'node-gyp install' to build the addon.")
            else()
                message(STATUS "Node library for addon: ${NODE_LIBRARY}")
            endif()
        elseif(NOT IS_WINDOWS)
            # Linux/macOS: no node.lib; symbols come from the loader when Node loads the .node
            set(NODE_LIBRARY "")
        endif()

        # On Windows, only build the Node addon when we have node.lib (required for linking)
        set(BUILD_SSTCORE_NODE TRUE)
        if(IS_WINDOWS AND NOT NODE_LIBRARY)
            set(BUILD_SSTCORE_NODE FALSE)
        endif()

        if(BUILD_SSTCORE_NODE)
        # Build Node.js native addon
        add_library(sstcore_node SHARED
            src/node/module_node.cpp
            src/node/node_biot_savart.cpp
            src/node/node_field_kernels.cpp
            src/node/node_field_ops.cpp
            src/node/node_fluid_dynamics.cpp
            src/node/node_knot.cpp
            src/node/node_frenet_helicity.cpp
            src/node/node_potential_timefield.cpp
            src/node/node_hyperbolic_volume.cpp
            src/node/node_radiation_flow.cpp
            src/node/node_swirl_field.cpp
            src/node/node_thermo_dynamics.cpp
            src/node/node_time_evolution.cpp
            src/node/node_vortex_ring.cpp
            src/node/node_vorticity_dynamics.cpp
            src/node/node_sst_gravity.cpp
            src/node/node_sst_extensions.cpp
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
            src/sst_extensions.cpp
            ${CMAKE_BINARY_DIR}/generated/knot_files_embedded.cpp
        )
        
        target_include_directories(sstcore_node PRIVATE
            ${NODE_CORE_INCLUDE_NORM}
            ${NODE_ADDON_API_INCLUDE_NORM}
            src
            include
            ${CMAKE_BINARY_DIR}/generated
        )
        if(NODE_LIBRARY)
            target_link_libraries(sstcore_node PRIVATE "${NODE_LIBRARY}")
        endif()
        
        # Set C++ standard (use 20 for better compatibility with node-gyp)
        set_target_properties(sstcore_node PROPERTIES
            CXX_STANDARD 20
            CXX_STANDARD_REQUIRED ON
        )
        
        if(IS_WINDOWS)
            set_target_properties(sstcore_node PROPERTIES
                PREFIX ""
                SUFFIX ".node"
            )
        else()
            set_target_properties(sstcore_node PROPERTIES
                PREFIX ""
                SUFFIX ".node"
            )
        endif()
        
        # Ensure generated files are created before building
        add_dependencies(sstcore_node knot_files_embedded)
        
        # Copy the built .node file to build/Release for node-gyp compatibility
        add_custom_command(TARGET sstcore_node POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:sstcore_node>
            ${CMAKE_BINARY_DIR}/Release/sstcore.node
            COMMENT "Copying Node.js addon to build/Release"
        )
        
        set(HAVE_SSTCORE_NODE ON CACHE BOOL "Node.js addon target is available")
        message(STATUS "Node.js native addon build enabled")
        else()
            set(HAVE_SSTCORE_NODE OFF CACHE BOOL "Node.js addon target is available")
        endif()
    else()
        if(NOT NODE_ADDON_API_INCLUDE_NORM OR NOT EXISTS "${NODE_ADDON_API_INCLUDE_NORM}")
            message(STATUS "node-addon-api not found or include dir invalid, skipping Node.js addon build")
        else()
            message(STATUS "Node.js core headers (node_api.h) not found at ${NODE_CORE_INCLUDE_NORM}, skipping Node.js addon build. Install Node.js with 'Install native build tools' or set NODE_CORE_INCLUDE_DIR.")
        endif()
        set(HAVE_SSTCORE_NODE OFF CACHE BOOL "Node.js addon target is available")
    endif()
endif()

# === WebAssembly Build (Emscripten) ===
# Check if Emscripten is available
if(CMAKE_CXX_COMPILER_ID STREQUAL "Emscripten" OR EMSCRIPTEN)
    message(STATUS "Emscripten detected, building WASM module")
    
    # WASM bindings will be created in src_bindings/wasm/
    # For now, we'll create a placeholder target
    # Full WASM implementation requires Emscripten-specific bindings
    
    add_library(sstcore_wasm STATIC
        # WASM sources will go here
        # src_bindings/wasm/module_wasm.cpp
        # ... other WASM bindings
    )
    
    # Emscripten-specific flags
    target_compile_options(sstcore_wasm PRIVATE
        -O3
        -s WASM=1
        -s EXPORT_ES6=1
        -s MODULARIZE=1
        -s EXPORT_NAME="createSSTcoreModule"
    )
    
    message(STATUS "WASM build target created (requires Emscripten bindings)")
else()
    message(STATUS "Emscripten not detected, skipping WASM build")
endif()


# Install targets
install(TARGETS sstcore_lib sstcore sstbindings
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin)
install(DIRECTORY include/ DESTINATION include)

# Install all runtime knot resources (ideal databases + fseries + metadata)
if(EXISTS "${SST_RESOURCES_DIR}")
    install(DIRECTORY "${SST_RESOURCES_DIR}/"
            DESTINATION share/sstcore/resources)
endif()

# === ✅ AUTO-COPY PYBIND MODULE TO PROJECT ROOT (best-effort) ===
# Copy to project root, examples/, tests/, ../SwirlStringTheory/, ../SST_Dashboard/ for easy import.
# Copy failures (e.g. .pyd locked by running Python) do not fail the build.

set(SWIRL_THEORY_DIR "${CMAKE_SOURCE_DIR}/../SwirlStringTheory")
set(SST_DASHBOARD_DIR "${CMAKE_SOURCE_DIR}/../SST_Dashboard")

add_custom_command(TARGET sstcore POST_BUILD
        COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/copy_pyd_fallback.cmake
        -DSOURCE=$<TARGET_FILE:sstcore>
        -DPROJECT_ROOT=${CMAKE_SOURCE_DIR}
        -DBUILD_DIR=${CMAKE_BINARY_DIR}
        COMMAND ${CMAKE_COMMAND} -E make_directory "${SWIRL_THEORY_DIR}"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:sstcore>
        "${SWIRL_THEORY_DIR}/$<TARGET_FILE_NAME:sstcore>"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${SST_DASHBOARD_DIR}"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:sstcore>
        "${SST_DASHBOARD_DIR}/$<TARGET_FILE_NAME:sstcore>"
        COMMENT "Copying sstcore module for easy import (best-effort)"
)

# Also copy sstcore when building sstbindings (same binary, different name for backwards compatibility)
add_custom_command(TARGET sstbindings POST_BUILD
        COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/copy_pyd_fallback.cmake
        -DSOURCE=$<TARGET_FILE:sstbindings>
        -DPROJECT_ROOT=${CMAKE_SOURCE_DIR}
        -DBUILD_DIR=${CMAKE_BINARY_DIR}
        COMMAND ${CMAKE_COMMAND} -E make_directory "${SWIRL_THEORY_DIR}"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:sstcore>
        "${SWIRL_THEORY_DIR}/$<TARGET_FILE_NAME:sstcore>"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${SST_DASHBOARD_DIR}"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:sstcore>
        "${SST_DASHBOARD_DIR}/$<TARGET_FILE_NAME:sstcore>"
        COMMENT "Copying sstcore/sstbindings for easy import (best-effort)"
)