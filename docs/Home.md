---
tags: [indice, toolkit, rete]
aliases: [Home, Index]
---

# GLR Network Toolkit — Documentazione

Toolkit desktop per il monitoraggio e la diagnostica di rete su Windows. Basato su PyQt6, ispirato a NirSoft PingInfoView, esteso con scanner, port scanner e strumenti di troubleshoot.

---

## Moduli principali

| Tab | Funzione | Note |
|-----|----------|------|
| [[Monitor]] | Polling continuo ICMP/TCP/HTTP | Statistiche, alert, storico |
| [[Network Scanner]] | Discovery subnet/range | ARP richiede privilegi elevati |
| [[Port Scanner]] | Scan porte TCP | Modalità Common / Full / Custom |
| [[Strumenti Troubleshoot]] | Traceroute, DNS, HTTP, SSL, Whois | 5 sotto-tab |

---

## Avvio rapido

```bash
pip install -r requirements.txt
python main.py
```

Per ARP scan e lookup MAC/vendor: usare il pulsante **Riavvia come Amministratore** nel banner giallo.

---

## Navigazione vault

```
Home (questo file)
├── Architettura          — struttura file, threading, modelli dati
├── Monitor               — tab Monitor in dettaglio
├── Network Scanner       — tab Scanner in dettaglio
├── Port Scanner          — tab Port Scanner in dettaglio
├── Strumenti Troubleshoot — Traceroute · DNS · HTTP · SSL · Whois
├── Configurazione        — settings.json, formato hosts, alert, privilegi
└── Guida allo Sviluppo   — ambiente, pattern, aggiungere probe/engine
```

---

## Dipendenze

Obbligatorie (in `requirements.txt`):
- `PyQt6 >= 6.5`
- `requests >= 2.31`

Opzionali:
- `scapy` — ARP scan + MAC/vendor (admin)
- `dnspython` — record MX e CNAME in DNS
- `python-whois` — parsing Whois strutturato

---

## Build portable

```bash
pip install pyinstaller
pyinstaller GLR-Network-Toolkit.spec
# output: dist/GLR-Network-Toolkit/GLR-Network-Toolkit.exe
```
