"""Panel de diagnóstico simplificado con los 4 indicadores clave para presentación."""

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from rc_simulator.rc_core_cpp import CircuitMetrics


class MetricCard(QFrame):
    """Tarjeta amplia para mostrar un indicador clave con alta legibilidad."""

    def __init__(
        self,
        title: str,
        symbol: str,
        formula_hint: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("MetricCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("MetricTitle")

        self.symbol_label = QLabel(symbol)
        self.symbol_label.setObjectName("MetricSymbol")

        header.addWidget(self.title_label)
        header.addStretch(1)
        header.addWidget(self.symbol_label)

        self.value_label = QLabel("--")
        self.value_label.setObjectName("MetricValue")

        self.sub_label = QLabel(formula_hint)
        self.sub_label.setObjectName("MetricSubtext")

        layout.addLayout(header)
        layout.addWidget(self.value_label)
        layout.addWidget(self.sub_label)

    def set_display(self, value_text: str, sub_text: str | None = None) -> None:
        self.value_label.setText(value_text)
        if sub_text is not None:
            self.sub_label.setText(sub_text)


class MetricsPanel(QFrame):
    """Panel resumen con los 4 resultados esenciales del circuito RC."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SectionCard")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)

        title = QLabel("3. Resultados Clave del Circuito")
        title.setObjectName("SectionTitle")
        main_layout.addWidget(title)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        self.card_tau = MetricCard("Rapidez de Respuesta", "tau", "Estable en ~4*tau")
        self.card_z = MetricCard("Impedancia Total", "Z", "Oposición total AC")
        self.card_phi = MetricCard("Ángulo de Desfase", "phi", "Adelanto de corriente")
        self.card_imax = MetricCard("Corriente Pico Estable", "I_max", "Amplitud estacionaria")

        grid.addWidget(self.card_tau, 0, 0)
        grid.addWidget(self.card_z, 0, 1)
        grid.addWidget(self.card_phi, 1, 0)
        grid.addWidget(self.card_imax, 1, 1)

        main_layout.addLayout(grid)

    def update_metrics(self, m: CircuitMetrics) -> None:
        self.card_tau.set_display(
            f"{m.tau:.2f} s",
            f"Estable en {m.ts_4tau:.2f} s",
        )
        self.card_z.set_display(
            f"{m.Z:.1f} Ohm",
            f"X_C = {m.Xc:.1f} Ohm",
        )
        self.card_phi.set_display(
            f"{m.phi_deg:.1f} deg",
            f"{m.phi_rad:.2f} rad",
        )
        self.card_imax.set_display(
            f"{m.I_max:.2f} A",
            f"Inicial i(0) = {m.i_0:+.2f} A",
        )
