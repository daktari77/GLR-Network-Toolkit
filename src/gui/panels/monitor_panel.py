import csv
import queue
from collections import deque
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFileDialog, QLabel, QSpinBox, QToolBar, QSplitter,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from src.gui.host_table import HostTable, COLUMNS
from src.gui.history_table import HistoryTable, MAX_ROWS
from src.gui.widgets.latency_chart import LatencyChart
from src.gui.widgets.status_summary import StatusSummary
from src.gui.settings_dlg import SettingsDialog
from src.gui.add_host_dlg import AddHostDialog
from src.gui.add_subnet_dlg import AddSubnetDialog
from src.models import HostEntry, ProbeResult, ProbeType, HostStats, HostStatus
from src.utils.ip_range import expand_range, is_range_notation
from src.monitor import Monitor
from src.alerting import Alerter, AlertConfig
import src.app_settings as app_settings


class MonitorPanel(QWidget):
    send_to_port_scanner = pyqtSignal(str)
    send_to_traceroute = pyqtSignal(str)
    send_to_dns = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)

    def __init__(self, settings: app_settings.AppSettings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._result_queue: queue.Queue[ProbeResult] = queue.Queue()
        self._monitor: Monitor | None = None
        self._alert_config = _cfg_from_settings(settings)
        self._alerter = Alerter(self._alert_config)
        self._entries: list[HostEntry] = []
        self._stats: dict[str, HostStats] = {}
        self._history: dict[str, deque[ProbeResult]] = {}
        self._host_status: dict[str, HostStatus] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._build_toolbar(layout)
        self._build_central(layout)

        self._flush_timer = QTimer()
        self._flush_timer.timeout.connect(self._flush_queue)
        self._flush_timer.start(400)

        self._interval.setValue(settings.interval)
        if settings.last_hosts_file:
            p = Path(settings.last_hosts_file)
            if p.exists():
                self._load_from_path(str(p))

    def _build_toolbar(self, layout: QVBoxLayout):
        tb = QToolBar("Monitor")
        tb.setMovable(False)

        act_load = QAction("Load Hosts…", self)
        act_load.triggered.connect(self._load_hosts)
        tb.addAction(act_load)

        act_add = QAction("＋ Add", self)
        act_add.triggered.connect(self._add_host)
        tb.addAction(act_add)

        act_add_range = QAction("＋ Add Range…", self)
        act_add_range.triggered.connect(self._add_subnet)
        tb.addAction(act_add_range)

        act_remove = QAction("－ Remove", self)
        act_remove.triggered.connect(self._remove_host)
        tb.addAction(act_remove)

        tb.addSeparator()

        self._act_start = QAction("▶  Start", self)
        self._act_start.triggered.connect(self._start)
        tb.addAction(self._act_start)

        self._act_stop = QAction("■  Stop", self)
        self._act_stop.triggered.connect(self._stop)
        self._act_stop.setEnabled(False)
        tb.addAction(self._act_stop)

        tb.addSeparator()
        tb.addWidget(QLabel("  Interval (s): "))
        self._interval = QSpinBox()
        self._interval.setRange(1, 300)
        self._interval.setValue(5)
        tb.addWidget(self._interval)

        tb.addSeparator()

        act_export = QAction("Export CSV…", self)
        act_export.triggered.connect(self._export_csv)
        tb.addAction(act_export)

        act_settings = QAction("Settings…", self)
        act_settings.triggered.connect(self._open_settings)
        tb.addAction(act_settings)

        layout.addWidget(tb)

    def _build_central(self, layout: QVBoxLayout):
        self._summary = StatusSummary()
        layout.addWidget(self._summary)

        self._splitter = QSplitter(Qt.Orientation.Vertical)

        self._table = HostTable()
        self._table.itemSelectionChanged.connect(self._on_host_selected)
        self._splitter.addWidget(self._table)

        # Bottom: history table (left) + latency chart (right)
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._history_table = HistoryTable()
        self._latency_chart = LatencyChart()
        bottom_splitter.addWidget(self._history_table)
        bottom_splitter.addWidget(self._latency_chart)
        bottom_splitter.setStretchFactor(0, 1)
        bottom_splitter.setStretchFactor(1, 1)
        self._splitter.addWidget(bottom_splitter)

        self._splitter.setStretchFactor(0, 3)
        self._splitter.setStretchFactor(1, 2)
        layout.addWidget(self._splitter)

    def _on_host_selected(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 0)
        if item is None:
            return
        host = item.text()
        history = list(self._history.get(host, []))
        self._history_table.set_host(host, history)
        self._latency_chart.set_data(host, history)

    def _load_hosts(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open host list", "", "Text files (*.txt);;All files (*)"
        )
        if path:
            self._load_from_path(path)

    def _load_from_path(self, path: str):
        self._entries = _parse_hosts_file(path)
        self._stats = {e.host: HostStats() for e in self._entries}
        self._history = {e.host: deque(maxlen=MAX_ROWS) for e in self._entries}
        self._host_status = {}
        self._table.set_entries(self._entries)
        self._history_table.clear()
        self._settings.last_hosts_file = path
        self._update_summary()
        self.status_changed.emit(f"Loaded {len(self._entries)} hosts from {path}")

    def _add_host(self):
        dlg = AddHostDialog(parent=self)
        if not dlg.exec():
            return
        entry = dlg.get_entry()
        self._entries.append(entry)
        self._stats[entry.host] = HostStats()
        self._history[entry.host] = deque(maxlen=MAX_ROWS)
        self._table.add_entry(entry)
        self._update_summary()
        if self._monitor:
            self._restart_monitor()

    def _add_subnet(self):
        dlg = AddSubnetDialog(parent=self)
        if not dlg.exec():
            return
        new_entries = dlg.get_entries()
        for entry in new_entries:
            if entry.host not in self._stats:
                self._entries.append(entry)
                self._stats[entry.host] = HostStats()
                self._history[entry.host] = deque(maxlen=MAX_ROWS)
                self._table.add_entry(entry)
        self._update_summary()
        self.status_changed.emit(f"Added {len(new_entries)} host(s) from range.")
        if self._monitor:
            self._restart_monitor()

    def _remove_host(self):
        host = self._table.remove_selected()
        if not host:
            return
        self._entries = [e for e in self._entries if e.host != host]
        self._stats.pop(host, None)
        self._history.pop(host, None)
        self._host_status.pop(host, None)
        self._history_table.clear()
        self._update_summary()
        if self._monitor:
            self._restart_monitor()

    def _start(self):
        if not self._entries:
            self.status_changed.emit("No hosts loaded — use 'Load Hosts…' or '＋ Add'")
            return
        self._monitor = Monitor(
            entries=self._entries,
            interval=self._interval.value(),
            on_result=self._result_queue.put,
        )
        self._monitor.start()
        self._act_start.setEnabled(False)
        self._act_stop.setEnabled(True)
        self.status_changed.emit("Monitoring…")

    def _stop(self):
        if self._monitor:
            self._monitor.stop()
            self._monitor = None
        self._act_start.setEnabled(True)
        self._act_stop.setEnabled(False)
        self.status_changed.emit("Stopped")

    def _restart_monitor(self):
        if self._monitor:
            self._monitor.stop()
        self._monitor = Monitor(
            entries=self._entries,
            interval=self._interval.value(),
            on_result=self._result_queue.put,
        )
        self._monitor.start()

    def _open_settings(self):
        dlg = SettingsDialog(self._alert_config, self._settings.theme, parent=self)
        if dlg.exec():
            _sync_cfg_to_settings(self._alert_config, self._settings)
            self._alerter = Alerter(self._alert_config)
            if dlg.theme_changed:
                self.theme_changed.emit(dlg.chosen_theme)

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "pinginfo_export.csv", "CSV files (*.csv)"
        )
        if not path:
            return
        rows = self._table.get_all_rows()
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(COLUMNS)
            csv.writer(f).writerows(rows)
        self.status_changed.emit(f"Exported {len(rows)} rows to {path}")

    def _flush_queue(self):
        changed = False
        while not self._result_queue.empty():
            result: ProbeResult = self._result_queue.get_nowait()
            stats = self._stats.setdefault(result.host, HostStats())
            stats.update(result)
            self._host_status[result.host] = result.status
            self._table.update_result(result, stats)
            self._alerter.check(result)
            self._history.setdefault(result.host, deque(maxlen=MAX_ROWS)).append(result)
            self._history_table.append_if_selected(result)
            self._latency_chart.append_point(result)
            changed = True
        if changed:
            self._update_summary()

    def _update_summary(self):
        total = len(self._entries)
        up = sum(1 for s in self._host_status.values() if s == HostStatus.UP)
        down = sum(1 for s in self._host_status.values() if s == HostStatus.DOWN)
        unknown = total - up - down
        latencies = [s.avg_ms for s in self._stats.values() if s.avg_ms is not None]
        avg_ms = f"{sum(latencies) / len(latencies):.1f} ms" if latencies else "—"
        self._summary.update_stats(total, up, down, unknown, avg_ms)

    def refresh_theme(self):
        self._summary.refresh_theme()
        self._table.refresh_theme()
        self._history_table.refresh_theme()
        self._latency_chart.update()

    def save_settings(self):
        self._stop()
        self._settings.interval = self._interval.value()

    def add_host_from_scan(self, ip: str):
        """Add a host (ICMP) from scanner context menu."""
        entry = HostEntry(host=ip, probe_type=ProbeType.ICMP)
        if ip not in self._stats:
            self._entries.append(entry)
            self._stats[ip] = HostStats()
            self._history[ip] = deque(maxlen=MAX_ROWS)
            self._table.add_entry(entry)
            self._update_summary()
            if self._monitor:
                self._restart_monitor()
            self.status_changed.emit(f"Added {ip} to monitor.")

    def add_host_tcp(self, ip: str, port: int):
        """Add a host as TCP probe from port scanner context menu."""
        entry = HostEntry(host=ip, probe_type=ProbeType.TCP, port=port)
        if ip not in self._stats:
            self._entries.append(entry)
            self._stats[ip] = HostStats()
            self._history[ip] = deque(maxlen=MAX_ROWS)
            self._table.add_entry(entry)
            self._update_summary()
            if self._monitor:
                self._restart_monitor()
            self.status_changed.emit(f"Added {ip}:{port} (TCP) to monitor.")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _parse_hosts_file(path: str) -> list[HostEntry]:
    entries: list[HostEntry] = []
    seen: set[str] = set()

    def _add(entry: HostEntry):
        if entry.host not in seen:
            seen.add(entry.host)
            entries.append(entry)

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            token = parts[0]
            probe_type = ProbeType.ICMP
            port: int | None = None
            if len(parts) >= 2:
                t = parts[1].upper()
                if t == "TCP":
                    probe_type = ProbeType.TCP
                    port = int(parts[2]) if len(parts) >= 3 else 80
                elif t == "HTTP":
                    probe_type = ProbeType.HTTP
                    port = int(parts[2]) if len(parts) >= 3 else None
                elif t == "HTTPS":
                    probe_type = ProbeType.HTTP
                    port = int(parts[2]) if len(parts) >= 3 else None
                    if not token.startswith("https://"):
                        token = f"https://{token}"

            if is_range_notation(token):
                try:
                    for ip in expand_range(token):
                        _add(HostEntry(host=ip, probe_type=probe_type, port=port))
                except ValueError:
                    pass
            else:
                _add(HostEntry(host=token, probe_type=probe_type, port=port))

    return entries


def _cfg_from_settings(s: app_settings.AppSettings) -> AlertConfig:
    cfg = AlertConfig()
    cfg.log_file = s.alert_log_file or None
    cfg.webhook_url = s.alert_webhook_url
    cfg.smtp_host = s.smtp_host
    cfg.smtp_port = s.smtp_port
    cfg.smtp_user = s.smtp_user
    cfg.smtp_password = s.smtp_password
    cfg.smtp_from = s.smtp_from
    cfg.smtp_to = list(s.smtp_to)
    return cfg


def _sync_cfg_to_settings(cfg: AlertConfig, s: app_settings.AppSettings):
    s.alert_log_file = cfg.log_file or ""
    s.alert_webhook_url = cfg.webhook_url
    s.smtp_host = cfg.smtp_host
    s.smtp_port = cfg.smtp_port
    s.smtp_user = cfg.smtp_user
    s.smtp_password = cfg.smtp_password
    s.smtp_from = cfg.smtp_from
    s.smtp_to = list(cfg.smtp_to)
