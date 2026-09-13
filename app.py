"""ctOS Profiler — Slice 3: fake authorized scan job. Localhost only."""

import json
import threading
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).parent
WEB = ROOT / "web"
DATA = ROOT / "data"
DEMO = DATA / "demo_hosts.json"

EMPTY = {
    "scan_id": None,
    "cidr": "",
    "status": "idle",
    "hosts": [],
    "log": ["[boot] ctOS profiler", "[gate] waiting for demo or authorized scan"],
}

STATE = dict(EMPTY)
CANCEL = threading.Event()
LOCK = threading.Lock()
JOB = None


def log_line(msg):
    STATE["log"] = (STATE.get("log") or [])[-180:] + [msg]


def load_demo():
    return json.loads(DEMO.read_text(encoding="utf-8"))


def fake_scan(cidr):
    demo = load_demo()
    hosts = demo.get("hosts") or []
    with LOCK:
        STATE["scan_id"] = "fake-" + str(int(time.time()))
        STATE["cidr"] = cidr
        STATE["status"] = "running"
        STATE["hosts"] = []
        log_line("[scan] authorized range " + cidr)
        log_line("[scan] fake profiler job (no packets sent)")
    for h in hosts:
        if CANCEL.is_set():
            with LOCK:
                STATE["status"] = "cancelled"
                log_line("[scan] cancelled")
            return
        time.sleep(0.7)
        with LOCK:
            STATE["hosts"] = STATE["hosts"] + [h]
            log_line("[node] " + h["ip"] + " " + (h.get("hostname") or ""))
    with LOCK:
        if not CANCEL.is_set():
            STATE["status"] = "done"
            log_line("[scan] complete · " + str(len(STATE["hosts"])) + " nodes")


app = FastAPI(title="ctOS Profiler")
app.mount("/static", StaticFiles(directory=WEB), name="static")


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


@app.get("/api/state")
def api_state():
    with LOCK:
        return dict(STATE)


@app.post("/api/demo")
def api_demo():
    global STATE
    with LOCK:
        STATE = load_demo()
    return STATE


@app.post("/api/scan")
def api_scan(body: dict):
    global JOB
    cidr = (body or {}).get("cidr") or ""
    authorized = bool((body or {}).get("authorized"))
    if not authorized:
        return JSONResponse({"error": "authorization required"}, status_code=400)
    if "/" not in cidr:
        return JSONResponse({"error": "cidr required"}, status_code=400)
    with LOCK:
        if STATE.get("status") == "running":
            return JSONResponse({"error": "scan already running"}, status_code=409)
    CANCEL.clear()
    JOB = threading.Thread(target=fake_scan, args=(cidr,), daemon=True)
    JOB.start()
    return {"ok": True}


@app.post("/api/cancel")
def api_cancel():
    CANCEL.set()
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8787, reload=True)