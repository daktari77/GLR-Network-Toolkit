# Configurazione

---

## File di configurazione

### `config/settings.json`

Creato automaticamente alla prima chiusura dell'app. Contiene:

```json
{
  "last_hosts_file": "config/hosts.txt",
  "interval": 5,
  "alert_log_file": "",
  "alert_webhook_url": "",
  "smtp_host": "",
  "smtp_port": 587,
  "smtp_user": "",
  "smtp_password": "",
  "smtp_from": "",
  "smtp_to": []
}
```

| Campo | Descrizione | Default |
|-------|-------------|---------|
| `last_hosts_file` | Percorso ultimo file hosts caricato | `""` |
| `interval` | Secondi tra cicli di polling | `5` |
| `alert_log_file` | Path file log alert (vuoto = disabilitato) | `""` |
| `alert_webhook_url` | URL webhook POST | `""` |
| `smtp_host` | Server SMTP | `""` |
| `smtp_port` | Porta SMTP | `587` |
| `smtp_user` | Username SMTP | `""` |
| `smtp_password` | Password SMTP | `""` |
| `smtp_from` | Mittente email | `""` |
| `smtp_to` | Lista destinatari | `[]` |

---

## Alert

Configurabili da **Monitor → Settings…**

### Log file

Ogni transizione di stato viene appesa al file di log in formato:

```
2024-01-15 10:30:00 | 192.168.1.1 | DOWN | Connection refused
2024-01-15 10:30:05 | 192.168.1.1 | UP   | 12.3ms
```

### Webhook

Invia un POST HTTP con body JSON:

```json
{
  "host": "192.168.1.1",
  "status": "DOWN",
  "latency_ms": null,
  "error": "Connection refused",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Email SMTP

Richiede un server SMTP accessibile. Supporta STARTTLS (porta 587).

---

## Formato file hosts

Vedi [[Monitor#Formato file hosts]] per la sintassi completa.

---

## Dipendenze Python

### Obbligatorie

```
PyQt6
requests
```

### Opzionali

| Pacchetto | Funzionalità abilitata |
|-----------|----------------------|
| `scapy` | ARP scan + MAC lookup in [[Network Scanner]] |
| `dnspython` | MX e CNAME lookup in [[Strumenti Troubleshoot#DNS Lookup]] |
| `python-whois` | Parsing strutturato Whois |

```bash
# Installa tutto
pip install PyQt6 requests scapy dnspython python-whois
```

---

## Privilegi di sistema

Vedi [[Architettura#Gestione privilegi]] per i dettagli tecnici.

| Funzionalità | Senza admin | Con admin |
|--------------|-------------|-----------|
| ICMP ping | ✅ (subprocess) | ✅ |
| TCP port scan | ✅ | ✅ |
| HTTP/HTTPS probe | ✅ | ✅ |
| Traceroute | ✅ (subprocess tracert) | ✅ |
| ARP scan | ❌ MAC vuoto | ✅ |
| Raw ICMP socket | ❌ | ✅ |
