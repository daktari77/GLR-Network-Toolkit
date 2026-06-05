import socket
from src.models import DnsResult


def run(query: str) -> DnsResult:
    result = DnsResult(query=query)

    try:
        infos = socket.getaddrinfo(query, None, socket.AF_INET)
        result.a_records = list({info[4][0] for info in infos})
    except Exception as e:
        result.error = str(e)

    try:
        ptr = socket.gethostbyaddr(query)
        result.ptr_record = ptr[0]
    except Exception:
        pass

    try:
        import dns.resolver
        try:
            mx_ans = dns.resolver.resolve(query, "MX")
            result.mx_records = [str(r.exchange).rstrip(".") for r in mx_ans]
        except Exception:
            pass
        try:
            cname_ans = dns.resolver.resolve(query, "CNAME")
            result.cname_record = str(cname_ans[0].target).rstrip(".")
        except Exception:
            pass
    except ImportError:
        pass

    return result
