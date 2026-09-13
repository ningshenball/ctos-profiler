<div align="center">
  <img src="noelle.gif" height="140" alt="noelle"/>
  <h1>ctOS Profiler</h1>
  <p>Local authorized LAN visibility tool. <b>Localhost only.</b></p>
  <img src="construction.gif" alt="under construction"/>
</div>
<br/>
<details>
  <summary><b>Ethical Use Disclaimer( -_•)</b></summary>
  <br/>
  <p align="center">
    <b>Demo first. Real scans ONLY on networks you own or have written permission to test.</b><br/>
    Educational / authorized local analysis only. Unauthorized scanning is illegal.<br/>
    ദ്ദി◝ ⩊ ◜.ᐟ
  </p>
</details>
<br/>
<h3>★ About <img src="ralsei.webp" height="50" alt=""/></h3>
<b>ctOS Profiler</b> is a localhost Watch Dogs–style profiler.
Start in demo mode, then scan a private /24 you actually own.
Ping + ARP + a short TCP list. No Nmap engine. No packet capture. No exploits.

<h3>★ Features <img src="explode.webp" height="38" alt=""/></h3>
✦ <b>Localhost only</b> — binds to 127.0.0.1:8787<br/>
✦ <b>Demo mode first</b> — fake hosts before anything live<br/>
✦ <b>Auth gate</b> — checkbox + private /24 cap (public ranges rejected)<br/>
✦ <b>Live grid</b> — vendor, ports, low/med/high badge, profile drawer<br/>
✦ <b>Export JSON</b> — last scan as a file<br/>
✦ <b>/docs</b> — FastAPI OpenAPI for the scan body

<h3>★ Built With</h3>
<p>
  <img src="https://skillicons.dev/icons?i=python,fastapi" />
</p>

<h3>★ How to Run <img src="cupcake.webp" height="58" alt=""/></h3>

```powershell
git clone https://github.com/ningshenball/ctos-profiler.git
cd ctos-profiler
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:8787

Docs: http://127.0.0.1:8787/docs
Bash# linux / mac
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
★ Tests
PowerShellpython -m pytest test/test_cidr.py -q
