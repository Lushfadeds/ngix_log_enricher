# ngix_log_enricher
Nginx log parser and data enricher work in progress

Setup

python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt

Run
python nginx_log_enricher.py --in samples/access.log --out samples/enriched.json
