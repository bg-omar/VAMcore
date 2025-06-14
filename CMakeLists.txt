cmake_minimum_required(VERSION 3.23)
project(VAMCore LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)



# Use vendored pybind11 from extern/ directory
add_subdirectory(extern/pybind11)

# Core VAM library sources
add_library(vamcore STATIC
        src/biot_savart.cpp
        src/vortex_knot_system.cpp
        src/frenet_helicity.cpp
        src/potential_timefield.cpp
        src/gravity_timefield.cpp
        src/knot_dynamics.cpp
        src/pressure_field.cpp
        src/time_evolution.cpp
        src/fluid_dynamics.cpp
        src/kinetic_energy.cpp
        src/swirl_field.cpp
)

target_include_directories(vamcore PUBLIC src)

# Python bindingsac
pybind11_add_module(vambindings src_bindings/module_vam.cpp)
target_sources(vambindings PRIVATE
        src_bindings/py_frenet_helicity.cpp
        src_bindings/py_potential_timefield.cpp
        src_bindings/py_gravity_timefield.cpp
        src_bindings/py_biot_savart.cpp
        src_bindings/py_knot_dynamics.cpp
        src_bindings/py_time_evolution.cpp
        src_bindings/py_pressure_field.cpp
        src_bindings/py_fluid_dynamics.cpp
        src_bindings/py_vortex_knot_system.cpp
        src_bindings/py_kinetic_energy.cpp
        src_bindings/py_swirl_field.cpp
)

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