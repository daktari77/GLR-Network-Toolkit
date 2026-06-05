# Monitor

> [!abstract]
> Polling continuo di host con probe ICMP, TCP e HTTP. Mostra statistiche in tempo reale, storico per host e può inviare alert su cambio di stato.

---

## Interfaccia

### Toolbar

| Azione | Funzione |
|--------|----------|
| **Load Hosts…** | Carica lista host da file `.txt` |
| **＋ Add** | Aggiunge singolo host via dialog |
| **＋ Add Range…** | Aggiunge range/subnet (es. `192.168.1.0/24`) |
| **－ Remove** | Rimuove host selezionato |
| **▶ Start** | Avvia ciclo di polling |
| **■ Stop** | Ferma il polling |
| **Interval (s)** | Secondi tra un ciclo e l'altro (1–300) |
| **Export CSV…** | Esporta risultati correnti in CSV |
| **Settings…** | Configura alert (log, SMTP, webhook) |

### Colonne tabella

| Colonna | Descrizione |
|---------|-------------|
| Host | IP o hostname |
| Type | ICMP / TCP / HTTP |
| Target | Porta target (TCP/HTTP) |
| Status | UP / DOWN / UNKNOWN |
| Last (ms) | Latenza ultimo probe |
| Avg (ms) | Media latenze |
| Min (ms) | Minimo storico |
| Max (ms) | Massimo storico |
| Loss % | Percentuale pacchetti persi |
| Sent | Probe totali inviati |
| Last Check | Timestamp ultimo probe |
| Error | Messaggio errore ultimo probe |

### Colori

| Colore | Significato |
|--------|-------------|
| Verde `#c8f7c5` | Host UP |
| Rosso `#f7c5c5` | Host DOWN |
| Grigio `#f0f0f0` | Stato UNKNOWN |

### Pannello storia

Click su una riga → pannello inferiore mostra lo storico dei probe per quell'host (ultimi N risultati).

---

## Formato file hosts

```
# Commento — riga ignorata
192.168.1.1              # ICMP ping
google.com               # ICMP ping
github.com TCP 443       # TCP check sulla porta 443
mysite.com HTTPS         # HTTP probe con https://
myapi.internal HTTP 8080 # HTTP probe su porta 8080
192.168.1.1-50           # Range — espande in 50 host ICMP
10.0.0.0/24              # Subnet CIDR — espande in 254 host
```

---

## Alert

Configurabili da **Settings…** → [[Configurazione#Alert]].

Tipi supportati:
- **Log file** — append riga per ogni transizione UP↔DOWN
- **Email SMTP** — invia email su DOWN/UP
- **Webhook** — POST JSON su URL configurato

> [!note]
> Gli alert scattano solo sulle **transizioni** di stato (UP→DOWN o DOWN→UP), non ad ogni probe.

---

## Menu contestuale (click destro)

Disponibile su ogni riga della tabella:

- **Send to Port Scanner** → pre-compila [[Port Scanner]] con l'IP selezionato
- **Send to Traceroute** → apre [[Strumenti Troubleshoot#Traceroute]] sull'host
- **Send to DNS Lookup** → apre [[Strumenti Troubleshoot#DNS Lookup]] sull'host

---

## Componenti rilevanti

| File | Ruolo |
|------|-------|
| `src/gui/panels/monitor_panel.py` | Widget principale del tab |
| `src/gui/host_table.py` | QTableWidget con 12 colonne |
| `src/gui/history_table.py` | Tabella storico probe |
| `src/monitor.py` | Engine background (ThreadPoolExecutor) |
| `src/probers/icmp.py` | subprocess ping → latency |
| `src/probers/tcp.py` | socket.connect_ex() |
| `src/probers/http.py` | requests.get() |
