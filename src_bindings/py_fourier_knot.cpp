// src_bindings/py_fourier_knot.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "../src/fourier_knot.h"

namespace py = pybind11;
using sst::FourierBlock;
using sst::fourier_knot;
using sst::Vec3;

static void _check_1d_same_len(const py::array &a, const py::array &b, const char* name){
  if(a.ndim()!=1 || b.ndim()!=1 || a.shape(0)!=b.shape(0))
    throw std::invalid_argument(std::string("fourier_knot_eval: ") + name + " must be 1D and same length");
}

void bind_fourier_knot(py::module_& m) {
  // DO NOT bind Vec3 (std::array) as a class — stl.h covers it

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

  // Numpy-friendly alias: fourier_knot_eval(a_x,b_x,a_y,b_y,a_z,b_z, s) -> (x,y,z)
  m.def("fourier_knot_eval",
        [](py::array_t<double, py::array::c_style | py::array::forcecast> a_x,
           py::array_t<double, py::array::c_style | py::array::forcecast> b_x,
           py::array_t<double, py::array::c_style | py::array::forcecast> a_y,
           py::array_t<double, py::array::c_style | py::array::forcecast> b_y,
           py::array_t<double, py::array::c_style | py::array::forcecast> a_z,
           py::array_t<double, py::array::c_style | py::array::forcecast> b_z,
           py::array_t<double, py::array::c_style | py::array::forcecast> s)
        {
          _check_1d_same_len(a_x, b_x, "a_x/b_x");
          _check_1d_same_len(a_y, b_y, "a_y/b_y");
          _check_1d_same_len(a_z, b_z, "a_z/b_z");
          if(s.ndim()!=1) throw std::invalid_argument("fourier_knot_eval: s must be 1D");

          FourierBlock blk;
          auto ax=a_x.unchecked<1>(), bx=b_x.unchecked<1>();
          auto ay=a_y.unchecked<1>(), by=b_y.unchecked<1>();
          auto az=a_z.unchecked<1>(), bz=b_z.unchecked<1>();
          const py::ssize_t M = ax.shape(0);
          blk.a_x.resize(M); blk.b_x.resize(M);
          blk.a_y.resize(M); blk.b_y.resize(M);
          blk.a_z.resize(M); blk.b_z.resize(M);
          for(py::ssize_t i=0;i<M;++i){
            blk.a_x[i]=ax(i); blk.b_x[i]=bx(i);
            blk.a_y[i]=ay(i); blk.b_y[i]=by(i);
            blk.a_z[i]=az(i); blk.b_z[i]=bz(i);
          }

          std::vector<double> S; S.reserve(static_cast<size_t>(s.shape(0)));
          auto sraw=s.unchecked<1>();
          for(py::ssize_t i=0;i<s.shape(0);++i) S.push_back(sraw(i));

          std::vector<Vec3> P = sst::fourier_knot::evaluate(blk, S);

          py::array_t<double> x(s.shape(0)), y(s.shape(0)), z(s.shape(0));
          auto xr=x.mutable_unchecked<1>();
          auto yr=y.mutable_unchecked<1>();
          auto zr=z.mutable_unchecked<1>();
          for(py::ssize_t i=0;i<s.shape(0);++i){
            xr(i)=P[(size_t)i][0];
            yr(i)=P[(size_t)i][1];
            zr(i)=P[(size_t)i][2];
          }
          return py::make_tuple(std::move(x), std::move(y), std::move(z));
        },
        py::arg("a_x"), py::arg("b_x"), py::arg("a_y"), py::arg("b_y"),
        py::arg("a_z"), py::arg("b_z"), py::arg("s"),
        "NumPy-friendly Fourier evaluation returning (x,y,z)");
}