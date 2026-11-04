"""Paleta de colores y hoja de estilos QSS para el dashboard de presentación en tema oscuro."""

PALETTE = {
    "bg_primary": "#0B0F17",
    "bg_secondary": "#111827",
    "bg_card": "#172033",
    "bg_input": "#0D1320",
    "border": "#26334D",
    "border_active": "#38BDF8",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "accent_cyan": "#38BDF8",
    "accent_amber": "#F59E0B",
    "accent_emerald": "#10B981",
    "accent_rose": "#F43F5E",
    "accent_violet": "#A855F7",
    "accent_indigo": "#6366F1",
    "plot_bg": "#0D131F",
    "plot_grid": "#1E293B",
}

DARK_TECH_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0B0F17;
    color: #F1F5F9;
    font-family: "Inter", "Segoe UI", "Ubuntu", "Noto Sans", sans-serif;
    font-size: 12px;
}

QFrame#SidebarFrame {
    background-color: #111827;
    border-right: 1px solid #26334D;
}

QFrame#HeaderBanner {
    background-color: #151E30;
    border: 1px solid #26334D;
    border-radius: 8px;
}

QFrame#SectionCard {
    background-color: #151E30;
    border: 1px solid #26334D;
    border-radius: 8px;
}

QFrame#SchematicCard {
    background-color: #111827;
    border: 1px solid #26334D;
    border-radius: 8px;
}

QFrame#PresetInfoBox {
    background-color: #0E1726;
    border-left: 3px solid #38BDF8;
    border-radius: 4px;
}

QFrame#MetricCard {
    background-color: #172033;
    border: 1px solid #26334D;
    border-radius: 6px;
}

QFrame#MetricCard:hover {
    border: 1px solid #38BDF8;
}

QFrame#CursorReadoutBar {
    background-color: #111827;
    border: 1px solid #26334D;
    border-radius: 6px;
}

QLabel#AppTitle {
    color: #F8FAFC;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.4px;
}

QLabel#AppSubtitle {
    color: #38BDF8;
    font-size: 12px;
    font-weight: 700;
    font-family: "JetBrains Mono", "Fira Code", "Ubuntu Mono", monospace;
}

QLabel#SectionTitle {
    color: #38BDF8;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

QLabel#PresetInfoText {
    color: #CBD5E1;
    font-size: 11px;
    line-height: 1.3;
}

QLabel#ParamLabel {
    color: #E2E8F0;
    font-size: 12px;
    font-weight: 600;
}

QLabel#MetricTitle {
    color: #94A3B8;
    font-size: 11px;
    font-weight: 600;
}

QLabel#MetricSymbol {
    color: #38BDF8;
    font-size: 12px;
    font-weight: 700;
    font-family: "JetBrains Mono", "Ubuntu Mono", monospace;
}

QLabel#MetricValue {
    color: #F8FAFC;
    font-size: 16px;
    font-weight: 800;
    font-family: "JetBrains Mono", "Ubuntu Mono", monospace;
}

QLabel#MetricSubtext {
    color: #94A3B8;
    font-size: 11px;
}

QLabel#CursorText {
    color: #E2E8F0;
    font-size: 11px;
    font-family: "JetBrains Mono", "Ubuntu Mono", monospace;
}

QPushButton#PresetButton {
    background-color: #172033;
    color: #E2E8F0;
    border: 1px solid #2B3B59;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 12px;
    font-weight: 600;
    text-align: left;
}

QPushButton#PresetButton:hover {
    background-color: #1E2B45;
    border: 1px solid #38BDF8;
    color: #FFFFFF;
}

QPushButton#PresetButton:pressed, QPushButton#PresetButton[active="true"] {
    background-color: #0E3A5A;
    border: 1px solid #38BDF8;
    color: #38BDF8;
}

QPushButton#PlaybackButton {
    background-color: #0284C7;
    color: #FFFFFF;
    border: 1px solid #38BDF8;
    border-radius: 5px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 700;
}

QPushButton#PlaybackButton:hover {
    background-color: #0369A1;
}

QPushButton#SecondaryActionButton {
    background-color: #172033;
    color: #E2E8F0;
    border: 1px solid #2B3B59;
    border-radius: 5px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}

QPushButton#SecondaryActionButton:hover {
    border: 1px solid #38BDF8;
    color: #FFFFFF;
}

QPushButton#SpeedButton {
    background-color: #151E30;
    color: #94A3B8;
    border: 1px solid #26334D;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
}

QPushButton#SpeedButton[active="true"] {
    background-color: #0E3A5A;
    color: #38BDF8;
    border: 1px solid #38BDF8;
}

QPushButton#ViewTabButton {
    background-color: #151E30;
    color: #94A3B8;
    border: 1px solid #26334D;
    border-radius: 6px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 700;
}

QPushButton#ViewTabButton:hover {
    background-color: #1E293B;
    color: #F1F5F9;
}

QPushButton#ViewTabButton[active="true"] {
    background-color: #0E3A5A;
    color: #38BDF8;
    border: 1px solid #38BDF8;
}

QDoubleSpinBox {
    background-color: #0B0F17;
    color: #38BDF8;
    border: 1px solid #26334D;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: "JetBrains Mono", "Ubuntu Mono", monospace;
    font-size: 12px;
    font-weight: 600;
}

QDoubleSpinBox:focus {
    border: 1px solid #38BDF8;
}

QSlider::groove:horizontal {
    border: 1px solid #26334D;
    height: 6px;
    background: #0B0F17;
    margin: 0px;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #0284C7;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #38BDF8;
    border: 1px solid #E0F2FE;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #7DD3FC;
}

QScrollArea {
    border: none;
    background-color: transparent;
}
"""
