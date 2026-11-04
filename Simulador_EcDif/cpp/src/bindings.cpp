#include "rc_solver.hpp"

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace {

/**
 * @brief Envuelve un std::vector<double> de un SimulationResult como una vista NumPy de solo lectura
 *        vinculada al ciclo de vida del objeto SimulationResult padre (Zero-Copy).
 */
py::array_t<double> as_numpy_view(const std::vector<double>& vec, py::handle parent) {
    return py::array_t<double>(
        {static_cast<py::ssize_t>(vec.size())},
        {static_cast<py::ssize_t>(sizeof(double))},
        vec.data(),
        parent
    );
}

} // namespace

PYBIND11_MODULE(rc_core_cpp, m) {
    m.doc() = "Módulo C++20 de alto rendimiento para la simulación analítica y numérica (RK4) de circuitos RC en serie.";

    py::class_<rc_sim::CircuitParams>(m, "CircuitParams")
        .def(py::init<double, double, double, double, double, double, std::size_t>(),
             py::arg("R") = 50.0,
             py::arg("C") = 0.01,
             py::arg("E0") = 200.0,
             py::arg("omega") = 2.0,
             py::arg("q0") = 0.0,
             py::arg("t_sim") = 3.0,
             py::arg("num_points") = 2500)
        .def_readwrite("R", &rc_sim::CircuitParams::R)
        .def_readwrite("C", &rc_sim::CircuitParams::C)
        .def_readwrite("E0", &rc_sim::CircuitParams::E0)
        .def_readwrite("omega", &rc_sim::CircuitParams::omega)
        .def_readwrite("q0", &rc_sim::CircuitParams::q0)
        .def_readwrite("t_sim", &rc_sim::CircuitParams::t_sim)
        .def_readwrite("num_points", &rc_sim::CircuitParams::num_points);

    py::class_<rc_sim::CircuitMetrics>(m, "CircuitMetrics")
        .def(py::init<>())
        .def_readonly("tau", &rc_sim::CircuitMetrics::tau)
        .def_readonly("ts_4tau", &rc_sim::CircuitMetrics::ts_4tau)
        .def_readonly("ts_5tau", &rc_sim::CircuitMetrics::ts_5tau)
        .def_readonly("Xc", &rc_sim::CircuitMetrics::Xc)
        .def_readonly("Z", &rc_sim::CircuitMetrics::Z)
        .def_readonly("phi_rad", &rc_sim::CircuitMetrics::phi_rad)
        .def_readonly("phi_deg", &rc_sim::CircuitMetrics::phi_deg)
        .def_readonly("I_max", &rc_sim::CircuitMetrics::I_max)
        .def_readonly("Vc_max", &rc_sim::CircuitMetrics::Vc_max)
        .def_readonly("i_0", &rc_sim::CircuitMetrics::i_0)
        .def_readonly("K_q", &rc_sim::CircuitMetrics::K_q)
        .def_readonly("K_i", &rc_sim::CircuitMetrics::K_i)
        .def_readonly("max_err_q", &rc_sim::CircuitMetrics::max_err_q)
        .def_readonly("max_err_i", &rc_sim::CircuitMetrics::max_err_i)
        .def_readonly("rmse_q", &rc_sim::CircuitMetrics::rmse_q)
        .def_readonly("rmse_i", &rc_sim::CircuitMetrics::rmse_i);

    py::class_<rc_sim::SimulationResult>(m, "SimulationResult")
        .def_readonly("metrics", &rc_sim::SimulationResult::metrics)
        .def_property_readonly("t", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().t, self);
        })
        .def_property_readonly("E_source", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().E_source, self);
        })
        .def_property_readonly("q_exact", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().q_exact, self);
        })
        .def_property_readonly("q_trans", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().q_trans, self);
        })
        .def_property_readonly("q_ss", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().q_ss, self);
        })
        .def_property_readonly("Vc_exact", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().Vc_exact, self);
        })
        .def_property_readonly("VR_exact", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().VR_exact, self);
        })
        .def_property_readonly("i_exact", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().i_exact, self);
        })
        .def_property_readonly("i_trans", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().i_trans, self);
        })
        .def_property_readonly("i_ss", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().i_ss, self);
        })
        .def_property_readonly("q_rk4", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().q_rk4, self);
        })
        .def_property_readonly("Vc_rk4", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().Vc_rk4, self);
        })
        .def_property_readonly("i_rk4", [](py::object self) {
            return as_numpy_view(self.cast<const rc_sim::SimulationResult&>().i_rk4, self);
        });

    py::class_<rc_sim::RCSolver>(m, "RCSolver")
        .def_static("compute_metrics", &rc_sim::RCSolver::compute_metrics,
                    py::arg("params"),
                    "Calcula las métricas físicas del circuito RC en tiempo constante O(1).")
        .def_static("simulate", &rc_sim::RCSolver::simulate,
                    py::arg("params"),
                    py::call_guard<py::gil_scoped_release>(),
                    "Ejecuta la simulación analítica y el integrador RK4 liberando el GIL.");
}

