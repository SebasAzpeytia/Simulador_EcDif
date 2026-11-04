#include "rc_solver.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>
#include <stdexcept>

namespace rc_sim {

namespace {
constexpr double kMinPositive = 1e-12;
} // namespace

CircuitMetrics RCSolver::compute_metrics(const CircuitParams& params) noexcept {
    CircuitMetrics m{};

    const double R = std::max(params.R, kMinPositive);
    const double C = std::max(params.C, kMinPositive);
    const double omega = std::max(std::abs(params.omega), kMinPositive);
    const double E0 = params.E0;
    const double q0 = params.q0;

    m.tau = R * C;
    m.ts_4tau = 4.0 * m.tau;
    m.ts_5tau = 5.0 * m.tau;

    m.Xc = 1.0 / (omega * C);
    m.Z = std::hypot(R, m.Xc);

    m.phi_rad = std::atan2(1.0, omega * m.tau);
    m.phi_deg = m.phi_rad * (180.0 / std::numbers::pi);

    m.I_max = E0 / m.Z;
    m.Vc_max = m.I_max * m.Xc;

    // En t = 0, E(0) = E0 * cos(0) = E0
    m.i_0 = (E0 - (q0 / C)) / R;

    // Estado estacionario en t = 0:
    // q_ss(t) = (C * E0 / (1 + (omega * tau)^2)) * (cos(omega * t) + omega * tau * sin(omega * t))
    const double omega_tau = omega * m.tau;
    const double denom = 1.0 + omega_tau * omega_tau;
    const double q_ss_0 = (C * E0) / denom;

    m.K_q = q0 - q_ss_0;
    m.K_i = -m.K_q / m.tau;

    return m;
}

SimulationResult RCSolver::simulate(const CircuitParams& params) {
    if (params.R <= 0.0) {
        throw std::invalid_argument("La resistencia R debe ser estrictamente positiva.");
    }
    if (params.C <= 0.0) {
        throw std::invalid_argument("La capacitancia C debe ser estrictamente positiva.");
    }
    if (params.t_sim <= 0.0) {
        throw std::invalid_argument("El tiempo de simulacion t_sim debe ser estrictamente positivo.");
    }
    const std::size_t N = std::max<std::size_t>(params.num_points, 2);

    SimulationResult res;
    res.metrics = compute_metrics(params);

    res.t.resize(N);
    res.E_source.resize(N);
    res.q_exact.resize(N);
    res.q_trans.resize(N);
    res.q_ss.resize(N);
    res.Vc_exact.resize(N);
    res.VR_exact.resize(N);
    res.i_exact.resize(N);
    res.i_trans.resize(N);
    res.i_ss.resize(N);
    res.q_rk4.resize(N);
    res.Vc_rk4.resize(N);
    res.i_rk4.resize(N);

    const double R = params.R;
    const double C = params.C;
    const double inv_R = 1.0 / R;
    const double inv_C = 1.0 / C;
    const double E0 = params.E0;
    const double omega = params.omega;
    const double tau = res.metrics.tau;
    const double inv_tau = 1.0 / tau;
    const double K_q = res.metrics.K_q;
    const double K_i = res.metrics.K_i;
    const double I_max = res.metrics.I_max;
    const double phi = res.metrics.phi_rad;

    const double omega_tau = omega * tau;
    const double q_ss_scale = (C * E0) / (1.0 + omega_tau * omega_tau);

    const double dt = params.t_sim / static_cast<double>(N - 1);

    // Función derivada de la EDO: dq/dt = f(t, q) = (E0 * cos(omega * t) - q / C) / R
    const auto ode_rhs = [E0, omega, inv_C, inv_R](double time, double charge) noexcept -> double {
        return (E0 * std::cos(omega * time) - charge * inv_C) * inv_R;
    };

    double q_num = params.q0;
    double max_err_q = 0.0;
    double max_err_i = 0.0;
    double sum_sq_err_q = 0.0;
    double sum_sq_err_i = 0.0;

    for (std::size_t idx = 0; idx < N; ++idx) {
        const double t_val = static_cast<double>(idx) * dt;
        res.t[idx] = t_val;

        const double cos_wt = std::cos(omega * t_val);
        const double sin_wt = std::sin(omega * t_val);
        const double exp_factor = std::exp(-t_val * inv_tau);

        // Fuente sinusoidal E(t)
        const double E_val = E0 * cos_wt;
        res.E_source[idx] = E_val;

        // Solución analítica exacta para la carga q(t)
        const double q_tr = K_q * exp_factor;
        const double q_st = q_ss_scale * (cos_wt + omega_tau * sin_wt);
        const double q_tot = q_tr + q_st;

        res.q_trans[idx] = q_tr;
        res.q_ss[idx] = q_st;
        res.q_exact[idx] = q_tot;
        res.Vc_exact[idx] = q_tot * inv_C;

        // Solución analítica exacta para la corriente i(t)
        const double i_tr = K_i * exp_factor;
        const double i_st = I_max * std::cos(omega * t_val + phi);
        const double i_tot = i_tr + i_st;

        res.i_trans[idx] = i_tr;
        res.i_ss[idx] = i_st;
        res.i_exact[idx] = i_tot;
        res.VR_exact[idx] = R * i_tot;

        // Estado numérico RK4 en el paso actual t_val
        const double i_num = ode_rhs(t_val, q_num);
        res.q_rk4[idx] = q_num;
        res.Vc_rk4[idx] = q_num * inv_C;
        res.i_rk4[idx] = i_num;

        // Acumulación de métricas de validación empírica (Analítica vs RK4)
        const double err_q = std::abs(q_tot - q_num);
        const double err_i = std::abs(i_tot - i_num);
        max_err_q = std::max(max_err_q, err_q);
        max_err_i = std::max(max_err_i, err_i);
        sum_sq_err_q += err_q * err_q;
        sum_sq_err_i += err_i * err_i;

        // Avance al siguiente paso temporal mediante Runge-Kutta de 4to orden (RK4)
        if (idx + 1 < N) {
            const double half_dt = 0.5 * dt;
            const double k1 = i_num;
            const double k2 = ode_rhs(t_val + half_dt, q_num + half_dt * k1);
            const double k3 = ode_rhs(t_val + half_dt, q_num + half_dt * k2);
            const double k4 = ode_rhs(t_val + dt, q_num + dt * k3);
            q_num += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
        }
    }

    res.metrics.max_err_q = max_err_q;
    res.metrics.max_err_i = max_err_i;
    res.metrics.rmse_q = std::sqrt(sum_sq_err_q / static_cast<double>(N));
    res.metrics.rmse_i = std::sqrt(sum_sq_err_i / static_cast<double>(N));

    return res;
}

} // namespace rc_sim

