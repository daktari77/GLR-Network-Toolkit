from dataclasses import dataclass
from PyQt6.QtWidgets import QApplication


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    surface: str
    surface_alt: str
    border: str
    text: str
    text_muted: str
    sel_bg: str
    sel_fg: str
    accent: str
    card_bg: str
    # Status badge (opaque pill)
    up_bg: str
    up_fg: str
    down_bg: str
    down_fg: str
    unknown_bg: str
    unknown_fg: str
    # History table status foreground
    hist_up_fg: str
    hist_down_fg: str
    hist_unknown_fg: str
    # Latency chart
    chart_bg: str
    chart_grid: str
    chart_line: str
    chart_dot: str
    chart_axis: str
    chart_title: str
    # Empty-state hint
    empty_fg: str


DARK = Theme(
    name="dark",
    bg="#0d1117",
    surface="#161b22",
    surface_alt="#1c2128",
    border="#30363d",
    text="#e6edf3",
    text_muted="#7d8590",
    sel_bg="#388bfd",
    sel_fg="#ffffff",
    accent="#388bfd",
    card_bg="#1c2128",
    up_bg="#238636",    up_fg="#ffffff",
    down_bg="#da3633",  down_fg="#ffffff",
    unknown_bg="#30363d", unknown_fg="#8b949e",
    hist_up_fg="#3fb950",
    hist_down_fg="#f85149",
    hist_unknown_fg="#6e7681",
    chart_bg="#0d1117",
    chart_grid="#21262d",
    chart_line="#3fb950",
    chart_dot="#f85149",
    chart_axis="#7d8590",
    chart_title="#c9d1d9",
    empty_fg="#30363d",
)

LIGHT = Theme(
    name="light",
    bg="#ffffff",
    surface="#f6f8fa",
    surface_alt="#f0f2f5",
    border="#d0d7de",
    text="#1f2328",
    text_muted="#656d76",
    sel_bg="#0969da",
    sel_fg="#ffffff",
    accent="#0969da",
    card_bg="#f6f8fa",
    up_bg="#1a7f37",    up_fg="#ffffff",
    down_bg="#cf222e",  down_fg="#ffffff",
    unknown_bg="#6e7781", unknown_fg="#ffffff",
    hist_up_fg="#1a7f37",
    hist_down_fg="#cf222e",
    hist_unknown_fg="#6e7781",
    chart_bg="#f6f8fa",
    chart_grid="#e1e4e8",
    chart_line="#1a7f37",
    chart_dot="#cf222e",
    chart_axis="#656d76",
    chart_title="#1f2328",
    empty_fg="#c9cdd2",
)

THEMES: dict[str, Theme] = {"dark": DARK, "light": LIGHT}
_current: Theme = DARK


def current() -> Theme:
    return _current


def apply(app: QApplication, t: Theme) -> None:
    global _current
    _current = t
    app.setStyleSheet(_build_qss(t))


def _build_qss(t: Theme) -> str:
    return f"""
/* ── Base ──────────────────────────────────────────────── */
QWidget {{
    background-color: {t.bg};
    color: {t.text};
    font-family: "Segoe UI", system-ui, sans-serif;
    font-size: 10pt;
}}
QMainWindow, QDialog {{
    background-color: {t.bg};
}}

/* ── Toolbar ─────────────────────────────────────────────── */
QToolBar {{
    background-color: {t.surface};
    border: none;
    border-bottom: 1px solid {t.border};
    padding: 4px 8px;
    spacing: 2px;
}}
QToolBar QToolButton {{
    background-color: transparent;
    color: {t.text};
    border: none;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 10pt;
}}
QToolBar QToolButton:hover {{
    background-color: {t.surface_alt};
}}
QToolBar QToolButton:pressed {{
    background-color: {t.sel_bg};
    color: {t.sel_fg};
}}
QToolBar QToolButton:disabled {{
    color: {t.text_muted};
}}
QToolBar::separator {{
    background-color: {t.border};
    width: 1px;
    margin: 4px 6px;
}}

/* ── Tabs ─────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: none;
    background-color: {t.bg};
}}
QTabBar {{
    background-color: {t.surface};
    border-bottom: 1px solid {t.border};
}}
QTabBar::tab {{
    background-color: transparent;
    color: {t.text_muted};
    padding: 8px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
}}
QTabBar::tab:selected {{
    color: {t.text};
    border-bottom: 2px solid {t.accent};
}}
QTabBar::tab:hover:!selected {{
    color: {t.text};
    background-color: {t.surface_alt};
}}

/* ── Tables ───────────────────────────────────────────────── */
QTableWidget {{
    background-color: {t.bg};
    alternate-background-color: {t.surface_alt};
    color: {t.text};
    gridline-color: {t.border};
    border: none;
    selection-background-color: {t.sel_bg};
    selection-color: {t.sel_fg};
    outline: none;
}}
QTableWidget::item {{
    padding: 4px 6px;
    border: none;
}}
QTableWidget::item:hover {{
    background-color: {t.surface_alt};
}}
QTableWidget::item:selected {{
    background-color: {t.sel_bg};
    color: {t.sel_fg};
}}
QHeaderView {{
    background-color: {t.surface};
    border: none;
}}
QHeaderView::section {{
    background-color: {t.surface};
    color: {t.text_muted};
    border: none;
    border-right: 1px solid {t.border};
    border-bottom: 1px solid {t.border};
    padding: 5px 8px;
    font-size: 9pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}
QHeaderView::section:last {{
    border-right: none;
}}

/* ── Splitter ─────────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {t.border};
}}
QSplitter::handle:vertical {{ height: 1px; }}
QSplitter::handle:horizontal {{ width: 1px; }}

/* ── Status bar ───────────────────────────────────────────── */
QStatusBar {{
    background-color: {t.surface};
    color: {t.text_muted};
    border-top: 1px solid {t.border};
    font-size: 9pt;
}}

/* ── Form controls ────────────────────────────────────────── */
QLineEdit {{
    background-color: {t.surface};
    color: {t.text};
    border: 1px solid {t.border};
    border-radius: 6px;
    padding: 5px 8px;
    selection-background-color: {t.sel_bg};
    selection-color: {t.sel_fg};
}}
QLineEdit:focus {{
    border-color: {t.accent};
}}
QLineEdit:disabled {{ color: {t.text_muted}; }}

QSpinBox {{
    background-color: {t.surface};
    color: {t.text};
    border: 1px solid {t.border};
    border-radius: 6px;
    padding: 4px 6px;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {t.surface};
    border: none;
    width: 16px;
    border-radius: 3px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {t.border};
}}

QComboBox {{
    background-color: {t.surface};
    color: {t.text};
    border: 1px solid {t.border};
    border-radius: 6px;
    padding: 5px 8px;
    min-width: 60px;
}}
QComboBox:focus {{ border-color: {t.accent}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background-color: {t.surface};
    color: {t.text};
    selection-background-color: {t.sel_bg};
    selection-color: {t.sel_fg};
    border: 1px solid {t.border};
    border-radius: 6px;
    outline: none;
}}

/* ── Buttons ──────────────────────────────────────────────── */
QPushButton {{
    background-color: {t.surface};
    color: {t.text};
    border: 1px solid {t.border};
    border-radius: 6px;
    padding: 5px 14px;
    min-width: 60px;
}}
QPushButton:hover {{
    background-color: {t.surface_alt};
    border-color: {t.accent};
}}
QPushButton:pressed {{
    background-color: {t.sel_bg};
    color: {t.sel_fg};
    border-color: {t.sel_bg};
}}
QPushButton:default {{
    background-color: {t.accent};
    color: #ffffff;
    border-color: {t.accent};
}}
QPushButton:default:hover {{
    background-color: {t.sel_bg};
}}
QPushButton:disabled {{
    color: {t.text_muted};
    border-color: {t.border};
}}

/* ── Scrollbars ───────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    border: none;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t.border};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {t.text_muted}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    border: none;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {t.border};
    border-radius: 3px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{ background: {t.text_muted}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Dialog chrome ────────────────────────────────────────── */
QGroupBox {{
    color: {t.text_muted};
    border: 1px solid {t.border};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 10px;
    color: {t.text_muted};
    font-size: 9pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}
QCheckBox {{
    color: {t.text};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {t.border};
    border-radius: 3px;
    background-color: {t.surface};
}}
QCheckBox::indicator:checked {{
    background-color: {t.accent};
    border-color: {t.accent};
}}
QLabel {{
    background-color: transparent;
    color: {t.text};
}}
QMenuBar {{
    background-color: {t.surface};
    color: {t.text};
    border-bottom: 1px solid {t.border};
}}
QMenuBar::item:selected {{
    background-color: {t.sel_bg};
    color: {t.sel_fg};
    border-radius: 4px;
}}
QMenu {{
    background-color: {t.surface};
    color: {t.text};
    border: 1px solid {t.border};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item {{
    padding: 5px 20px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {t.sel_bg};
    color: {t.sel_fg};
}}
QMenu::separator {{
    height: 1px;
    background: {t.border};
    margin: 4px 0;
}}
"""
