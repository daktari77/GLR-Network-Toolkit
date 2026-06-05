# Development

## Setup

```bash
git clone https://github.com/daktari77/-GLR-NetScope
cd GLR-Network-Toolkit
pip install -r requirements.txt
python main.py
```

Optional packages for full feature coverage:

```bash
pip install scapy dnspython python-whois
```

---

## Run tests

```bash
pytest
pytest tests/test_monitor.py::test_cycle -v

# Verify the import chain cleanly
python -c "from src.gui.main_window import MainWindow; print('OK')"
```

---

## Standard patterns

### Queue + QTimer (thread-safe GUI updates)

Every background engine follows this pattern. **Never call Qt APIs from a background thread.**

```python
class MyPanel(QWidget):
    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._timer = QTimer()
        self._timer.timeout.connect(self._flush)
        self._timer.start(200)  # ms — adjust per panel

    def _start(self, target: str):
        engine = MyEngine(on_result=self._queue.put, on_done=lambda: self._queue.put(None))
        engine.run(target)

    def _flush(self):
        while not self._queue.empty():
            item = self._queue.get_nowait()
            if item is None:           # sentinel → engine finished
                self._on_done()
                return
            self._table.add_result(item)
```

### Standard engine structure

```python
class MyEngine:
    def __init__(self, on_result=None, on_done=None):
        self.on_result = on_result
        self.on_done = on_done
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self, target: str):
        self._stop.clear()
        threading.Thread(target=self._work, args=(target,), daemon=True).start()

    def _work(self, target: str):
        # pure Python, no Qt
        result = MyResult(...)
        if self.on_result:
            self.on_result(result)
        if self.on_done:
            self.on_done()
```

Engines in `src/engines/` have zero Qt imports — they're testable standalone.

---

## Adding a probe type

Four steps to add, e.g., a UDP probe:

**1. Add the enum value** in `src/models.py`:

```python
class ProbeType(Enum):
    ICMP = "icmp"
    TCP  = "tcp"
    HTTP = "http"
    UDP  = "udp"   # ← new
```

**2. Create the prober** at `src/probers/udp.py`:

```python
from src.probers.base import AbstractProber
from src.models import HostEntry, ProbeResult, HostStatus
import time

class UdpProber(AbstractProber):
    def probe(self, entry: HostEntry) -> ProbeResult:
        start = time.perf_counter()
        # ... UDP logic ...
        latency = (time.perf_counter() - start) * 1000
        return ProbeResult(host=entry.host, status=HostStatus.UP, latency_ms=latency)
```

**3. Add the dispatch branch** in `Monitor._probe()` in `src/monitor.py`:

```python
if entry.probe_type == ProbeType.UDP:
    return self._udp_prober.probe(entry)
```

**4. Expose it** in `AddHostDialog` (combo box) and in `_parse_hosts_file()` in `src/gui/panels/monitor_panel.py` (token parser).

---

## Adding a troubleshoot engine

Three steps:

**1. Add a result dataclass** in `src/models.py`:

```python
@dataclass
class MyToolResult:
    query: str
    result: str = ""
    error: str = ""
```

**2. Create the engine** at `src/engines/my_tool_engine.py` (no Qt):

```python
from src.models import MyToolResult

def run(query: str) -> MyToolResult:
    try:
        # ... logic ...
        return MyToolResult(query=query, result="...")
    except Exception as e:
        return MyToolResult(query=query, error=str(e))
```

**3. Add a sub-view and tab** in `src/gui/panels/troubleshoot_panel.py`:

```python
class MyToolView(QWidget):
    def set_target(self, host: str):
        self._input.setText(host)

    def _run(self):
        result = my_tool_engine.run(self._input.text())
        self._display(result)

# In TroubleshootPanel.__init__:
self._mytool = MyToolView()
self._tabs.addTab(self._mytool, "My Tool")
```

---

## Adding a context menu item

Example: "Resolve DNS" action in `ScanResultTable`.

```python
# In src/gui/widgets/scan_result_table.py — add signal to the class
resolve_dns = pyqtSignal(str)

# In _show_context_menu:
act = menu.addAction("Resolve DNS")
act.triggered.connect(lambda: self.resolve_dns.emit(selected_ip))
```

Wire it in `ScannerPanel`:

```python
self._table.resolve_dns.connect(self._send_to_dns)
```

---

## Adding a theme token

1. Add the field to the `Theme` dataclass in `src/gui/theme.py`
2. Set values in both `DARK` and `LIGHT` instances
3. Add the QSS rule in `_build_qss(t)` (for standard widgets) **or** read `theme.current().new_field` directly in `paintEvent()` / `refresh_theme()` (for custom widgets)

---

## Build a portable executable

```bash
pip install pyinstaller
pyinstaller GLR-NetScope.spec
```

Output: `dist/GLR-NetScope/GLR-NetScope.exe` (one-folder bundle, no console window).

The spec bundles `config/` and `docs/`. Optional packages are excluded — install them alongside the `.exe` if needed.

To rebuild after changing the spec:

```bash
pyinstaller --clean GLR-NetScope.spec
```

---

## Project conventions

- **No Qt in engines.** `src/engines/` and `src/probers/` have zero Qt imports.
- **No cross-thread Qt calls.** Queue → QTimer, always.
- **No `setSortingEnabled(True)` during live updates.** `HostTable` sorts manually via `_on_header_clicked` to keep `_row_map` stable.
- **Theme reads at paint time.** Custom widgets call `theme.current()` in `paintEvent()` — no caching of color objects between paints.
