import queue
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLineEdit, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QSpinBox, QCheckBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor


# ---------------------------------------------------------------------------
# Traceroute view
# ---------------------------------------------------------------------------

class TracerouteView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue: queue.Queue = queue.Queue()
        self._engine = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        top = QHBoxLayout()
        top.addWidget(QLabel("Host:"))
        self._input = QLineEdit()
        self._input.setPlaceholderText("hostname or IP")
        self._input.returnPressed.connect(self._start)
        top.addWidget(self._input, stretch=1)
        self._btn_trace = QPushButton("Trace")
        self._btn_trace.clicked.connect(self._start)
        top.addWidget(self._btn_trace)
        self._btn_stop = QPushButton("Stop")
        self._btn_stop.clicked.connect(self._stop)
        self._btn_stop.setEnabled(False)
        top.addWidget(self._btn_stop)
        layout.addLayout(top)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Hop", "IP", "Hostname", "RTT (ms)"])
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self._table)

        self._timer = QTimer()
        self._timer.timeout.connect(self._flush)
        self._timer.start(150)

    def set_target(self, host: str):
        self._input.setText(host)

    def _start(self):
        host = self._input.text().strip()
        if not host:
            return
        self._table.setRowCount(0)
        self._btn_trace.setEnabled(False)
        self._btn_stop.setEnabled(True)
        from src.engines.traceroute_engine import TracerouteEngine
        self._engine = TracerouteEngine(
            on_hop=self._queue.put,
            on_done=lambda: self._queue.put(None),
        )
        self._engine.run(host)

    def _stop(self):
        if self._engine:
            self._engine.stop()
        self._btn_trace.setEnabled(True)
        self._btn_stop.setEnabled(False)

    def _flush(self):
        while not self._queue.empty():
            item = self._queue.get_nowait()
            if item is None:
                self._btn_trace.setEnabled(True)
                self._btn_stop.setEnabled(False)
                continue
            row = self._table.rowCount()
            self._table.insertRow(row)
            rtt = f"{item.rtt_ms:.0f}" if item.rtt_ms is not None else "*"
            for col, text in enumerate([
                str(item.hop), item.ip, item.hostname, rtt,
            ]):
                cell = QTableWidgetItem(text)
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if item.ip == "*":
                    cell.setForeground(QColor("#888888"))
                self._table.setItem(row, col, cell)


# ---------------------------------------------------------------------------
# DNS view
# ---------------------------------------------------------------------------

class DnsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        top = QHBoxLayout()
        top.addWidget(QLabel("Query:"))
        self._input = QLineEdit()
        self._input.setPlaceholderText("hostname or IP")
        self._input.returnPressed.connect(self._lookup)
        top.addWidget(self._input, stretch=1)
        self._btn = QPushButton("Lookup")
        self._btn.clicked.connect(self._lookup)
        top.addWidget(self._btn)
        layout.addLayout(top)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Field", "Value"])
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self._table)

    def set_target(self, host: str):
        self._input.setText(host)

    def _lookup(self):
        query = self._input.text().strip()
        if not query:
            return
        self._table.setRowCount(0)
        self._btn.setEnabled(False)
        threading.Thread(target=self._run, args=(query,), daemon=True).start()

    def _run(self, query: str):
        from src.engines import dns_engine
        result = dns_engine.run(query)
        from PyQt6.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(
            self, "_show_result",
            Qt.ConnectionType.QueuedConnection,
            *[],
        )
        self._pending = result
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._show_pending)

    def _show_pending(self):
        result = getattr(self, "_pending", None)
        if result is None:
            return
        self._btn.setEnabled(True)
        self._table.setRowCount(0)
        rows = [
            ("A Records", ", ".join(result.a_records) or "—"),
            ("PTR", result.ptr_record or "—"),
            ("MX", ", ".join(result.mx_records) or "—"),
            ("CNAME", result.cname_record or "—"),
        ]
        if result.error:
            rows.append(("Error", result.error))
        for field, value in rows:
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(field))
            self._table.setItem(r, 1, QTableWidgetItem(value))


# ---------------------------------------------------------------------------
# HTTP Inspector view
# ---------------------------------------------------------------------------

class HttpView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        top = QHBoxLayout()
        top.addWidget(QLabel("URL:"))
        self._input = QLineEdit()
        self._input.setPlaceholderText("https://example.com")
        self._input.returnPressed.connect(self._inspect)
        top.addWidget(self._input, stretch=1)
        self._chk_redirect = QCheckBox("Follow redirects")
        self._chk_redirect.setChecked(True)
        top.addWidget(self._chk_redirect)
        self._btn = QPushButton("Inspect")
        self._btn.clicked.connect(self._inspect)
        top.addWidget(self._btn)
        layout.addLayout(top)

        self._lbl_status = QLabel("")
        self._lbl_status.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self._lbl_status)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Header", "Value"])
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self._table)

    def set_target(self, host: str):
        url = host if host.startswith("http") else f"https://{host}"
        self._input.setText(url)

    def _inspect(self):
        url = self._input.text().strip()
        if not url:
            return
        self._table.setRowCount(0)
        self._lbl_status.setText("…")
        self._btn.setEnabled(False)
        follow = self._chk_redirect.isChecked()
        threading.Thread(target=self._run, args=(url, follow), daemon=True).start()

    def _run(self, url: str, follow: bool):
        from src.engines import http_inspector_engine
        result = http_inspector_engine.run(url, follow_redirects=follow)
        self._pending = result
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._show_pending)

    def _show_pending(self):
        result = getattr(self, "_pending", None)
        if not result:
            return
        self._btn.setEnabled(True)
        if result.error:
            self._lbl_status.setText(f"Error: {result.error}")
            return
        color = "#2d8a2d" if result.status_code < 400 else "#c00000"
        self._lbl_status.setText(
            f'<span style="color:{color}">{result.status_code}</span>'
            f"  —  {result.response_time_ms:.0f} ms  —  {result.url}"
        )
        self._table.setRowCount(0)
        for header, value in sorted(result.headers.items()):
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(header))
            self._table.setItem(r, 1, QTableWidgetItem(value))


# ---------------------------------------------------------------------------
# SSL Checker view
# ---------------------------------------------------------------------------

class SslView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        top = QHBoxLayout()
        top.addWidget(QLabel("Host:"))
        self._input = QLineEdit()
        self._input.setPlaceholderText("example.com")
        self._input.returnPressed.connect(self._check)
        top.addWidget(self._input, stretch=1)
        top.addWidget(QLabel("Port:"))
        self._port = QSpinBox()
        self._port.setRange(1, 65535)
        self._port.setValue(443)
        top.addWidget(self._port)
        self._btn = QPushButton("Check")
        self._btn.clicked.connect(self._check)
        top.addWidget(self._btn)
        layout.addLayout(top)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Field", "Value"])
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table)

    def set_target(self, host: str):
        self._input.setText(host)

    def _check(self):
        host = self._input.text().strip()
        if not host:
            return
        self._table.setRowCount(0)
        self._btn.setEnabled(False)
        port = self._port.value()
        threading.Thread(target=self._run, args=(host, port), daemon=True).start()

    def _run(self, host: str, port: int):
        from src.engines import ssl_engine
        result = ssl_engine.run(host, port)
        self._pending = result
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._show_pending)

    def _show_pending(self):
        result = getattr(self, "_pending", None)
        if not result:
            return
        self._btn.setEnabled(True)
        self._table.setRowCount(0)
        if result.error:
            self._add_row("Error", result.error, "#c00000")
            return
        days = result.days_remaining
        if days < 30:
            days_color = "#c00000"
        elif days < 90:
            days_color = "#cc6600"
        else:
            days_color = "#2d8a2d"
        rows = [
            ("Valid", "Yes" if result.valid else "No"),
            ("Subject", result.subject),
            ("Issuer", result.issuer),
            ("Expiry", result.expiry),
            ("Days remaining", str(days)),
            ("Cipher", result.cipher),
        ]
        for field, value in rows:
            color = days_color if field == "Days remaining" else None
            self._add_row(field, value, color)

    def _add_row(self, field: str, value: str, color: str | None = None):
        r = self._table.rowCount()
        self._table.insertRow(r)
        fi = QTableWidgetItem(field)
        vi = QTableWidgetItem(value)
        if color:
            vi.setForeground(QColor(color))
        self._table.setItem(r, 0, fi)
        self._table.setItem(r, 1, vi)


# ---------------------------------------------------------------------------
# Whois view
# ---------------------------------------------------------------------------

class WhoisView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        top = QHBoxLayout()
        top.addWidget(QLabel("Query:"))
        self._input = QLineEdit()
        self._input.setPlaceholderText("domain.com or IP")
        self._input.returnPressed.connect(self._lookup)
        top.addWidget(self._input, stretch=1)
        self._btn = QPushButton("Lookup")
        self._btn.clicked.connect(self._lookup)
        top.addWidget(self._btn)
        layout.addLayout(top)

        self._summary = QTableWidget(0, 2)
        self._summary.setHorizontalHeaderLabels(["Field", "Value"])
        self._summary.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._summary.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._summary.setMaximumHeight(160)
        layout.addWidget(self._summary)

        layout.addWidget(QLabel("Raw output:"))
        self._raw = QTextEdit()
        self._raw.setReadOnly(True)
        self._raw.setFontFamily("Courier New")
        layout.addWidget(self._raw)

    def set_target(self, host: str):
        self._input.setText(host)

    def _lookup(self):
        query = self._input.text().strip()
        if not query:
            return
        self._summary.setRowCount(0)
        self._raw.setPlainText("Looking up…")
        self._btn.setEnabled(False)
        threading.Thread(target=self._run, args=(query,), daemon=True).start()

    def _run(self, query: str):
        from src.engines import whois_engine
        result = whois_engine.run(query)
        self._pending = result
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._show_pending)

    def _show_pending(self):
        result = getattr(self, "_pending", None)
        if not result:
            return
        self._btn.setEnabled(True)
        self._summary.setRowCount(0)
        rows = [
            ("Registrar", result.registrar),
            ("Created", result.created),
            ("Expires", result.expires),
            ("Name Servers", ", ".join(result.name_servers)),
        ]
        if result.error:
            rows.append(("Error", result.error))
        for field, value in rows:
            if not value:
                continue
            r = self._summary.rowCount()
            self._summary.insertRow(r)
            self._summary.setItem(r, 0, QTableWidgetItem(field))
            self._summary.setItem(r, 1, QTableWidgetItem(value))
        self._raw.setPlainText(result.raw)


# ---------------------------------------------------------------------------
# Main TroubleshootPanel
# ---------------------------------------------------------------------------

class TroubleshootPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()
        self._traceroute = TracerouteView()
        self._dns = DnsView()
        self._http = HttpView()
        self._ssl = SslView()
        self._whois = WhoisView()

        self._tabs.addTab(self._traceroute, "Traceroute")
        self._tabs.addTab(self._dns, "DNS Lookup")
        self._tabs.addTab(self._http, "HTTP Inspector")
        self._tabs.addTab(self._ssl, "SSL Checker")
        self._tabs.addTab(self._whois, "Whois")

        layout.addWidget(self._tabs)

    def set_traceroute_target(self, host: str):
        self._traceroute.set_target(host)
        self._tabs.setCurrentWidget(self._traceroute)

    def set_dns_target(self, host: str):
        self._dns.set_target(host)
        self._tabs.setCurrentWidget(self._dns)

    def set_target(self, host: str):
        current = self._tabs.currentWidget()
        if hasattr(current, "set_target"):
            current.set_target(host)
