#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "swirl_field.h"

namespace py = pybind11;

void bind_swirl_field(py::module_& m) {
			m.def("compute_swirl_field", &vam::compute_swirl_field,
						py::arg("res"), py::arg("time"),
						R"pbdoc(
				Compute 2D swirl force field at a given resolution and time.
			)pbdoc");
}
