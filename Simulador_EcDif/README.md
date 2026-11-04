# Simulador Interactivo de Circuito RC en Serie (Core C++20 + PySide6 / PyQtGraph)

Simulador de escritorio de alto rendimiento para el análisis dinámico (transitorio y estacionario) de un circuito eléctrico RC en serie excitado por una fuente sinusoidal de voltaje, gobernado por la ecuación diferencial lineal de primer orden:

$$R \frac{dq}{dt} + \frac{1}{C} q = E(t), \quad E(t) = E_0 \cos(\omega t), \quad q(0) = q_0$$

---

## 1. Arquitectura Técnica

- **Backend de Cálculo en C++20 (`cpp/`)**:
  - Implementa la **solución analítica exacta** para $q(t)$, $q_{\text{trans}}(t)$, $q_{\text{ss}}(t)$, $V_C(t)$, $V_R(t)$, $i(t)$, $i_{\text{trans}}(t)$ e $i_{\text{ss}}(t)$.
  - Incluye un **integrador numérico Runge-Kutta de 4.º orden (RK4)** ejecutado en paralelo sobre la misma malla temporal para validación empírica, calculando el error absoluto máximo ($\|q_{\text{exact}} - q_{\text{rk4}}\|_\infty$) y el error cuadrático medio (RMSE).
  - Exportado a Python mediante **`pybind11`** (`rc_core_cpp`) exponiendo vistas de arreglos de NumPy sin copia de memoria (*zero-copy*) y liberando el GIL durante el cálculo.
- **Frontend Interactivo (`src/rc_simulator/ui/`)**:
  - Construido con **PySide6 (Qt 6)** y **PyQtGraph** para renderizado fluido a 60 FPS en tema oscuro técnico.
  - Tres lienzos sincronizados con cursores *crosshair* de inspección instantánea y doble eje vertical sincronizado para $q(t)$ y $V_C(t)$.

---

## 2. Estructura del Proyecto

```text
Simulador_EcDif/
├── CMakeLists.txt                  # Configuración CMake C++20 + pybind11
├── pyproject.toml                  # Configuración scikit-build-core + dependencias uv
├── README.md                       # Documentación e instrucciones
├── cpp/
│   ├── include/
│   │   └── rc_solver.hpp           # Estructuras y declaraciones del motor C++20
│   └── src/
│       ├── rc_solver.cpp           # Solución analítica + resolvedor RK4
│       └── bindings.cpp            # Bindings pybind11 con vistas NumPy zero-copy
├── src/
│   └── rc_simulator/
│       ├── __init__.py
│       ├── main.py                 # Punto de entrada de la aplicación de escritorio
│       ├── presets.py              # Escenarios preconfigurados (AF6, Alta Frecuencia, etc.)
│       └── ui/
│           ├── __init__.py
│           ├── main_window.py      # Ventana principal tipo dashboard técnico
│           ├── metrics_panel.py    # Panel de lectura de métricas físicas y error RK4
│           ├── parameter_slider.py # Sliders sincronizados con campos numéricos editables
│           ├── plots_widget.py     # Sistema de 3 gráficas interactivas PyQtGraph
│           └── theme.py            # Hoja de estilos QSS (tema oscuro) y paleta
└── tests/
    └── test_rc_core.py             # Pruebas unitarias de precisión matemática y UI
```

---

## 3. Compilación y Ejecución

### Requisitos del Sistema
- Compilador C++20 (`g++ >= 11` o `clang++ >= 14`)
- `cmake >= 3.20`
- `python >= 3.10` (con encabezados `python3-dev`)
- Gestor de paquetes [`uv`](https://docs.astral.sh/uv/) (o `pip`)

### Opción Recomendada (con `uv`)

1. **Compilar el módulo C++20, sincronizar dependencias y ejecutar el simulador:**
   ```bash
   uv run rc-simulator
   ```

2. **Ejecutar la suite de pruebas automatizadas (validación analítica vs. RK4 e interfaz):**
   ```bash
   uv run pytest -v
   ```

### Opción Alternativa (con `venv` + `pip`)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
rc-simulator
```

---

## 4. Formulación Matemática Implementada

Para $R \frac{dq}{dt} + \frac{1}{C} q = E_0 \cos(\omega t)$ con $q(0) = q_0$:

- **Constante de tiempo y establecimiento:**
  $$\tau = R C, \quad t_s \approx 4\tau \text{ (2\%) o } 5\tau \text{ (1\%)}$$
- **Reactancia capacitiva, impedancia y desfase:**
  $$X_C = \frac{1}{\omega C}, \quad Z = \sqrt{R^2 + X_C^2}, \quad \phi = \arctan\left(\frac{1}{\omega R C}\right)$$
- **Carga eléctrica total $q(t) = q_{\text{trans}}(t) + q_{\text{ss}}(t)$:**
  $$q_{\text{ss}}(t) = \frac{C E_0}{1 + (\omega \tau)^2}\left(\cos(\omega t) + \omega \tau \sin(\omega t)\right), \quad q_{\text{trans}}(t) = K_q e^{-t/\tau}, \quad K_q = q_0 - \frac{C E_0}{1 + (\omega \tau)^2}$$
- **Corriente eléctrica total $i(t) = i_{\text{trans}}(t) + i_{\text{ss}}(t)$:**
  $$i_{\text{trans}}(t) = K_i e^{-t/\tau} \text{ con } K_i = -\frac{K_q}{\tau}, \quad i_{\text{ss}}(t) = I_{\max} \cos(\omega t + \phi) \text{ con } I_{\max} = \frac{E_0}{Z}$$

