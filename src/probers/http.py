import time
from urllib.parse import urlparse, urlunparse
import requests
from src.models import HostEntry, ProbeResult, HostStatus, ProbeType
from .base import AbstractProber


class HttpProber(AbstractProber):
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def probe(self, entry: HostEntry) -> ProbeResult:
        url = _build_url(entry)
        try:
            start = time.monotonic()
            resp = requests.get(url, timeout=self.timeout, allow_redirects=True)
            latency_ms = round((time.monotonic() - start) * 1000, 1)

            if resp.ok:
                return ProbeResult(host=entry.host, probe_type=ProbeType.HTTP,
                                   status=HostStatus.UP, latency_ms=latency_ms)
            return ProbeResult(host=entry.host, probe_type=ProbeType.HTTP,
                               status=HostStatus.DOWN, error=f"HTTP {resp.status_code}")

        except requests.Timeout:
            return ProbeResult(host=entry.host, probe_type=ProbeType.HTTP,
                               status=HostStatus.DOWN, error="timeout")
        except Exception as exc:
            return ProbeResult(host=entry.host, probe_type=ProbeType.HTTP,
                               status=HostStatus.DOWN, error=str(exc))


def _build_url(entry: HostEntry) -> str:
    host = entry.host
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    if entry.port:
        parsed = urlparse(host)
        host = urlunparse(parsed._replace(netloc=f"{parsed.hostname}:{entry.port}"))
    return host
