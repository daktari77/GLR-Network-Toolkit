import subprocess
import re
import platform
from src.models import HostEntry, ProbeResult, HostStatus, ProbeType
from .base import AbstractProber


class IcmpProber(AbstractProber):
    def __init__(self, timeout_ms: int = 1000, count: int = 1):
        self.timeout_ms = timeout_ms
        self.count = count

    def probe(self, entry: HostEntry) -> ProbeResult:
        try:
            if platform.system() == "Windows":
                cmd = ["ping", "-n", str(self.count), "-w", str(self.timeout_ms), entry.host]
            else:
                cmd = ["ping", "-c", str(self.count), "-W", str(max(1, self.timeout_ms // 1000)), entry.host]

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_ms / 1000 + 3,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            if proc.returncode == 0:
                # On Windows, ICMP "Host Unreachable" (router replies on behalf
                # of a dead host) also returns exit code 0.  A genuine echo
                # reply ALWAYS includes "TTL=" in the per-packet output line;
                # an unreachable message never does.
                if platform.system() == "Windows" and "TTL=" not in proc.stdout.upper():
                    return ProbeResult(host=entry.host, probe_type=ProbeType.ICMP,
                                       status=HostStatus.DOWN, error="unreachable")
                latency = _parse_latency(proc.stdout)
                return ProbeResult(host=entry.host, probe_type=ProbeType.ICMP,
                                   status=HostStatus.UP, latency_ms=latency)
            return ProbeResult(host=entry.host, probe_type=ProbeType.ICMP,
                               status=HostStatus.DOWN, error="no reply")

        except subprocess.TimeoutExpired:
            return ProbeResult(host=entry.host, probe_type=ProbeType.ICMP,
                               status=HostStatus.DOWN, error="timeout")
        except Exception as exc:
            return ProbeResult(host=entry.host, probe_type=ProbeType.ICMP,
                               status=HostStatus.DOWN, error=str(exc))


def _parse_latency(output: str) -> float | None:
    # Windows — all locales: the last "= Nms" or "< Nms" in the output is
    # always the average/media from the statistics line (EN "Average", IT "Media", etc.).
    # TTL values like "TTL=128" are excluded because they have no "ms" suffix.
    all_ms = re.findall(r"[=<]\s*(\d+)\s*ms", output, re.IGNORECASE)
    if all_ms:
        return float(all_ms[-1])
    # Linux/macOS: "min/avg/max/mdev = 1.2/2.3/3.4/0.5 ms"
    m = re.search(r"min/avg/max.*?=\s*[\d.]+/([\d.]+)/", output)
    if m:
        return float(m.group(1))
    return None
