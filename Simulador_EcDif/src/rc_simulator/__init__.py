"""Paquete principal del Simulador Interactivo de Circuito RC en Serie."""

from rc_simulator.rc_core_cpp import CircuitMetrics, CircuitParams, RCSolver, SimulationResult

__all__ = [
    "CircuitParams",
    "CircuitMetrics",
    "SimulationResult",
    "RCSolver",
]

