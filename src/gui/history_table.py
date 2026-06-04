from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.models import ProbeResult, HostStatus

_COLUMNS = ["Timestamp", "Status", "Latency (ms)", "Error"]
MAX_ROWS = 500

_STATUS_BG = {
    HostStatus.UP: QColor("#c8f7c5"),
    HostStatus.DOWN: QColor("#f7c5c5"),
    HostStatus.UNKNOWN: QColor("#f0f0f0"),
}


class HistoryTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(2)

        self._label = QLabel("Seleziona un host per vedere lo storico")
        self._label.setStyleSheet("font-weight: bold; padding: 2px 6px;")
        layout.addWidget(self._label)

        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table)

        self._current_host: str | None = None

    def set_host(self, host: str, results: list[ProbeResult]):
        """Full refresh for the given host (called on selection change)."""
        self._current_host = host
        self._label.setText(f"Storico — {host}  ({len(results)} campioni)")
        self._table.setRowCount(0)
        for result in reversed(results):   # newest first
            self._append_row(self._table.rowCount(), result)

    def append_if_selected(self, result: ProbeResult):
        """Prepend a new result row if this host is currently shown."""
        if result.host != self._current_host:
            return
        self._append_row(0, result)
        if self._table.rowCount() > MAX_ROWS:
            self._table.removeRow(self._table.rowCount() - 1)
        # update sample count in label
        count = self._table.rowCount()
        host = self._current_host
        self._label.setText(f"Storico — {host}  ({count} campioni)")

    def clear(self):
        self._current_host = None
        self._table.setRowCount(0)
        self._label.setText("Seleziona un host per vedere lo storico")

    # ------------------------------------------------------------------
    def _append_row(self, row: int, result: ProbeResult):
        bg = _STATUS_BG[result.status]
        self._table.insertRow(row)
        self._cell(row, 0, result.timestamp.strftime("%Y-%m-%d %H:%M:%S"), bg)
        self._cell(row, 1, result.status.value.upper(), bg)
        self._cell(row, 2, f"{result.latency_ms:.1f}" if result.latency_ms is not None else "—", bg)
        self._cell(row, 3, result.error, bg)

    def _cell(self, row: int, col: int, text: str, bg: QColor | None = None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if bg:
            item.setBackground(bg)
        self._table.setItem(row, col, item)
