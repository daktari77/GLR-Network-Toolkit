# Configuration

## Hosts file

The Monitor tab loads host lists from plain `.txt` files. Each line is one target.

### Format reference

```
# Lines starting with # are comments

# --- ICMP ping (default) ---
192.168.1.1
google.com
10.0.0.1

# --- TCP port check ---
github.com TCP 443
192.168.1.1 TCP 22
myserver.local TCP 3389

# --- HTTP / HTTPS probe ---
google.com HTTPS
myapi.local HTTP 8080
myapi.local HTTP              # defaults to port 80

# --- CIDR subnet (ICMP on every host) ---
192.168.1.0/24
10.0.0.0/28

# --- IP range notation ---
192.168.1.1-50                # .1 through .50
10.0.0.100-200

# --- CIDR × TCP (all hosts, same port) ---
192.168.1.0/24 TCP 22

# --- Range × TCP ---
10.0.0.1-10 TCP 80
```

### Rules

- Duplicate hosts are silently deduplicated (first occurrence wins)
- Comments and blank lines are ignored
- `HTTPS` creates an HTTP probe with `https://` prefix auto-prepended
- Range notation supports `/N` CIDR and `start-end` shorthand; only the last octet is expanded in `start-end`
- Load via toolbar **Load Hosts…** or drop `config/hosts.txt` in place (reloads automatically on startup)

---

## settings.json

Auto-created at `config/settings.json` on first window close.

```json
{
  "last_hosts_file": "config/hosts.txt",
  "interval": 5,
  "theme": "dark",
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

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `last_hosts_file` | string | `""` | Absolute or relative path to the last loaded hosts file. Reloaded on startup if the file still exists. |
| `interval` | int | `5` | Seconds between polling cycles (1–300). |
| `theme` | string | `"dark"` | `"dark"` or `"light"`. Set via Monitor → Settings… → Appearance. |
| `alert_log_file` | string | `""` | Full path for the alert log. Empty = disabled. |
| `alert_webhook_url` | string | `""` | HTTP POST target. Empty = disabled. |
| `smtp_host` | string | `""` | SMTP server hostname. |
| `smtp_port` | int | `587` | SMTP port (STARTTLS). |
| `smtp_user` | string | `""` | SMTP username / login. |
| `smtp_password` | string | `""` | SMTP password (stored in plaintext). |
| `smtp_from` | string | `""` | Sender address in alert emails. |
| `smtp_to` | array | `[]` | List of recipient addresses. |

---

## Alert channels

All three channels fire **only on status transitions** (UP→DOWN or DOWN→UP), not on every probe result.

### Log file

One line per event:

```
2024-01-15 10:30:00 | 192.168.1.1 | DOWN | Connection timed out
2024-01-15 10:30:15 | 192.168.1.1 | UP   | 12.3ms
2024-01-15 11:45:02 | github.com  | DOWN | Name resolution failed
```

### Webhook

HTTP POST, `Content-Type: application/json`:

```json
{
  "host": "192.168.1.1",
  "status": "DOWN",
  "latency_ms": null,
  "error": "Connection timed out",
  "timestamp": "2024-01-15T10:30:00"
}
```

```json
{
  "host": "192.168.1.1",
  "status": "UP",
  "latency_ms": 12.3,
  "error": "",
  "timestamp": "2024-01-15T10:30:15"
}
```

### SMTP email

- Subject: `[GLR Monitor] <HOST> is <STATUS>`
- Body: host, status, latency/error, timestamp
- Transport: STARTTLS on port 587 (configurable)
- No TLS/SSL-only (port 465) support in current version

---

## Privilege matrix

| Feature | Without admin | With admin |
|---------|:------------:|:----------:|
| ICMP ping (subprocess) | ✓ | ✓ |
| TCP port check | ✓ | ✓ |
| HTTP / HTTPS probe | ✓ | ✓ |
| Traceroute (`tracert`) | ✓ | ✓ |
| Network Scanner (ICMP sweep) | ✓ | ✓ |
| ARP scan | — | ✓ |
| MAC / vendor lookup | — | ✓ |
| Raw ICMP socket | — | ✓ |

Click **Restart as Administrator** in the yellow banner to re-launch elevated. The banner is hidden when already running as admin.
