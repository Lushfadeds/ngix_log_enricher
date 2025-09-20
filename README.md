# ngix_log_enricher
Nginx log parser and data enricher work in progress

Setup
Create and activate a virtual enviroment
python -m venv .venv
# Windows: 
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt

Run
python nginx_log_enricher.py --in samples/access.log --out samples/enriched.json

On Windows PowerShell without activating .venv, you can also use:
& ".venv/Scripts/python.exe" "nginx_log_enricher.py" --in "samples/access.log" --out "samples/enriched.json"

Example Input

samples/access.log
127.0.0.1 - - [19/Sep/2025:10:05:23 +0000] "GET /index.html HTTP/1.1" 200 1024 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
203.0.113.9 - - [19/Sep/2025:10:07:11 +0000] "POST /login HTTP/1.1" 302 512 "https://example.com" "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"

Example Output
samples/enriched.json
[
  {
    "remote_addr": "127.0.0.1",
    "method": "GET",
    "path": "/index.html",
    "status": 200,
    "ua_browser": "Chrome",
    "ua_browser_version": "120.0.0",
    "ua_os": "Windows",
    "ua_os_version": "10",
    "ua_device": "Other",
    "ua_is_pc": true,
    "ua_is_mobile": false,
    "ua_is_bot": false
  }
]
ASSUMPTIONS
Assumed log format = Nginx combined

"-" → treated as missing

status/body_bytes_sent → integers; bytes "-" → 0

Keep time_local raw; add ISO timestamp

UA parsing via user-agents; fill None/False on failure

Skipped lines are logged & counted