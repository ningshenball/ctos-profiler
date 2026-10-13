"""Short TCP connect checks on a frozen port list. Own-LAN hosts only."""

from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

PORTS = {
    21: ("ftp", 25),
    22: ("ssh", 10),
    23: ("telnet", 40),
    80: ("http", 8),
    135: ("rpc", 15),
    139: ("netbios", 15),
    443: ("https", 4),
    445: ("smb", 20),
    3389: ("rdp", 25),
    5900: ("vnc", 20),
    8080: ("http-alt", 8),
}


def _one(ip: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def probe(ip: str, cancel=None) -> list[dict]:
    found = []
    missed = []

    def stopped() -> bool:
        return cancel is not None and cancel.is_set()

    with ThreadPoolExecutor(max_workers=11) as pool:
        futs = {pool.submit(_one, ip, p, 0.5): p for p in PORTS}
        for fut in as_completed(futs):
            if stopped():
                break
            port = futs[fut]
            try:
                open_ = fut.result()
            except Exception:
                open_ = False
            if open_:
                name, _w = PORTS[port]
                found.append({"port": port, "name": name, "state": "open"})
            elif port in PORTS:
                missed.append(port)

    if missed and not stopped():
        with ThreadPoolExecutor(max_workers=11) as pool:
            futs = {pool.submit(_one, ip, p, 1.2): p for p in missed}
            for fut in as_completed(futs):
                if stopped():
                    break
                port = futs[fut]
                try:
                    open_ = fut.result()
                except Exception:
                    open_ = False
                if open_ and port in PORTS:
                    name, _w = PORTS[port]
                    found.append({"port": port, "name": name, "state": "open"})

    found.sort(key=lambda x: x["port"])
    return found