import time
from src.models import HttpInspectResult

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


def run(url: str, follow_redirects: bool = True, timeout: int = 10) -> HttpInspectResult:
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    if not _HAS_REQUESTS:
        return HttpInspectResult(url=url, error="requests library not available")
    try:
        start = time.perf_counter()
        resp = _requests.get(url, allow_redirects=follow_redirects, timeout=timeout)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return HttpInspectResult(
            url=resp.url,
            status_code=resp.status_code,
            response_time_ms=round(elapsed_ms, 1),
            headers=dict(resp.headers),
        )
    except Exception as e:
        return HttpInspectResult(url=url, error=str(e))
