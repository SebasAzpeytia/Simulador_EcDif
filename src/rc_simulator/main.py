"""Punto de entrada principal para el Simulador Interactivo de Circuito RC en Serie."""

from pathlib import Path
import sys

# Garantiza que el paquete rc_simulator sea importable incluso al ejecutar main.py directamente
_SRC_DIR = str(Path(__file__).resolve().parent.parent)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from rc_simulator.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Simulador Circuito RC Serie")
    app.setOrganizationName("ScientificComputingLab")

    default_font = QFont("Inter", 10)
    app.setFont(default_font)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

