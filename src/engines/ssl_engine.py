import socket
import ssl
from datetime import datetime
from src.models import SslResult


def run(host: str, port: int = 443, timeout: int = 10) -> SslResult:
    result = SslResult(host=host)
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()

                subject = dict(x[0] for x in cert.get("subject", []))
                result.subject = subject.get("commonName", "")

                issuer = dict(x[0] for x in cert.get("issuer", []))
                result.issuer = issuer.get("organizationName", "")

                not_after = cert.get("notAfter", "")
                result.expiry = not_after
                try:
                    expiry_dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                    result.days_remaining = (expiry_dt - datetime.utcnow()).days
                except Exception:
                    pass

                result.cipher = cipher[0] if cipher else ""
                result.valid = True
    except ssl.SSLCertVerificationError as e:
        result.error = f"Verification failed: {e}"
    except Exception as e:
        result.error = str(e)
    return result
