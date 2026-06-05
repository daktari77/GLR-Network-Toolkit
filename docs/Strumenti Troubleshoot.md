# Strumenti Troubleshoot

> [!abstract]
> Hub di strumenti diagnostici di rete organizzati in sub-tab. Ogni tool riceve input da tastiera o dai menu contestuali degli altri tab.

---

## Sub-tab disponibili

| Tab | Funzione |
|-----|----------|
| [[#Traceroute]] | Hop-by-hop path verso un host |
| [[#DNS Lookup]] | Risoluzione forward, reverse, MX, CNAME |
| [[#HTTP Inspector]] | Headers, status code, tempo risposta |
| [[#SSL Checker]] | Certificato, scadenza, cipher |
| [[#Whois]] | Info registrar, date, name server |

---

## Traceroute

Esegue `tracert` di Windows e mostra i risultati hop per hop in **tempo reale**.

### Input
- **Host**: IP o hostname di destinazione
- **Trace**: avvia il traceroute
- **Stop**: interrompe

### Colonne

| Colonna | Descrizione |
|---------|-------------|
| Hop | Numero hop |
| IP | Indirizzo IP del router |
| Hostname | Hostname risolto (se disponibile) |
| RTT (ms) | Round-trip time |

> [!note]
> Hop con timeout mostrano `*` nell'IP e testo grigio. Sono normali — alcuni router non rispondono ai pacchetti TTL.

### Componente
`src/engines/traceroute_engine.py` — wrappa `tracert -h 30 -w 1000 <host>` e fa il parsing dell'output riga per riga in streaming.

---

## DNS Lookup

Risolve un hostname o IP tramite query DNS.

### Input
- **Query**: hostname (es. `google.com`) o IP per reverse lookup

### Risultati

| Campo | Descrizione |
|-------|-------------|
| A Records | Indirizzi IPv4 associati |
| PTR | Hostname per reverse lookup di un IP |
| MX | Mail server (richiede `dnspython`) |
| CNAME | Canonical name alias (richiede `dnspython`) |

> [!tip] MX e CNAME
> Per MX e CNAME installa `dnspython`:
> ```bash
> pip install dnspython
> ```
> Senza `dnspython`, A Records e PTR funzionano sempre con la stdlib.

### Componente
`src/engines/dns_engine.py`

---

## HTTP Inspector

Invia una richiesta GET e mostra i dettagli della risposta.

### Input
- **URL**: indirizzo completo o solo hostname (aggiunge `https://` automaticamente)
- **Follow redirects**: segue i redirect (default: attivo)

### Risultati
- **Header principale**: status code (verde < 400, rosso ≥ 400) + tempo risposta + URL finale
- **Tabella header**: tutti gli header di risposta

### Componente
`src/engines/http_inspector_engine.py` — usa `requests`

---

## SSL Checker

Verifica il certificato SSL/TLS di un server.

### Input
- **Host**: hostname del server (es. `google.com`)
- **Port**: porta (default: 443)

### Risultati

| Campo | Colore |
|-------|--------|
| Valid | — |
| Subject | — |
| Issuer | — |
| Expiry | — |
| Days remaining | Rosso < 30gg, Arancione < 90gg, Verde ≥ 90gg |
| Cipher | — |

> [!warning]
> Il campo **Days remaining** usa `datetime.utcnow()` — corretto per certificati con timezone UTC nel campo `notAfter`.

### Componente
`src/engines/ssl_engine.py` — usa solo `ssl` + `socket` dalla stdlib, nessuna dipendenza esterna.

---

## Whois

Ricerca informazioni di registrazione per un dominio o IP.

### Input
- **Query**: dominio (es. `example.com`) o IP

### Risultati
- **Tabella summary**: Registrar, Created, Expires, Name Servers
- **Raw output**: risposta whois completa

> [!note] Dipendenza opzionale
> Con `pip install python-whois`: parsing strutturato.
> Senza: query raw TCP diretta a `whois.iana.org:43` con follow dei riferimenti.

### Componente
`src/engines/whois_engine.py`

---

## Integrazione cross-tab

Tutti i sub-tool ricevono il target dai menu contestuali degli altri tab:

```
Click destro su host nel Monitor → "Send to Traceroute"
Click destro su IP nello Scanner → "Send to DNS Lookup"
```

Il tab Troubleshoot si attiva automaticamente e pre-compila il sub-tab corretto.

È anche possibile passare da un sub-tool all'altro manualmente cambiando tab e inserendo l'input.
