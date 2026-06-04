import socket
import time
from src.models import HostEntry, ProbeResult, HostStatus, ProbeType
from .base import AbstractProber


class TcpProber(AbstractProber):
    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout

    def probe(self, entry: HostEntry) -> ProbeResult:
        port = entry.port or 80
        try:
            start = time.monotonic()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            code = sock.connect_ex((entry.host, port))
            latency_ms = (time.monotonic() - start) * 1000
            sock.close()

            if code == 0:
                return ProbeResult(host=entry.host, probe_type=ProbeType.TCP,
                                   status=HostStatus.UP, latency_ms=round(latency_ms, 1))
            return ProbeResult(host=entry.host, probe_type=ProbeType.TCP,
                               status=HostStatus.DOWN, error=f"port {port} refused")

        except socket.timeout:
            return ProbeResult(host=entry.host, probe_type=ProbeType.TCP,
                               status=HostStatus.DOWN, error="timeout")
        except Exception as exc:
            return ProbeResult(host=entry.host, probe_type=ProbeType.TCP,
                               status=HostStatus.DOWN, error=str(exc))
