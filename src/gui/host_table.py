from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.models import HostEntry, ProbeResult, HostStatus, HostStats, ProbeType

COLUMNS = [
    "Host", "Type", "Target",
    "Status", "Last (ms)", "Avg (ms)", "Min (ms)", "Max (ms)",
    "Loss %", "Sent", "Last Check", "Error",
]

_STATUS_BG = {
    HostStatus.UP: QColor("#c8f7c5"),
    HostStatus.DOWN: QColor("#f7c5c5"),
    HostStatus.UNKNOWN: QColor("#f0f0f0"),
}


class HostTable(QTableWidget):
    def __init__(self):
        super().__init__(0, len(COLUMNS))
        self.setHorizontalHeaderLabels(COLUMNS)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self._row_map: dict[str, int] = {}

    def set_entries(self, entries: list[HostEntry]):
        self.setRowCount(0)
        self._row_map.clear()
        for i, entry in enumerate(entries):
            self.insertRow(i)
            self._fill_static(i, entry)

    def add_entry(self, entry: HostEntry):
        i = self.rowCount()
        self.insertRow(i)
        self._fill_static(i, entry)

    def remove_selected(self) -> str | None:
        rows = self.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        host = self.item(row, 0).text()
        self.removeRow(row)
        self._row_map = {self.item(r, 0).text(): r for r in range(self.rowCount())}
        return host

    def update_result(self, result: ProbeResult, stats: HostStats):
        row = self._row_map.get(result.host)
        if row is None:
            return
        bg = _STATUS_BG[result.status]
        self._cell(row, 3, result.status.value.upper(), bg)
        self._cell(row, 4, f"{result.latency_ms:.1f}" if result.latency_ms is not None else "—", bg)
        self._cell(row, 5, str(stats.avg_ms) if stats.avg_ms is not None else "—", bg)
        self._cell(row, 6, str(stats.min_ms) if stats.min_ms is not None else "—", bg)
        self._cell(row, 7, str(stats.max_ms) if stats.max_ms is not None else "—", bg)
        self._cell(row, 8, f"{stats.loss_pct}%", bg)
        self._cell(row, 9, str(stats.sent), bg)
        self._cell(row, 10, result.timestamp.strftime("%H:%M:%S"), bg)
        self._cell(row, 11, result.error, bg)

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

    def _cell(self, row: int, col: int, text: str, bg: QColor | None = None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if bg:
            item.setBackground(bg)
        self.setItem(row, col, item)


def _target(entry: HostEntry) -> str:
    if entry.probe_type == ProbeType.HTTP:
        return f":{entry.port}" if entry.port else "80"
    if entry.probe_type == ProbeType.TCP:
        return str(entry.port) if entry.port else "80"
    return "—"
