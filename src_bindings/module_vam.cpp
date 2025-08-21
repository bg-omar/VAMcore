// bindings/py_vam.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <algorithm>

namespace py = pybind11;

// Forward declaration only!
void bind_biot_savart(py::module_& m);
void bind_fluid_dynamics(py::module_ &m);
void bind_fluid_rotation(py::module_ &m);
void bind_field_kernels(py::module_ &m);
void bind_fourier_knot(py::module_& m);
void bind_frenet_helicity(py::module_& m);
void bind_gravity_timefield(py::module_& m);
void bind_heavy_knot(py::module_& m);
void bind_hyperbolic_volume(py::module_& m);
void bind_kinetic_energy(py::module_& m);
void bind_knot_dynamics(py::module_& m);
void bind_knot_pd(py::module_& m);
void bind_potential_flow(py::module_& m);
void bind_potential_timefield(py::module_& m);
void bind_pressure_field(py::module_& m);
void bind_radiation_flow(py::module_& m);
void bind_relative_vorticity(py::module_& m);
void bind_swirl_field(py::module_& m);
void bind_thermo_dynamics(py::module_& m);
void bind_time_evolution(py::module_& m);
void bind_vortex_knot_system(py::module_& m);
void bind_vortex_ring(py::module_& m);
void bind_vorticity_dynamics(py::module_& m);
void bind_vorticity_transport(py::module_& m);




PYBIND11_MODULE(vambindings, m) {
  m.doc() = "VAM Core Bindings";
  bind_biot_savart(m);
  bind_fluid_dynamics(m);
  bind_fluid_rotation(m);
  bind_field_kernels(m);
  bind_fourier_knot(m);
  bind_frenet_helicity(m);
  bind_gravity_timefield(m);
  bind_heavy_knot(m);
  bind_hyperbolic_volume(m);
  bind_kinetic_energy(m);
  bind_knot_dynamics(m);
  bind_knot_pd(m),
  bind_potential_flow(m);
  bind_potential_timefield(m);
  bind_pressure_field(m);
  bind_radiation_flow(m);
  bind_relative_vorticity(m);
  bind_swirl_field(m);
  bind_thermo_dynamics(m);
  bind_time_evolution(m);
  bind_vortex_knot_system(m);
  bind_vortex_ring(m);
  bind_vorticity_dynamics(m);
  bind_vorticity_transport(m);

 // module-wide listing utility
    m.def(
        "list_bindings",
        [m](const py::object &pattern /* = None */,
          const bool include_private /* = false */) {
            const auto names = m.attr("__dir__")().cast<py::list>();
            py::list funcs, classes, attrs;

            const bool use_pat = !pattern.is_none();
            std::string pat = use_pat ? std::string(py::str(pattern)) : std::string();
            std::ranges::transform(pat, pat.begin(), ::tolower);

            for (const py::handle h : names) {
                std::string name = py::str(h);
                if (!include_private && !name.empty() && name[0] == '_') continue;
                if (name == "list_bindings") continue;

                std::string namelow = name;
                if (use_pat) {
                    std::ranges::transform(namelow, namelow.begin(), ::tolower);
                    if (namelow.find(pat) == std::string::npos) continue;
                }

                if (const py::object obj = m.attr(name.c_str());
                    py::isinstance<py::function>(obj)) {
                    funcs.append(py::str(name));
                } else if (py::isinstance<py::type>(obj)) {
                    classes.append(py::str(name));
                } else {
                    attrs.append(py::str(name));
                }
            }

            // also populate __all__ for convenience (public functions + classes)
            py::list all;
            for (auto&& f : funcs) all.append(f);
            for (auto&& c : classes) all.append(c);
            m.attr("__all__") = all;

            py::dict counts;
            counts["functions"]  = py::len(funcs);
            counts["classes"]    = py::len(classes);
            counts["attributes"] = py::len(attrs);

            py::dict out;
            out["functions"]  = funcs;
            out["classes"]    = classes;
            out["attributes"] = attrs;
            out["counts"]     = counts;
            return out;
        },
        py::arg("pattern") = py::none(),
        py::arg("include_private") = false,
        R"pbdoc(
        Return a dictionary of exported names in vambindings.

        Args:
          pattern (str|None): optional case-insensitive substring filter.
          include_private (bool): include names beginning with '_' if True.

        Returns:
          dict with keys: 'functions', 'classes', 'attributes', and 'counts'.
        Also sets module __all__ = functions + classes (public names).
        )pbdoc");
}

