# GLR NetScope

> [!abstract] Panoramica
> Tool desktop **PyQt6** per il monitoraggio e il troubleshooting di reti. Ispirato a NirSoft PingInfoView, esteso con scanner di rete, port scanner e strumenti diagnostici avanzati.

---

## Moduli principali

| Tab | Funzione | Note |
|-----|----------|------|
| [[Monitor]] | Polling continuo ICMP/TCP/HTTP | Statistiche, alert, history |
| [[Network Scanner]] | Discovery one-shot di subnet/range | ARP con privilegi elevati |
| [[Port Scanner]] | Scansione porte TCP | Common / Full / Custom |
| [[Strumenti Troubleshoot]] | Traceroute, DNS, HTTP, SSL, Whois | Sub-tab dedicati |

---

## Avvio rapido

```bash
# Installa dipendenze
pip install -r requirements.txt

# Avvia
python main.py

# Avvia con privilegi elevati (ARP scan, MAC lookup)
# Usa il tasto "Riavvia come Amministratore" nel banner giallo
```

> [!warning] Privilegi elevati
> Alcune funzionalità ([[Network Scanner#ARP e MAC lookup]]) richiedono l'avvio come Amministratore su Windows. L'app mostra un banner giallo con il tasto di riavvio quando non è in modalità admin.

---

## Architettura

Vedi [[Architettura]] per la struttura completa del progetto, il modello di threading e i flussi dati.

---

## Sviluppo

Vedi [[Guida allo Sviluppo]] per:
- Aggiungere nuovi probe type
- Aggiungere nuovi engine di troubleshoot
- Configurazione alert (log, email, webhook)

---

## Link rapidi

- [[Architettura]]
- [[Monitor]]
- [[Network Scanner]]
- [[Port Scanner]]
- [[Strumenti Troubleshoot]]
- [[Guida allo Sviluppo]]
- [[Configurazione]]
