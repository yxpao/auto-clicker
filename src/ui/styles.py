"""Premium Dark Theme QSS Stylesheets — Refined Design System.

Design principles applied:
- Softer background progression (3–4 value tiers, no harsh jumps)
- Larger corner radii and generous padding for a spacious feel
- Subtle inner-shadow borders using layered border + inset box styling
- Accent color palette: Electric indigo primary, teal secondary, coral danger
- Consistent 4px spacing grid
- Typography: Segoe UI Variable or Segoe UI, 13–14px body, 600–700 headings
"""

# ─── Color Tokens ────────────────────────────────────────────────

COLORS = {
    # Backgrounds — gentle dark-to-dark progression
    "bg_base":         "#0e1015",
    "bg_surface":      "#151820",
    "bg_card":         "#1a1e28",
    "bg_elevated":     "#21262f",
    "bg_hover":        "#262c38",
    "bg_input":        "#1d2230",

    # Borders
    "border_subtle":   "#252a36",
    "border_default":  "#2e3545",
    "border_focus":    "#6366f1",

    # Text
    "text_primary":    "#eef0f6",
    "text_secondary":  "#9ba1b0",
    "text_muted":      "#636a7a",
    "text_inverse":    "#ffffff",

    # Accent — Electric Indigo
    "accent":          "#6366f1",
    "accent_hover":    "#5558e3",
    "accent_surface":  "rgba(99, 102, 241, 0.12)",

    # Semantic
    "green":           "#22c55e",
    "green_hover":     "#16a34a",
    "green_surface":   "rgba(34, 197, 94, 0.12)",

    "red":             "#f43f5e",
    "red_hover":       "#e11d48",
    "red_surface":     "rgba(244, 63, 94, 0.12)",

    "amber":           "#f59e0b",
    "amber_surface":   "rgba(245, 158, 11, 0.10)",

    "teal":            "#2dd4bf",
    "teal_surface":    "rgba(45, 212, 191, 0.10)",

    "purple":          "#a78bfa",
}


# ─── Main QSS Stylesheet ────────────────────────────────────────

MAIN_STYLE = """

/* ═══════════════════════════════════════════════
   GLOBAL FOUNDATIONS
   ═══════════════════════════════════════════════ */

* {
    outline: none;
}

QMainWindow, QWidget#centralWidget, QDialog {
    background-color: #0e1015;
    color: #eef0f6;
    font-family: 'Segoe UI Variable', 'Segoe UI', 'Inter', system-ui, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #eef0f6;
    font-family: 'Segoe UI Variable', 'Segoe UI', 'Inter', system-ui, sans-serif;
    font-size: 13px;
    selection-background-color: #6366f1;
    selection-color: #ffffff;
}

QDialog {
    background-color: #151820;
    border: 1px solid #2e3545;
    border-radius: 12px;
}


/* ═══════════════════════════════════════════════
   TAB WIDGET — Pill-style top tabs
   ═══════════════════════════════════════════════ */

QTabWidget {
    background-color: transparent;
}

QTabWidget::pane {
    background-color: #151820;
    border: 1px solid #252a36;
    border-radius: 10px;
    padding: 4px;
    top: -1px;
}

QTabBar {
    background-color: transparent;
}

QTabBar::tab {
    background-color: transparent;
    color: #636a7a;
    padding: 9px 20px;
    margin-right: 2px;
    border: 1px solid transparent;
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-weight: 600;
    font-size: 13px;
    min-width: 110px;
}

QTabBar::tab:selected {
    background-color: #151820;
    color: #eef0f6;
    border: 1px solid #252a36;
    border-bottom: 2px solid #6366f1;
}

QTabBar::tab:hover:!selected {
    background-color: rgba(99, 102, 241, 0.06);
    color: #9ba1b0;
}


/* ═══════════════════════════════════════════════
   GROUP BOXES — Card containers
   ═══════════════════════════════════════════════ */

QGroupBox {
    background-color: #1a1e28;
    border: 1px solid #252a36;
    border-radius: 10px;
    margin-top: 20px;
    padding: 20px 16px 14px 16px;
    font-weight: 600;
    font-size: 13px;
    color: #9ba1b0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 2px 8px;
    background-color: #1a1e28;
    border-radius: 4px;
    color: #9ba1b0;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}


/* ═══════════════════════════════════════════════
   INPUTS — Text fields, Spinners, Dropdowns
   ═══════════════════════════════════════════════ */

QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #1d2230;
    border: 1px solid #2e3545;
    border-radius: 8px;
    color: #eef0f6;
    padding: 7px 12px;
    font-size: 13px;
    min-height: 18px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #6366f1;
    background-color: #212636;
}

QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {
    background-color: #151820;
    color: #636a7a;
    border-color: #1e2230;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 22px;
    border: none;
    border-left: 1px solid #2e3545;
    border-top-right-radius: 8px;
    background-color: transparent;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 22px;
    border: none;
    border-left: 1px solid #2e3545;
    border-bottom-right-radius: 8px;
    background-color: transparent;
}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    width: 8px;
    height: 8px;
}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    width: 8px;
    height: 8px;
}

QComboBox {
    background-color: #1d2230;
    border: 1px solid #2e3545;
    border-radius: 8px;
    color: #eef0f6;
    padding: 7px 12px;
    padding-right: 28px;
    font-size: 13px;
    min-height: 18px;
}

QComboBox:focus, QComboBox:on {
    border: 1px solid #6366f1;
    background-color: #212636;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
    padding-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #1a1e28;
    border: 1px solid #2e3545;
    border-radius: 8px;
    padding: 4px;
    outline: none;
    selection-background-color: rgba(99, 102, 241, 0.2);
    selection-color: #eef0f6;
    color: #eef0f6;
}

QComboBox QAbstractItemView::item {
    padding: 6px 10px;
    border-radius: 4px;
    min-height: 22px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: rgba(99, 102, 241, 0.12);
}


/* ═══════════════════════════════════════════════
   BUTTONS — Layered system
   ═══════════════════════════════════════════════ */

QPushButton {
    background-color: #21262f;
    color: #eef0f6;
    border: 1px solid #2e3545;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
    min-height: 16px;
}

QPushButton:hover {
    background-color: #262c38;
    border-color: #3a4255;
}

QPushButton:pressed {
    background-color: #1a1e28;
    border-color: #2e3545;
}

QPushButton:disabled {
    background-color: #151820;
    color: #3d4350;
    border-color: #1e2230;
}

/* Primary green — Start / Play */
QPushButton#btn_start, QPushButton#btn_play {
    background-color: #22c55e;
    color: #052e16;
    border: 1px solid #16a34a;
    font-size: 14px;
    font-weight: 700;
}
QPushButton#btn_start:hover, QPushButton#btn_play:hover {
    background-color: #16a34a;
    color: #ffffff;
}
QPushButton#btn_start:disabled, QPushButton#btn_play:disabled {
    background-color: rgba(34, 197, 94, 0.15);
    color: rgba(34, 197, 94, 0.40);
    border-color: rgba(34, 197, 94, 0.1);
}

/* Danger red — Stop */
QPushButton#btn_stop {
    background-color: #f43f5e;
    color: #ffffff;
    border: 1px solid #e11d48;
    font-size: 14px;
    font-weight: 700;
}
QPushButton#btn_stop:hover {
    background-color: #e11d48;
}
QPushButton#btn_stop:disabled {
    background-color: rgba(244, 63, 94, 0.15);
    color: rgba(244, 63, 94, 0.40);
    border-color: rgba(244, 63, 94, 0.1);
}

/* Record — Deep red pulsing feel */
QPushButton#btn_record {
    background-color: #dc2626;
    color: #ffffff;
    border: 1px solid #b91c1c;
    font-size: 14px;
    font-weight: 700;
}
QPushButton#btn_record:hover {
    background-color: #b91c1c;
}

/* Accent — Indigo */
QPushButton#btn_accent {
    background-color: #6366f1;
    color: #ffffff;
    border: 1px solid #5558e3;
}
QPushButton#btn_accent:hover {
    background-color: #5558e3;
}

/* Ghost / Subtle button */
QPushButton#btn_ghost {
    background-color: transparent;
    color: #9ba1b0;
    border: 1px solid transparent;
}
QPushButton#btn_ghost:hover {
    background-color: rgba(99, 102, 241, 0.08);
    color: #eef0f6;
    border-color: #252a36;
}


/* ═══════════════════════════════════════════════
   CHECKBOXES & RADIO BUTTONS
   ═══════════════════════════════════════════════ */

QRadioButton, QCheckBox {
    color: #c8ccd6;
    spacing: 8px;
    font-size: 13px;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1.5px solid #3a4255;
    background-color: #1d2230;
    border-radius: 4px;
}

QRadioButton::indicator {
    border-radius: 9px;
}

QRadioButton::indicator:hover, QCheckBox::indicator:hover {
    border-color: #6366f1;
}

QRadioButton::indicator:checked, QCheckBox::indicator:checked {
    background-color: #6366f1;
    border-color: #6366f1;
}


/* ═══════════════════════════════════════════════
   TABLE WIDGET
   ═══════════════════════════════════════════════ */

QTableWidget {
    background-color: #151820;
    alternate-background-color: #181c26;
    border: 1px solid #252a36;
    border-radius: 8px;
    gridline-color: #1e2230;
    color: #eef0f6;
    selection-background-color: rgba(99, 102, 241, 0.18);
    selection-color: #eef0f6;
    font-size: 13px;
}

QTableWidget::item {
    padding: 6px 8px;
    border-bottom: 1px solid #1e2230;
}

QTableWidget::item:selected {
    background-color: rgba(99, 102, 241, 0.18);
}

QTableWidget::item:hover {
    background-color: rgba(99, 102, 241, 0.08);
}

QHeaderView {
    background-color: transparent;
}

QHeaderView::section {
    background-color: #0e1015;
    color: #636a7a;
    padding: 8px 10px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: none;
    border-right: 1px solid #1e2230;
    border-bottom: 1px solid #252a36;
}

QHeaderView::section:first {
    border-top-left-radius: 8px;
}

QHeaderView::section:last {
    border-right: none;
    border-top-right-radius: 8px;
}


/* ═══════════════════════════════════════════════
   SCROLLBARS — Thin, auto-hiding style
   ═══════════════════════════════════════════════ */

QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 8px;
    margin: 4px 2px;
}
QScrollBar::handle:vertical {
    background-color: #2e3545;
    min-height: 30px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background-color: #3a4255;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    height: 0px;
    background: transparent;
}

QScrollBar:horizontal {
    border: none;
    background-color: transparent;
    height: 8px;
    margin: 2px 4px;
}
QScrollBar::handle:horizontal {
    background-color: #2e3545;
    min-width: 30px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #3a4255;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    width: 0px;
    background: transparent;
}


/* ═══════════════════════════════════════════════
   SLIDER
   ═══════════════════════════════════════════════ */

QSlider::groove:horizontal {
    height: 4px;
    background: #252a36;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #6366f1;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #eef0f6;
    border: 2px solid #6366f1;
    width: 14px;
    height: 14px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #ffffff;
    border-color: #5558e3;
}


/* ═══════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════ */

QProgressBar {
    border: 1px solid #252a36;
    border-radius: 6px;
    background-color: #1a1e28;
    text-align: center;
    color: #9ba1b0;
    font-weight: 600;
    font-size: 12px;
    min-height: 14px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366f1, stop:1 #818cf8);
    border-radius: 5px;
}


/* ═══════════════════════════════════════════════
   STATUS BAR
   ═══════════════════════════════════════════════ */

QStatusBar {
    background-color: #0e1015;
    color: #636a7a;
    border-top: 1px solid #1e2230;
    font-size: 12px;
    padding: 2px 8px;
}

QStatusBar::item {
    border: none;
}


/* ═══════════════════════════════════════════════
   LABELS — Utility classes via objectName
   ═══════════════════════════════════════════════ */

QLabel#lbl_heading {
    color: #eef0f6;
    font-size: 16px;
    font-weight: 700;
}

QLabel#lbl_subheading {
    color: #636a7a;
    font-size: 12px;
    font-weight: 400;
}

QLabel#lbl_stat_primary {
    color: #6366f1;
    font-size: 18px;
    font-weight: 700;
}

QLabel#lbl_stat_value {
    color: #eef0f6;
    font-size: 15px;
    font-weight: 600;
}

QLabel#lbl_stat_label {
    color: #636a7a;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}


/* ═══════════════════════════════════════════════
   FRAME — Card container widget
   ═══════════════════════════════════════════════ */

QFrame#card {
    background-color: #1a1e28;
    border: 1px solid #252a36;
    border-radius: 10px;
}

QFrame#card_stat {
    background-color: #1a1e28;
    border: 1px solid #252a36;
    border-radius: 10px;
    padding: 12px;
}

QFrame#card_telemetry {
    background-color: #1a1e28;
    border: 1px solid #252a36;
    border-radius: 10px;
    padding: 10px 14px;
}

QFrame#divider {
    background-color: #252a36;
    max-height: 1px;
    min-height: 1px;
}


/* ═══════════════════════════════════════════════
   TOOLTIPS
   ═══════════════════════════════════════════════ */

QToolTip {
    background-color: #21262f;
    color: #eef0f6;
    border: 1px solid #2e3545;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""
