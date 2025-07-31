cmake_minimum_required(VERSION 3.23)
project(VAMCore LANGUAGES CXX)
# === Python Executable Compatibility ===
# If Python3_EXECUTABLE is set but not Python_EXECUTABLE, map it
if(Python3_EXECUTABLE AND NOT Python_EXECUTABLE)
    set(Python_EXECUTABLE ${Python3_EXECUTABLE})
endif()

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)



# Use vendored pybind11 from extern/ directory
add_subdirectory(extern/pybind11)

# Core VAM library sources
add_library(vamcore STATIC
        src/biot_savart.cpp
        src/fluid_dynamics.cpp
        src/fluid_rotation.cpp
        src/frenet_helicity.cpp
        src/gravity_timefield.cpp
        src/kinetic_energy.cpp
        src/knot_dynamics.cpp
        src/potential_flow.cpp
        src/potential_timefield.cpp
        src/pressure_field.cpp
        src/radiation_flow.cpp
        src/relative_vorticity.cpp
        src/swirl_field.cpp
        src/thermo_dynamics.cpp
        src/time_evolution.cpp
        src/vortex_knot_system.cpp
        src/vortex_ring.cpp
        src/vorticity_dynamics.cpp
        src/vorticity_transport.cpp
)

target_include_directories(vamcore PUBLIC src)

# Python bindingsac
pybind11_add_module(vambindings src_bindings/module_vam.cpp)
target_sources(vambindings PRIVATE
        src_bindings/py_biot_savart.cpp
        src_bindings/py_fluid_dynamics.cpp
        src_bindings/py_fluid_rotation.cpp
        src_bindings/py_frenet_helicity.cpp
        src_bindings/py_gravity_timefield.cpp
        src_bindings/py_kinetic_energy.cpp
        src_bindings/py_knot_dynamics.cpp
        src_bindings/py_potential_flow.cpp
        src_bindings/py_potential_timefield.cpp
        src_bindings/py_pressure_field.cpp
        src_bindings/py_radiation_flow.cpp
        src_bindings/py_relative_vorticity.cpp
        src_bindings/py_swirl_field.cpp
        src_bindings/py_thermo_dynamics.cpp
        src_bindings/py_time_evolution.cpp
        src_bindings/py_vortex_knot_system.cpp
        src_bindings/py_vortex_ring.cpp
        src_bindings/py_vorticity_dynamics.cpp
        src_bindings/py_vorticity_transport.cpp)

target_link_libraries(vambindings PRIVATE vamcore)
target_include_directories(vambindings PRIVATE extern/pybind11/include)
add_executable(test_frenet tests/test_frenet_helicity.cpp)
target_link_libraries(test_frenet PRIVATE vamcore)


# Install targets
install(TARGETS vamcore vambindings
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin)
install(DIRECTORY include/ DESTINATION include)

# === ✅ AUTO-COPY PYBIND MODULE TO PROJECT ROOT ===
# After vambindings is built, copy it to ${CMAKE_SOURCE_DIR}
# So you can easily import it from Python scripts in the root directory

add_custom_command(TARGET vambindings POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:vambindings>
        ${CMAKE_SOURCE_DIR}/$<TARGET_FILE_NAME:vambindings>
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:vambindings>
        ${CMAKE_SOURCE_DIR}/examples/$<TARGET_FILE_NAME:vambindings>
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:vambindings>
        ${CMAKE_SOURCE_DIR}/../VAM/$<TARGET_FILE_NAME:vambindings>
        COMMENT "Copied vambindings module to project root, examples/, and ../VAM/ for easy import"
)
