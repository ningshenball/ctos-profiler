"""ctOS Profiler — Slice 2: demo state API. Localhost only."""

import json
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
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

app = FastAPI(title="ctOS Profiler")
app.mount("/static", StaticFiles(directory=WEB), name="static")


def load_demo():
    return json.loads(DEMO.read_text(encoding="utf-8"))


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


@app.get("/api/state")
def api_state():
    return STATE


@app.post("/api/demo")
def api_demo():
    global STATE
    STATE = load_demo()
    return STATE


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8787, reload=True)