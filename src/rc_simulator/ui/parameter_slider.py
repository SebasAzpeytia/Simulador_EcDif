"""Control compuesto de alta precisión: QSlider sincronizado con QDoubleSpinBox."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class ParameterSlider(QWidget):
    """Widget que combina una etiqueta, un QDoubleSpinBox editable y un QSlider continuo."""

    valueChanged = Signal(float)

    SLIDER_STEPS = 10000

    def __init__(
        self,
        label_text: str,
        unit: str,
        min_val: float,
        max_val: float,
        default_val: float,
        decimals: int = 2,
        step: float = 0.1,
        tooltip: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._min_val = float(min_val)
        self._max_val = float(max_val)
        self._span = max(self._max_val - self._min_val, 1e-12)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 1, 0, 2)
        layout.setSpacing(2)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.label.setObjectName("ParamLabel")
        if tooltip:
            self.label.setToolTip(tooltip)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setDecimals(decimals)
        self.spinbox.setRange(self._min_val, self._max_val)
        self.spinbox.setSingleStep(step)
        self.spinbox.setSuffix(f" {unit}")
        self.spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.spinbox.setMinimumWidth(115)
        if tooltip:
            self.spinbox.setToolTip(tooltip)

        top_row.addWidget(self.label)
        top_row.addStretch(1)
        top_row.addWidget(self.spinbox)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, self.SLIDER_STEPS)
        if tooltip:
            self.slider.setToolTip(tooltip)

        layout.addLayout(top_row)
        layout.addWidget(self.slider)

        self.set_value(default_val, emit_signal=False)

        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)

    def _float_to_slider(self, value: float) -> int:
        clamped = max(self._min_val, min(self._max_val, value))
        ratio = (clamped - self._min_val) / self._span
        return int(round(ratio * self.SLIDER_STEPS))

    def _slider_to_float(self, slider_pos: int) -> float:
        ratio = slider_pos / float(self.SLIDER_STEPS)
        return self._min_val + ratio * self._span

    def _on_slider_changed(self, slider_pos: int) -> None:
        val = self._slider_to_float(slider_pos)
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(val)
        self.spinbox.blockSignals(False)
        self.valueChanged.emit(self.spinbox.value())

    def _on_spinbox_changed(self, val: float) -> None:
        self.slider.blockSignals(True)
        self.slider.setValue(self._float_to_slider(val))
        self.slider.blockSignals(False)
        self.valueChanged.emit(val)

    def value(self) -> float:
        return float(self.spinbox.value())

    def set_value(self, val: float, emit_signal: bool = True) -> None:
        clamped = max(self._min_val, min(self._max_val, float(val)))
        self.spinbox.blockSignals(True)
        self.slider.blockSignals(True)
        self.spinbox.setValue(clamped)
        self.slider.setValue(self._float_to_slider(clamped))
        self.spinbox.blockSignals(False)
        self.slider.blockSignals(False)
        if emit_signal:
            self.valueChanged.emit(self.spinbox.value())

    def set_enabled_state(self, enabled: bool) -> None:
        self.spinbox.setEnabled(enabled)
        self.slider.setEnabled(enabled)
        self.label.setEnabled(enabled)

