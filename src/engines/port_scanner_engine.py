import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from src.models import PortScanResult

COMMON_PORTS: list[int] = sorted({
    20, 21, 22, 23, 25, 53, 69, 79, 80, 88, 110, 111, 119, 123,
    135, 137, 138, 139, 143, 161, 162, 179, 194, 389, 443, 445,
    465, 514, 515, 548, 554, 587, 631, 636, 873, 993, 995,
    1080, 1194, 1433, 1521, 1723, 1883, 1900, 2049, 2181, 2375,
    2376, 2379, 2380, 3000, 3128, 3306, 3389, 4000, 4369, 4443,
    4848, 5000, 5001, 5432, 5601, 5671, 5672, 5900, 5985, 5986,
    6000, 6379, 6443, 7000, 7001, 7199, 7474, 8000, 8008, 8080,
    8161, 8300, 8301, 8302, 8443, 8500, 8600, 8888, 8880, 8983,
    9000, 9042, 9090, 9092, 9160, 9200, 9300, 9418, 9999,
    10250, 10255, 11211, 15672, 27017, 27018, 28017, 50000, 61616,
})


def _get_service(port: int) -> str:
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return ""


def _grab_banner(host: str, port: int, timeout: float = 1.0) -> str:
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(timeout)
            try:
                s.sendall(b"\r\n")
            except Exception:
                pass
            data = s.recv(1024)
            return data.decode("utf-8", errors="replace").strip()[:200]
    except Exception:
        return ""


def _parse_port_spec(spec: str) -> list[int]:
    ports: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, _, b = part.partition("-")
            try:
                lo, hi = int(a.strip()), int(b.strip())
                ports.update(range(max(1, lo), min(65535, hi) + 1))
            except ValueError:
                pass
        else:
            try:
                p = int(part)
                if 1 <= p <= 65535:
                    ports.add(p)
            except ValueError:
                pass
    return sorted(ports)


def ports_for_mode(mode: str, custom_spec: str = "") -> list[int]:
    if mode == "common":
        return list(COMMON_PORTS)
    if mode == "full":
        return list(range(1, 65536))
    if mode == "custom":
        return _parse_port_spec(custom_spec)
    return list(COMMON_PORTS)


class PortScannerEngine:
    MAX_WORKERS = 200
    BATCH_SIZE = 500

    def __init__(self):
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)

    def scan(
        self,
        host: str,
        mode: str,
        port_spec: str = "",
        on_result: Callable[[PortScanResult], None] | None = None,
        on_progress: Callable[[int, int], None] | None = None,
        on_done: Callable[[float], None] | None = None,
        timeout_ms: int = 500,
    ):
        self.stop()
        self._stop_event.clear()
        ports = ports_for_mode(mode, port_spec)
        self._thread = threading.Thread(
            target=self._run,
            args=(host, ports, on_result, on_progress, on_done, timeout_ms),
            daemon=True,
        )
        self._thread.start()

    def _run(self, host, ports, on_result, on_progress, on_done, timeout_ms):
        total = len(ports)
        scanned = 0
        timeout_s = timeout_ms / 1000.0
        start = time.monotonic()

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as pool:
            for batch_start in range(0, total, self.BATCH_SIZE):
                if self._stop_event.is_set():
                    break
                batch = ports[batch_start:batch_start + self.BATCH_SIZE]
                futures = {
                    pool.submit(self._probe, host, p, timeout_s): p
                    for p in batch
                }
                for fut in as_completed(futures):
                    if self._stop_event.is_set():
                        break
                    try:
                        result = fut.result()
                    except Exception:
                        p = futures[fut]
                        result = PortScanResult(ip=host, port=p, state="filtered")
                    if on_result:
                        on_result(result)
                    scanned += 1
                    if on_progress:
                        on_progress(scanned, total)

        if on_done:
            on_done(time.monotonic() - start)

    @staticmethod
    def _probe(host: str, port: int, timeout_s: float) -> PortScanResult:
        service = _get_service(port)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout_s)
            code = s.connect_ex((host, port))
            s.close()
        except socket.timeout:
            return PortScanResult(ip=host, port=port, state="filtered", service=service)
        except OSError:
            return PortScanResult(ip=host, port=port, state="filtered", service=service)

        if code == 0:
            banner = _grab_banner(host, port)
            return PortScanResult(ip=host, port=port, state="open", service=service, banner=banner)
        if code in (111, 10061, 61):
            return PortScanResult(ip=host, port=port, state="closed", service=service)
        return PortScanResult(ip=host, port=port, state="filtered", service=service)
