"""Simple exposure badge from open ports. Not CVSS."""

from scanner.ports import PORTS


def score_host(ports: list[dict]) -> tuple[int, str, list[str]]:
    total = 0
    reasons = []
    names = {p["port"]: p["name"] for p in ports if p.get("state") == "open"}
    for port, name in names.items():
        _n, weight = PORTS.get(port, (name, 5))
        total += weight
        reasons.append(f"{name.upper()} exposed")
    if 23 in names:
        level = "high"
    elif total >= 40:
        level = "high"
    elif total >= 18:
        level = "medium"
    else:
        level = "low"
    return total, level, reasons