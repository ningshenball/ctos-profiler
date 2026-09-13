"""MAC vendor label. Randomized MACs called out. Optional online DB."""

from __future__ import annotations

LOCAL = {
    "080027": "Oracle VirtualBox",
    "B827EB": "Raspberry Pi",
    "DCA632": "Raspberry Pi",
    "E45F01": "Raspberry Pi",
    "DCB72E": "Xiaomi",
    "C6949E": "Xiaomi",
    "6AD483": "OPPO/Realme",
    "906717": "Alphion/router",
    "423F8C": "TP-Link",
}


def _norm(mac: str) -> str:
    return mac.replace(":", "").replace("-", "").upper()


def is_randomized(mac: str) -> bool:
    raw = _norm(mac)
    if len(raw) < 2:
        return False
    try:
        first = int(raw[0:2], 16)
    except ValueError:
        return False
    return bool(first & 0x02)


def vendor_of(mac: str) -> str:
    if not mac:
        return ""
    raw = _norm(mac)
    if is_randomized(mac) and raw[:6] not in LOCAL:
        return "randomized MAC"
    prefix = raw[:6]
    if prefix in LOCAL:
        return LOCAL[prefix]
    try:
        from mac_vendor_lookup import MacLookup

        name = MacLookup().lookup(mac)
        return name or ""
    except Exception:
        return ""