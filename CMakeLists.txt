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
)

target_include_directories(vamcore PUBLIC src)

# Python bindings
pybind11_add_module(vambindings bindings/py_vam.cpp)
target_sources(vambindings PRIVATE
        bindings/py_frenet_helicity.cpp
        bindings/py_potential_timefield.cpp
        bindings/py_gravity_timefield.cpp
        bindings/py_biot_savart.cpp
        bindings/py_knot_dynamics.cpp
        bindings/py_time_evolution.cpp
        bindings/py_pressure_field.cpp
        bindings/py_fluid_dynamics.cpp
        bindings/py_vortex_knot_system.cpp
        bindings/py_kinetic_energy.cpp
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
