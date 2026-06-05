import queue
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QComboBox, QProgressBar, QCheckBox,
)
from PyQt6.QtCore import QTimer, pyqtSignal
from src.engines.port_scanner_engine import PortScannerEngine
from src.gui.widgets.port_result_table import PortResultTable
from src.models import PortScanResult


class PortScannerPanel(QWidget):
    add_to_monitor = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue: queue.Queue = queue.Queue()
        self._engine = PortScannerEngine()
        self._scan_start = 0.0
        self._counts: dict[str, int] = {"open": 0, "filtered": 0, "closed": 0}
        self._build_ui()
        self._flush_timer = QTimer()
        self._flush_timer.timeout.connect(self._flush)
        self._flush_timer.start(200)

    def set_target(self, host: str):
        self._host_input.setText(host)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.addWidget(QLabel("Host:"))
        self._host_input = QLineEdit()
        self._host_input.setPlaceholderText("IP or hostname")
        top.addWidget(self._host_input, stretch=1)
        top.addWidget(QLabel("Ports:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["Common (~100)", "Full (1-65535)", "Custom range"])
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        top.addWidget(self._mode_combo)
        self._custom_input = QLineEdit()
        self._custom_input.setPlaceholderText("e.g. 80,443,8080-8090")
        self._custom_input.setVisible(False)
        top.addWidget(self._custom_input)
        self._btn_scan = QPushButton("Scan")
        self._btn_scan.clicked.connect(self._start_scan)
        top.addWidget(self._btn_scan)
        self._btn_stop = QPushButton("Stop")
        self._btn_stop.clicked.connect(self._stop_scan)
        self._btn_stop.setEnabled(False)
        top.addWidget(self._btn_stop)
        layout.addLayout(top)

        mid = QHBoxLayout()
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        mid.addWidget(self._progress, stretch=1)
        self._lbl_stats = QLabel("Ready")
        mid.addWidget(self._lbl_stats)
        self._chk_closed = QCheckBox("Show closed")
        self._chk_closed.toggled.connect(
            lambda v: self._table.set_show_closed(v))
        mid.addWidget(self._chk_closed)
        layout.addLayout(mid)

        self._table = PortResultTable()
        self._table.add_to_monitor.connect(self.add_to_monitor)
        layout.addWidget(self._table)

    def _on_mode_changed(self, idx: int):
        self._custom_input.setVisible(idx == 2)

    def _start_scan(self):
        host = self._host_input.text().strip()
        if not host:
            return
        mode_map = {0: "common", 1: "full", 2: "custom"}
        mode = mode_map[self._mode_combo.currentIndex()]
        port_spec = self._custom_input.text().strip()

        self._table.clear_results()
        self._table.set_host(host)
        self._counts = {"open": 0, "filtered": 0, "closed": 0}
        self._scan_start = time.monotonic()
        self._progress.setValue(0)
        self._progress.setVisible(True)
        self._lbl_stats.setText("Scanning…")
        self._btn_scan.setEnabled(False)
        self._btn_stop.setEnabled(True)

        self._engine.scan(
            host=host,
            mode=mode,
            port_spec=port_spec,
            on_result=self._queue.put,
            on_progress=lambda s, t: self._queue.put(("progress", s, t)),
            on_done=lambda elapsed: self._queue.put(("done", elapsed)),
            timeout_ms=500,
        )

    def _stop_scan(self):
        self._engine.stop()
        self._btn_scan.setEnabled(True)
        self._btn_stop.setEnabled(False)

    def _flush(self):
        while not self._queue.empty():
            item = self._queue.get_nowait()
            if isinstance(item, PortScanResult):
                self._counts[item.state] = self._counts.get(item.state, 0) + 1
                self._table.add_result(item)
            elif isinstance(item, tuple):
                tag = item[0]
                if tag == "progress":
                    _, s, t = item
                    self._progress.setMaximum(t)
                    self._progress.setValue(s)
                    elapsed = time.monotonic() - self._scan_start
                    self._lbl_stats.setText(
                        f"{self._counts['open']} open | {elapsed:.0f}s"
                    )
                elif tag == "done":
                    _, elapsed = item
                    self._btn_scan.setEnabled(True)
                    self._btn_stop.setEnabled(False)
                    self._lbl_stats.setText(
                        f"{self._counts['open']} open, "
                        f"{self._counts['filtered']} filtered, "
                        f"{self._counts['closed']} closed | {elapsed:.1f}s"
                    )
