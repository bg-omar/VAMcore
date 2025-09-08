// src_bindings/py_field_ops.cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <stdexcept>

namespace py = pybind11;

// Periodic 2nd‑order central‑difference curl
void bind_field_ops(py::module_& m){
  m.def("curl3d_central",
        [](py::array_t<double, py::array::c_style | py::array::forcecast> vel,
           double spacing)
        {
          if(vel.ndim()!=4 || vel.shape(3)!=3)
            throw std::invalid_argument("curl3d_central: vel must be (Nx,Ny,Nz,3)");
          const py::ssize_t Nx=vel.shape(0), Ny=vel.shape(1), Nz=vel.shape(2);
          auto V = vel.unchecked<4>();

          py::array_t<double> out({Nx,Ny,Nz,(py::ssize_t)3});
          auto C = out.mutable_unchecked<4>();
          const double h2 = 2.0*spacing;

          auto wp = [](py::ssize_t a, py::ssize_t n){ return (a>=0)? (a%n) : ((a%n)+n)%n; };

          for(py::ssize_t i=0;i<Nx;++i){
            const py::ssize_t im = wp(i-1,Nx), ip = wp(i+1,Nx);
            for(py::ssize_t j=0;j<Ny;++j){
              const py::ssize_t jm = wp(j-1,Ny), jp = wp(j+1,Ny);
              for(py::ssize_t k=0;k<Nz;++k){
                const py::ssize_t km = wp(k-1,Nz), kp = wp(k+1,Nz);

                const double dvz_dy = (V(i,jp,k,2) - V(i,jm,k,2)) / h2;
                const double dvy_dz = (V(i,j,kp,1) - V(i,j,km,1)) / h2;

                const double dvx_dz = (V(i,j,kp,0) - V(i,j,km,0)) / h2;
                const double dvz_dx = (V(ip,j,k,2) - V(im,j,k,2)) / h2;

                const double dvy_dx = (V(ip,j,k,1) - V(im,j,k,1)) / h2;
                const double dvx_dy = (V(i,jp,k,0) - V(i,jm,k,0)) / h2;

                C(i,j,k,0) = dvz_dy - dvy_dz;
                C(i,j,k,1) = dvx_dz - dvz_dx;
                C(i,j,k,2) = dvy_dx - dvx_dy;
              }
            }
          }
          return out;
        },
        py::arg("vel"), py::arg("spacing"),
        "Central‑difference curl with periodic BCs. vel:(Nx,Ny,Nz,3) -> curl:(Nx,Ny,Nz,3)");
}
