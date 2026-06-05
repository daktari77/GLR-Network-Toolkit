import re
import subprocess
import threading
from typing import Callable

from src.models import TraceHop


class TracerouteEngine:
    def __init__(
        self,
        on_hop: Callable[[TraceHop], None] | None = None,
        on_done: Callable[[], None] | None = None,
        max_hops: int = 30,
        timeout_ms: int = 1000,
    ):
        self.on_hop = on_hop
        self.on_done = on_done
        self.max_hops = max_hops
        self.timeout_ms = timeout_ms
        self._stop_event = threading.Event()
        self._proc: subprocess.Popen | None = None

    def stop(self):
        self._stop_event.set()
        if self._proc:
            try:
                self._proc.kill()
            except Exception:
                pass

    def run(self, host: str):
        self._stop_event.clear()
        threading.Thread(target=self._trace, args=(host,), daemon=True).start()

    def _trace(self, host: str):
        try:
            self._proc = subprocess.Popen(
                ["tracert", "-h", str(self.max_hops), "-w", str(self.timeout_ms), host],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            for line in self._proc.stdout:
                if self._stop_event.is_set():
                    break
                hop = _parse_tracert_line(line)
                if hop and self.on_hop:
                    self.on_hop(hop)
            self._proc.wait()
        except Exception:
            pass
        finally:
            if self.on_done:
                self.on_done()


def _parse_tracert_line(line: str) -> TraceHop | None:
    line = line.strip()
    m = re.match(r"^\s*(\d+)\s+", line)
    if not m:
        return None
    hop = int(m.group(1))

    if "Request timed out" in line or re.search(r"\*\s+\*\s+\*", line):
        return TraceHop(hop=hop, ip="*", hostname="Request timed out", rtt_ms=None)

    rtts = re.findall(r"[<]?(\d+)\s*ms", line)
    rtt = float(rtts[0]) if rtts else None

    ip_bracket = re.search(r"\[(\d{1,3}(?:\.\d{1,3}){3})\]", line)
    ip_bare = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})\s*$", line)

    if ip_bracket:
        ip = ip_bracket.group(1)
        hn_match = re.search(r"ms\s+(.+?)\s+\[", line)
        hostname = hn_match.group(1).strip() if hn_match else ""
    elif ip_bare:
        ip = ip_bare.group(1)
        hostname = ""
    else:
        return None

    return TraceHop(hop=hop, ip=ip, hostname=hostname, rtt_ms=rtt)
