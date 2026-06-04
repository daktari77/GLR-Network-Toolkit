import ipaddress

MAX_HOSTS = 1024


def expand_range(notation: str) -> list[str]:
    """Expand CIDR or IP-range notation into individual address strings.

    Accepted forms:
      - CIDR:        "192.168.1.0/24"
      - Full range:  "192.168.1.1-192.168.1.50"
      - Short range: "192.168.1.1-50"  (last-octet shorthand for IPv4)

    Raises ValueError for invalid notation or ranges exceeding MAX_HOSTS.
    """
    notation = notation.strip()

    if "/" in notation:
        net = ipaddress.ip_network(notation, strict=False)
        hosts = list(net.hosts())
        if not hosts:  # /32 single host
            hosts = [net.network_address]
        if len(hosts) > MAX_HOSTS:
            raise ValueError(
                f"Subnet contains {len(hosts):,} hosts; max allowed is {MAX_HOSTS}. "
                "Use a more specific prefix."
            )
        return [str(ip) for ip in hosts]

    if "-" in notation:
        dash = notation.index("-")
        start_str = notation[:dash].strip()
        end_str = notation[dash + 1 :].strip()

        try:
            start = ipaddress.ip_address(start_str)
        except ValueError as exc:
            raise ValueError(f"Invalid start address: {start_str!r}") from exc

        # Short form: only last octet supplied (IPv4 only)
        if "." not in end_str and ":" not in end_str:
            octets = start_str.rsplit(".", 1)
            if len(octets) != 2:
                raise ValueError(f"Short range not valid for address: {start_str!r}")
            try:
                end = ipaddress.ip_address(f"{octets[0]}.{end_str}")
            except ValueError as exc:
                raise ValueError(f"Invalid end octet: {end_str!r}") from exc
        else:
            try:
                end = ipaddress.ip_address(end_str)
            except ValueError as exc:
                raise ValueError(f"Invalid end address: {end_str!r}") from exc

        start_int, end_int = int(start), int(end)
        if end_int < start_int:
            raise ValueError(f"End address {end} is before start address {start}.")

        count = end_int - start_int + 1
        if count > MAX_HOSTS:
            raise ValueError(
                f"Range contains {count:,} hosts; max allowed is {MAX_HOSTS}."
            )
        return [str(ipaddress.ip_address(i)) for i in range(start_int, end_int + 1)]

    raise ValueError(
        f"Not a valid CIDR or IP-range notation: {notation!r}\n"
        "Examples: 192.168.1.0/24   10.0.0.1-50   10.0.0.1-10.0.0.100"
    )


def is_range_notation(token: str) -> bool:
    """Return True if *token* looks like CIDR or IP range notation."""
    t = token.strip()
    if "/" in t:
        try:
            ipaddress.ip_network(t, strict=False)
            return True
        except ValueError:
            return False
    if "-" in t:
        start_str = t.split("-", 1)[0].strip()
        try:
            ipaddress.ip_address(start_str)
            return True
        except ValueError:
            return False
    return False
