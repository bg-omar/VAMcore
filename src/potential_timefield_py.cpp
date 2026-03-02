// src/potential_timefield_py.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "potential_timefield.h"

namespace py = pybind11;

void bind_timefield(py::module_& m) {
        m.def("compute_gravitational_potential_gradient", &sst::TimeField::compute_gravitational_potential_gradient,
		  py::arg("positions"),
		  py::arg("vorticity"),
		  py::arg("epsilon") = 7e-7,
		  R"pbdoc(
            Compute Ætheric gravitational potential field from vorticity gradients.
        )pbdoc");

        m.def("compute_time_dilation_map_sqrt", &sst::TimeField::compute_time_dilation_map_sqrt,
		  py::arg("tangents"),
		  py::arg("C_e") = 1093845.63,
		  R"pbdoc(
            Compute time dilation factors from knot tangential velocities (sqrt method).
        )pbdoc");

        m.def("compute_gravitational_potential_direct", &sst::TimeField::compute_gravitational_potential_direct,
		  py::arg("positions"),
		  py::arg("vorticity"),
		  py::arg("epsilon") = 0.1,
		  R"pbdoc(
            Compute Æther gravitational potential field from vorticity.
        )pbdoc");

        m.def("compute_time_dilation_map_linear", &sst::TimeField::compute_time_dilation_map_linear,
		  py::arg("tangents"),
		  py::arg("C_e"),
		  R"pbdoc(
            Compute local time dilation factor map from tangential velocities.
        )pbdoc");

		m.def("compute_gravitational_potential", &sst::compute_gravitational_potential,
		  py::arg("positions"),
		  py::arg("vorticity"),
		  py::arg("epsilon") = 7e-7,
		  R"pbdoc(
            Compute Ætheric gravitational potential field (backward compatibility).
        )pbdoc");

        m.def("compute_time_dilation_map", &sst::compute_time_dilation_map,
		  py::arg("tangents"),
		  py::arg("C_e") = 1093845.63,
		  R"pbdoc(
            Compute time dilation factors (backward compatibility).
        )pbdoc");
}
