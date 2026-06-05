from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QDesktopServices
from PyQt6.QtCore import QUrl
from src.models import PortScanResult

COLUMNS = ["Port", "State", "Service", "Banner"]

_OPEN_BG = QColor("#c8f7c5")
_FILTERED_BG = QColor("#fff3cd")

_BROWSER_PORTS = {80, 443, 8080, 8443, 8000, 8008, 8888}


class PortResultTable(QTableWidget):
    add_to_monitor = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(0, len(COLUMNS), parent)
        self.setHorizontalHeaderLabels(COLUMNS)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._show_closed = False
        self._results: list[PortScanResult] = []
        self._current_host = ""

    def set_host(self, host: str):
        self._current_host = host

    def set_show_closed(self, show: bool):
        if self._show_closed == show:
            return
        self._show_closed = show
        self._rebuild()

    def add_result(self, result: PortScanResult):
        self._results.append(result)
        if result.state == "closed" and not self._show_closed:
            return
        self._insert_row(result)

    def clear_results(self):
        self.setRowCount(0)
        self._results.clear()

    def get_selected_port(self) -> int | None:
        rows = self.selectionModel().selectedRows()
        if not rows:
            return None
        item = self.item(rows[0].row(), 0)
        try:
            return int(item.text()) if item else None
        except ValueError:
            return None

    def _rebuild(self):
        self.setRowCount(0)
        for r in self._results:
            if r.state == "closed" and not self._show_closed:
                continue
            self._insert_row(r)

    def _insert_row(self, result: PortScanResult):
        row = self.rowCount()
        self.insertRow(row)
        if result.state == "open":
            bg = _OPEN_BG
        elif result.state == "filtered":
            bg = _FILTERED_BG
        else:
            bg = None
        for col, text in enumerate([
            str(result.port), result.state, result.service, result.banner,
        ]):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if bg:
                item.setBackground(bg)
            self.setItem(row, col, item)

    def _show_context_menu(self, _pos):
        rows = self.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        port_item = self.item(row, 0)
        state_item = self.item(row, 1)
        if not port_item:
            return
        port = int(port_item.text())
        state = state_item.text() if state_item else ""

        menu = QMenu(self)
        menu.addAction("Copy port").triggered.connect(
            lambda: QApplication.clipboard().setText(str(port)))

        if port in _BROWSER_PORTS:
            scheme = "https" if port in (443, 8443) else "http"
            url = f"{scheme}://{self._current_host}:{port}"
            menu.addAction("Open in browser").triggered.connect(
                lambda: QDesktopServices.openUrl(QUrl(url)))

        if state == "open":
            menu.addAction("Add to Monitor as TCP").triggered.connect(
                lambda: self.add_to_monitor.emit(self._current_host, port))

        menu.exec(QCursor.pos())
