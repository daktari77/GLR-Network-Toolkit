from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
    QApplication,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import sys, os
from src.gui.panels.monitor_panel import MonitorPanel
from src.gui.panels.scanner_panel import ScannerPanel
from src.gui.panels.port_scanner_panel import PortScannerPanel
from src.gui.panels.troubleshoot_panel import TroubleshootPanel
from src.models import ProbeType, HostEntry
from src.utils.privileges import is_admin, restart_as_admin
import src.app_settings as app_settings
import src.gui.theme as theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GLR NetScope")
        self.setMinimumSize(1200, 700)

        base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base, '..', '..', 'Icon', 'app.ico')
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     '..', '..', 'Icon', 'app.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._settings = app_settings.load()

        # Apply saved theme before building any widgets
        t = theme.THEMES.get(self._settings.theme, theme.DARK)
        theme.apply(QApplication.instance(), t)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        if not is_admin():
            self._admin_banner = self._build_admin_banner()
            root_layout.addWidget(self._admin_banner)

        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        root_layout.addWidget(self._tabs)
        self.setCentralWidget(root)

        self._monitor = MonitorPanel(self._settings)
        self._scanner = ScannerPanel()
        self._port_scanner = PortScannerPanel()
        self._troubleshoot = TroubleshootPanel()

        self._tabs.addTab(self._monitor, "Monitor")
        self._tabs.addTab(self._scanner, "Network Scanner")
        self._tabs.addTab(self._port_scanner, "Port Scanner")
        self._tabs.addTab(self._troubleshoot, "Troubleshoot")

        self._monitor.status_changed.connect(self.statusBar().showMessage)
        self._monitor.theme_changed.connect(self._on_theme_changed)

        # Cross-panel wiring: scanner → other tabs
        self._scanner.send_to_monitor.connect(self._add_host_to_monitor)
        self._scanner.send_to_port_scanner.connect(self._send_to_port_scanner)
        self._scanner.send_to_traceroute.connect(self._troubleshoot.set_traceroute_target)
        self._scanner.send_to_dns.connect(self._troubleshoot.set_dns_target)

        # Cross-panel wiring: monitor → other tabs
        self._monitor.send_to_port_scanner.connect(self._send_to_port_scanner)
        self._monitor.send_to_traceroute.connect(self._troubleshoot.set_traceroute_target)
        self._monitor.send_to_dns.connect(self._troubleshoot.set_dns_target)

        # Cross-panel wiring: port scanner → monitor
        self._port_scanner.add_to_monitor.connect(self._add_tcp_to_monitor)

    def _build_admin_banner(self) -> QWidget:
        banner = QWidget()
        banner.setObjectName("admin_banner")
        banner.setStyleSheet(
            "QWidget#admin_banner { background:#856404; border-bottom:1px solid #6d5204; }"
        )
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(8, 4, 8, 4)
        lbl = QLabel("Some features require elevated privileges (ARP scan, MAC lookup).")
        lbl.setStyleSheet("color:#fff8dc; background:transparent;")
        bl.addWidget(lbl)
        bl.addStretch()
        btn = QPushButton("Restart as Administrator")
        btn.setStyleSheet(
            "background:#ffc107; color:#000; border:none; padding:4px 12px;"
            "border-radius:4px; font-weight:bold;"
        )
        btn.clicked.connect(restart_as_admin)
        bl.addWidget(btn)
        return banner

    def _on_theme_changed(self, theme_name: str):
        t = theme.THEMES.get(theme_name, theme.DARK)
        theme.apply(QApplication.instance(), t)
        self._settings.theme = theme_name
        self._monitor.refresh_theme()

    def _add_host_to_monitor(self, ip: str):
        self._monitor.add_host_from_scan(ip)
        self._tabs.setCurrentWidget(self._monitor)

    def _send_to_port_scanner(self, ip: str):
        self._port_scanner.set_target(ip)
        self._tabs.setCurrentWidget(self._port_scanner)

    def _add_tcp_to_monitor(self, host: str, port: int):
        self._monitor.add_host_tcp(host, port)
        self._tabs.setCurrentWidget(self._monitor)

    def closeEvent(self, event):
        self._monitor.save_settings()
        app_settings.save(self._settings)
        event.accept()
