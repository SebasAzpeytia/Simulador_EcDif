"""Esquemático interactivo y animado a 60 FPS del circuito RC en serie."""

from __future__ import annotations

import math
from typing import Dict

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from rc_simulator.rc_core_cpp import CircuitParams, SimulationResult


class CircuitCanvas(QWidget):
    """Lienzo vectorial QPainter que dibuja el circuito RC y anima el flujo de corriente."""

    NUM_PARTICLES = 26

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(235)

        # Estado instantáneo para renderizado
        self._phase_offset: float = 0.0
        self._t_val: float = 0.0
        self._i_val: float = 0.0
        self._i_ref_max: float = 4.0
        self._q_val: float = 0.0
        self._vc_val: float = 0.0
        self._vc_ref_max: float = 200.0
        self._vr_val: float = 0.0
        self._e_val: float = 0.0
        self._r_ohm: float = 50.0
        self._c_mf: float = 10.0

    def set_circuit_state(
        self,
        t_val: float,
        i_val: float,
        i_ref_max: float,
        q_val: float,
        vc_val: float,
        vc_ref_max: float,
        vr_val: float,
        e_val: float,
        r_ohm: float,
        c_mf: float,
    ) -> None:
        self._t_val = t_val
        self._i_val = i_val
        self._i_ref_max = max(abs(i_ref_max), 0.1)
        self._q_val = q_val
        self._vc_val = vc_val
        self._vc_ref_max = max(abs(vc_ref_max), 1.0)
        self._vr_val = vr_val
        self._e_val = e_val
        self._r_ohm = r_ohm
        self._c_mf = c_mf
        self.update()

    def advance_particles(self, dt_sec: float) -> None:
        norm_i = max(-1.5, min(1.5, self._i_val / self._i_ref_max))
        # Velocidad visual proporcional a la corriente instantánea i(t)
        self._phase_offset = (self._phase_offset + norm_i * dt_sec * 0.55) % 1.0
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        w = float(self.width())
        h = float(self.height())

        # Fondo del lienzo
        bg_rect = QRectF(2.0, 2.0, w - 4.0, h - 4.0)
        painter.setPen(QPen(QColor("#1E293B"), 1.0))
        painter.setBrush(QBrush(QColor("#0B0F17")))
        painter.drawRoundedRect(bg_rect, 6.0, 6.0)

        # Geometría de la malla del circuito
        left_x = max(135.0, w * 0.19)
        right_x = min(w - 165.0, w * 0.78)
        top_y = 52.0
        bottom_y = h - 38.0
        mid_x = 0.5 * (left_x + right_x)
        mid_y = 0.5 * (top_y + bottom_y)

        # Coordenadas de componentes
        res_half_w = 54.0
        src_radius = 24.0
        cap_gap = 13.0
        cap_plate_half_w = 28.0

        # 1. Dibujar los conductores de la malla (dejando hueco para Fuente, Resistencia y Capacitor)
        wire_pen = QPen(QColor("#334155"), 3.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(wire_pen)

        # Rama izquierda (con hueco para la fuente E(t))
        painter.drawLine(QPointF(left_x, top_y), QPointF(left_x, mid_y - src_radius))
        painter.drawLine(QPointF(left_x, mid_y + src_radius), QPointF(left_x, bottom_y))

        # Rama superior (con hueco para la resistencia R)
        painter.drawLine(QPointF(left_x, top_y), QPointF(mid_x - res_half_w, top_y))
        painter.drawLine(QPointF(mid_x + res_half_w, top_y), QPointF(right_x, top_y))

        # Rama derecha (con hueco para las placas del capacitor C)
        painter.drawLine(QPointF(right_x, top_y), QPointF(right_x, mid_y - cap_gap))
        painter.drawLine(QPointF(right_x, mid_y + cap_gap), QPointF(right_x, bottom_y))

        # Rama inferior completa
        painter.drawLine(QPointF(right_x, bottom_y), QPointF(left_x, bottom_y))

        # 2. Dibujar Partículas de Corriente a lo largo del conductor
        self._draw_current_particles(painter, left_x, right_x, top_y, bottom_y, mid_y, cap_gap)

        # 3. Dibujar Fuente de Voltaje Sinusoidal E(t) en la rama izquierda
        self._draw_voltage_source(painter, left_x, mid_y, src_radius)

        # 4. Dibujar Resistencia R en la rama superior
        self._draw_resistor(painter, mid_x, top_y, res_half_w)

        # 5. Dibujar Capacitor C en la rama derecha
        self._draw_capacitor(painter, right_x, mid_y, cap_gap, cap_plate_half_w)

        # 6. Dibujar Indicador Central de Flujo de Corriente i(t)
        self._draw_center_flow_indicator(painter, mid_x, mid_y)

    def _draw_current_particles(
        self,
        painter: QPainter,
        left_x: float,
        right_x: float,
        top_y: float,
        bottom_y: float,
        mid_y: float,
        cap_gap: float,
    ) -> None:
        """Distribuye partículas a lo largo del conductor (desde la placa inferior a la superior)."""
        # Camino abierto desde la placa inferior del capacitor hasta la placa superior pasando por la fuente y R:
        # P0: (right_x, mid_y + cap_gap) -> P1: (right_x, bottom_y) -> P2: (left_x, bottom_y)
        # -> P3: (left_x, top_y) -> P4: (right_x, top_y) -> P5: (right_x, mid_y - cap_gap)
        pts = [
            QPointF(right_x, mid_y + cap_gap + 4.0),
            QPointF(right_x, bottom_y),
            QPointF(left_x, bottom_y),
            QPointF(left_x, top_y),
            QPointF(right_x, top_y),
            QPointF(right_x, mid_y - cap_gap - 4.0),
        ]

        seg_lengths = []
        total_len = 0.0
        for idx in range(len(pts) - 1):
            dx = pts[idx + 1].x() - pts[idx].x()
            dy = pts[idx + 1].y() - pts[idx].y()
            seg_len = math.hypot(dx, dy)
            seg_lengths.append(seg_len)
            total_len += seg_len

        if total_len <= 1.0:
            return

        intensity = min(1.0, abs(self._i_val) / self._i_ref_max)
        if abs(self._i_val) < 1e-3:
            particle_color = QColor("#64748B")
        elif self._i_val > 0:
            particle_color = QColor("#38BDF8")
        else:
            particle_color = QColor("#F59E0B")

        glow_color = QColor(particle_color)
        glow_color.setAlpha(int(65 + 110 * intensity))

        for k in range(self.NUM_PARTICLES):
            frac = (k / float(self.NUM_PARTICLES) + self._phase_offset) % 1.0
            target_dist = frac * total_len

            accum = 0.0
            px, py = pts[0].x(), pts[0].y()
            for idx, seg_len in enumerate(seg_lengths):
                if accum + seg_len >= target_dist or idx == len(seg_lengths) - 1:
                    local_t = (target_dist - accum) / max(seg_len, 1e-6)
                    px = pts[idx].x() + local_t * (pts[idx + 1].x() - pts[idx].x())
                    py = pts[idx].y() + local_t * (pts[idx + 1].y() - pts[idx].y())
                    break
                accum += seg_len

            # Halo exterior
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow_color))
            painter.drawEllipse(QPointF(px, py), 6.0, 6.0)

            # Núcleo de la partícula
            painter.setBrush(QBrush(particle_color))
            painter.drawEllipse(QPointF(px, py), 3.3, 3.3)

    def _draw_voltage_source(self, painter: QPainter, cx: float, cy: float, radius: float) -> None:
        # Círculo de la fuente
        painter.setPen(QPen(QColor("#38BDF8"), 2.2))
        painter.setBrush(QBrush(QColor("#111827")))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # Onda sinusoidal interna
        sine_path = QPainterPath()
        w_sine = radius * 1.15
        for step in range(25):
            u = step / 24.0
            x = cx - 0.5 * w_sine + u * w_sine
            y = cy - math.sin(u * 2.0 * math.pi) * (radius * 0.36)
            if step == 0:
                sine_path.moveTo(x, y)
            else:
                sine_path.lineTo(x, y)
        painter.setPen(QPen(QColor("#38BDF8"), 2.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(sine_path)

        # Signos de polaridad instantánea
        font_pol = QFont("JetBrains Mono", 11, QFont.Weight.Bold)
        painter.setFont(font_pol)
        top_sign = "+" if self._e_val >= 0 else "-"
        bot_sign = "-" if self._e_val >= 0 else "+"
        painter.setPen(QColor("#38BDF8" if self._e_val >= 0 else "#F43F5E"))
        painter.drawText(QRectF(cx + radius + 5.0, cy - radius - 2.0, 20.0, 18.0), Qt.AlignmentFlag.AlignCenter, top_sign)
        painter.setPen(QColor("#94A3B8"))
        painter.drawText(QRectF(cx + radius + 5.0, cy + radius - 16.0, 20.0, 18.0), Qt.AlignmentFlag.AlignCenter, bot_sign)

        # Etiqueta lateral izquierda de la fuente
        label_rect = QRectF(8.0, cy - 32.0, max(100.0, cx - radius - 14.0), 64.0)
        painter.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        painter.setPen(QColor("#E2E8F0"))
        painter.drawText(
            QRectF(label_rect.left(), label_rect.top(), label_rect.width(), 20.0),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            "Fuente AC E(t)",
        )
        painter.setFont(QFont("JetBrains Mono", 11, QFont.Weight.Bold))
        painter.setPen(QColor("#38BDF8"))
        painter.drawText(
            QRectF(label_rect.left(), label_rect.top() + 20.0, label_rect.width(), 22.0),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            f"{self._e_val:+6.1f} V",
        )

    def _draw_resistor(self, painter: QPainter, cx: float, cy: float, half_w: float) -> None:
        # Halo térmico proporcional a |V_R(t)|
        vr_ratio = min(1.0, abs(self._vr_val) / max(self._vc_ref_max, 1.0))
        if vr_ratio > 0.03:
            glow = QColor("#F59E0B")
            glow.setAlpha(int(25 + 95 * vr_ratio))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow))
            painter.drawRoundedRect(QRectF(cx - half_w - 6.0, cy - 16.0, 2.0 * half_w + 12.0, 32.0), 10.0, 10.0)

        # Zigzag de la resistencia
        zig_path = QPainterPath()
        zig_path.moveTo(cx - half_w, cy)
        num_teeth = 6
        step_x = (2.0 * half_w) / (num_teeth * 2.0)
        amp_y = 11.0
        for k in range(num_teeth * 2):
            x = (cx - half_w) + (k + 0.5) * step_x
            y = cy - amp_y if (k % 2 == 0) else cy + amp_y
            zig_path.lineTo(x, y)
        zig_path.lineTo(cx + half_w, cy)

        painter.setPen(QPen(QColor("#F59E0B"), 2.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(zig_path)

        # Etiqueta sobre la resistencia
        painter.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        painter.setPen(QColor("#F8FAFC"))
        painter.drawText(
            QRectF(cx - 140.0, cy - 42.0, 280.0, 20.0),
            Qt.AlignmentFlag.AlignCenter,
            f"Resistencia R ({self._r_ohm:.0f} Ohm)   |   V_R = {self._vr_val:+6.1f} V",
        )

    def _draw_capacitor(
        self,
        painter: QPainter,
        cx: float,
        cy: float,
        gap: float,
        plate_half_w: float,
    ) -> None:
        charge_ratio = max(-1.0, min(1.0, self._vc_val / self._vc_ref_max))
        abs_ratio = abs(charge_ratio)

        top_color = QColor("#38BDF8") if charge_ratio >= 0 else QColor("#F43F5E")
        bot_color = QColor("#F43F5E") if charge_ratio >= 0 else QColor("#38BDF8")
        if abs_ratio < 0.02:
            top_color = QColor("#94A3B8")
            bot_color = QColor("#94A3B8")

        # Halo de carga alrededor de las placas
        if abs_ratio > 0.03:
            halo_top = QColor(top_color)
            halo_top.setAlpha(int(35 + 115 * abs_ratio))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo_top))
            painter.drawRoundedRect(QRectF(cx - plate_half_w - 4.0, cy - gap - 9.0, 2.0 * plate_half_w + 8.0, 14.0), 4.0, 4.0)

            halo_bot = QColor(bot_color)
            halo_bot.setAlpha(int(35 + 115 * abs_ratio))
            painter.setBrush(QBrush(halo_bot))
            painter.drawRoundedRect(QRectF(cx - plate_half_w - 4.0, cy + gap - 5.0, 2.0 * plate_half_w + 8.0, 14.0), 4.0, 4.0)

        # Placa superior y placa inferior
        painter.setPen(QPen(top_color, 4.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(cx - plate_half_w, cy - gap), QPointF(cx + plate_half_w, cy - gap))

        painter.setPen(QPen(bot_color, 4.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(cx - plate_half_w, cy + gap), QPointF(cx + plate_half_w, cy + gap))

        # Líneas de campo eléctrico entre las placas cuando hay carga
        if abs_ratio > 0.05:
            field_color = QColor("#E2E8F0")
            field_color.setAlpha(int(60 + 140 * abs_ratio))
            painter.setPen(QPen(field_color, 1.3, Qt.PenStyle.DotLine))
            for offset_x in (-16.0, 0.0, 16.0):
                painter.drawLine(
                    QPointF(cx + offset_x, cy - gap + 4.0),
                    QPointF(cx + offset_x, cy + gap - 4.0),
                )

        # Signos + y - en las placas
        if abs_ratio > 0.02:
            painter.setFont(QFont("JetBrains Mono", 12, QFont.Weight.Bold))
            top_sign = "+" if charge_ratio >= 0 else "-"
            bot_sign = "-" if charge_ratio >= 0 else "+"
            painter.setPen(top_color)
            painter.drawText(
                QRectF(cx - plate_half_w - 24.0, cy - gap - 12.0, 20.0, 20.0),
                Qt.AlignmentFlag.AlignCenter,
                top_sign,
            )
            painter.setPen(bot_color)
            painter.drawText(
                QRectF(cx - plate_half_w - 24.0, cy + gap - 8.0, 20.0, 20.0),
                Qt.AlignmentFlag.AlignCenter,
                bot_sign,
            )

        # Etiqueta derecha del capacitor
        right_box_x = cx + plate_half_w + 10.0
        right_box_w = max(125.0, float(self.width()) - right_box_x - 8.0)

        painter.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        painter.setPen(QColor("#E2E8F0"))
        painter.drawText(
            QRectF(right_box_x, cy - 32.0, right_box_w, 18.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"Capacitor ({self._c_mf:.1f} mF)",
        )
        painter.setFont(QFont("JetBrains Mono", 11, QFont.Weight.Bold))
        painter.setPen(QColor("#F43F5E"))
        painter.drawText(
            QRectF(right_box_x, cy - 12.0, right_box_w, 20.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"V_C = {self._vc_val:+6.1f} V",
        )
        painter.setFont(QFont("JetBrains Mono", 10, QFont.Weight.Medium))
        painter.setPen(QColor("#10B981"))
        painter.drawText(
            QRectF(right_box_x, cy + 10.0, right_box_w, 20.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"q = {self._q_val:+6.3f} C",
        )

    def _draw_center_flow_indicator(self, painter: QPainter, cx: float, cy: float) -> None:
        box_w = 250.0
        box_h = 64.0
        rect = QRectF(cx - 0.5 * box_w, cy - 0.5 * box_h, box_w, box_h)

        painter.setPen(QPen(QColor("#1E293B"), 1.2))
        painter.setBrush(QBrush(QColor(17, 24, 39, 220)))
        painter.drawRoundedRect(rect, 8.0, 8.0)

        if abs(self._i_val) < 1e-3:
            dir_text = "Sentido: Corriente Nula (0 A)"
            color_i = QColor("#94A3B8")
            arrow_dir = 0
        elif self._i_val > 0:
            dir_text = "Sentido Horario  [ i(t) > 0 ]"
            color_i = QColor("#38BDF8")
            arrow_dir = 1
        else:
            dir_text = "Sentido Antihorario  [ i(t) < 0 ]"
            color_i = QColor("#F59E0B")
            arrow_dir = -1

        painter.setFont(QFont("JetBrains Mono", 12, QFont.Weight.Bold))
        painter.setPen(color_i)
        painter.drawText(
            QRectF(rect.left(), rect.top() + 8.0, rect.width(), 24.0),
            Qt.AlignmentFlag.AlignCenter,
            f"i(t) = {self._i_val:+6.3f} A",
        )

        painter.setFont(QFont("Inter", 10, QFont.Weight.DemiBold))
        painter.setPen(QColor("#CBD5E1"))
        painter.drawText(
            QRectF(rect.left(), rect.top() + 34.0, rect.width(), 22.0),
            Qt.AlignmentFlag.AlignCenter,
            dir_text,
        )

        # Flechas vectoriales direccionales (arriba y abajo del cuadro central) para indicar giro horario/antihorario
        if arrow_dir != 0:
            top_arrow_y = cy - 0.5 * box_h - 10.0
            bot_arrow_y = cy + 0.5 * box_h + 10.0
            painter.setPen(QPen(color_i, 2.0))
            painter.setBrush(QBrush(color_i))
            if arrow_dir > 0:
                # Giro Horario: arriba hacia la derecha (->), abajo hacia la izquierda (<-)
                p1_t = QPointF(cx + 14.0, top_arrow_y)
                painter.drawLine(QPointF(cx - 14.0, top_arrow_y), p1_t)
                painter.drawPolygon(QPolygonF([p1_t, QPointF(cx + 5.0, top_arrow_y - 4.0), QPointF(cx + 5.0, top_arrow_y + 4.0)]))

                p1_b = QPointF(cx - 14.0, bot_arrow_y)
                painter.drawLine(QPointF(cx + 14.0, bot_arrow_y), p1_b)
                painter.drawPolygon(QPolygonF([p1_b, QPointF(cx - 5.0, bot_arrow_y - 4.0), QPointF(cx - 5.0, bot_arrow_y + 4.0)]))
            else:
                # Giro Antihorario: arriba hacia la izquierda (<-), abajo hacia la derecha (->)
                p1_t = QPointF(cx - 14.0, top_arrow_y)
                painter.drawLine(QPointF(cx + 14.0, top_arrow_y), p1_t)
                painter.drawPolygon(QPolygonF([p1_t, QPointF(cx - 5.0, top_arrow_y - 4.0), QPointF(cx - 5.0, top_arrow_y + 4.0)]))

                p1_b = QPointF(cx + 14.0, bot_arrow_y)
                painter.drawLine(QPointF(cx - 14.0, bot_arrow_y), p1_b)
                painter.drawPolygon(QPolygonF([p1_b, QPointF(cx + 5.0, bot_arrow_y - 4.0), QPointF(cx + 5.0, bot_arrow_y + 4.0)]))


class CircuitAnimationPanel(QFrame):
    """Panel superior que integra el circuito animado y la barra de reproducción temporal."""

    timeIndexChanged = Signal(int)
    modeChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SchematicCard")

        self._result: SimulationResult | None = None
        self._params: CircuitParams | None = None
        self._current_idx: int = 0
        self._float_idx: float = 0.0
        self._speed_mult: float = 1.0
        self._is_playing: bool = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Encabezado y barra de reproducción en una sola fila limpia
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(8)

        title = QLabel("SIMULACIÓN EN VIVO DEL FLUJO DE CORRIENTE Y CARGA")
        title.setObjectName("SectionTitle")
        top_bar.addWidget(title)
        top_bar.addStretch(1)
#   -----------------------------------------------------------------------
#    BOTONES: Sencillo / Avanzado ---

        self.btn_simple = QPushButton("Sencillo")
        self.btn_simple.setObjectName("SpeedButton")
        self.btn_simple.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simple.clicked.connect(lambda: self._set_mode("simple"))

        self.btn_advanced = QPushButton("Avanzado")
        self.btn_advanced.setObjectName("SpeedButton")
        self.btn_advanced.setProperty("active", "true")
        self.btn_advanced.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_advanced.clicked.connect(lambda: self._set_mode("avanzado"))

        top_bar.addWidget(self.btn_simple)
        top_bar.addWidget(self.btn_advanced)
        top_bar.addSpacing(20) # Espacio separador
#----------------------------------------------------------------------

        self.btn_play = QPushButton("Pausar Animación")
        self.btn_play.setObjectName("PlaybackButton")
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play.clicked.connect(self.toggle_play)

        self.btn_reset = QPushButton("Reiniciar (t = 0)")
        self.btn_reset.setObjectName("SecondaryActionButton")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_animation)

        top_bar.addWidget(self.btn_play)
        top_bar.addWidget(self.btn_reset)

        # Selector de velocidad
        self._speed_buttons: Dict[float, QPushButton] = {}
        for spd in (0.5, 1.0, 2.0):
            btn = QPushButton(f"{spd:.1f}x")
            btn.setObjectName("SpeedButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, s=spd: self.set_speed(s))
            self._speed_buttons[spd] = btn
            top_bar.addWidget(btn)

        layout.addLayout(top_bar)

        # Lienzo animado del circuito RC
        self.canvas = CircuitCanvas()
        layout.addWidget(self.canvas)

        # Barra deslizante de línea de tiempo (Scrubber)
        timeline_row = QHBoxLayout()
        timeline_row.setContentsMargins(0, 0, 0, 0)
        timeline_row.setSpacing(10)

        lbl_timeline = QLabel("Instante de Tiempo (t):")
        lbl_timeline.setObjectName("MetricSubtext")

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 2499)
        self.time_slider.valueChanged.connect(self._on_slider_scrubbed)

        self.lbl_time_readout = QLabel("t = 0.00 s / 3.00 s")
        self.lbl_time_readout.setObjectName("CursorText")
        self.lbl_time_readout.setMinimumWidth(145)

        timeline_row.addWidget(lbl_timeline)
        timeline_row.addWidget(self.time_slider, stretch=1)
        timeline_row.addWidget(self.lbl_time_readout)

        layout.addLayout(timeline_row)

        # Reloj de animación a 60 FPS (~16 ms)
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._on_timer_tick)

        self.set_speed(1.0)
        self._timer.start()

#--------------------------------------------------------
# CAMBIAR EL COLOR DE LOS BOTONES Y EMITIR LA SEÑAL
    def _set_mode(self, mode: str) -> None:
        is_adv = (mode == "avanzado")
        self.btn_advanced.setProperty("active", "true" if is_adv else "false")
        self.btn_simple.setProperty("active", "false" if is_adv else "true")
        
        self.btn_advanced.style().unpolish(self.btn_advanced)
        self.btn_advanced.style().polish(self.btn_advanced)
        self.btn_simple.style().unpolish(self.btn_simple)
        self.btn_simple.style().polish(self.btn_simple)
        
        self.modeChanged.emit(mode)

#-------------------------------------------------------
    def set_speed(self, speed: float) -> None:
        self._speed_mult = speed
        for spd, btn in self._speed_buttons.items():
            btn.setProperty("active", "true" if abs(spd - speed) < 1e-3 else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def toggle_play(self) -> None:
        self._is_playing = not self._is_playing
        if self._is_playing:
            self.btn_play.setText("Pausar Animación")
            self._timer.start()
        else:
            self.btn_play.setText("Reproducir Animación")
            self._timer.stop()

    def reset_animation(self) -> None:
        self._float_idx = 0.0
        self.set_time_index(0, emit_signal=True)

    def load_simulation(self, result: SimulationResult, params: CircuitParams) -> None:
        self._result = result
        self._params = params
        n_pts = len(result.t)
        self.time_slider.blockSignals(True)
        self.time_slider.setRange(0, max(0, n_pts - 1))
        self.time_slider.blockSignals(False)

        if self._current_idx >= n_pts:
            self._current_idx = 0
            self._float_idx = 0.0

        self.set_time_index(self._current_idx, emit_signal=True)

    def set_time_index(self, idx: int, emit_signal: bool = False) -> None:
        if self._result is None or self._params is None:
            return
        n_pts = len(self._result.t)
        if n_pts == 0:
            return

        clamped_idx = max(0, min(n_pts - 1, idx))
        self._current_idx = clamped_idx
        self._float_idx = float(clamped_idx)

        self.time_slider.blockSignals(True)
        self.time_slider.setValue(clamped_idx)
        self.time_slider.blockSignals(False)

        t_val = float(self._result.t[clamped_idx])
        t_max = float(self._result.t[-1])
        self.lbl_time_readout.setText(f"t = {t_val:5.2f} s / {t_max:5.2f} s")

        i_ref = max(abs(self._result.metrics.i_0), abs(self._result.metrics.I_max), 0.5)
        vc_ref = max(abs(self._params.E0), abs(self._params.q0 / self._params.C), 10.0)

        self.canvas.set_circuit_state(
            t_val=t_val,
            i_val=float(self._result.i_exact[clamped_idx]),
            i_ref_max=i_ref,
            q_val=float(self._result.q_exact[clamped_idx]),
            vc_val=float(self._result.Vc_exact[clamped_idx]),
            vc_ref_max=vc_ref,
            vr_val=float(self._result.VR_exact[clamped_idx]),
            e_val=float(self._result.E_source[clamped_idx]),
            r_ohm=self._params.R,
            c_mf=self._params.C * 1e3,
        )

        if emit_signal:
            self.timeIndexChanged.emit(clamped_idx)

    def _on_slider_scrubbed(self, val: int) -> None:
        self.set_time_index(val, emit_signal=True)

    def _on_timer_tick(self) -> None:
        if self._result is None or not self._is_playing:
            return
        n_pts = len(self._result.t)
        if n_pts <= 1:
            return

        # Recorrer toda la ventana de simulación en ~8 segundos a velocidad 1.0x
        step_indices = (n_pts / (8.0 * 60.0)) * self._speed_mult
        self._float_idx = (self._float_idx + step_indices) % float(n_pts)
        new_idx = int(self._float_idx)

        self.canvas.advance_particles(0.016 * self._speed_mult)
        self.set_time_index(new_idx, emit_signal=True)
