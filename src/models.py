import math
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ProbeType(Enum):
    ICMP = "icmp"
    TCP = "tcp"
    HTTP = "http"


class HostStatus(Enum):
    UNKNOWN = "unknown"
    UP = "up"
    DOWN = "down"


@dataclass
class HostEntry:
    host: str
    probe_type: ProbeType = ProbeType.ICMP
    port: int | None = None
    label: str = ""


@dataclass
class ProbeResult:
    host: str
    probe_type: ProbeType
    status: HostStatus
    latency_ms: float | None = None
    error: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class HostStats:
    def __init__(self):
        self.sent = 0
        self.received = 0
        self._min_ms: float = math.inf
        self._max_ms: float = 0.0
        self._total_ms: float = 0.0

    def update(self, result: ProbeResult):
        self.sent += 1
        if result.status == HostStatus.UP and result.latency_ms is not None:
            self.received += 1
            self._total_ms += result.latency_ms
            self._min_ms = min(self._min_ms, result.latency_ms)
            self._max_ms = max(self._max_ms, result.latency_ms)

    @property
    def loss_pct(self) -> float:
        return round(100 * (self.sent - self.received) / self.sent, 1) if self.sent else 0.0

    @property
    def avg_ms(self) -> float | None:
        return round(self._total_ms / self.received, 1) if self.received else None

    @property
    def min_ms(self) -> float | None:
        return round(self._min_ms, 1) if self.received else None

    @property
    def max_ms(self) -> float | None:
        return round(self._max_ms, 1) if self.received else None
