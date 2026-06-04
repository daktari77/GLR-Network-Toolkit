from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QDialogButtonBox, QVBoxLayout,
)
from src.models import HostEntry, ProbeType


class AddHostDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Host")
        self.setMinimumWidth(360)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._host = QLineEdit()
        self._host.setPlaceholderText("hostname, IP or http://...")
        form.addRow("Host:", self._host)

        self._type = QComboBox()
        self._type.addItems(["ICMP", "TCP", "HTTP"])
        self._type.currentTextChanged.connect(self._on_type_changed)
        form.addRow("Type:", self._type)

        self._port = QSpinBox()
        self._port.setRange(1, 65535)
        self._port.setValue(80)
        self._port.setEnabled(False)
        form.addRow("Port:", self._port)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_type_changed(self, t: str):
        self._port.setEnabled(t in ("TCP", "HTTP"))

    def _validate_and_accept(self):
        if self._host.text().strip():
            self.accept()

    def get_entry(self) -> HostEntry:
        _map = {"ICMP": ProbeType.ICMP, "TCP": ProbeType.TCP, "HTTP": ProbeType.HTTP}
        t = self._type.currentText()
        port = self._port.value() if t in ("TCP", "HTTP") else None
        return HostEntry(host=self._host.text().strip(), probe_type=_map[t], port=port)
