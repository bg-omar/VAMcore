// py_field_kernels.cpp — robust across older pybind11/MSVC
// Key changes:
//  - Include order + NOMINMAX
//  - Accept py::array in signatures; locally ensure/cast to array_t<double>
//  - Use shape(i) to build std::vector<ssize_t> for output arrays

#define NOMINMAX
#define USE_MATH_DEFINES
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "../src/field_kernels.h"

namespace py = pybind11;
using sst::FieldKernels;
using sst::Vec3;

static void require_same_shape(const py::array &A, const py::array &B, const py::array &C) {
    if (A.ndim() != B.ndim() || A.ndim() != C.ndim())
        throw std::invalid_argument("X, Y, Z must share the same number of dimensions");
    for (py::ssize_t i = 0; i < A.ndim(); ++i) {
        if (A.shape(i) != B.shape(i) || A.shape(i) != C.shape(i))
            throw std::invalid_argument("X, Y, Z must have identical shapes");
    }
}

static void require_Nx3(const py::array &A, const char *name) {
    if (A.ndim() != 2 || A.shape(1) != 3)
        throw std::invalid_argument(std::string(name) + " must have shape [N,3]");
    if (A.shape(0) < 1)
        throw std::invalid_argument(std::string(name) + " must have at least 1 row");
}

// Build a shape vector usable in py::array_t constructors
static std::vector<py::ssize_t> shape_vec(const py::array &A) {
    std::vector<py::ssize_t> s(static_cast<size_t>(A.ndim()));
    for (py::ssize_t i = 0; i < A.ndim(); ++i) s[static_cast<size_t>(i)] = A.shape(i);
    return s;
}

// ---------------- NumPy wrappers ----------------

static py::tuple biot_savart_wire_grid_np(py::array X,
                                          py::array Y,
                                          py::array Z,
                                          py::array wire_points,
                                          double current)
{
    require_same_shape(X, Y, Z);
    require_Nx3(wire_points, "wire_points");

    // Ensure double dtype + C-style where possible
    auto Xd = py::array_t<double>::ensure(X);
    auto Yd = py::array_t<double>::ensure(Y);
    auto Zd = py::array_t<double>::ensure(Z);
    auto WP = py::array_t<double>::ensure(wire_points);
    if (!Xd || !Yd || !Zd || !WP) throw std::invalid_argument("Inputs must be convertible to float64 arrays");

    // Flattened element count
    const size_t n_grid = static_cast<size_t>(Xd.size());

    // Input buffers
    auto Xb = Xd.request(), Yb = Yd.request(), Zb = Zd.request();
    const double *Xp = static_cast<const double*>(Xb.ptr);
    const double *Yp = static_cast<const double*>(Yb.ptr);
    const double *Zp = static_cast<const double*>(Zb.ptr);

    // Outputs with same shape
    auto shp = shape_vec(Xd);
    py::array_t<double> bx(shp), by(shp), bz(shp);
    auto Bxb = bx.request(), Byb = by.request(), Bzb = bz.request();
    double *Bxp = static_cast<double*>(Bxb.ptr);
    double *Byp = static_cast<double*>(Byb.ptr);
    double *Bzp = static_cast<double*>(Bzb.ptr);
    std::fill(Bxp, Bxp + n_grid, 0.0);
    std::fill(Byp, Byp + n_grid, 0.0);
    std::fill(Bzp, Bzp + n_grid, 0.0);

    // Polyline -> std::vector<Vec3>
    auto wp = py::cast<py::array_t<double>>(WP).template unchecked<2>();
    std::vector<Vec3> W;
    W.reserve(static_cast<size_t>(wp.shape(0)));
    for (py::ssize_t i = 0; i < wp.shape(0); ++i)
        W.push_back(Vec3{wp(i,0), wp(i,1), wp(i,2)});

    FieldKernels::biot_savart_wire_grid(Xp, Yp, Zp, n_grid, W, current, Bxp, Byp, Bzp);
    return py::make_tuple(bx, by, bz);
}

static py::tuple dipole_ring_field_grid_np(py::array X,
                                           py::array Y,
                                           py::array Z,
                                           py::array positions,
                                           py::array moments)
{
    require_same_shape(X, Y, Z);
    require_Nx3(positions, "positions");
    require_Nx3(moments,   "moments");
    if (positions.shape(0) != moments.shape(0))
        throw std::invalid_argument("positions and moments must have the same number of rows");

    auto Xd = py::array_t<double>::ensure(X);
    auto Yd = py::array_t<double>::ensure(Y);
    auto Zd = py::array_t<double>::ensure(Z);
    auto P  = py::array_t<double>::ensure(positions);
    auto M  = py::array_t<double>::ensure(moments);
    if (!Xd || !Yd || !Zd || !P || !M) throw std::invalid_argument("Inputs must be convertible to float64 arrays");

    const size_t n_grid = static_cast<size_t>(Xd.size());

    auto Xb = Xd.request();
    auto Yb = Yd.request();
    auto Zb = Zd.request();
    const double *Xp = static_cast<const double*>(Xb.ptr);
    const double *Yp = static_cast<const double*>(Yb.ptr);
    const double *Zp = static_cast<const double*>(Zb.ptr);

    auto shp = shape_vec(Xd);
    py::array_t<double> bx(shp), by(shp), bz(shp);
    auto Bxb = bx.request(), Byb = by.request(), Bzb = bz.request();
    auto *Bxp = static_cast<double*>(Bxb.ptr);
    auto *Byp = static_cast<double*>(Byb.ptr);
    auto *Bzp = static_cast<double*>(Bzb.ptr);
    std::fill_n(Bxp, n_grid, 0.0);
    std::fill_n(Byp, n_grid, 0.0);
    std::fill_n(Bzp, n_grid, 0.0);

    auto Pu = P.unchecked<2>();
    auto Mu = M.unchecked<2>();
    const size_t rows = static_cast<size_t>(Pu.shape(0));
    std::vector<Vec3> pos, mom;
    pos.reserve(rows); mom.reserve(rows);
    for (py::ssize_t i = 0; i < Pu.shape(0); ++i) {
        pos.push_back(Vec3{Pu(i,0), Pu(i,1), Pu(i,2)});
        mom.emplace_back(Vec3{Mu(i,0), Mu(i,1), Mu(i,2)});
    }

    FieldKernels::dipole_ring_field_grid(Xp, Yp, Zp, n_grid, pos, mom, Bxp, Byp, Bzp);
    return py::make_tuple(bx, by, bz);
}

// -------------------------------------------------------------------------
// Compute Magnetic Vector Potential (A)
// A(r) = (mu0 I / 4pi) * Integral( dl / |r-r'| )
// Represents the "Ether Momentum" flow.
// -------------------------------------------------------------------------
static void biot_savart_vector_potential(const double* X,
                                         const double* Y,
                                         const double* Z,
                                         std::size_t n_grid,
                                         const std::vector<Vec3>& wire_points,
                                         double current,
                                         double* Ax,
                                         double* Ay,
                                         double* Az)
{
    constexpr double PI = 3.1415926535897932384626433832795;
    constexpr double K  = 1.0 / (4.0 * PI); // mu0/4pi
    const double factor = K * current;
    const double eps = 1e-12;

    if (wire_points.size() < 2) return;

    // Precompute segments
    const std::size_t S = wire_points.size() - 1;
    std::vector<Vec3> mid(S), dl(S);
    for (std::size_t i = 0; i < S; ++i) {
        const Vec3& p0 = wire_points[i];
        const Vec3& p1 = wire_points[i+1];
        mid[i] = { 0.5*(p0[0]+p1[0]), 0.5*(p0[1]+p1[1]), 0.5*(p0[2]+p1[2]) };
        dl[i]  = { p1[0]-p0[0],       p1[1]-p0[1],       p1[2]-p0[2]       };
    }

    // Grid Loop
    for (std::size_t i = 0; i < n_grid; ++i) {
        double local_Ax = 0.0, local_Ay = 0.0, local_Az = 0.0;

        for (std::size_t s = 0; s < S; ++s) {
            const Vec3& mp = mid[s];
            const Vec3& d  = dl[s];

            // Distance R
            double rx = X[i] - mp[0];
            double ry = Y[i] - mp[1];
            double rz = Z[i] - mp[2];
            double R = std::sqrt(rx*rx + ry*ry + rz*rz);

            if (R < eps) continue;

            // Integration: dl / R
            double invR = 1.0 / R;
            local_Ax += d[0] * invR;
            local_Ay += d[1] * invR;
            local_Az += d[2] * invR;
        }

        Ax[i] += factor * local_Ax;
        Ay[i] += factor * local_Ay;
        Az[i] += factor * local_Az;
    }
}

// ------------- Class-style binder -------------
void bind_field_kernels(py::module_ &m) {
    m.def("dipole_field_at_point",
          &FieldKernels::dipole_field_at_point,
          py::arg("r"), py::arg("m"),
          R"pbdoc(Analytical point dipole field (mu0=1).)pbdoc");

    m.def("biot_savart_wire_grid",
          &biot_savart_wire_grid_np,
          py::arg("X"), py::arg("Y"), py::arg("Z"),
          py::arg("wire_points"), py::arg("current") = 1.0,
          R"pbdoc(Biot–Savart of polyline on a 3D grid (midpoint per segment).)pbdoc");

    m.def("dipole_ring_field_grid",
          &dipole_ring_field_grid_np,
          py::arg("X"), py::arg("Y"), py::arg("Z"),
          py::arg("positions"), py::arg("moments"),
          R"pbdoc(Superposition of point dipoles on a 3D grid.)pbdoc");
}