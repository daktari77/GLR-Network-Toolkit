import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


_FILE = _base_dir() / "config" / "settings.json"


@dataclass
class AppSettings:
    last_hosts_file: str = ""
    interval: int = 5
    alert_log_file: str = "alerts.log"
    alert_webhook_url: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_to: list[str] = field(default_factory=list)
    theme: str = "dark"


def load() -> AppSettings:
    if _FILE.exists():
        try:
            data = json.loads(_FILE.read_text(encoding="utf-8"))
            valid = {k: v for k, v in data.items() if k in AppSettings.__dataclass_fields__}
            return AppSettings(**valid)
        except Exception:
            pass
    return AppSettings()


def save(settings: AppSettings):
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
