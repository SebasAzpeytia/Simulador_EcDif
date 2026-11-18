"""Sistema de visualización de gráficas con selector por pestañas grandes y marcador sincronizado."""

from __future__ import annotations

from typing import Dict

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from rc_simulator.rc_core_cpp import SimulationResult
from rc_simulator.ui.theme import PALETTE


class PlotsDashboard(QWidget):
    """Panel de gráficas con selector de vista por pestañas para máxima legibilidad en presentaciones."""

    userScrubbedIndex = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        pg.setConfigOptions(antialias=True, background=PALETTE["plot_bg"], foreground=PALETTE["text_secondary"])

        self._last_result: SimulationResult | None = None
        self._active_view: str = "current"
        self._tab_buttons: Dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Barra de pestañas para elegir qué gráfica ver en grande (o las 3 juntas)
        tabs_bar = QHBoxLayout()
        tabs_bar.setContentsMargins(0, 0, 0, 0)
        tabs_bar.setSpacing(6)

        tab_specs = [
            ("current", "1. Corriente i(t)"),
            ("charge", "2. Carga q(t) y Voltaje V_C(t)"),
            ("voltage", "3. Comparador E(t) vs V_C(t)"),
            ("all", "Ver las 3 Juntas"),
        ]
        for key, title in tab_specs:
            btn = QPushButton(title)
            btn.setObjectName("ViewTabButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=key: self.set_view_mode(k))
            self._tab_buttons[key] = btn
            tabs_bar.addWidget(btn)

        tabs_bar.addStretch(1)

        # Lectura compacta del instante actual
        self.cursor_bar = QFrame()
        self.cursor_bar.setObjectName("CursorReadoutBar")
        cursor_layout = QHBoxLayout(self.cursor_bar)
        cursor_layout.setContentsMargins(10, 4, 10, 4)

        self.cursor_label = QLabel("Valores en t = 0.00 s")
        self.cursor_label.setObjectName("CursorText")
        cursor_layout.addWidget(self.cursor_label)
        tabs_bar.addWidget(self.cursor_bar)

        layout.addLayout(tabs_bar)

        # Lienzo PyQtGraph
        self.graphics_layout = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graphics_layout, stretch=1)

        self._init_plots()
        self.set_view_mode("current")

    def _style_plot(self, plot_item: pg.PlotItem, title: str, y_label: str, y_units: str) -> None:
        plot_item.setTitle(f"<span style='color:#F8FAFC;font-size:11pt;font-weight:700;'>{title}</span>")
        plot_item.setLabel("left", y_label, units=y_units, color=PALETTE["text_primary"])
        plot_item.setLabel("bottom", "Tiempo (t)", units="s", color=PALETTE["text_secondary"])
        plot_item.showGrid(x=True, y=True, alpha=0.28)
        plot_item.getAxis("left").setPen(pg.mkPen(color=PALETTE["border"], width=1))
        plot_item.getAxis("bottom").setPen(pg.mkPen(color=PALETTE["border"], width=1))

    def _init_plots(self) -> None:
        # ---------------------------------------------------------------------
        # 1. Gráfica de Corriente i(t), i_trans(t) e i_ss(t)
        # ---------------------------------------------------------------------
        self.plot_current: pg.PlotItem = self.graphics_layout.ci.addPlot(row=0, col=0)
        self._style_plot(
            self.plot_current,
            "1. Comportamiento de la Corriente: Total i(t), Transitoria i_trans(t) y Estacionaria i_ss(t)",
            "Corriente i",
            "A",
        )
        self.legend_current = self.plot_current.addLegend(
            offset=(-15, 10),
            labelTextColor=PALETTE["text_primary"],
            brush=pg.mkBrush(17, 24, 39, 220),
            pen=pg.mkPen(color=PALETTE["border"], width=1),
        )

        self.curve_i_ss = self.plot_current.plot(
            pen=pg.mkPen(color="#818CF8", width=1.8, style=Qt.PenStyle.DashLine),
            name="Estacionaria i_ss(t)",
        )
        self.curve_i_trans = self.plot_current.plot(
            pen=pg.mkPen(color="#F59E0B", width=2.2, style=Qt.PenStyle.DotLine),
            name="Transitoria i_trans(t) = K_i exp(-t/tau)",
        )
        self.curve_i_total = self.plot_current.plot(
            pen=pg.mkPen(color="#38BDF8", width=3.0),
            name="Corriente Total i(t)",
        )

        # ---------------------------------------------------------------------
        # 2. Gráfica de Carga q(t) [C] y Voltaje del Capacitor Vc(t) = q(t)/C [V]
        # ---------------------------------------------------------------------
        self.plot_charge: pg.PlotItem = self.graphics_layout.ci.addPlot(row=1, col=0)
        self._style_plot(
            self.plot_charge,
            "2. Acumulación de Carga q(t) y Voltaje en el Capacitor V_C(t) = q(t) / C",
            "Carga q(t)",
            "C",
        )
        self.plot_charge.getViewBox().setXLink(self.plot_current.getViewBox())
        self.legend_charge = self.plot_charge.addLegend(
            offset=(-15, 10),
            labelTextColor=PALETTE["text_primary"],
            brush=pg.mkBrush(17, 24, 39, 220),
            pen=pg.mkPen(color=PALETTE["border"], width=1),
        )

        self.plot_charge.showAxis("right")
        self.plot_charge.getAxis("right").setLabel("Voltaje Capacitor V_C(t)", units="V", color="#F43F5E")
        self.plot_charge.getAxis("right").setPen(pg.mkPen(color="#F43F5E", width=1))

        self.vc_viewbox = pg.ViewBox()
        charge_scene = self.plot_charge.scene()
        if charge_scene is not None:
            charge_scene.addItem(self.vc_viewbox)
        self.plot_charge.getAxis("right").linkToView(self.vc_viewbox)
        self.vc_viewbox.setXLink(self.plot_charge.getViewBox())

        self.curve_q_trans = self.plot_charge.plot(
            pen=pg.mkPen(color="#F59E0B", width=2.0, style=Qt.PenStyle.DotLine),
            name="Carga Transitoria q_trans(t) [C]",
        )
        self.curve_q_exact = self.plot_charge.plot(
            pen=pg.mkPen(color="#10B981", width=3.0),
            name="Carga Total q(t) [C]",
        )

        self.curve_vc_dual = pg.PlotCurveItem(
            pen=pg.mkPen(color="#F43F5E", width=2.0, style=Qt.PenStyle.DashLine),
            name="Voltaje V_C(t) = q(t)/C [V]",
        )
        self.vc_viewbox.addItem(self.curve_vc_dual)
        self.legend_charge.addItem(self.curve_vc_dual, "Voltaje V_C(t) [V] (Eje Der.)")

        self.plot_charge.getViewBox().sigResized.connect(self._sync_vc_viewbox)

        # ---------------------------------------------------------------------
        # 3. Gráfica Comparadora de Voltajes: Fuente E(t) vs Capacitor V_C(t)
        # ---------------------------------------------------------------------
        self.plot_voltage: pg.PlotItem = self.graphics_layout.ci.addPlot(row=2, col=0)
        self._style_plot(
            self.plot_voltage,
            "3. Comparador de Voltajes: Fuente E(t) = E_0 cos(omega*t) vs. Capacitor V_C(t)",
            "Voltaje V",
            "V",
        )
        self.plot_voltage.getViewBox().setXLink(self.plot_current.getViewBox())
        self.legend_voltage = self.plot_voltage.addLegend(
            offset=(-15, 10),
            labelTextColor=PALETTE["text_primary"],
            brush=pg.mkBrush(17, 24, 39, 220),
            pen=pg.mkPen(color=PALETTE["border"], width=1),
        )

        self.curve_e_source = self.plot_voltage.plot(
            pen=pg.mkPen(color="#94A3B8", width=2.2, style=Qt.PenStyle.DashLine),
            name="Fuente E(t)",
        )
        self.curve_vc_compare = self.plot_voltage.plot(
            pen=pg.mkPen(color="#F43F5E", width=3.0),
            name="Capacitor V_C(t)",
        )

        # ---------------------------------------------------------------------
        # Marcadores verticales de tiempo sincronizados con la animación
        # ---------------------------------------------------------------------
        cursor_pen = pg.mkPen(color="#38BDF8", width=1.6, style=Qt.PenStyle.SolidLine)
        self.vline_current = pg.InfiniteLine(angle=90, movable=False, pen=cursor_pen)
        self.vline_charge = pg.InfiniteLine(angle=90, movable=False, pen=cursor_pen)
        self.vline_voltage = pg.InfiniteLine(angle=90, movable=False, pen=cursor_pen)

        self.plot_current.addItem(self.vline_current, ignoreBounds=True)
        self.plot_charge.addItem(self.vline_charge, ignoreBounds=True)
        self.plot_voltage.addItem(self.vline_voltage, ignoreBounds=True)

        # Puntos luminosos sobre cada curva principal en el instante actual t
        self.dot_current = self.plot_current.plot(
            [], [], pen=None, symbol="o", symbolSize=10, symbolBrush="#38BDF8", symbolPen="#FFFFFF"
        )
        self.dot_charge = self.plot_charge.plot(
            [], [], pen=None, symbol="o", symbolSize=10, symbolBrush="#10B981", symbolPen="#FFFFFF"
        )
        self.dot_voltage = self.plot_voltage.plot(
            [], [], pen=None, symbol="o", symbolSize=10, symbolBrush="#F43F5E", symbolPen="#FFFFFF"
        )

        # Línea de referencia del tiempo de establecimiento t_s = 4*tau
        ts_pen = pg.mkPen(color="#F59E0B", width=1.2, style=Qt.PenStyle.DashLine)
        self.ts_line_current = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen=ts_pen,
            label="Establecimiento (4*tau)",
            labelOpts={"position": 0.88, "color": "#F59E0B"},
        )
        self.plot_current.addItem(self.ts_line_current, ignoreBounds=True)

        if self.graphics_layout.sceneObj is not None:
            self.graphics_layout.sceneObj.sigMouseClicked.connect(self._on_mouse_clicked)

    def set_view_mode(self, mode: str) -> None:
        self._active_view = mode
        for key, btn in self._tab_buttons.items():
            btn.setProperty("active", "true" if key == mode else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        show_current = mode in ("current", "all")
        show_charge = mode in ("charge", "all")
        show_voltage = mode in ("voltage", "all")

        self.plot_current.setVisible(show_current)
        self.plot_charge.setVisible(show_charge)
        self.vc_viewbox.setVisible(show_charge)
        self.plot_voltage.setVisible(show_voltage)

        self._sync_vc_viewbox()

    @property
    def active_view(self) -> str:
        return self._active_view

    def _sync_vc_viewbox(self) -> None:
        charge_vb = self.plot_charge.getViewBox()
        self.vc_viewbox.setGeometry(charge_vb.sceneBoundingRect())
        self.vc_viewbox.linkedViewChanged(charge_vb, self.vc_viewbox.XAxis)

    def update_plots(self, res: SimulationResult, capacitance_f: float) -> None:
        self._last_result = res
        t = res.t

        # 1. Gráfica de Corriente
        self.curve_i_total.setData(t, res.i_exact)
        self.curve_i_trans.setData(t, res.i_trans)
        self.curve_i_ss.setData(t, res.i_ss)
        self.ts_line_current.setPos(res.metrics.ts_4tau)

        # 2. Gráfica de Carga y V_C(t)
        self.curve_q_exact.setData(t, res.q_exact)
        self.curve_q_trans.setData(t, res.q_trans)
        self.curve_vc_dual.setData(t, res.Vc_exact)

        q_min = float(np.min(res.q_exact))
        q_max = float(np.max(res.q_exact))
        q_trans_min = float(np.min(res.q_trans))
        q_trans_max = float(np.max(res.q_trans))
        y_min_q = min(q_min, q_trans_min)
        y_max_q = max(q_max, q_trans_max)
        if abs(y_max_q - y_min_q) < 1e-9:
            y_min_q -= 0.1
            y_max_q += 0.1
        else:
            pad = 0.10 * (y_max_q - y_min_q)
            y_min_q -= pad
            y_max_q += pad

        self.plot_charge.getViewBox().setYRange(y_min_q, y_max_q, padding=0)
        self.vc_viewbox.setYRange(y_min_q / capacitance_f, y_max_q / capacitance_f, padding=0)
        self._sync_vc_viewbox()

        # 3. Gráfica Comparadora de Voltajes
        self.curve_e_source.setData(t, res.E_source)
        self.curve_vc_compare.setData(t, res.Vc_exact)

        self.set_time_index(0)

    def set_time_index(self, idx: int) -> None:
        if self._last_result is None:
            return
        t_arr = self._last_result.t
        if len(t_arr) == 0:
            return

        clamped_idx = max(0, min(len(t_arr) - 1, idx))
        t_val = float(t_arr[clamped_idx])

        self.vline_current.setPos(t_val)
        self.vline_charge.setPos(t_val)
        self.vline_voltage.setPos(t_val)

        i_tot = float(self._last_result.i_exact[clamped_idx])
        q_tot = float(self._last_result.q_exact[clamped_idx])
        vc_val = float(self._last_result.Vc_exact[clamped_idx])
        e_val = float(self._last_result.E_source[clamped_idx])

        self.dot_current.setData([t_val], [i_tot])
        self.dot_charge.setData([t_val], [q_tot])
        self.dot_voltage.setData([t_val], [vc_val])

        self.cursor_label.setText(
            f"t = {t_val:5.2f} s  |  i = {i_tot:+5.2f} A  |  q = {q_tot:+5.2f} C  |  V_C = {vc_val:+6.1f} V"
        )

    def _on_mouse_clicked(self, event) -> None:
        if self._last_result is None:
            return
        pos: QPointF = event.scenePos()
        target_vb = None
        for plot_item in (self.plot_current, self.plot_charge, self.plot_voltage):
            if plot_item.isVisible() and plot_item.sceneBoundingRect().contains(pos):
                target_vb = plot_item.getViewBox()
                break

        if target_vb is None:
            return

        mouse_point = target_vb.mapSceneToView(pos)
        t_cursor = float(mouse_point.x())
        t_arr = self._last_result.t
        if len(t_arr) == 0:
            return

        t_clamped = max(float(t_arr[0]), min(float(t_arr[-1]), t_cursor))
        idx = int(np.searchsorted(t_arr, t_clamped))
        idx = max(0, min(len(t_arr) - 1, idx))
        self.set_time_index(idx)
        self.userScrubbedIndex.emit(idx)
