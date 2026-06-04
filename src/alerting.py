import logging
import smtplib
from dataclasses import dataclass, field
from typing import Optional
from src.models import ProbeResult, HostStatus

logger = logging.getLogger(__name__)


@dataclass
class AlertConfig:
    log_file: Optional[str] = "alerts.log"
    webhook_url: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_to: list[str] = field(default_factory=list)


class Alerter:
    def __init__(self, config: AlertConfig):
        self.config = config
        self._prev: dict[str, HostStatus] = {}
        if config.log_file:
            file_handler = logging.FileHandler(config.log_file, encoding="utf-8")
            file_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
            logger.addHandler(file_handler)
            logger.setLevel(logging.INFO)

    def check(self, result: ProbeResult):
        prev = self._prev.get(result.host)
        self._prev[result.host] = result.status
        if prev is not None and prev != result.status:
            self._fire(result)

    def _fire(self, result: ProbeResult):
        msg = (
            f"[{result.status.value.upper()}] {result.host} "
            f"at {result.timestamp.strftime('%H:%M:%S')}"
        )
        logger.info(msg)
        if self.config.smtp_to and self.config.smtp_host:
            self._send_email(msg)
        if self.config.webhook_url:
            self._send_webhook(result, msg)

    def _send_email(self, msg: str):
        try:
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_password)
                server.sendmail(
                    self.config.smtp_from,
                    self.config.smtp_to,
                    f"Subject: PingInfo Alert\n\n{msg}",
                )
        except Exception as exc:
            logger.error(f"Email alert failed: {exc}")

    def _send_webhook(self, result: ProbeResult, msg: str):
        try:
            import requests
            requests.post(
                self.config.webhook_url,
                json={
                    "host": result.host,
                    "status": result.status.value,
                    "latency_ms": result.latency_ms,
                    "message": msg,
                },
                timeout=5,
            )
        except Exception as exc:
            logger.error(f"Webhook alert failed: {exc}")
