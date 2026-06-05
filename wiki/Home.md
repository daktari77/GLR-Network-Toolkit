# GLR Network Toolkit

**Desktop network monitor and diagnostic suite for Windows.**
Parallel ICMP / TCP / HTTP probing, subnet discovery, port scanning, and 5 troubleshooting tools — all in one PyQt6 app.

---

## What's inside

| Tab | What it does |
|-----|-------------|
| **Monitor** | Continuous polling of any host list — live latency table, per-host history, charts, UP↔DOWN alerts |
| **Network Scanner** | Subnet / range host discovery — ICMP sweep + ARP (admin) for MAC and vendor lookup |
| **Port Scanner** | TCP port scan — Common / Full (1–65535) / Custom modes; right-click to add open ports to Monitor |
| **Troubleshoot** | Traceroute · DNS (A / PTR / MX / CNAME) · HTTP Inspector · SSL/TLS certificate · Whois |

---

## Quick start

**Requirements:** Windows 10/11 · Python 3.10+

```bash
git clone https://github.com/<YOUR_USERNAME>/GLR-ParallelPingInfo
cd GLR-ParallelPingInfo
pip install -r requirements.txt
python main.py
```

Some features require elevation. When running without admin rights the app shows a yellow banner — click **Restart as Administrator** to unlock ARP scanning and MAC/vendor lookup.

---

## Optional packages

```bash
pip install scapy dnspython python-whois
```

| Package | Feature unlocked |
|---------|----------------|
| `scapy` | ARP scan + MAC / vendor in Network Scanner *(admin required)* |
| `dnspython` | MX and CNAME records in Troubleshoot › DNS |
| `python-whois` | Structured Whois output (registrar, dates, name servers) |

---

## Cross-tab workflow

Right-clicking any row in Monitor, Network Scanner, or Port Scanner opens a **Send to →** menu that switches the target tab and pre-fills the input:

```
ScannerPanel     → Monitor          (add host as ICMP probe)
ScannerPanel     → Port Scanner     (scan the selected IP)
ScannerPanel     → Traceroute / DNS
MonitorPanel     → Port Scanner
MonitorPanel     → Traceroute / DNS
PortScannerPanel → Monitor          (add open port as TCP probe)
```

---

## Wiki pages

| Page | Contents |
|------|---------|
| [Installation](Installation) | Full install guide, optional packages, PyInstaller build |
| [Configuration](Configuration) | Hosts file format, `settings.json` reference, alert channels, privilege matrix |
| [Architecture](Architecture) | Threading model, data flow, file structure, signal wiring |
| [Development](Development) | Dev setup, adding probe types, engines, context menus, build pipeline |

---

## Alerts (Monitor tab)

Three independent alert channels, all triggered on UP↔DOWN transitions only (not on every probe):

| Channel | How to configure |
|---------|----------------|
| Log file | Monitor → Settings… → Log file path |
| HTTP webhook | Monitor → Settings… → Webhook URL |
| SMTP email | Monitor → Settings… → SMTP section |

---

## Portable / standalone build

```bash
pip install pyinstaller
pyinstaller GLR-Network-Toolkit.spec
# output: dist/GLR-Network-Toolkit/GLR-Network-Toolkit.exe
```

The bundled build includes `config/` and `docs/`. Optional packages (`scapy`, `dnspython`, `python-whois`) are excluded from the bundle — install separately if needed.
