# Network Scanner

> [!abstract]
> Discovery one-shot di host attivi su subnet, range IP o lista di indirizzi. Rileva hostname, MAC address (con privilegi elevati) e latenza ICMP.

---

## Utilizzo

1. Inserire il target nel campo **Target**
2. Click **Scan** (o Invio)
3. I risultati appaiono in tempo reale man mano che gli host vengono sondati
4. Click **Stop** per interrompere

---

## Formati target accettati

| Formato | Esempio | Note |
|---------|---------|------|
| CIDR | `192.168.1.0/24` | Espande in tutti gli host della subnet |
| Range ultimo ottetto | `192.168.1.1-254` | Da .1 a .254 |
| Range IP completo | `10.0.0.1-10.0.0.50` | |
| Lista separata da virgole | `192.168.1.1,192.168.1.5,10.0.0.1` | |
| IP singolo | `192.168.1.100` | |
| Hostname | `myserver.local` | |

---

## Colonne risultati

| Colonna | Descrizione |
|---------|-------------|
| IP | Indirizzo IPv4 |
| Hostname | Reverse DNS (se disponibile) |
| MAC | Indirizzo MAC (solo con admin + ARP) |
| Vendor | Produttore dalla OUI del MAC |
| Latency (ms) | RTT ICMP |
| Status | ALIVE / DOWN |

### Colori

| Colore | Significato |
|--------|-------------|
| Verde `#c8f7c5` | Host raggiungibile (ALIVE) |
| Rosso `#f7c5c5` | Host non risponde (DOWN) |

---

## ARP e MAC lookup

> [!warning] Richiede privilegi elevati
> L'ARP scan (che permette di rilevare MAC address e vendor) funziona **solo se l'app è avviata come Amministratore** e `scapy` è installato.
>
> Senza privilegi: MAC e Vendor saranno vuoti. Il banner giallo in cima alla finestra mostra il tasto **"Riavvia come Amministratore"**.

```bash
pip install scapy
```

Se `scapy` non è installato, il campo MAC rimane vuoto senza errori.

---

## Menu contestuale (click destro)

Disponibile su ogni riga della tabella dei risultati:

| Azione | Effetto |
|--------|---------|
| **Add to Monitor** | Aggiunge l'IP al tab [[Monitor]] come probe ICMP |
| **Send to Port Scanner** | Pre-compila [[Port Scanner]] con l'IP |
| **Send to Traceroute** | Apre [[Strumenti Troubleshoot#Traceroute]] sull'IP |
| **Send to DNS Lookup** | Apre [[Strumenti Troubleshoot#DNS Lookup]] sull'IP |
| **Copy IP** | Copia l'IP negli appunti |

---

## Componenti rilevanti

| File | Ruolo |
|------|-------|
| `src/engines/scanner_engine.py` | Engine backend (zero Qt) |
| `src/gui/panels/scanner_panel.py` | Widget tab |
| `src/gui/widgets/scan_result_table.py` | Tabella risultati con context menu |
| `src/utils/privileges.py` | Check admin per abilitare ARP |

---

## Performance

- **ThreadPoolExecutor** con max 128 worker
- Timeout ICMP: 1000 ms per host (configurabile nell'engine)
- Una subnet /24 (254 host) in circa 3–10 secondi a seconda della rete
- DNS reverse lookup in parallelo solo per host ALIVE
