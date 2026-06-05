from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QComboBox,
    QDialogButtonBox, QGroupBox, QVBoxLayout,
)
from src.alerting import AlertConfig


class SettingsDialog(QDialog):
    def __init__(self, config: AlertConfig, current_theme: str = "dark", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(420)
        self.config = config
        self._initial_theme = current_theme
        self._build_ui(current_theme)

    def _build_ui(self, current_theme: str):
        layout = QVBoxLayout(self)

        appear_box = QGroupBox("Appearance")
        appear_form = QFormLayout(appear_box)
        self._theme_cb = QComboBox()
        self._theme_cb.addItems(["Dark", "Light"])
        self._theme_cb.setCurrentText(current_theme.capitalize())
        appear_form.addRow("Theme:", self._theme_cb)
        layout.addWidget(appear_box)

        alert_box = QGroupBox("Alerts")
        alert_form = QFormLayout(alert_box)
        self._log_file = QLineEdit(self.config.log_file or "")
        self._webhook = QLineEdit(self.config.webhook_url)
        alert_form.addRow("Log file:", self._log_file)
        alert_form.addRow("Webhook URL:", self._webhook)
        layout.addWidget(alert_box)

        smtp_box = QGroupBox("Email (SMTP)")
        smtp_form = QFormLayout(smtp_box)
        self._smtp_host = QLineEdit(self.config.smtp_host)
        self._smtp_port = QSpinBox()
        self._smtp_port.setRange(1, 65535)
        self._smtp_port.setValue(self.config.smtp_port)
        self._smtp_user = QLineEdit(self.config.smtp_user)
        self._smtp_pass = QLineEdit(self.config.smtp_password)
        self._smtp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self._smtp_from = QLineEdit(self.config.smtp_from)
        self._smtp_to = QLineEdit(", ".join(self.config.smtp_to))
        smtp_form.addRow("Host:", self._smtp_host)
        smtp_form.addRow("Port:", self._smtp_port)
        smtp_form.addRow("User:", self._smtp_user)
        smtp_form.addRow("Password:", self._smtp_pass)
        smtp_form.addRow("From:", self._smtp_from)
        smtp_form.addRow("To (comma-sep.):", self._smtp_to)
        layout.addWidget(smtp_box)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save_and_accept(self):
        self.config.log_file = self._log_file.text() or None
        self.config.webhook_url = self._webhook.text()
        self.config.smtp_host = self._smtp_host.text()
        self.config.smtp_port = self._smtp_port.value()
        self.config.smtp_user = self._smtp_user.text()
        self.config.smtp_password = self._smtp_pass.text()
        self.config.smtp_from = self._smtp_from.text()
        self.config.smtp_to = [s.strip() for s in self._smtp_to.text().split(",") if s.strip()]
        self.accept()

    @property
    def chosen_theme(self) -> str:
        return self._theme_cb.currentText().lower()

    @property
    def theme_changed(self) -> bool:
        return self.chosen_theme != self._initial_theme
