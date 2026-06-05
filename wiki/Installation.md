# Installation

## Requirements

| Requirement | Version |
|-------------|---------|
| OS | Windows 10 / 11 |
| Python | 3.10 or newer |
| PyQt6 | ≥ 6.5 |
| requests | ≥ 2.31 |

---

## From source (recommended for development)

```bash
git clone https://github.com/daktari77/GLR-NetScope
cd GLR-Network-Toolkit
pip install -r requirements.txt
python main.py
```

---

## Optional packages

Install these to unlock additional features:

```bash
pip install scapy dnspython python-whois
```

| Package | What it unlocks | Notes |
|---------|----------------|-------|
| `scapy` | ARP scan + MAC / vendor lookup | Requires admin |
| `dnspython` | MX and CNAME records in DNS tool | — |
| `python-whois` | Structured Whois parsing | — |

These are intentionally **not** in `requirements.txt` — the app runs fully without them (features that need them degrade gracefully).

---

## Portable / standalone build (PyInstaller)

Build a self-contained `.exe` that requires no Python installation:

```bash
pip install pyinstaller
pyinstaller GLR-NetScope.spec
```

Output: `dist/GLR-NetScope/GLR-NetScope.exe`

The folder `dist/GLR-NetScope/` is the portable distribution — copy it anywhere and run the `.exe` directly.

### What the spec bundles

- `config/` — default hosts file and settings
- `docs/` — documentation vault
- All `src/` modules (hidden imports declared in the spec)

### What is NOT bundled

`scapy`, `dnspython`, `python-whois` are excluded from the bundle (they make the binary much larger and require special treatment for network drivers). Install them system-wide if needed alongside the portable build.

### Rebuild after changes

```bash
pyinstaller --clean GLR-NetScope.spec
```

---

## Elevated privileges

Some features require running as Administrator:

- **ARP scan** (MAC / vendor lookup in Network Scanner)
- **Raw ICMP socket** (falls back to subprocess ping when unprivileged — still works)

The app detects privilege level at startup. When running without admin rights, a yellow banner appears at the top with a **Restart as Administrator** button. Click it to re-launch elevated via `ShellExecuteW("runas")`.

Everything except ARP scanning and MAC lookup works without elevation.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'PyQt6'`**
```bash
pip install PyQt6
```

**App launches but Network Scanner shows no MAC/vendor column data**
Launch as Administrator (or click the banner button).

**`scapy` import errors on Windows**
Scapy requires the Npcap driver on Windows. Download from [npcap.com](https://npcap.com) and install before using `scapy`.

**PyInstaller build fails with `RecursionError`**
Add to the top of the spec file:
```python
import sys
sys.setrecursionlimit(5000)
```
