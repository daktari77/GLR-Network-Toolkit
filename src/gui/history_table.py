from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.models import ProbeResult, HostStatus
import src.gui.theme as theme

_COLUMNS = ["Timestamp", "Status", "Latency (ms)", "Error"]
MAX_ROWS = 500

_HIST_COL_ALIGN = {
    0: Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
    1: Qt.AlignmentFlag.AlignCenter,
    2: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
    3: Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
}


def _status_fg(status: HostStatus) -> QColor:
    t = theme.current()
    if status == HostStatus.UP:
        return QColor(t.hist_up_fg)
    if status == HostStatus.DOWN:
        return QColor(t.hist_down_fg)
    return QColor(t.hist_unknown_fg)


class HistoryTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(2)

        self._label = QLabel("Select a host to view history")
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
        self._table.setSortingEnabled(False)
        self._table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        self._table.horizontalHeader().setSortIndicatorShown(True)
        self._sort_col: int = -1
        self._sort_order: Qt.SortOrder = Qt.SortOrder.AscendingOrder
        layout.addWidget(self._table)

        self._current_host: str | None = None
        # track status per row for theme refresh
        self._row_status: list[HostStatus] = []

    def _on_header_clicked(self, col: int):
        if self._sort_col == col:
            self._sort_order = (
                Qt.SortOrder.DescendingOrder
                if self._sort_order == Qt.SortOrder.AscendingOrder
                else Qt.SortOrder.AscendingOrder
            )
        else:
            self._sort_col = col
            self._sort_order = Qt.SortOrder.AscendingOrder
        self._table.sortItems(col, self._sort_order)
        self._table.horizontalHeader().setSortIndicator(col, self._sort_order)

    def set_host(self, host: str, results: list[ProbeResult]):
        self._current_host = host
        self._label.setText(f"History: {host} ({len(results)} samples)")
        self._table.setRowCount(0)
        self._row_status.clear()
        for result in reversed(results):
            self._append_row(self._table.rowCount(), result)

    def append_if_selected(self, result: ProbeResult):
        if result.host != self._current_host:
            return
        self._append_row(0, result)
        self._row_status.insert(0, result.status)
        if self._table.rowCount() > MAX_ROWS:
            self._table.removeRow(self._table.rowCount() - 1)
            if len(self._row_status) > MAX_ROWS:
                self._row_status.pop()
        count = self._table.rowCount()
        self._label.setText(f"History: {self._current_host} ({count} samples)")

    def clear(self):
        self._current_host = None
        self._table.setRowCount(0)
        self._row_status.clear()
        self._label.setText("Select a host to view history")

    def refresh_theme(self):
        for row, status in enumerate(self._row_status):
            item = self._table.item(row, 1)
            if item:
                item.setForeground(_status_fg(status))

    def _append_row(self, row: int, result: ProbeResult):
        self._table.insertRow(row)
        self._cell(row, 0, result.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        self._status_cell(row, 1, result.status.value.upper(), _status_fg(result.status))
        self._cell(row, 2, f"{result.latency_ms:.1f}" if result.latency_ms is not None else "—")
        self._cell(row, 3, result.error)
        self._row_status.insert(row, result.status)

    def _status_cell(self, row: int, col: int, text: str, fg: QColor):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(fg)
        self._table.setItem(row, col, item)

    def _cell(self, row: int, col: int, text: str):
        item = QTableWidgetItem(text)
        item.setTextAlignment(
            _HIST_COL_ALIGN.get(col, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        )
        self._table.setItem(row, col, item)
