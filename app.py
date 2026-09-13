from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).parent
WEB = ROOT / "web"

app = FastAPI(title="ctOS Profiler")
app.mount("/static", StaticFiles(directory=WEB), name="static")

@app.get("/")
def index():
    return FileResponse(WEB / "index.html")

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8787, reload=True)