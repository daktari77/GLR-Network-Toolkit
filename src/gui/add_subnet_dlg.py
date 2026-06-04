from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QDialogButtonBox, QVBoxLayout, QLabel,
)
from PyQt6.QtCore import Qt
from src.models import HostEntry, ProbeType
from src.utils.ip_range import expand_range, MAX_HOSTS


class AddSubnetDialog(QDialog):
    """Dialog for adding all hosts in a subnet or IP range at once."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Subnet / IP Range")
        self.setMinimumWidth(440)
        self._entries: list[HostEntry] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._range_input = QLineEdit()
        self._range_input.setPlaceholderText(
            "e.g.  192.168.1.0/24   or   10.0.0.1-50   or   10.0.0.1-10.0.0.100"
        )
        self._range_input.textChanged.connect(self._on_input_changed)
        form.addRow("Range / Subnet:", self._range_input)

        self._type = QComboBox()
        self._type.addItems(["ICMP", "TCP"])
        self._type.currentTextChanged.connect(self._on_type_changed)
        form.addRow("Probe type:", self._type)

        self._port = QSpinBox()
        self._port.setRange(1, 65535)
        self._port.setValue(22)
        self._port.setEnabled(False)
        form.addRow("Port:", self._port)

        layout.addLayout(form)

        self._preview = QLabel(f"Enter a CIDR subnet or IP range (max {MAX_HOSTS} hosts).")
        self._preview.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._preview.setWordWrap(True)
        layout.addWidget(self._preview)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        ok_btn = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.setEnabled(False)
        self._buttons.accepted.connect(self._validate_and_accept)
        self._buttons.rejected.connect(self.reject)
        layout.addWidget(self._buttons)

    def _on_type_changed(self, t: str):
        self._port.setEnabled(t == "TCP")

    def _on_input_changed(self, text: str):
        ok_btn = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        text = text.strip()
        if not text:
            self._preview.setText(f"Enter a CIDR subnet or IP range (max {MAX_HOSTS} hosts).")
            ok_btn.setEnabled(False)
            return
        try:
            ips = expand_range(text)
            self._preview.setText(f"<b>{len(ips)}</b> host(s) will be added.")
            ok_btn.setEnabled(True)
        except ValueError as exc:
            self._preview.setText(f"<span style='color:#c0392b'>{exc}</span>")
            ok_btn.setEnabled(False)

    def _validate_and_accept(self):
        text = self._range_input.text().strip()
        try:
            ips = expand_range(text)
        except ValueError:
            return
        t = self._type.currentText()
        probe_type = ProbeType.ICMP if t == "ICMP" else ProbeType.TCP
        port = self._port.value() if t == "TCP" else None
        self._entries = [
            HostEntry(host=ip, probe_type=probe_type, port=port) for ip in ips
        ]
        self.accept()

    def get_entries(self) -> list[HostEntry]:
        return self._entries
