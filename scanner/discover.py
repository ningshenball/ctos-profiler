"""Own-LAN host discovery. Private IPv4 only. No exploit logic."""

from __future__ import annotations

import ipaddress
import os
import re
import socket
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

MAC_RE = re.compile(
    r"(\d{1,3}(?:\.\d{1,3}){3})\s+([0-9a-fA-F]{2}(?:[-:][0-9a-fA-F]{2}){5})"
)


def require_small_private(cidr: str) -> ipaddress.IPv4Network:
    net = ipaddress.ip_network(cidr.strip(), strict=False)
    if not isinstance(net, ipaddress.IPv4Network):
        raise ValueError("IPv4 only")
    if net.prefixlen < 24:
        raise ValueError("max range is /24")
    if not net.is_private:
        raise ValueError("private ranges only (192.168/10/172.16-31)")
    if net.num_addresses > 256:
        raise ValueError("range too large")
    return net


def local_ipv4() -> str | None:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()


def _ping(ip: str) -> bool:
    if os.name == "nt":
        cmd = ["ping", "-n", "1", "-w", "400", ip]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", ip]
    try:
        r = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _arp_table() -> dict[str, str]:
    try:
        raw = subprocess.check_output(["arp", "-a"], text=True, timeout=8, errors="ignore")
    except (OSError, subprocess.TimeoutExpired):
        return {}
    out = {}
    for ip, mac in MAC_RE.findall(raw):
        out[ip] = mac.replace("-", ":").upper()
    return out


def _hostname(ip: str) -> str:
    try:
        socket.setdefaulttimeout(0.4)
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except OSError:
        return ""


def discover(cidr: str, cancel: threading.Event, on_host, on_log) -> None:
    net = require_small_private(cidr)
    self_ip = local_ipv4()
    on_log(f"[scan] ping sweep {net} (own LAN only)")
    targets = [str(h) for h in net.hosts()]
    live: list[str] = []

    with ThreadPoolExecutor(max_workers=32) as pool:
        futs = {pool.submit(_ping, ip): ip for ip in targets}
        for fut in as_completed(futs):
            if cancel.is_set():
                on_log("[scan] cancelled")
                return
            ip = futs[fut]
            try:
                ok = fut.result()
            except Exception:
                ok = False
            if ok:
                live.append(ip)
                on_log(f"[ping] {ip}")

    table = _arp_table()
    for ip, mac in table.items():
        try:
            if ipaddress.ip_address(ip) in net and ip not in live:
                live.append(ip)
                on_log(f"[arp] {ip}")
        except ValueError:
            pass

    live = sorted(live, key=lambda x: tuple(int(p) for p in x.split(".")))
    live = [
        ip
        for ip in live
        if not ip.endswith(".255") and table.get(ip, "") != "FF:FF:FF:FF:FF:FF"
    ]

    for ip in live:
        if cancel.is_set():
            on_log("[scan] cancelled")
            return
        host = {
            "ip": ip,
            "mac": table.get(ip, ""),
            "vendor": "",
            "hostname": _hostname(ip),
            "ports": [],
            "score": 0,
            "level": "low",
            "reasons": [],
            "is_self": ip == self_ip,
        }
        on_host(host)
    on_log(f"[scan] complete · {len(live)} nodes")