import queue
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox,
)
from PyQt6.QtCore import QTimer, pyqtSignal
from src.engines.scanner_engine import ScannerEngine
from src.gui.widgets.scan_result_table import ScanResultTable
from src.models import ScanResult
from src.utils.privileges import is_admin


class ScannerPanel(QWidget):
    send_to_monitor = pyqtSignal(str)
    send_to_port_scanner = pyqtSignal(str)
    send_to_traceroute = pyqtSignal(str)
    send_to_dns = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue: queue.Queue = queue.Queue()
        self._engine: ScannerEngine | None = None
        self._scanned = 0
        self._admin = is_admin()
        self._all_results: list[ScanResult] = []  # full cache for re-filtering
        self._build_ui()
        self._flush_timer = QTimer()
        self._flush_timer.timeout.connect(self._flush)
        self._flush_timer.start(300)

    def set_target(self, host: str):
        self._target_input.setText(host)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.addWidget(QLabel("Target (IP, CIDR, range):"))
        self._target_input = QLineEdit()
        self._target_input.setPlaceholderText("e.g. 192.168.1.0/24 or 192.168.1.1-254")
        self._target_input.returnPressed.connect(self._start_scan)
        top.addWidget(self._target_input, stretch=1)
        self._btn_scan = QPushButton("Scan")
        self._btn_scan.clicked.connect(self._start_scan)
        top.addWidget(self._btn_scan)
        self._btn_stop = QPushButton("Stop")
        self._btn_stop.clicked.connect(self._stop_scan)
        self._btn_stop.setEnabled(False)
        top.addWidget(self._btn_stop)
        layout.addLayout(top)

        info = QHBoxLayout()
        self._lbl_progress = QLabel("Ready")
        info.addWidget(self._lbl_progress)
        if not self._admin:
            warn = QLabel("  Not admin — ARP/MAC unavailable")
            warn.setStyleSheet("color: #cc6600;")
            info.addWidget(warn)
        info.addStretch()

        self._chk_alive_only = QCheckBox("Show only alive hosts")
        self._chk_alive_only.setChecked(False)
        self._chk_alive_only.toggled.connect(self._on_filter_changed)
        info.addWidget(self._chk_alive_only)

        layout.addLayout(info)

        self._table = ScanResultTable()
        self._table.send_to_monitor.connect(self.send_to_monitor)
        self._table.send_to_port_scanner.connect(self.send_to_port_scanner)
        self._table.send_to_traceroute.connect(self.send_to_traceroute)
        self._table.send_to_dns.connect(self.send_to_dns)
        layout.addWidget(self._table)

    def _on_filter_changed(self):
        """Re-apply the alive-only filter to the cached results without re-scanning."""
        self._table.clear_results()
        only_alive = self._chk_alive_only.isChecked()
        for r in self._all_results:
            if only_alive and not r.is_alive:
                continue
            self._table.add_result(r)
        total = self._table.rowCount()
        alive = sum(1 for r in self._all_results if r.is_alive)
        if self._all_results:
            self._lbl_progress.setText(
                f"Done — {alive} alive / {len(self._all_results)} scanned"
                + (f"  (showing {total})" if only_alive else "")
            )

    def _start_scan(self):
        target = self._target_input.text().strip()
        if not target:
            return
        self._table.clear_results()
        self._all_results.clear()
        self._scanned = 0
        self._lbl_progress.setText("Scanning…")
        self._btn_scan.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._engine = ScannerEngine(
            on_result=self._queue.put,
            on_done=lambda: self._queue.put(None),
            use_arp=self._admin,
        )
        self._engine.run(target)

    def _stop_scan(self):
        if self._engine:
            self._engine.stop()
        self._btn_scan.setEnabled(True)
        self._btn_stop.setEnabled(False)
        alive = sum(1 for r in self._all_results if r.is_alive)
        self._lbl_progress.setText(
            f"Stopped — {alive} alive / {len(self._all_results)} scanned"
        )

    def _flush(self):
        only_alive = self._chk_alive_only.isChecked()
        while not self._queue.empty():
            item = self._queue.get_nowait()
            if item is None:
                # Scan complete
                self._btn_scan.setEnabled(True)
                self._btn_stop.setEnabled(False)
                alive = sum(1 for r in self._all_results if r.is_alive)
                total_shown = self._table.rowCount()
                total_scanned = len(self._all_results)
                msg = f"Done — {alive} alive / {total_scanned} scanned"
                if only_alive and total_shown < total_scanned:
                    msg += f"  (showing {total_shown})"
                self._lbl_progress.setText(msg)
                continue
            self._scanned += 1
            self._lbl_progress.setText(f"Scanned {self._scanned} hosts…")
            self._all_results.append(item)
            if only_alive and not item.is_alive:
                continue
            self._table.add_result(item)
