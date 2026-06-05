from PyQt6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.models import HostEntry, ProbeResult, HostStatus, HostStats, ProbeType
import src.gui.theme as theme


class _NumItem(QTableWidgetItem):
    """TableWidgetItem that sorts numerically; '—' sorts as -inf."""
    def __lt__(self, other: QTableWidgetItem) -> bool:
        def _val(t: str) -> float:
            t = t.rstrip("%").strip()
            try:
                return float(t)
            except ValueError:
                return float("-inf")
        return _val(self.text()) < _val(other.text())


COLUMNS = [
    "Host", "Type", "Target",
    "Status", "Last (ms)", "Avg (ms)", "Min (ms)", "Max (ms)",
    "Loss %", "Sent", "Last Check", "Error",
]

_COL_ALIGN = {
    0: Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
    1: Qt.AlignmentFlag.AlignCenter,
    2: Qt.AlignmentFlag.AlignCenter,
    3: Qt.AlignmentFlag.AlignCenter,
    4: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
    5: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
    6: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
    7: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
    8: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
    9: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
    10: Qt.AlignmentFlag.AlignCenter,
    11: Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
}

_STATUS_BG = {
    HostStatus.UP: QColor("#2d9e4e"),
    HostStatus.DOWN: QColor("#c0392b"),
    HostStatus.UNKNOWN: QColor("#6c757d"),
}
_STATUS_FG = QColor("white")


class HostTable(QTableWidget):
    def __init__(self):
        super().__init__(0, len(COLUMNS))
        self.setHorizontalHeaderLabels(COLUMNS)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        # Sorting is manual-only: header click sorts once and rebuilds _row_map.
        # Keeping setSortingEnabled(True) during live updates causes auto-resort
        # after every setItem call, which invalidates _row_map mid-update.
        self.setSortingEnabled(False)
        self.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        self.horizontalHeader().setSortIndicatorShown(True)
        self._sort_col: int = -1
        self._sort_order: Qt.SortOrder = Qt.SortOrder.AscendingOrder
        self._row_map: dict[str, int] = {}

        self._empty_label = QLabel(
            "No hosts loaded — use Load Hosts or + Add to begin monitoring",
            self.viewport(),
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(
            f"color: {theme.current().empty_fg}; font-size: 10pt; background: transparent;"
        )
        self._empty_label.resize(self.viewport().size())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._empty_label.resize(self.viewport().size())

    def _update_empty_state(self):
        self._empty_label.setVisible(self.rowCount() == 0)

    def refresh_theme(self):
        self._empty_label.setStyleSheet(
            f"color: {theme.current().empty_fg}; font-size: 10pt; background: transparent;"
        )

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
        self.sortItems(col, self._sort_order)
        self.horizontalHeader().setSortIndicator(col, self._sort_order)
        self._rebuild_row_map()

    def _rebuild_row_map(self):
        self._row_map = {
            self.item(r, 0).text(): r
            for r in range(self.rowCount())
            if self.item(r, 0)
        }

    def set_entries(self, entries: list[HostEntry]):
        self.setRowCount(0)
        self._row_map.clear()
        for i, entry in enumerate(entries):
            self.insertRow(i)
            self._fill_static(i, entry)
        self._update_empty_state()

    def add_entry(self, entry: HostEntry):
        i = self.rowCount()
        self.insertRow(i)
        self._fill_static(i, entry)
        self._update_empty_state()

    def remove_selected(self) -> str | None:
        rows = self.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        host = self.item(row, 0).text()
        self.removeRow(row)
        self._rebuild_row_map()
        self._update_empty_state()
        return host

    def update_result(self, result: ProbeResult, stats: HostStats):
        row = self._row_map.get(result.host)
        if row is None:
            return
        self._status_cell(row, 3, result.status.value.upper(), _STATUS_BG[result.status])
        self._num(row, 4, f"{result.latency_ms:.1f}" if result.latency_ms is not None else "—")
        self._num(row, 5, str(stats.avg_ms) if stats.avg_ms is not None else "—")
        self._num(row, 6, str(stats.min_ms) if stats.min_ms is not None else "—")
        self._num(row, 7, str(stats.max_ms) if stats.max_ms is not None else "—")
        self._num(row, 8, f"{stats.loss_pct}%")
        self._num(row, 9, str(stats.sent))
        self._cell(row, 10, result.timestamp.strftime("%H:%M:%S"))
        self._cell(row, 11, result.error)

    def get_all_rows(self) -> list[list[str]]:
        return [
            [self.item(r, c).text() if self.item(r, c) else "" for c in range(len(COLUMNS))]
            for r in range(self.rowCount())
        ]

    def _fill_static(self, i: int, entry: HostEntry):
        self._row_map[entry.host] = i
        self._cell(i, 0, entry.host)
        self._cell(i, 1, entry.probe_type.value.upper())
        self._cell(i, 2, _target(entry))
        for col in range(3, len(COLUMNS)):
            self._cell(i, col, "—")

    def _status_cell(self, row: int, col: int, text: str, bg: QColor):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setBackground(bg)
        item.setForeground(_STATUS_FG)
        self.setItem(row, col, item)

    def _cell(self, row: int, col: int, text: str, bg: QColor | None = None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(_COL_ALIGN.get(col, Qt.AlignmentFlag.AlignCenter))
        if bg:
            item.setBackground(bg)
        self.setItem(row, col, item)

    def _num(self, row: int, col: int, text: str, bg: QColor | None = None):
        item = _NumItem(text)
        item.setTextAlignment(
            _COL_ALIGN.get(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        )
        if bg:
            item.setBackground(bg)
        self.setItem(row, col, item)


def _target(entry: HostEntry) -> str:
    if entry.probe_type == ProbeType.HTTP:
        return f":{entry.port}" if entry.port else "80"
    if entry.probe_type == ProbeType.TCP:
        return str(entry.port) if entry.port else "80"
    return "—"
