"""ctOS Profiler — authorized private-LAN discovery. Localhost UI."""

import json
import threading
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from scanner.discover import discover, require_small_private

ROOT = Path(__file__).parent
WEB = ROOT / "web"
DATA = ROOT / "data"
DEMO = DATA / "demo_hosts.json"
LAST = DATA / "last_scan.json"

EMPTY = {
    "scan_id": None,
    "cidr": "",
    "status": "idle",
    "hosts": [],
    "log": ["[boot] ctOS profiler", "[gate] private /24 only · authorization required"],
}

STATE = dict(EMPTY)
CANCEL = threading.Event()
LOCK = threading.Lock()


def log_line(msg: str) -> None:
    STATE["log"] = (STATE.get("log") or [])[-180:] + [msg]


def add_host(host: dict) -> None:
    STATE["hosts"] = STATE["hosts"] + [host]


def load_demo():
    return json.loads(DEMO.read_text(encoding="utf-8"))


def save_last() -> None:
    DATA.mkdir(exist_ok=True)
    LAST.write_text(json.dumps(STATE, indent=2), encoding="utf-8")


def run_discover(cidr: str) -> None:
    try:
        with LOCK:
            STATE["scan_id"] = "live-" + str(int(time.time()))
            STATE["cidr"] = cidr
            STATE["status"] = "running"
            STATE["hosts"] = []
            log_line("[scan] authorized range " + cidr)

        def on_host(h):
            with LOCK:
                add_host(h)

        def on_log(m):
            with LOCK:
                log_line(m)

        discover(cidr, CANCEL, on_host, on_log)
        with LOCK:
            if CANCEL.is_set():
                STATE["status"] = "cancelled"
            elif STATE["status"] == "running":
                STATE["status"] = "done"
            save_last()
    except Exception as exc:
        with LOCK:
            STATE["status"] = "error"
            log_line("[error] " + str(exc))


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
        save_last()
    return STATE


@app.post("/api/scan")
def api_scan(body: dict):
    cidr = (body or {}).get("cidr") or ""
    authorized = bool((body or {}).get("authorized"))
    if not authorized:
        return JSONResponse({"error": "authorization required"}, status_code=400)
    try:
        require_small_private(cidr)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    with LOCK:
        if STATE.get("status") == "running":
            return JSONResponse({"error": "scan already running"}, status_code=409)
    CANCEL.clear()
    threading.Thread(target=run_discover, args=(cidr,), daemon=True).start()
    return {"ok": True}


@app.post("/api/cancel")
def api_cancel():
    CANCEL.set()
    return {"ok": True}


@app.get("/api/export")
def api_export():
    with LOCK:
        payload = dict(STATE)
    return JSONResponse(
        payload,
        headers={"Content-Disposition": "attachment; filename=ctos-scan.json"},
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8787, reload=True)