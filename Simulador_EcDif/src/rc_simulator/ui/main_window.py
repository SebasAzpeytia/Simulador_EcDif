"""Ventana principal rediseñada para presentación con esquemático animado del circuito RC."""

from __future__ import annotations

from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from rc_simulator.presets import PRESETS, PresetScenario
from rc_simulator.rc_core_cpp import CircuitParams, RCSolver
from rc_simulator.ui.circuit_schematic import CircuitAnimationPanel
from rc_simulator.ui.metrics_panel import MetricsPanel
from rc_simulator.ui.parameter_slider import ParameterSlider
from rc_simulator.ui.plots_widget import PlotsDashboard
from rc_simulator.ui.theme import DARK_TECH_STYLESHEET


class MainWindow(QMainWindow):
    """Dashboard interactivo de presentación para el circuito RC en serie."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Simulador Interactivo de Circuito RC en Serie")
        self.resize(1500, 940)
        self.setMinimumSize(1180, 760)
        self.setStyleSheet(DARK_TECH_STYLESHEET)

        self._updating_preset = False
        self._active_preset: PresetScenario | None = None
        self._preset_buttons: Dict[str, QPushButton] = {}

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---------------------------------------------------------------------
        # Menú Lateral Izquierdo Simplificado (415 px)
        # ---------------------------------------------------------------------
        sidebar_container = QFrame()
        sidebar_container.setObjectName("SidebarFrame")
        sidebar_container.setFixedWidth(415)

        sidebar_outer_layout = QVBoxLayout(sidebar_container)
        sidebar_outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        sidebar_content = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_content)
        sidebar_layout.setContentsMargins(14, 14, 14, 14)
        sidebar_layout.setSpacing(10)

        sidebar_layout.addWidget(self._build_header_banner())
        sidebar_layout.addWidget(self._build_presets_card())
        sidebar_layout.addWidget(self._build_parameters_card())

        self.metrics_panel = MetricsPanel()
        sidebar_layout.addWidget(self.metrics_panel)
        sidebar_layout.addStretch(1)

        scroll_area.setWidget(sidebar_content)
        sidebar_outer_layout.addWidget(scroll_area)

        # ---------------------------------------------------------------------
        # Área Principal Derecha: Circuito Animado (Arriba) + Gráficas (Abajo)
        # ---------------------------------------------------------------------
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(12)

        self.circuit_panel = CircuitAnimationPanel()
        self.plots_dashboard = PlotsDashboard()

        # Sincronización bidireccional de tiempo entre animación y gráficas
        self.circuit_panel.timeIndexChanged.connect(self.plots_dashboard.set_time_index)
        self.plots_dashboard.userScrubbedIndex.connect(
            lambda idx: self.circuit_panel.set_time_index(idx, emit_signal=False)
        )

        right_layout.addWidget(self.circuit_panel, stretch=4)
        right_layout.addWidget(self.plots_dashboard, stretch=6)

        root_layout.addWidget(sidebar_container)
        root_layout.addWidget(right_panel, stretch=1)

        # Cargar escenario inicial (Caso Base AF6)
        self.apply_preset(PRESETS["af6_base"])

    def _build_header_banner(self) -> QFrame:
        banner = QFrame()
        banner.setObjectName("HeaderBanner")
        layout = QVBoxLayout(banner)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        title = QLabel("SIMULADOR DE CIRCUITO RC EN SERIE")
        title.setObjectName("AppTitle")

        eq_label = QLabel("R * (dq/dt) + (1/C) * q = E_0 * cos(omega * t)")
        eq_label.setObjectName("AppSubtitle")

        desc = QLabel("Condición inicial: q(0) = q_0")
        desc.setObjectName("MetricSubtext")

        layout.addWidget(title)
        layout.addWidget(eq_label)
        layout.addWidget(desc)
        return banner

    def _build_presets_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("SectionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        sec_title = QLabel("1. Escenarios de Demostración")
        sec_title.setObjectName("SectionTitle")
        layout.addWidget(sec_title)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        for idx, (key, preset) in enumerate(PRESETS.items()):
            btn = QPushButton(preset.title)
            btn.setObjectName("PresetButton")
            btn.setToolTip(f"{preset.subtitle}\n\n{preset.description}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, p=preset: self.apply_preset(p))
            self._preset_buttons[key] = btn
            grid.addWidget(btn, idx // 2, idx % 2)

        layout.addLayout(grid)

        info_box = QFrame()
        info_box.setObjectName("PresetInfoBox")
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(10, 8, 10, 8)

        self.preset_desc_label = QLabel("")
        self.preset_desc_label.setObjectName("PresetInfoText")
        self.preset_desc_label.setWordWrap(True)
        info_layout.addWidget(self.preset_desc_label)

        layout.addWidget(info_box)
        return card

    def _build_parameters_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("SectionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        sec_title = QLabel("2. Variables del Circuito")
        sec_title.setObjectName("SectionTitle")
        layout.addWidget(sec_title)

        self.slider_R = ParameterSlider(
            label_text="Resistencia (R)",
            unit="Ohm",
            min_val=1.0,
            max_val=1000.0,
            default_val=50.0,
            decimals=1,
            step=5.0,
            tooltip="Resistencia eléctrica en serie R [1 Ohm a 1000 Ohm]",
        )
        self.slider_C = ParameterSlider(
            label_text="Capacitancia (C)",
            unit="mF",
            min_val=0.1,
            max_val=50.0,
            default_val=10.0,
            decimals=1,
            step=0.5,
            tooltip="Capacitancia C en milifaradios (10 mF = 0.01 F)",
        )
        self.slider_E0 = ParameterSlider(
            label_text="Voltaje de la Fuente (E_0)",
            unit="V",
            min_val=0.0,
            max_val=500.0,
            default_val=200.0,
            decimals=0,
            step=10.0,
            tooltip="Amplitud pico de la fuente sinusoidal E_0 [0 V a 500 V]",
        )
        self.slider_omega = ParameterSlider(
            label_text="Frecuencia Angular (omega)",
            unit="rad/s",
            min_val=0.5,
            max_val=50.0,
            default_val=2.0,
            decimals=1,
            step=0.5,
            tooltip="Frecuencia angular de la fuente omega [0.5 rad/s a 50 rad/s]",
        )
        self.slider_q0 = ParameterSlider(
            label_text="Carga Inicial (q_0)",
            unit="C",
            min_val=-1.0,
            max_val=1.0,
            default_val=0.0,
            decimals=2,
            step=0.05,
            tooltip="Carga inicial almacenada en el capacitor q(0) [-1 C a 1 C]",
        )

        for w in (
            self.slider_R,
            self.slider_C,
            self.slider_E0,
            self.slider_omega,
            self.slider_q0,
        ):
            layout.addWidget(w)
            w.valueChanged.connect(self._on_user_parameter_changed)

        return card

    def _highlight_preset_button(self, active_key: str | None) -> None:
        for key, btn in self._preset_buttons.items():
            is_active = key == active_key
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def apply_preset(self, preset: PresetScenario) -> None:
        self._updating_preset = True
        self._active_preset = preset
        try:
            self.slider_R.set_value(preset.R_ohm, emit_signal=False)
            self.slider_C.set_value(preset.C_mf, emit_signal=False)
            self.slider_E0.set_value(preset.E0_volt, emit_signal=False)
            self.slider_omega.set_value(preset.omega_rad_s, emit_signal=False)
            self.slider_q0.set_value(preset.q0_coulomb, emit_signal=False)

            self.preset_desc_label.setText(f"{preset.title}: {preset.description}")
            self._highlight_preset_button(preset.key)
        finally:
            self._updating_preset = False

        self.circuit_panel.reset_animation()
        self.run_simulation()

    def _on_user_parameter_changed(self, _value: float) -> None:
        if self._updating_preset:
            return
        self._active_preset = None
        self._highlight_preset_button(None)
        self.preset_desc_label.setText(
            "Modo Personalizado: Ajustando parámetros manualmente en tiempo real."
        )
        self.run_simulation()

    def get_current_params(self) -> CircuitParams:
        r_ohm = self.slider_R.value()
        c_farad = self.slider_C.value() * 1e-3  # Conversión de mF a Faradios
        e0_volt = self.slider_E0.value()
        omega = self.slider_omega.value()
        q0 = self.slider_q0.value()

        if self._active_preset is not None and not self._active_preset.auto_t_sim:
            t_sim = self._active_preset.manual_t_sim_s
        else:
            tau = r_ohm * c_farad
            # Horizonte automático de 6*tau acotado entre 1.5 s y 15.0 s para buena visualización
            t_sim = min(15.0, max(1.5, 6.0 * tau))

        return CircuitParams(
            R=r_ohm,
            C=c_farad,
            E0=e0_volt,
            omega=omega,
            q0=q0,
            t_sim=t_sim,
            num_points=2500,
        )

    def run_simulation(self) -> None:
        params = self.get_current_params()
        result = RCSolver.simulate(params)

        self.metrics_panel.update_metrics(result.metrics)
        self.plots_dashboard.update_plots(result, params.C)
        self.circuit_panel.load_simulation(result, params)
