"""Escenarios preconfigurados (Presets) para el análisis dinámico del circuito RC."""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class PresetScenario:
    key: str
    title: str
    subtitle: str
    description: str
    R_ohm: float
    C_mf: float
    E0_volt: float
    omega_rad_s: float
    q0_coulomb: float
    auto_t_sim: bool = True
    manual_t_sim_s: float = 3.0


PRESETS: Dict[str, PresetScenario] = {
    "af6_base": PresetScenario(
        key="af6_base",
        title="Caso Base AF6",
        subtitle="R=50 Ohm, C=10 mF, E0=200 V, w=2 rad/s, q0=0 C",
        description=(
            "Condición de resonancia de reactancia donde Xc = R = 50 Ohm, "
            "produciendo un desfase exacto de 45 grados (pi/4 rad) y constante "
            "de tiempo tau = 0.5 s."
        ),
        R_ohm=50.0,
        C_mf=10.0,
        E0_volt=200.0,
        omega_rad_s=2.0,
        q0_coulomb=0.0,
        auto_t_sim=True,
        manual_t_sim_s=3.0,
    ),
    "high_freq": PresetScenario(
        key="high_freq",
        title="Alta Frecuencia (Paso Bajas)",
        subtitle="R=50 Ohm, C=10 mF, E0=200 V, w=40 rad/s, q0=0 C",
        description=(
            "Comportamiento de filtro paso bajas a frecuencia elevada: Xc = 2.5 Ohm << R. "
            "El capacitor actúa casi como cortocircuito en AC, atenuando fuertemente Vc(t) "
            "con un desfase cercano a 0 grados en corriente."
        ),
        R_ohm=50.0,
        C_mf=10.0,
        E0_volt=200.0,
        omega_rad_s=40.0,
        q0_coulomb=0.0,
        auto_t_sim=True,
        manual_t_sim_s=3.0,
    ),
    "slow_transient": PresetScenario(
        key="slow_transient",
        title="Transitorio Lento",
        subtitle="R=400 Ohm, C=25 mF, E0=200 V, w=4 rad/s, q0=-0.5 C",
        description=(
            "Constante de tiempo elevada (tau = R*C = 10.0 s) con carga inicial negativa. "
            "La envolvente exponencial persiste durante varios ciclos de la fuente sinusoidal."
        ),
        R_ohm=400.0,
        C_mf=25.0,
        E0_volt=200.0,
        omega_rad_s=4.0,
        q0_coulomb=-0.5,
        auto_t_sim=False,
        manual_t_sim_s=15.0,
    ),
    "initial_discharge": PresetScenario(
        key="initial_discharge",
        title="Descarga Inicial",
        subtitle="R=100 Ohm, C=10 mF, E0=0 V, w=2 rad/s, q0=0.8 C",
        description=(
            "Respuesta natural pura sin excitación externa (E0 = 0 V) y capacitor "
            "previamente cargado (q0 = 0.8 C, Vc(0) = 80 V). Decaimiento exponencial puro."
        ),
        R_ohm=100.0,
        C_mf=10.0,
        E0_volt=0.0,
        omega_rad_s=2.0,
        q0_coulomb=0.8,
        auto_t_sim=True,
        manual_t_sim_s=6.0,
    ),
}

