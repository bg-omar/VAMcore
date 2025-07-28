#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/vorticity_transport.h"

namespace py = pybind11;
using namespace vam;

void bind_vorticity_transport(py::module_& m) {
    m.def("baroclinic_term", &VorticityTransport::baroclinic_term, "Baroclinic torque term");
    m.def("compute_vorticity_rhs", &VorticityTransport::compute_rhs, "Vorticity transport RHS");
}