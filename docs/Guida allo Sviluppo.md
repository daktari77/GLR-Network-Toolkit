# Guida allo Sviluppo

---

## Setup ambiente

```bash
git clone <repo>
cd GLR-ParallelPingInfo
pip install -r requirements.txt
python main.py
```

### Test

```bash
pytest
pytest tests/test_monitor.py::test_cycle -v
```

---

## Aggiungere un nuovo probe type

1. **`src/models.py`** — aggiungere valore a `ProbeType`:
   ```python
   class ProbeType(Enum):
       ICMP = "icmp"
       TCP  = "tcp"
       HTTP = "http"
       UDP  = "udp"   # ← nuovo
   ```

2. **`src/probers/udp.py`** — creare classe che estende `AbstractProber`:
   ```python
   from src.probers.base import AbstractProber
   from src.models import HostEntry, ProbeResult, HostStatus
   
   class UdpProber(AbstractProber):
       def probe(self, entry: HostEntry) -> ProbeResult:
           ...
   ```

3. **`src/monitor.py`** — aggiungere dispatch in `Monitor._probe()`:
   ```python
   if entry.probe_type == ProbeType.UDP:
       return self._udp.probe(entry)
   ```

4. **`src/gui/panels/monitor_panel.py`** — aggiungere l'opzione nel parser hosts e in `AddHostDialog`.

---

## Aggiungere un nuovo engine di troubleshoot

1. **`src/models.py`** — aggiungere dataclass risultato:
   ```python
   @dataclass
   class MyToolResult:
       query: str
       result: str = ""
       error: str = ""
   ```

2. **`src/engines/my_tool_engine.py`** — creare engine (zero Qt):
   ```python
   from src.models import MyToolResult
   
   def run(query: str) -> MyToolResult:
       ...
   ```

3. **`src/gui/panels/troubleshoot_panel.py`** — aggiungere sub-view e tab:
   ```python
   class MyToolView(QWidget):
       def set_target(self, host: str): ...
       def _run(self, query: str): ...
   
   # In TroubleshootPanel.__init__:
   self._mytool = MyToolView()
   self._tabs.addTab(self._mytool, "My Tool")
   ```

---

## Aggiungere una voce al menu contestuale

Il menu contestuale è implementato direttamente nelle tabelle (`ScanResultTable`, `PortResultTable`, `HostTable`).

Esempio — aggiungere "Ping rapido" in `ScanResultTable`:

```python
# src/gui/widgets/scan_result_table.py
ping_action = pyqtSignal(str)   # ← aggiungere signal alla classe

# In _show_context_menu:
menu.addAction("Ping rapido").triggered.connect(
    lambda: self.ping_action.emit(ip))
```

Poi in `scanner_panel.py` connettere il signal al comportamento desiderato.

---

## Pattern queue + QTimer

Tutti gli engine usano lo stesso pattern per la comunicazione thread-safe con la GUI:

```python
class MyPanel(QWidget):
    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._timer = QTimer()
        self._timer.timeout.connect(self._flush)
        self._timer.start(200)  # ms

    def _start(self):
        engine = MyEngine(on_result=self._queue.put)
        engine.run(...)

    def _flush(self):
        while not self._queue.empty():
            item = self._queue.get_nowait()
            if item is None:          # sentinel → done
                self._on_done()
                continue
            self._table.add_result(item)
```

> [!important]
> **Non aggiornare mai la GUI direttamente da un thread background.** Usa sempre queue + QTimer o `QTimer.singleShot(0, callback)`.

---

## Struttura engine

Gli engine devono essere **puri Python, zero Qt**:

```python
# Struttura tipo per engine asincrono
class MyEngine:
    def __init__(self, on_result=None, on_done=None):
        self.on_result = on_result
        self.on_done = on_done
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self, target: str):
        self._stop_event.clear()
        threading.Thread(target=self._work, args=(target,), daemon=True).start()

    def _work(self, target: str):
        # ... logica ...
        if self.on_result:
            self.on_result(result)
        if self.on_done:
            self.on_done()
```

Questo garantisce che gli engine siano **testabili indipendentemente** senza avviare Qt.

---

## Comandi utili

```bash
# Avvia l'app
python main.py

# Esegui tutti i test
pytest

# Esegui test specifico con output dettagliato
pytest tests/test_monitor.py::test_cycle -v

# Check import chain (verifica che non ci siano errori di import)
python -c "from src.gui.main_window import MainWindow; print('OK')"
```

---

## Architettura di riferimento

Vedi [[Architettura]] per:
- Struttura directory completa
- Diagramma threading
- Modelli dati
- Comunicazione cross-tab
