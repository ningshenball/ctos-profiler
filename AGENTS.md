# ctOS Profiler — agent rules

## What this is
Localhost LAN visibility for networks the operator owns.
FastAPI on 127.0.0.1:8787. Demo first. Live scan is ping + ARP + a frozen TCP list.

## Hard limits
- Private IPv4 only, prefix /24 or tighter.
- Live scan requires the authorization checkbox.
- No Nmap, no packet capture, no service banners, no public CIDRs.
- No scanning college, cafe, or anyone else's network.
- Bind stays 127.0.0.1.

## Two networks
- Use this LAN (/api/suggest) to fill the current NIC /24.
- Home Wi-Fi and a phone hotspot are different CIDRs.
- Snapshots are per CIDR: data/last-<slug>.json
- Those files are gitignored. Never commit them.
- Do not scan both ranges in one click. Scan the net you are on.

## Files
- app.py — API, STATE, suggest, ports list, snapshots
- scanner/discover.py — ping/ARP/TTL/adapter/SSID
- scanner/ports.py — frozen port list
- scanner/score.py — low/med/high
- scanner/history.py — NEW / CHANGED / same-MAC
- web/index.html — UI
- test/ — pytest

## How to change things
- Plan first. One task per edit.
- After edits: python -m pytest test -q
- Keep the Y2K README layout if you touch README.md
