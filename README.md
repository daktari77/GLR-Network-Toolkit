# GLR NetScope

Desktop network monitor for Windows. Parallel ICMP/TCP/HTTP probes, live status table, latency charts, subnet scanner, port scanner, and troubleshooting tools — all in one PyQt6 app.

---

## Install

**Python 3.10+ required.**

```bash
pip install -r requirements.txt
python main.py
```

Some features (ARP scan, MAC lookup) require elevated privileges. The app shows a banner with a **Restart as Administrator** button when running without them — everything else works unprivileged.

---

## Features

### Monitor tab
- Probe hosts continuously via **ICMP ping**, **TCP port check**, or **HTTP/HTTPS** — all in parallel
- Live color-coded status table: per-host latency (last/avg/min/max), packet loss, sent count
- Per-host probe history and latency chart (last 500 samples)
- Load hosts from a text file or add them one at a time
- Alerts on UP↔DOWN transitions: log file, HTTP webhook, or SMTP email
- Export results to CSV
- Light / Dark theme toggle (Settings…)

### Network Scanner tab
- Discover live hosts in a subnet or IP range
- ICMP ping sweep + optional ARP scan (admin required for MAC/vendor lookup)
- Right-click any result to send host to Monitor, Port Scanner, Traceroute, or DNS

### Port Scanner tab
- TCP port scan: Common ports / Full range (1–65535) / Custom list
- Right-click any open port to add it to Monitor as a TCP probe

### Troubleshoot tab
- **Traceroute** — hop-by-hop path with RTT
- **DNS** — forward (A/CNAME/MX) and reverse (PTR) lookups
- **HTTP Inspector** — response code, headers, response time
- **SSL/TLS** — certificate subject, issuer, expiry, cipher
- **Whois** — registrar, creation/expiry dates, name servers

---

## Hosts file format

```
# comment lines are ignored
192.168.1.1              # ICMP ping (default)
google.com               # ICMP ping
github.com TCP 443       # TCP port check
google.com HTTPS         # HTTPS probe (https://)
myhost HTTP 8080         # HTTP probe on custom port
192.168.1.0/24           # CIDR — ICMP on all subnet hosts
10.0.0.1-20              # range notation — hosts .1 through .20
192.168.1.0/24 TCP 22    # CIDR × TCP
```

Load a hosts file from the toolbar or drop it in `config/hosts.txt` — the last-used file reloads automatically on startup.

---

## Alerts

Configure via **Monitor → Settings…**

| Channel | What it does |
|---------|-------------|
| Log file | Appends one line per state change: `timestamp \| host \| STATUS \| detail` |
| Webhook | HTTP POST with JSON body `{host, status, latency_ms, error, timestamp}` |
| SMTP email | Sends on each UP↔DOWN transition; supports STARTTLS (port 587) |

Settings are saved to `config/settings.json` on close.

---

## Optional packages

```bash
pip install scapy dnspython python-whois
```

| Package | Unlocks |
|---------|---------|
| `scapy` | ARP scan + MAC/vendor lookup in Network Scanner (admin required) |
| `dnspython` | MX and CNAME records in Troubleshoot DNS |
| `python-whois` | Structured Whois parsing |

---

## Development

```bash
# Run tests
pytest

# Run a single test
pytest tests/test_monitor.py::test_cycle -v

# Verify import chain
python -c "from src.gui.main_window import MainWindow; print('OK')"
```

**Threading rule:** all background engines post results to `queue.Queue`; a `QTimer` on the main thread drains it every 200–400 ms. Never call Qt APIs from a background thread.

**Adding a probe type:** see `CLAUDE.md` → *Adding a new probe type* (4 steps).

**Build a standalone executable:**
```bash
pip install pyinstaller
pyinstaller GLR-NetScope.spec
```

Output lands in `dist/GLR-NetScope/`.

---

## Requirements

- Windows 10/11
- Python 3.10+
- `PyQt6 >= 6.5`
- `requests >= 2.31`
