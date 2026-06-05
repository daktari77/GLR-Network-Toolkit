import socket
from src.models import WhoisResult


def _raw_whois(query: str) -> str:
    def _query(server: str, q: str) -> str:
        with socket.create_connection((server, 43), timeout=10) as s:
            s.sendall(f"{q}\r\n".encode())
            chunks = []
            while True:
                data = s.recv(4096)
                if not data:
                    break
                chunks.append(data.decode("utf-8", errors="replace"))
            return "".join(chunks)

    try:
        raw = _query("whois.iana.org", query)
        for line in raw.splitlines():
            if line.lower().startswith("refer:"):
                server = line.split(":", 1)[1].strip()
                try:
                    return _query(server, query)
                except Exception:
                    pass
        return raw
    except Exception as e:
        return f"Error: {e}"


def _parse_fields(raw: str) -> dict:
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith(("%", "#")):
            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()
            if key and value and key not in fields:
                fields[key] = value
    return fields


def run(query: str) -> WhoisResult:
    result = WhoisResult(query=query)
    try:
        import whois as python_whois
        w = python_whois.whois(query)
        result.registrar = str(w.registrar or "")
        cd = w.creation_date
        result.created = str(cd[0] if isinstance(cd, list) else cd or "")
        ed = w.expiration_date
        result.expires = str(ed[0] if isinstance(ed, list) else ed or "")
        ns = w.name_servers or []
        result.name_servers = sorted(ns) if isinstance(ns, (list, set)) else [str(ns)]
        result.raw = str(w.text or "")
    except ImportError:
        raw = _raw_whois(query)
        result.raw = raw
        fields = _parse_fields(raw)
        result.registrar = fields.get("registrar", "")
        result.created = fields.get("creation date", fields.get("created", ""))
        result.expires = fields.get("expiry date", fields.get("expiration date", fields.get("expires", "")))
        ns = fields.get("name server", "")
        result.name_servers = [ns] if ns else []
    except Exception as e:
        result.error = str(e)
        try:
            result.raw = _raw_whois(query)
        except Exception:
            pass
    return result
