import ipaddress
import re
import socket
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from src.models import ScanResult

_COMMON_VENDORS = {
    "00:50:56": "VMware",
    "00:0c:29": "VMware",
    "00:1a:a0": "Dell",
    "00:14:22": "Dell",
    "3c:97:0e": "Apple",
    "a4:83:e7": "Apple",
    "00:1b:21": "Intel",
    "8c:8d:28": "Intel",
    "00:e0:4c": "Realtek",
    "dc:a6:32": "Raspberry Pi",
    "b8:27:eb": "Raspberry Pi",
}


def _mac_vendor(mac: str) -> str:
    return _COMMON_VENDORS.get(mac[:8].lower(), "")


def _ping_host(ip: str, timeout_ms: int = 1000) -> tuple[bool, float | None]:
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", str(timeout_ms), ip],
            capture_output=True, text=True,
            timeout=timeout_ms / 1000 + 3,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode == 0:
            # Genuine echo reply always contains "TTL=" in the per-packet line.
            # ICMP "Host Unreachable" (returncode 0 on Windows) never does.
            if "TTL=" not in result.stdout.upper():
                return False, None
            all_ms = re.findall(r"[=<]\s*(\d+)\s*ms", result.stdout, re.IGNORECASE)
            latency = float(all_ms[-1]) if all_ms else None
            return True, latency
        return False, None
    except Exception:
        return False, None


def _resolve_hostname(ip: str, timeout: float = 2.0) -> str:
    """Reverse DNS with a hard timeout to avoid blocking worker threads."""
    result: list[str] = []

    def _lookup():
        try:
            result.append(socket.gethostbyaddr(ip)[0])
        except Exception:
            pass

    t = threading.Thread(target=_lookup, daemon=True)
    t.start()
    t.join(timeout)
    return result[0] if result else ""


def _arp_lookup(ip: str) -> tuple[str, str]:
    try:
        from scapy.layers.l2 import ARP, Ether
        from scapy.sendrecv import srp
        import scapy.config
        scapy.config.conf.verb = 0
        pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
        ans, _ = srp(pkt, timeout=1, retry=0)
        if ans:
            mac = ans[0][1].hwsrc
            return mac, _mac_vendor(mac)
    except Exception:
        pass
    return "", ""


def _expand_target(target: str) -> list[str]:
    target = target.strip()
    try:
        net = ipaddress.ip_network(target, strict=False)
        return [str(ip) for ip in net.hosts()]
    except ValueError:
        pass
    if "-" in target:
        parts = target.split("-", 1)
        base = parts[0].strip()
        end = parts[1].strip()
        try:
            start_ip = ipaddress.ip_address(base)
            if "." not in end:
                prefix = ".".join(base.split(".")[:-1])
                end_ip = ipaddress.ip_address(f"{prefix}.{end}")
            else:
                end_ip = ipaddress.ip_address(end)
            ips = []
            current = start_ip
            while current <= end_ip:
                ips.append(str(current))
                current += 1
            return ips
        except ValueError:
            pass
    if "," in target:
        return [ip.strip() for ip in target.split(",") if ip.strip()]
    return [target]


class ScannerEngine:
    def __init__(
        self,
        on_result: Callable[[ScanResult], None] | None = None,
        on_done: Callable[[], None] | None = None,
        use_arp: bool = False,
        timeout_ms: int = 1000,
    ):
        self.on_result = on_result
        self.on_done = on_done
        self.use_arp = use_arp
        self.timeout_ms = timeout_ms
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self, target: str):
        self._stop_event.clear()
        threading.Thread(target=self._scan, args=(target,), daemon=True).start()

    def _scan(self, target: str):
        ips = _expand_target(target)
        max_workers = min(len(ips), 64)
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(self._probe_ip, ip): ip for ip in ips}
            for future in as_completed(futures):
                if self._stop_event.is_set():
                    break
                result = future.result()
                if self.on_result:
                    self.on_result(result)
        if self.on_done:
            self.on_done()

    def _probe_ip(self, ip: str) -> ScanResult:
        is_alive, latency = _ping_host(ip, self.timeout_ms)
        hostname = mac = vendor = ""
        if is_alive:
            hostname = _resolve_hostname(ip)
            if self.use_arp:
                mac, vendor = _arp_lookup(ip)
        return ScanResult(
            ip=ip, hostname=hostname, mac=mac, vendor=vendor,
            latency_ms=latency, is_alive=is_alive,
        )
