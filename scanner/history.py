"""Diff this scan against the last saved scan. Own-LAN snapshots only."""

from __future__ import annotations


def annotate(hosts: list[dict], previous: dict | None) -> list[dict]:
    old = {h.get("ip"): h for h in (previous or {}).get("hosts") or [] if h.get("ip")}
    macs: dict[str, int] = {}
    for h in hosts:
        mac = (h.get("mac") or "").upper()
        if mac:
            macs[mac] = macs.get(mac, 0) + 1

    out = []
    for h in hosts:
        row = dict(h)
        ip = row.get("ip")
        prev = old.get(ip)
        if not prev:
            row["flag"] = "new" if old else ""
        else:
            old_p = {p.get("port") for p in prev.get("ports") or []}
            new_p = {p.get("port") for p in row.get("ports") or []}
            row["flag"] = "changed" if old_p != new_p else ""
        mac = (row.get("mac") or "").upper()
        row["mac_peers"] = macs.get(mac, 1) if mac else 1
        out.append(row)
    return out