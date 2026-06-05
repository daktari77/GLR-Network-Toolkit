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
    # Status badge (opaque pill — same palette works on both bg colours)
    up_bg: str
    up_fg: str
    down_bg: str
    down_fg: str
    unknown_bg: str
    unknown_fg: str
    # History table status foreground (text on table bg)
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
    bg="#1e1e2e",
    surface="#2a2a3e",
    surface_alt="#252535",
    border="#3e3e54",
    text="#cccccc",
    text_muted="#888888",
    sel_bg="#3d3d5c",
    sel_fg="#ffffff",
    up_bg="#2d9e4e",   up_fg="#ffffff",
    down_bg="#c0392b", down_fg="#ffffff",
    unknown_bg="#4a4a5a", unknown_fg="#aaaaaa",
    hist_up_fg="#50d890",
    hist_down_fg="#ff6b6b",
    hist_unknown_fg="#777777",
    chart_bg="#1e1e2e",
    chart_grid="#2e2e3e",
    chart_line="#50d890",
    chart_dot="#ff6b6b",
    chart_axis="#aaaaaa",
    chart_title="#cccccc",
    empty_fg="#555566",
)

LIGHT = Theme(
    name="light",
    bg="#ffffff",
    surface="#f2f2f2",
    surface_alt="#f9f9f9",
    border="#d4d4d4",
    text="#1a1a1a",
    text_muted="#666666",
    sel_bg="#0078d4",
    sel_fg="#ffffff",
    up_bg="#2d9e4e",   up_fg="#ffffff",
    down_bg="#c0392b", down_fg="#ffffff",
    unknown_bg="#6c757d", unknown_fg="#ffffff",
    hist_up_fg="#1a7a2e",
    hist_down_fg="#a01515",
    hist_unknown_fg="#666666",
    chart_bg="#f5f5f5",
    chart_grid="#e0e0e0",
    chart_line="#1a7a2e",
    chart_dot="#c0392b",
    chart_axis="#555555",
    chart_title="#333333",
    empty_fg="#aaaaaa",
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
QWidget {{
    background-color: {t.bg};
    color: {t.text};
}}
QMainWindow, QDialog {{
    background-color: {t.bg};
}}

/* ── Toolbar ─────────────────────────────────────────── */
QToolBar {{
    background-color: {t.surface};
    border: none;
    border-bottom: 1px solid {t.border};
    padding: 2px 4px;
    spacing: 2px;
}}
QToolBar QToolButton {{
    background-color: transparent;
    color: {t.text};
    border: none;
    border-radius: 3px;
    padding: 3px 7px;
}}
QToolBar QToolButton:hover {{
    background-color: {t.border};
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
    margin: 3px 4px;
}}

/* ── Tabs ─────────────────────────────────────────────── */
QTabWidget::pane {{
    border: none;
    background-color: {t.bg};
}}
QTabBar {{
    background-color: {t.surface};
}}
QTabBar::tab {{
    background-color: {t.surface};
    color: {t.text_muted};
    padding: 6px 16px;
    border-right: 1px solid {t.border};
}}
QTabBar::tab:selected {{
    background-color: {t.bg};
    color: {t.text};
    border-bottom: 2px solid {t.sel_bg};
}}
QTabBar::tab:hover:!selected {{
    color: {t.text};
    background-color: {t.surface_alt};
}}

/* ── Tables ───────────────────────────────────────────── */
QTableWidget {{
    background-color: {t.bg};
    alternate-background-color: {t.surface_alt};
    color: {t.text};
    gridline-color: {t.border};
    border: none;
    selection-background-color: {t.sel_bg};
    selection-color: {t.sel_fg};
}}
QTableWidget::item:selected {{
    background-color: {t.sel_bg};
    color: {t.sel_fg};
}}
QHeaderView {{
    background-color: {t.surface};
}}
QHeaderView::section {{
    background-color: {t.surface};
    color: {t.text_muted};
    border: none;
    border-right: 1px solid {t.border};
    border-bottom: 1px solid {t.border};
    padding: 4px 6px;
    font-weight: 600;
}}
QHeaderView::section:last {{
    border-right: none;
}}

/* ── Splitter ─────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {t.border};
}}
QSplitter::handle:vertical {{
    height: 1px;
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}

/* ── Status bar ───────────────────────────────────────── */
QStatusBar {{
    background-color: {t.surface};
    color: {t.text_muted};
    border-top: 1px solid {t.border};
}}

/* ── Form controls ────────────────────────────────────── */
QLineEdit {{
    background-color: {t.surface};
    color: {t.text};
    border: 1px solid {t.border};
    border-radius: 3px;
    padding: 4px 6px;
    selection-background-color: {t.sel_bg};
    selection-color: {t.sel_fg};
}}
QLineEdit:focus {{
    border-color: {t.sel_bg};
}}
QLineEdit:disabled {{
    color: {t.text_muted};
}}
QSpinBox {{
    background-color: {t.surface};
    color: {t.text};
    border: 1px solid {t.border};
    border-radius: 3px;
    padding: 3px 6px;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {t.surface};
    border: none;
    width: 16px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {t.border};
}}
QComboBox {{
    background-color: {t.surface};
    color: {t.text};
    border: 1px solid {t.border};
    border-radius: 3px;
    padding: 4px 6px;
    min-width: 60px;
}}
QComboBox:focus {{
    border-color: {t.sel_bg};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {t.surface};
    color: {t.text};
    selection-background-color: {t.sel_bg};
    selection-color: {t.sel_fg};
    border: 1px solid {t.border};
    outline: none;
}}

/* ── Buttons ──────────────────────────────────────────── */
QPushButton {{
    background-color: {t.surface};
    color: {t.text};
    border: 1px solid {t.border};
    border-radius: 3px;
    padding: 4px 14px;
    min-width: 60px;
}}
QPushButton:hover {{
    background-color: {t.border};
}}
QPushButton:pressed {{
    background-color: {t.sel_bg};
    color: {t.sel_fg};
}}
QPushButton:default {{
    border: 1px solid {t.sel_bg};
}}
QPushButton:disabled {{
    color: {t.text_muted};
    border-color: {t.border};
}}

/* ── Scrollbars ───────────────────────────────────────── */
QScrollBar:vertical {{
    background: {t.surface};
    width: 8px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {t.border};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {t.surface};
    height: 8px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {t.border};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Dialog chrome ────────────────────────────────────── */
QGroupBox {{
    color: {t.text_muted};
    border: 1px solid {t.border};
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 6px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 8px;
    color: {t.text_muted};
}}
QCheckBox {{
    color: {t.text};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {t.border};
    border-radius: 2px;
    background-color: {t.surface};
}}
QCheckBox::indicator:checked {{
    background-color: {t.sel_bg};
    border-color: {t.sel_bg};
}}
QLabel {{
    background-color: transparent;
    color: {t.text};
}}
QMenuBar {{
    background-color: {t.surface};
    color: {t.text};
}}
QMenuBar::item:selected {{
    background-color: {t.sel_bg};
    color: {t.sel_fg};
}}
QMenu {{
    background-color: {t.surface};
    color: {t.text};
    border: 1px solid {t.border};
}}
QMenu::item:selected {{
    background-color: {t.sel_bg};
    color: {t.sel_fg};
}}
"""
