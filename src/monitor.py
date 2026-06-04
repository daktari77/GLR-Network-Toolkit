import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable
from src.models import HostEntry, ProbeResult, ProbeType
from src.probers.icmp import IcmpProber
from src.probers.tcp import TcpProber
from src.probers.http import HttpProber


class Monitor:
    def __init__(
        self,
        entries: list[HostEntry],
        interval: int = 5,
        on_result: Callable[[ProbeResult], None] | None = None,
    ):
        self.entries = entries
        self.interval = interval
        self.on_result = on_result
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._icmp = IcmpProber()
        self._tcp = TcpProber()
        self._http = HttpProber()

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _loop(self):
        while not self._stop_event.is_set():
            self._run_cycle()
            self._stop_event.wait(self.interval)

    def _run_cycle(self):
        max_workers = min(len(self.entries), 64)
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(self._probe, entry): entry for entry in self.entries}
            for future in as_completed(futures):
                result = future.result()
                if self.on_result:
                    self.on_result(result)

    def _probe(self, entry: HostEntry) -> ProbeResult:
        if entry.probe_type == ProbeType.TCP:
            return self._tcp.probe(entry)
        if entry.probe_type == ProbeType.HTTP:
            return self._http.probe(entry)
        return self._icmp.probe(entry)
