import base64
import json
import sys

import requests

if len(sys.argv) < 3:
    raise SystemExit("Uso: python test_local.py <pdf_path> <endpoint_url>")

pdf_path = sys.argv[1]
endpoint_url = sys.argv[2].rstrip("/")

with open(pdf_path, "rb") as f:
    pdf_b64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "file_name": pdf_path.split("/")[-1],
    "pdf_base64": pdf_b64,
}

r = requests.post(f"{endpoint_url}/extract-pdf-text", json=payload, timeout=180)
print(r.status_code)
print(json.dumps(r.json(), indent=2, ensure_ascii=False)[:4000])
