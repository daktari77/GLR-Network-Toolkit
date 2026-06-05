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


@dataclass
class ScanResult:
    ip: str
    hostname: str = ""
    mac: str = ""
    vendor: str = ""
    latency_ms: float | None = None
    is_alive: bool = False


@dataclass
class PortScanResult:
    ip: str
    port: int
    state: str = "closed"
    service: str = ""
    banner: str = ""


@dataclass
class TraceHop:
    hop: int
    ip: str
    hostname: str = ""
    rtt_ms: float | None = None


@dataclass
class DnsResult:
    query: str
    a_records: list = field(default_factory=list)
    ptr_record: str = ""
    mx_records: list = field(default_factory=list)
    cname_record: str = ""
    error: str = ""


@dataclass
class SslResult:
    host: str
    subject: str = ""
    issuer: str = ""
    expiry: str = ""
    days_remaining: int = 0
    cipher: str = ""
    valid: bool = False
    error: str = ""


@dataclass
class HttpInspectResult:
    url: str
    status_code: int = 0
    response_time_ms: float = 0.0
    headers: dict = field(default_factory=dict)
    error: str = ""


@dataclass
class WhoisResult:
    query: str
    registrar: str = ""
    created: str = ""
    expires: str = ""
    name_servers: list = field(default_factory=list)
    raw: str = ""
    error: str = ""


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
