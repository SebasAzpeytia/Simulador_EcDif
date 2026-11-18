"""Pruebas unitarias y de integración para el núcleo C++20 (rc_core_cpp) y la interfaz PySide6."""

import math
import os

import numpy as np
import pytest

from rc_simulator.presets import PRESETS
from rc_simulator.rc_core_cpp import CircuitParams, RCSolver


def test_af6_base_metrics_exact():
    """Verifica las métricas físicas exactas del Caso Base AF6:
    R=50 Ohm, C=0.01 F, E0=200 V, omega=2 rad/s, q0=0 C.
    """
    params = CircuitParams(R=50.0, C=0.01, E0=200.0, omega=2.0, q0=0.0, t_sim=3.0, num_points=2500)
    m = RCSolver.compute_metrics(params)

    assert math.isclose(m.tau, 0.5, rel_tol=1e-12)
    assert math.isclose(m.ts_4tau, 2.0, rel_tol=1e-12)
    assert math.isclose(m.ts_5tau, 2.5, rel_tol=1e-12)
    assert math.isclose(m.Xc, 50.0, rel_tol=1e-12)
    assert math.isclose(m.Z, 50.0 * math.sqrt(2.0), rel_tol=1e-12)
    assert math.isclose(m.phi_rad, math.pi / 4.0, rel_tol=1e-12)
    assert math.isclose(m.phi_deg, 45.0, rel_tol=1e-12)
    assert math.isclose(m.I_max, 2.0 * math.sqrt(2.0), rel_tol=1e-12)
    assert math.isclose(m.i_0, 4.0, rel_tol=1e-12)
    assert math.isclose(m.K_q, -1.0, rel_tol=1e-12)
    assert math.isclose(m.K_i, 2.0, rel_tol=1e-12)


def test_kirchhoff_voltage_law_and_initial_conditions():
    """Verifica que la solución analítica satisfaga R*i(t) + q(t)/C = E(t) en todo t y q(0) = q0."""
    params = CircuitParams(R=75.0, C=0.008, E0=150.0, omega=6.5, q0=-0.35, t_sim=4.0, num_points=3000)
    res = RCSolver.simulate(params)

    assert math.isclose(res.q_exact[0], params.q0, abs_tol=1e-14)
    assert math.isclose(res.i_exact[0], res.metrics.i_0, abs_tol=1e-13)

    # Ley de Voltajes de Kirchhoff en todo instante: V_R(t) + V_C(t) == E(t)
    kvl_lhs = res.VR_exact + res.Vc_exact
    assert np.allclose(kvl_lhs, res.E_source, rtol=1e-12, atol=1e-12)

    # Aditividad de componentes transitoria y estacionaria
    assert np.allclose(res.q_trans + res.q_ss, res.q_exact, rtol=1e-14, atol=1e-14)
    assert np.allclose(res.i_trans + res.i_ss, res.i_exact, rtol=1e-14, atol=1e-14)


def test_rk4_empirical_validation_accuracy():
    """Verifica que el resolvedor numérico RK4 converja con alta precisión a la solución analítica."""
    params = CircuitParams(R=50.0, C=0.01, E0=200.0, omega=2.0, q0=0.0, t_sim=3.0, num_points=2500)
    res = RCSolver.simulate(params)

    assert res.metrics.max_err_q < 1e-8
    assert res.metrics.max_err_i < 1e-7
    assert np.allclose(res.q_exact, res.q_rk4, atol=1e-8)
    assert np.allclose(res.i_exact, res.i_rk4, atol=1e-7)


def test_initial_discharge_pure_exponential():
    """Verifica el caso de descarga inicial con E0 = 0 V y q0 != 0 C."""
    params = CircuitParams(R=100.0, C=0.01, E0=0.0, omega=2.0, q0=0.8, t_sim=6.0, num_points=2000)
    res = RCSolver.simulate(params)

    tau = 1.0
    expected_q = 0.8 * np.exp(-res.t / tau)
    expected_i = -(0.8 / tau) * np.exp(-res.t / tau)

    assert np.allclose(res.q_exact, expected_q, atol=1e-14)
    assert np.allclose(res.i_exact, expected_i, atol=1e-14)
    assert np.allclose(res.q_ss, 0.0, atol=1e-15)
    assert np.allclose(res.i_ss, 0.0, atol=1e-15)


def test_invalid_parameters_raise():
    """Verifica validación de parámetros físicos inválidos en C++."""
    with pytest.raises(ValueError):
        RCSolver.simulate(CircuitParams(R=-10.0, C=0.01, E0=100.0, omega=2.0, q0=0.0, t_sim=1.0))
    with pytest.raises(ValueError):
        RCSolver.simulate(CircuitParams(R=10.0, C=0.0, E0=100.0, omega=2.0, q0=0.0, t_sim=1.0))


def test_ui_main_window_and_presets():
    """Verifica la inicialización de la interfaz gráfica y el cambio de todos los presets."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from rc_simulator.ui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    app.processEvents()

    for key, preset in PRESETS.items():
        window.apply_preset(preset)
        app.processEvents()
        assert math.isclose(window.slider_R.value(), preset.R_ohm, rel_tol=1e-4)
        assert math.isclose(window.slider_C.value(), preset.C_mf, rel_tol=1e-4)
        assert math.isclose(window.slider_E0.value(), preset.E0_volt, rel_tol=1e-4)
        assert math.isclose(window.slider_omega.value(), preset.omega_rad_s, rel_tol=1e-4)
        assert math.isclose(window.slider_q0.value(), preset.q0_coulomb, abs_tol=1e-4)

    # Verificar el cambio entre las 4 pestañas de gráficas y la sincronización temporal
    for view_key in ("current", "charge", "voltage", "all"):
        window.plots_dashboard.set_view_mode(view_key)
        app.processEvents()
        assert window.plots_dashboard.active_view == view_key

    # Pausar animación para verificar posicionamiento exacto manual en t
    window.circuit_panel.toggle_play()
    window.circuit_panel.set_time_index(450, emit_signal=True)
    app.processEvents()
    assert window.circuit_panel.time_slider.value() == 450

    window.close()
    window.deleteLater()
    app.processEvents()

