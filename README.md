# pdf-text-extractor

Microservicio en FastAPI para extraer texto nativo de PDFs digitales usando PyMuPDF.

## Qué hace

Expone un endpoint:

- `GET /health`
- `POST /extract-pdf-text`

Entrada:

```json
{
  "file_name": "pedido.pdf",
  "pdf_base64": "JVBERi0xLjcK..."
}
```

Salida:

```json
{
  "ok": true,
  "file_name": "pedido.pdf",
  "method": "native_pdf_text_pymupdf",
  "num_pages": 2,
  "text": "...",
  "text_length": 12345,
  "truncated": false
}
```

## Ejecutar en local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Healthcheck:

```bash
curl http://localhost:8080/health
```

## Probar el endpoint

Ejemplo con Python:

```python
import base64
import json
import requests

with open("pedido.pdf", "rb") as f:
    pdf_b64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "file_name": "pedido.pdf",
    "pdf_base64": pdf_b64,
}

r = requests.post("http://localhost:8080/extract-pdf-text", json=payload, timeout=120)
print(r.status_code)
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
```

## Despliegue en Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/pdf-text-extractor

gcloud run deploy pdf-text-extractor \
  --image gcr.io/PROJECT_ID/pdf-text-extractor \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

## Integración desde Apps Script

```javascript
function extraerTextoPdfDesdeServicio_(fileId, endpointUrl) {
  const file = DriveApp.getFileById(fileId);
  const blob = file.getBlob();
  const pdfBase64 = Utilities.base64Encode(blob.getBytes());

  const payload = {
    file_name: file.getName(),
    pdf_base64: pdfBase64
  };

  const response = UrlFetchApp.fetch(endpointUrl + "/extract-pdf-text", {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });

  const code = response.getResponseCode();
  const body = response.getContentText();

  if (code < 200 || code >= 300) {
    throw new Error("Error extractor PDF (" + code + "): " + body);
  }

  const parsed = JSON.parse(body);
  return parsed.text || "";
}
```

## Siguiente capa recomendada

1. extracción nativa de texto
2. prompt desde Google Sheets (`Prompts`)
3. identificación de cliente y headers
4. posterior paso a rutas deterministas por cliente/formato
