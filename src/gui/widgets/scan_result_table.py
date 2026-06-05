from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QCursor
from src.models import ScanResult

COLUMNS = ["IP", "Hostname", "MAC", "Vendor", "Latency (ms)", "Status"]

_ALIVE_BG = QColor("#c8f7c5")
_DEAD_BG = QColor("#f7c5c5")


class ScanResultTable(QTableWidget):
    send_to_monitor = pyqtSignal(str)
    send_to_port_scanner = pyqtSignal(str)
    send_to_traceroute = pyqtSignal(str)
    send_to_dns = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(0, len(COLUMNS), parent)
        self.setHorizontalHeaderLabels(COLUMNS)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        self.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._ip_map: dict[str, int] = {}
        self._sort_col: int = -1
        self._sort_order: Qt.SortOrder = Qt.SortOrder.AscendingOrder

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
        self._rebuild_ip_map()

    def _rebuild_ip_map(self):
        self._ip_map = {
            self.item(r, 0).text(): r
            for r in range(self.rowCount())
            if self.item(r, 0)
        }

    def add_result(self, result: ScanResult):
        if result.ip in self._ip_map:
            row = self._ip_map[result.ip]
        else:
            row = self.rowCount()
            self.insertRow(row)
            self._ip_map[result.ip] = row

        bg = _ALIVE_BG if result.is_alive else _DEAD_BG
        latency = f"{result.latency_ms:.1f}" if result.latency_ms is not None else "—"
        status = "ALIVE" if result.is_alive else "DOWN"

        for col, text in enumerate([
            result.ip, result.hostname, result.mac, result.vendor, latency, status,
        ]):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(bg)
            self.setItem(row, col, item)

    def clear_results(self):
        self.setRowCount(0)
        self._ip_map.clear()

    def get_selected_ip(self) -> str | None:
        rows = self.selectionModel().selectedRows()
        if not rows:
            return None
        item = self.item(rows[0].row(), 0)
        return item.text() if item else None

    def _show_context_menu(self, _pos):
        ip = self.get_selected_ip()
        if not ip:
            return
        menu = QMenu(self)
        menu.addAction("Add to Monitor").triggered.connect(
            lambda: self.send_to_monitor.emit(ip))
        menu.addAction("Send to Port Scanner").triggered.connect(
            lambda: self.send_to_port_scanner.emit(ip))
        menu.addAction("Send to Traceroute").triggered.connect(
            lambda: self.send_to_traceroute.emit(ip))
        menu.addAction("Send to DNS Lookup").triggered.connect(
            lambda: self.send_to_dns.emit(ip))
        menu.addSeparator()
        menu.addAction("Copy IP").triggered.connect(
            lambda: QApplication.clipboard().setText(ip))
        menu.exec(QCursor.pos())
