

PALETTE = {
    "bg_primary": "#000000",
    "bg_secondary": "#050505",
    "bg_card": "#0A0A0A",
    "bg_input": "#000000",
    "border": "#0F290F",
    "border_active": "#39FF14",
    "text_primary": "#F0FDF4",
    "text_secondary": "#86EFAC",
    "text_muted": "#166534",
    "accent_cyan": "#39FF14", 
    "accent_amber": "#EAB308",
    "accent_emerald": "#39FF14",
    "accent_rose": "#EF4444",
    "accent_violet": "#39FF14",
    "accent_indigo": "#39FF14",
    "plot_bg": "#000000",
    "plot_grid": "#062006",
}

DARK_TECH_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #000000;
    color: #F0FDF4;
    font-family: "Inter", "Segoe UI", "Ubuntu", sans-serif;
    font-size: 12px;
}

QFrame#SidebarFrame {
    background-color: #050505;
    border-left: 1px solid #143614;
}

QFrame#HeaderBanner, QFrame#SectionCard, QFrame#SchematicCard {
    background-color: #0A0A0A;
    border: 1px solid #143614;
    border-radius: 8px;
}

QFrame#PresetInfoBox {
    background-color: #000000;
    border-left: 3px solid #39FF14;
    border-radius: 4px;
}

QFrame#MetricCard {
    background-color: #050505;
    border: 1px solid #143614;
    border-radius: 6px;
}

QFrame#MetricCard:hover {
    border: 1px solid #39FF14;
    background-color: #0A1A0A;
}

QFrame#CursorReadoutBar {
    background-color: #050505;
    border: 1px solid #143614;
    border-radius: 6px;
}

QLabel#AppTitle {
    color: #39FF14;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

QLabel#AppSubtitle, QLabel#SectionTitle, QLabel#MetricSymbol {
    color: #86EFAC;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    font-family: "JetBrains Mono", monospace;
}

QLabel#PresetInfoText {
    color: #DCFCE7;
    font-size: 11px;
}

QLabel#ParamLabel {
    color: #DCFCE7;
    font-size: 12px;
    font-weight: 600;
}

QLabel#MetricTitle {
    color: #86EFAC;
    font-size: 11px;
    font-weight: 600;
}

QLabel#MetricValue {
    color: #39FF14;
    font-size: 16px;
    font-weight: 800;
    font-family: "JetBrains Mono", monospace;
}

QLabel#MetricSubtext, QLabel#CursorText {
    color: #22C55E;
    font-size: 11px;
}

QPushButton#PresetButton {
    background-color: #0A0A0A;
    color: #DCFCE7;
    border: 1px solid #166534;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 12px;
    font-weight: 600;
    text-align: left;
}

QPushButton#PresetButton:hover {
    background-color: #062006;
    border: 1px solid #39FF14;
    color: #FFFFFF;
}

QPushButton#PresetButton:pressed, QPushButton#PresetButton[active="true"] {
    background-color: #39FF14;
    border: 1px solid #39FF14;
    color: #000000;
}

QPushButton#PlaybackButton {
    background-color: #16A34A;
    color: #000000;
    border: 1px solid #39FF14;
    border-radius: 5px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 800;
}

QPushButton#PlaybackButton:hover {
    background-color: #39FF14;
}

QPushButton#SecondaryActionButton, QPushButton#ViewTabButton {
    background-color: #0A0A0A;
    color: #86EFAC;
    border: 1px solid #166534;
    border-radius: 5px;
    padding: 5px 12px;
    font-weight: 600;
}

QPushButton#SecondaryActionButton:hover, QPushButton#ViewTabButton:hover {
    border: 1px solid #39FF14;
    color: #39FF14;
}

QPushButton#ViewTabButton[active="true"] {
    background-color: #39FF14;
    color: #000000;
    border: 1px solid #39FF14;
}

QPushButton#SpeedButton {
    background-color: #050505;
    color: #86EFAC;
    border: 1px solid #143614;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
}

QPushButton#SpeedButton[active="true"] {
    background-color: #39FF14;
    color: #000000;
    border: 1px solid #39FF14;
}

QDoubleSpinBox {
    background-color: #000000;
    color: #39FF14;
    border: 1px solid #166534;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: "JetBrains Mono", monospace;
    font-weight: 600;
}

QDoubleSpinBox:focus {
    border: 1px solid #39FF14;
}

QSlider::groove:horizontal {
    border: 1px solid #166534;
    height: 6px;
    background: #000000;
    margin: 0px;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #16A34A;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #39FF14;
    border: 1px solid #FFFFFF;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #86EFAC;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QSplitter::handle {
    background-color: #143614;
    width: 4px;
}
QSplitter::handle:hover {
    background-color: #39FF14;
}
"""