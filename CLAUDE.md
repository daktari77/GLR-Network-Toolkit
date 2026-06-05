# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

**GLR NetScope** is a Python/PyQt6 desktop tool inspired by NirSoft PingInfoView. It monitors multiple network hosts in parallel via ICMP ping, TCP port checks, and HTTP/HTTPS health checks. It displays live results with per-host statistics in a color-coded table and fires alerts (log file, email, webhook) on status changes.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Run tests
pytest

# Run a single test
pytest tests/test_monitor.py::test_cycle -v
```

## Architecture

```
main.py                        # QApplication entry point
src/
  models.py                    # HostEntry, ProbeResult, ProbeType, HostStatus, HostStats
  monitor.py                   # Monitor: background thread + ThreadPoolExecutor → on_result callback
  alerting.py                  # Alerter + AlertConfig: fires on UP↔DOWN transitions (log/email/webhook)
  app_settings.py              # AppSettings dataclass, load()/save() → config/settings.json
  probers/
    base.py                    # AbstractProber (ABC)
    icmp.py                    # IcmpProber: subprocess ping, parses Average latency
    tcp.py                     # TcpProber: socket.connect_ex() with timeout
    http.py                    # HttpProber: requests.get(), measures response time
  gui/
    main_window.py             # MainWindow: toolbar, wires Monitor→queue, QTimer flush loop
    host_table.py              # HostTable (QTableWidget): 12 columns incl. stats
    settings_dlg.py            # SettingsDialog: AlertConfig editor (log/smtp/webhook)
    add_host_dlg.py            # AddHostDialog: inline host add (ICMP/TCP/HTTP + port)
config/
  hosts.txt                    # Host list (see format below)
  settings.json                # Auto-saved app state (created at first close)
```

### Threading model

`Monitor` runs in a daemon thread. Each probe cycle uses `ThreadPoolExecutor` (max 64 workers). Results are posted to a `queue.Queue`; the GUI drains it every 400 ms via `QTimer` on the main thread — no direct cross-thread Qt calls.

### Stats tracking

`HostStats` (in `models.py`) is a plain class (not dataclass) that tracks `sent`, `received`, and running min/max/total for latency. One instance per host, held in `MainWindow._stats`. Updated in `_flush_queue` before passing to `HostTable.update_result`.

### Settings persistence

`AppSettings` is saved to `config/settings.json` on window close and loaded on startup. It stores: last hosts file path, interval, and all alert config fields. On startup, the last hosts file is reloaded automatically if it still exists.

### Host list format (`config/hosts.txt`)

```
# comment
192.168.1.1           # ICMP ping
google.com            # ICMP ping
github.com TCP 443    # TCP port check
google.com HTTPS      # HTTPS check (http probe with https:// prefix)
myhost HTTP 8080      # HTTP check on custom port
```

### Adding a new probe type

1. Add a value to `ProbeType` in `models.py`
2. Create `src/probers/<type>.py` subclassing `AbstractProber`
3. Add the dispatch branch in `Monitor._probe()`
4. Add the type to `AddHostDialog` combo and `_parse_hosts_file()` in `main_window.py`
