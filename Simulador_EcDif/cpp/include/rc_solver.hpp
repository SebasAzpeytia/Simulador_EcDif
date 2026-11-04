#pragma once

#include <cstddef>
#include <vector>

namespace rc_sim {

/**
 * @brief Parámetros de entrada para el circuito RC en serie excitado por E(t) = E0 * cos(omega * t)
 *        Ecuación diferencial: R * (dq/dt) + (1/C) * q = E0 * cos(omega * t), con q(0) = q0
 */
struct CircuitParams {
    double R = 50.0;               // Resistencia [Ohm]
    double C = 0.01;               // Capacitancia [F]
    double E0 = 200.0;             // Amplitud de la fuente de voltaje [V]
    double omega = 2.0;            // Frecuencia angular [rad/s]
    double q0 = 0.0;               // Carga inicial en el capacitor q(0) [C]
    double t_sim = 3.0;            // Tiempo total de simulación [s]
    std::size_t num_points = 2500; // Número de muestras discretas en [0, t_sim]
};

/**
 * @brief Métricas físicas y de validación numérica del circuito RC
 */
struct CircuitMetrics {
    double tau = 0.0;        // Constante de tiempo: R * C [s]
    double ts_4tau = 0.0;    // Tiempo de establecimiento (criterio 2%): 4 * tau [s]
    double ts_5tau = 0.0;    // Tiempo de establecimiento (criterio 1%): 5 * tau [s]
    double Xc = 0.0;         // Reactancia capacitiva: 1 / (omega * C) [Ohm]
    double Z = 0.0;          // Impedancia total: sqrt(R^2 + Xc^2) [Ohm]
    double phi_rad = 0.0;    // Ángulo de desfase: arctan(1 / (omega * R * C)) [rad]
    double phi_deg = 0.0;    // Ángulo de desfase en grados [deg]
    double I_max = 0.0;      // Amplitud de corriente estacionaria: E0 / Z [A]
    double Vc_max = 0.0;     // Amplitud de voltaje estacionario en capacitor: I_max * Xc [V]
    double i_0 = 0.0;        // Corriente inicial instantánea: (E(0) - q0 / C) / R [A]
    double K_q = 0.0;        // Coeficiente transitorio de carga: q0 - q_ss(0) [C]
    double K_i = 0.0;        // Coeficiente transitorio de corriente: -K_q / tau [A]
    double max_err_q = 0.0;  // Error absoluto máximo |q_exact - q_rk4| [C]
    double max_err_i = 0.0;  // Error absoluto máximo |i_exact - i_rk4| [A]
    double rmse_q = 0.0;     // Error cuadrático medio de carga [C]
    double rmse_i = 0.0;     // Error cuadrático medio de corriente [A]
};

/**
 * @brief Resultados completos de la simulación temporal (Analítica Exacta + RK4)
 */
struct SimulationResult {
    CircuitMetrics metrics;
    std::vector<double> t;         // Vector de tiempo [s]
    std::vector<double> E_source;  // Fuente de voltaje E(t) = E0 * cos(omega * t) [V]
    std::vector<double> q_exact;   // Carga total analítica q(t) = q_trans(t) + q_ss(t) [C]
    std::vector<double> q_trans;   // Componente transitoria de carga K_q * exp(-t/tau) [C]
    std::vector<double> q_ss;      // Componente estacionaria de carga q_ss(t) [C]
    std::vector<double> Vc_exact;  // Voltaje del capacitor analítico Vc(t) = q(t) / C [V]
    std::vector<double> VR_exact;  // Voltaje en la resistencia VR(t) = R * i(t) [V]
    std::vector<double> i_exact;   // Corriente total analítica i(t) = i_trans(t) + i_ss(t) [A]
    std::vector<double> i_trans;   // Componente transitoria de corriente K_i * exp(-t/tau) [A]
    std::vector<double> i_ss;      // Componente estacionaria de corriente i_ss(t) [A]
    std::vector<double> q_rk4;     // Carga obtenida por Runge-Kutta de 4to orden [C]
    std::vector<double> Vc_rk4;    // Voltaje del capacitor obtenido por RK4 [V]
    std::vector<double> i_rk4;     // Corriente obtenida por RK4 [A]
};

/**
 * @brief Motor de resolución analítica y numérica (RK4) en C++20
 */
class RCSolver {
public:
    [[nodiscard]] static CircuitMetrics compute_metrics(const CircuitParams& params) noexcept;
    [[nodiscard]] static SimulationResult simulate(const CircuitParams& params);
};

} // namespace rc_sim

