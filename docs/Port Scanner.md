# Port Scanner

> [!abstract]
> Scansione TCP di porte su un singolo host. Supporta modalità Common (~100 porte note), Full (1–65535) e Custom (range/lista personalizzata). Classifica le porte come open, filtered o closed con rilevamento automatico del servizio e banner grab.

---

## Utilizzo

1. Inserire l'host nel campo **Host**
2. Scegliere la modalità porte
3. Click **Scan**
4. Risultati in tempo reale con progress bar
5. Click **Stop** per interrompere

---

## Modalità di scansione

| Modalità | Porte | Uso consigliato |
|----------|-------|-----------------|
| **Common (~100)** | ~100 porte più usate | Ricognizione rapida |
| **Full (1-65535)** | Tutte le 65535 porte | Audit completo |
| **Custom range** | Definite dall'utente | Target specifico |

### Sintassi Custom

```
80                    → porta singola
80,443                → due porte
8080-8090             → range
22,80,443,8080-8090   → combinazione
```

---

## Classificazione stati

| Stato | Colore | Significato |
|-------|--------|-------------|
| **open** | Verde `#c8f7c5` | Connessione accettata |
| **filtered** | Giallo `#fff3cd` | Timeout — firewall o host non risponde |
| **closed** | Default | Connection refused (ECONNREFUSED) |

> [!tip]
> Le porte **closed** sono nascoste di default. Usa il checkbox **"Show closed"** per visualizzarle.

---

## Colonne risultati

| Colonna | Descrizione |
|---------|-------------|
| Port | Numero porta |
| State | open / filtered / closed |
| Service | Nome servizio (da `socket.getservbyport`) |
| Banner | Prima risposta del servizio (max 200 char) |

---

## Menu contestuale (click destro)

| Azione | Disponibile | Effetto |
|--------|-------------|---------|
| **Copy port** | Sempre | Copia il numero porta negli appunti |
| **Open in browser** | Porte 80/443/8080/8443 | Apre `http(s)://host:port` nel browser |
| **Add to Monitor as TCP** | Porte open | Aggiunge al [[Monitor]] come probe TCP |

---

## Porte Common incluse

Categorie coperte:

- File transfer: FTP (20/21), SFTP/SSH (22), TFTP (69)
- Mail: SMTP (25/465/587), POP3 (110/995), IMAP (143/993)
- Web: HTTP (80/8080/8000), HTTPS (443/8443/8888)
- Database: MySQL (3306), PostgreSQL (5432), MSSQL (1433), Oracle (1521), MongoDB (27017), Redis (6379), Elasticsearch (9200)
- Remote: RDP (3389), VNC (5900), Telnet (23)
- SMB/Windows: 135/139/445
- Container/K8s: Docker (2375/2376), K8s API (6443), kubelet (10250)
- Message queue: Kafka (9092), RabbitMQ (5672/15672), AMQP (5671)
- Monitoraggio: Prometheus (9090), Grafana (3000), Kibana (5601)

---

## Performance

- **ThreadPoolExecutor** max 200 worker
- Scansione in batch da 500 porte (interrompibile tra batch)
- Timeout default: 500 ms per porta
- Full scan (65535 porte): ~5–15 minuti a seconda del timeout e della rete
- Common scan (~100 porte): < 5 secondi

---

## Componenti rilevanti

| File | Ruolo |
|------|-------|
| `src/engines/port_scanner_engine.py` | Engine backend TCP |
| `src/gui/panels/port_scanner_panel.py` | Widget tab |
| `src/gui/widgets/port_result_table.py` | Tabella con filtro closed e context menu |
