#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/fourier_knot.h"

namespace py = pybind11;
using vam::FourierBlock;
using vam::fourier_knot;
using vam::Vec3;

void bind_fourier_knot(py::module_& m) {
    py::class_<Vec3>(m, "Vec3")
        .def_property("x",
            [](const Vec3& v) { return v[0]; },
            [](Vec3& v, double value) { v[0] = value; })
        .def_property("y",
            [](const Vec3& v) { return v[1]; },
            [](Vec3& v, double value) { v[1] = value; })
        .def_property("z",
            [](const Vec3& v) { return v[2]; },
            [](Vec3& v, double value) { v[2] = value; });

    py::class_<FourierBlock>(m, "FourierBlock")
        .def(py::init<>())
        .def_readwrite("header", &FourierBlock::header)
        .def_readwrite("a_x", &FourierBlock::a_x)
        .def_readwrite("b_x", &FourierBlock::b_x)
        .def_readwrite("a_y", &FourierBlock::a_y)
        .def_readwrite("b_y", &FourierBlock::b_y)
        .def_readwrite("a_z", &FourierBlock::a_z)
        .def_readwrite("b_z", &FourierBlock::b_z);

    py::class_<fourier_knot>(m, "fourier_knot")
        .def(py::init<>())
        .def("loadBlocks", &fourier_knot::loadBlocks)
        .def("selectMaxHarmonics", &fourier_knot::selectMaxHarmonics)
        .def("reconstruct", &fourier_knot::reconstruct)
        .def_readwrite("points", &fourier_knot::points)
        .def_readwrite("blocks", &fourier_knot::blocks)
        .def_readwrite("activeBlock", &fourier_knot::activeBlock);

    m.def("parse_fseries_multi", &fourier_knot::parse_fseries_multi,
          py::arg("path"), "Parse a .fseries file into Fourier blocks.");

    m.def("index_of_largest_block", &fourier_knot::index_of_largest_block,
          py::arg("blocks"), "Return index of block with most harmonics.");

    m.def("evaluate_fourier_block", &fourier_knot::evaluate,
          py::arg("block"), py::arg("s"),
          "Evaluate r(s) for the given Fourier block.");

    m.def("center_points", &fourier_knot::center_points,
          py::arg("points"), "Center points at their centroid.");

    m.def("curvature_of_points", &fourier_knot::curvature,
          py::arg("points"), py::arg("eps") = 1e-8,
          "Discrete curvature using periodic central differences.");

    m.def("load_knot_from_fseries", &fourier_knot::load_knot,
          py::arg("path"), py::arg("nsamples") = 1000,
          "Load, evaluate (largest block), center and compute curvature.");
}
